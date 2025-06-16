# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse
# from pydantic import BaseModel, HttpUrl
# import logging
# from scraper import scrape_url
# from preprocess import clean_text
# from topic_model import model_topics
# from visualization import generate_wordclouds_html, generate_full_html_page
# main.py
import uuid
import os
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="URL Processor", version="1.0.0")

# Pydantic model for request
class URLRequest(BaseModel):
    url: HttpUrl

# In-memory storage for results (use Redis in production for multiple instances)
class ResultStore:
    def __init__(self):
        self.store: Dict[str, dict] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.max_age = 3600  # 1 hour
    
    def store_result(self, html_content: str, url: str) -> str:
        result_id = str(uuid.uuid4())
        self.store[result_id] = {
            'html': html_content,
            'url': url,
            'created_at': datetime.now(),
            'accessed': False
        }
        logger.info(f"📦 Stored result {result_id} for URL: {url}")
        return result_id
    
    def get_result(self, result_id: str) -> Optional[dict]:
        if result_id in self.store:
            result = self.store[result_id]
            result['accessed'] = True
            logger.info(f"📤 Retrieved result {result_id}")
            return result
        return None
    
    def remove_result(self, result_id: str):
        if result_id in self.store:
            del self.store[result_id]
            logger.info(f"🗑️ Removed result {result_id}")
    
    def cleanup_old_results(self):
        """Remove old results to prevent memory leaks"""
        now = datetime.now()
        to_remove = []
        
        for result_id, data in self.store.items():
            age = now - data['created_at']
            # Remove if older than max_age or if accessed and older than 5 minutes
            if age > timedelta(seconds=self.max_age) or (data['accessed'] and age > timedelta(seconds=300)):
                to_remove.append(result_id)
        
        for result_id in to_remove:
            self.remove_result(result_id)
        
        if to_remove:
            logger.info(f"🧹 Cleaned up {len(to_remove)} old results")

# Global result store
result_store = ResultStore()

# Background task for cleanup
async def periodic_cleanup():
    while True:
        await asyncio.sleep(result_store.cleanup_interval)
        result_store.cleanup_old_results()

# Start cleanup task when app starts
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_cleanup())
    logger.info("🚀 App started, cleanup task initialized")

# Health check endpoint for Render
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Main processing endpoint - now returns redirect
@app.post("/process/")
async def process_url_redirect(data: URLRequest, background_tasks: BackgroundTasks):
    try:
        url_str = str(data.url)
        logger.info(f"🚀 Starting to process URL: {url_str}")
        
        # Step 1: Scraping
        logger.info("📡 Step 1: Starting web scraping...")
        # Import your scraping function here
        # raw_text = scrape_url(url_str, headless=True, timeout=30, max_content_length=15000)
        raw_text = f"Sample scraped content from {url_str}"  # Placeholder
        logger.info(f"✅ Scraping completed. Text length: {len(raw_text)} characters")
        
        # Check if scraping failed
        if raw_text.startswith("[Timeout]") or raw_text.startswith("[Error]"):
            logger.error(f"❌ Scraping failed: {raw_text}")
            raise Exception(f"Scraping failed: {raw_text}")
        
        # Step 2: Text cleaning
        logger.info("🧹 Step 2: Cleaning text...")
        # docs = clean_text(raw_text)
        docs = [raw_text]  # Placeholder
        logger.info(f"✅ Text cleaning completed. Number of documents: {len(docs)}")
        
        if not docs or len(docs) == 0:
            raise Exception("No valid documents found after cleaning")
        
        # Step 3: Dynamic topic modeling
        logger.info("🔍 Step 3: Running topic modeling...")
        n_docs = len(docs)
        if n_docs == 1:
            n_clusters = 1
        elif n_docs < 5:
            n_clusters = n_docs
        else:
            n_clusters = min(5, n_docs)
        
        # topics, _ = model_topics(docs, n_clusters=n_clusters)
        topics = [f"Topic {i+1}" for i in range(n_clusters)]  # Placeholder
        logger.info(f"✅ Topic modeling completed. Number of topics: {len(topics)}")
        
        if not topics:
            raise Exception("No topics generated from the text")
        
        # Step 4: Generate wordclouds
        logger.info("☁️ Step 4: Generating wordclouds...")
        # wordclouds = generate_wordclouds_html(topics)
        wordclouds = ["<div>Wordcloud 1</div>", "<div>Wordcloud 2</div>"]  # Placeholder
        logger.info(f"✅ Wordclouds generated. Number of wordclouds: {len(wordclouds)}")
        
        # Step 5: Generate HTML page
        logger.info("📄 Step 5: Generating HTML page...")
        html_page = generate_full_html_page(
            url=url_str,
            wordclouds=wordclouds,
            topics=topics,
            num_documents=len(docs)
        )
        logger.info("✅ HTML page generation completed")
        
        # Store the result and get unique ID
        result_id = result_store.store_result(html_page, url_str)
        
        # Schedule cleanup of this specific result after 1 hour
        background_tasks.add_task(delayed_cleanup, result_id)
        
        logger.info(f"✅ Processing completed. Redirecting to result page: {result_id}")
        
        # Return redirect response
        return RedirectResponse(url=f"/result/{result_id}", status_code=303)
        
    except Exception as e:
        url_str = str(data.url) if hasattr(data, 'url') else 'unknown'
        logger.error(f"❌ Error processing URL {url_str}: {str(e)}")
        
        # Create error result and redirect to it
        error_html = generate_error_html(url_str, str(e))
        result_id = result_store.store_result(error_html, url_str)
        
        return RedirectResponse(url=f"/result/{result_id}", status_code=303)

