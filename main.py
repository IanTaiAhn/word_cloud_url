"""
main.py - FastAPI REST endpoints for URL scraping service
"""

import os
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

# Import our scraping module
from scraper import scrape_url_with_progress, validate_url, ScrapingError, get_memory_usage

app = FastAPI(
    title="URL Scraper API",
    description="Asynchronous URL scraping service with progress tracking",
    version="1.0.0"
)

# Redis setup with fallback to memory storage
def get_redis_client():
    """Initialize Redis client with fallback to None"""
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        r.ping()  # Test connection
        print("✅ Connected to Redis")
        return r
    except (redis.ConnectionError, redis.TimeoutError):
        print("❌ Redis not available, using in-memory storage")
        return None

# Initialize storage
redis_client = get_redis_client()
USE_REDIS = redis_client is not None
memory_jobs: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class URLRequest(BaseModel):
    url: str

class JobResponse(BaseModel):
    job_id: str
    status: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    memory_mb: Optional[float] = None
    updated_at: str

class JobResult(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Job management functions
def create_job(job_id: str, url: str) -> Dict[str, Any]:
    """Create a new job record"""
    job_data = {
        'job_id': job_id,
        'url': url,
        'status': 'pending',
        'progress': 0,
        'message': 'Job queued for processing',
        'result': None,
        'error': None,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'memory_mb': round(get_memory_usage(), 2)
    }
    
    if USE_REDIS:
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))  # 1 hour TTL
    else:
        memory_jobs[job_id] = job_data
    
    return job_data

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve job data by ID"""
    if USE_REDIS:
        job_json = redis_client.get(f"job:{job_id}")
        return json.loads(job_json) if job_json else None
    else:
        return memory_jobs.get(job_id)

def update_job_status(job_id: str, status: str, progress: int, message: str, result=None, error=None):
    """Update job status - this is the callback function for the scraper"""
    job = get_job(job_id)
    if not job:
        return
    
    job.update({
        'status': status,
        'progress': progress,
        'message': message,
        'updated_at': datetime.now().isoformat(),
        'memory_mb': round(get_memory_usage(), 2)
    })
    
    if result is not None:
        job['result'] = result
    if error is not None:
        job['error'] = error
    
    if USE_REDIS:
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job))
    else:
        memory_jobs[job_id] = job

def delete_job(job_id: str):
    """Delete a job record"""
    if USE_REDIS:
        redis_client.delete(f"job:{job_id}")
    else:
        memory_jobs.pop(job_id, None)

# Background scraping function
def run_scraping_job(job_id: str, url: str):
    """Run the scraping job in a background thread"""
    try:
        # Create progress callback that updates job status
        def progress_callback(status: str, progress: int, message: str):
            update_job_status(job_id, status, progress, message)
        
        # Run the scraping
        result = scrape_url_with_progress(url, progress_callback, job_id)
        
        # Update with final result
        update_job_status(
            job_id, 
            'completed', 
            100, 
            'Scraping completed successfully!', 
            result=result
        )
        
    except ScrapingError as e:
        update_job_status(
            job_id, 
            'failed', 
            0, 
            'Scraping failed', 
            error=str(e)
        )
    except Exception as e:
        update_job_status(
            job_id, 
            'failed', 
            0, 
            'Unexpected error occurred', 
            error=f"Unexpected error: {str(e)}"
        )

# API Endpoints
@app.post("/start-process/", response_model=JobResponse)
async def start_process(request: URLRequest):
    """
    Start a new scraping job
    
    - **url**: The URL to scrape (must start with http:// or https://)
    """
    # Validate URL
    if not validate_url(request.url):
        raise HTTPException(
            status_code=400, 
            detail="Invalid URL. Must start with http:// or https:// and contain a domain."
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    create_job(job_id, request.url)
    
    # Start background scraping thread
    thread = threading.Thread(
        target=run_scraping_job, 
        args=(job_id, request.url),
        daemon=True
    )
    thread.start()
    
    return JobResponse(job_id=job_id, status="started")

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the current status of a scraping job
    
    - **job_id**: The unique job identifier returned by /start-process/
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatus(
        job_id=job_id,
        status=job['status'],
        progress=job['progress'],
        message=job['message'],
        memory_mb=job.get('memory_mb'),
        updated_at=job['updated_at']
    )

@app.get("/result/{job_id}", response_model=JobResult)
async def get_job_result(job_id: str):
    """
    Get the final result of a completed scraping job
    
    - **job_id**: The unique job identifier returned by /start-process/
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job['status'] == 'completed':
        return JobResult(success=True, result=job['result'])
    elif job['status'] == 'failed':
        return JobResult(success=False, error=job['error'])
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Job not completed yet. Current status: {job['status']} ({job['progress']}%)"
        )

@app.delete("/jobs/{job_id}")
async def delete_job_endpoint(job_id: str):
    """
    Delete a job record (cleanup)
    
    - **job_id**: The unique job identifier to delete
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    delete_job(job_id)
    return {"message": f"Job {job_id} deleted successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint with system information
    """
    return {
        'status': 'healthy',
        'memory_mb': round(get_memory_usage(), 2),
        'redis_connected': USE_REDIS,
        'active_jobs': len(memory_jobs) if not USE_REDIS else "unknown",
        'timestamp': datetime.now().isoformat()
    }

@app.get("/jobs")
async def list_jobs():
    """
    List all active jobs (for debugging)
    """
    if USE_REDIS:
        # Get all job keys from Redis
        job_keys = redis_client.keys("job:*")
        jobs = []
        for key in job_keys:
            job_data = redis_client.get(key)
            if job_data:
                job = json.loads(job_data)
                jobs.append({
                    'job_id': job['job_id'],
                    'status': job['status'],
                    'progress': job['progress'],
                    'url': job['url'],
                    'created_at': job['created_at']
                })
        return {'jobs': jobs, 'count': len(jobs)}
    else:
        jobs = [
            {
                'job_id': job['job_id'],
                'status': job['status'],
                'progress': job['progress'],
                'url': job['url'],
                'created_at': job['created_at']
            }
            for job in memory_jobs.values()
        ]
        return {'jobs': jobs, 'count': len(jobs)}

# Root endpoint
@app.get("/")
async def root():
    """
    API information
    """
    return {
        "service": "URL Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "start_process": "POST /start-process/",
            "check_status": "GET /status/{job_id}",
            "get_result": "GET /result/{job_id}",
            "health_check": "GET /health",
            "list_jobs": "GET /jobs"
        },
        "docs": "/docs"
    }