# Result display endpoint
@app.get("/result/{result_id}", response_class=HTMLResponse)
async def get_result(result_id: str):
    logger.info(f"📤 Retrieving result: {result_id}")
    
    result = result_store.get_result(result_id)
    if not result:
        logger.warning(f"❌ Result not found: {result_id}")
        return HTMLResponse(
            content=generate_not_found_html(),
            status_code=404
        )
    
    # Set headers for better compatibility
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-Content-Type-Options": "nosniff"
    }
    
    return HTMLResponse(
        content=result['html'], 
        status_code=200,
        headers=headers
    )

# Background task for delayed cleanup
async def delayed_cleanup(result_id: str):
    await asyncio.sleep(3600)  # Wait 1 hour
    result_store.remove_result(result_id)

# Home page with form
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=generate_home_html())

# Utility functions for HTML generation
def generate_full_html_page(url: str, wordclouds: list, topics: list, num_documents: int) -> str:
    """Generate the full HTML page with results"""
    wordclouds_html = "\n".join(wordclouds) if wordclouds else "<p>No wordclouds generated</p>"
    topics_html = "\n".join([f"<li>{topic}</li>" for topic in topics]) if topics else "<li>No topics found</li>"
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Analysis Results</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ background: #007bff; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            .section {{ background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }}
            .wordclouds {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
            .back-link {{ display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Analysis Complete!</h1>
                <p><strong>URL:</strong> {url}</p>
                <p><strong>Documents processed:</strong> {num_documents}</p>
                <p><strong>Topics found:</strong> {len(topics)}</p>
            </div>
            
            <div class="section">
                <h2>🔍 Topics Discovered</h2>
                <ul>{topics_html}</ul>
            </div>
            
            <div class="section">
                <h2>☁️ Word Clouds</h2>
                <div class="wordclouds">
                    {wordclouds_html}
                </div>
            </div>
            
            <a href="/" class="back-link">← Analyze Another URL</a>
        </div>
    </body>
    </html>
    """

def generate_error_html(url: str, error: str) -> str:
    """Generate error HTML page"""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Error Processing URL</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; text-align: center; }}
            .error-container {{ max-width: 600px; margin: 50px auto; padding: 20px; }}
            .error-box {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 20px; border-radius: 8px; }}
            .back-link {{ display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-box">
                <h1>❌ Error Processing URL</h1>
                <p>Sorry, we couldn't process the URL:</p>
                <p><strong>{url}</strong></p>
                <p><strong>Error:</strong> {error}</p>
            </div>
            <a href="/" class="back-link">← Try Another URL</a>
        </div>
    </body>
    </html>
    """

def generate_not_found_html() -> str:
    """Generate not found HTML page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Result Not Found</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; text-align: center; }
            .container { max-width: 600px; margin: 50px auto; padding: 20px; }
            .back-link { display: inline-block; margin-top: 20px; color: #007bff; text-decoration: none; }
            .back-link:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Result Not Found</h1>
            <p>The result you're looking for has expired or doesn't exist.</p>
            <p>Results are automatically cleaned up after 1 hour for security.</p>
            <a href="/" class="back-link">← Go Back Home</a>
        </div>
    </body>
    </html>
    """

def generate_home_html() -> str:
    """Generate home page HTML"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>URL Processor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
            .container { max-width: 600px; margin: 50px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .form-group { margin: 20px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="url"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            .loading { display: none; margin-top: 10px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 URL Processor</h1>
            <p>Enter a URL to analyze its content and generate topic models with word clouds.</p>
            
            <form id="urlForm" method="post" action="/process/">
                <div class="form-group">
                    <label for="url">Website URL:</label>
                    <input type="url" id="url" name="url" required placeholder="https://example.com">
                </div>
                <button type="submit">🚀 Analyze URL</button>
                <div class="loading" id="loading">⏳ Processing... This may take a moment.</div>
            </form>
        </div>
        
        <script>
            document.getElementById('urlForm').addEventListener('submit', function() {
                document.getElementById('loading').style.display = 'block';
            });
        </script>
    </body>
    </html>
    """




##############old prod code below#######################


# # Set up logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler()  # This will output to console/Render logs
#     ]
# )

# # Create logger instance
# logger = logging.getLogger(__name__)

# app = FastAPI()

# # Step 1: Define a request model
# class URLRequest(BaseModel):
#     url: HttpUrl

# @app.post("/process/", response_class=HTMLResponse)
# async def process_url_html_new(data: URLRequest):
#     try:
#         # Convert Pydantic HttpUrl to string
#         url_str = str(data.url)
#         logger.info(f"🚀 Starting to process URL: {url_str}")
        
#         # Step 1: Scraping
#         logger.info("📡 Step 1: Starting web scraping...")
#         raw_text = scrape_url(url_str, headless=True, timeout=30, max_content_length=15000)
#         logger.info(f"✅ Scraping completed. Text length: {len(raw_text)} characters")
        
#         # Check if scraping failed
#         if raw_text.startswith("[Timeout]") or raw_text.startswith("[Error]"):
#             logger.error(f"❌ Scraping failed: {raw_text}")
#             raise Exception(f"Scraping failed: {raw_text}")
        
#         # Step 2: Text cleaning
#         logger.info("🧹 Step 2: Cleaning text...")
#         docs = clean_text(raw_text)
#         logger.info(f"✅ Text cleaning completed. Number of documents: {len(docs)}")
        
#         if not docs or len(docs) == 0:
#             raise Exception("No valid documents found after cleaning")
        
#         # Step 3: Dynamic topic modeling based on document count
#         logger.info("🔍 Step 3: Running topic modeling...")
        
#         # Calculate appropriate number of clusters
#         n_docs = len(docs)
#         if n_docs == 1:
#             n_clusters = 1
#             logger.info(f"Single document detected. Using {n_clusters} cluster.")
#         elif n_docs < 5:
#             n_clusters = n_docs
#             logger.info(f"Few documents ({n_docs}). Using {n_clusters} clusters.")
#         else:
#             n_clusters = min(5, n_docs)
#             logger.info(f"Multiple documents ({n_docs}). Using {n_clusters} clusters.")
        
#         topics, _ = model_topics(docs, n_clusters=n_clusters)
#         logger.info(f"✅ Topic modeling completed. Number of topics: {len(topics) if topics else 0}")
        
#         if not topics:
#             raise Exception("No topics generated from the text")
        
#         # Step 4: Generate wordclouds
#         logger.info("☁️ Step 4: Generating wordclouds...")
#         wordclouds = generate_wordclouds_html(topics)
#         logger.info(f"✅ Wordclouds generated. Number of wordclouds: {len(wordclouds) if wordclouds else 0}")
        
#         # Step 5: Generate HTML page
#         logger.info("📄 Step 5: Generating HTML page...")
#         html_page = generate_full_html_page(
#             url=url_str,  # Pass string version
#             wordclouds=wordclouds,
#             topics=topics,
#             num_documents=len(docs)
#         )
#         logger.info("✅ HTML page generation completed")
        
#         return HTMLResponse(content=html_page, status_code=200)
        
#     except Exception as e:
#         # Log the full error details
#         url_str = str(data.url) if hasattr(data, 'url') else 'unknown'
#         logger.error(f"❌ Error processing URL {url_str}: {str(e)}")
#         logger.error(f"Error type: {type(e).__name__}")
#         import traceback
#         logger.error(f"Full traceback: {traceback.format_exc()}")
        
#         error_html = f"""
#         <!DOCTYPE html>
#         <html>
#         <head><title>Error</title></head>
#         <body style="font-family: Arial; padding: 20px; text-align: center;">
#             <h1>❌ Error Processing URL</h1>
#             <p>Sorry, we couldn't process the URL: <strong>{url_str}</strong></p>
#             <p><strong>Error:</strong> {str(e)}</p>
#             <a href="/" style="color: #007bff;">← Try Another URL</a>
#         </body>
#         </html>
#         """
#         return HTMLResponse(content=error_html, status_code=400)

# # @app.post("/process_local/", response_class=HTMLResponse)
# # async def process_url_html_new(data: URLRequest):
# #     try:
# #         # Convert Pydantic HttpUrl to string
# #         url_str = str(data.url)
# #         logger.info(f"🚀 Starting to process URL: {url_str}")
        
# #         # Step 1: Scraping
# #         logger.info("📡 Step 1: Starting web scraping...")
# #         raw_text = scrape_url_local(url_str, headless=True, timeout=30, ignore_ssl=True)  # Pass string, not HttpUrl object
# #         logger.info(f"✅ Scraping completed. Text length: {len(raw_text)} characters")
        
# #         # Check if scraping failed
# #         if raw_text.startswith("[Timeout]") or raw_text.startswith("[Error]"):
# #             logger.error(f"❌ Scraping failed: {raw_text}")
# #             raise Exception(f"Scraping failed: {raw_text}")
        
# #         # Step 2: Text cleaning
# #         logger.info("🧹 Step 2: Cleaning text...")
# #         docs = clean_text(raw_text)
# #         logger.info(f"✅ Text cleaning completed. Number of documents: {len(docs)}")
        
# #         if not docs or len(docs) == 0:
# #             raise Exception("No valid documents found after cleaning")
        
# #         # Step 3: Dynamic topic modeling based on document count
# #         logger.info("🔍 Step 3: Running topic modeling...")
        
# #         # Calculate appropriate number of clusters
# #         n_docs = len(docs)
# #         if n_docs == 1:
# #             n_clusters = 1
# #             logger.info(f"Single document detected. Using {n_clusters} cluster.")
# #         elif n_docs < 5:
# #             n_clusters = n_docs
# #             logger.info(f"Few documents ({n_docs}). Using {n_clusters} clusters.")
# #         else:
# #             n_clusters = min(5, n_docs)
# #             logger.info(f"Multiple documents ({n_docs}). Using {n_clusters} clusters.")
        
# #         topics, _ = model_topics(docs, n_clusters=n_clusters)
# #         logger.info(f"✅ Topic modeling completed. Number of topics: {len(topics) if topics else 0}")
        
# #         if not topics:
# #             raise Exception("No topics generated from the text")
        
# #         # Step 4: Generate wordclouds
# #         logger.info("☁️ Step 4: Generating wordclouds...")
# #         wordclouds = generate_wordclouds_html(topics)
# #         logger.info(f"✅ Wordclouds generated. Number of wordclouds: {len(wordclouds) if wordclouds else 0}")
        
# #         # Step 5: Generate HTML page
# #         logger.info("📄 Step 5: Generating HTML page...")
# #         html_page = generate_full_html_page(
# #             url=url_str,  # Pass string version
# #             wordclouds=wordclouds,
# #             topics=topics,
# #             num_documents=len(docs)
# #         )
# #         logger.info("✅ HTML page generation completed")
        
# #         return HTMLResponse(content=html_page, status_code=200)
        
# #     except Exception as e:
# #         # Log the full error details
# #         url_str = str(data.url) if hasattr(data, 'url') else 'unknown'
# #         logger.error(f"❌ Error processing URL {url_str}: {str(e)}")
# #         logger.error(f"Error type: {type(e).__name__}")
# #         import traceback
# #         logger.error(f"Full traceback: {traceback.format_exc()}")
        
# #         error_html = f"""
# #         <!DOCTYPE html>
# #         <html>
# #         <head><title>Error</title></head>
# #         <body style="font-family: Arial; padding: 20px; text-align: center;">
# #             <h1>❌ Error Processing URL</h1>
# #             <p>Sorry, we couldn't process the URL: <strong>{url_str}</strong></p>
# #             <p><strong>Error:</strong> {str(e)}</p>
# #             <a href="/" style="color: #007bff;">← Try Another URL</a>
# #         </body>
# #         </html>
# #         """
# #         return HTMLResponse(content=error_html, status_code=400)


# # Optional: Add a simple form page for URL input
# @app.get("/", response_class=HTMLResponse)
# async def home():
#     return HTMLResponse(content="""
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Topic Analysis Tool</title>
#         <style>
#             body { 
#                 font-family: 'Segoe UI', sans-serif; 
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 min-height: 100vh;
#                 display: flex;
#                 align-items: center;
#                 justify-content: center;
#                 margin: 0;
#             }
#             .form-container {
#                 background: rgba(255, 255, 255, 0.95);
#                 padding: 40px;
#                 border-radius: 15px;
#                 box-shadow: 0 20px 40px rgba(0,0,0,0.1);
#                 backdrop-filter: blur(10px);
#                 max-width: 500px;
#                 width: 90%;
#             }
#             h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
#             input[type="url"] {
#                 width: 100%;
#                 padding: 15px;
#                 border: 2px solid #e9ecef;
#                 border-radius: 8px;
#                 font-size: 16px;
#                 margin-bottom: 20px;
#                 box-sizing: border-box;
#             }
#             button {
#                 width: 100%;
#                 padding: 15px;
#                 background: linear-gradient(45deg, #667eea, #764ba2);
#                 color: white;
#                 border: none;
#                 border-radius: 8px;
#                 font-size: 18px;
#                 cursor: pointer;
#                 transition: all 0.3s ease;
#             }
#             button:hover { transform: translateY(-2px); }
#         </style>
#     </head>
#     <body>
#         <div class="form-container">
#             <h1>🔍 Topic Analysis Tool</h1>
#             <form id="urlForm">
#                 <input type="url" id="urlInput" placeholder="Enter URL to analyze..." required>
#                 <button type="submit">Analyze Topics</button>
#             </form>
#         </div>
        
#         <script>
#             document.getElementById('urlForm').addEventListener('submit', async (e) => {
#                 e.preventDefault();
#                 const url = document.getElementById('urlInput').value;
#                 const button = e.target.querySelector('button');
                
#                 button.textContent = '🔄 Analyzing...';
#                 button.disabled = true;
                
#                 try {
#                     const response = await fetch('/process/', {
#                         method: 'POST',
#                         headers: {'Content-Type': 'application/json'},
#                         body: JSON.stringify({url: url})
#                     });
                    
#                     if (response.ok) {
#                         const html = await response.text();
#                         document.body.innerHTML = html;
#                     } else {
#                         throw new Error('Failed to analyze URL');
#                     }
#                 } catch (error) {
#                     button.textContent = '❌ Error - Try Again';
#                     button.disabled = false;
#                     setTimeout(() => {
#                         button.textContent = 'Analyze Topics';
#                     }, 2000);
#                 }
#             });
#         </script>
#     </body>
#     </html>
#     """)

# @app.post("/test/")
# async def test_endpoint(data: URLRequest):
#     return {"received_url": data.url}

