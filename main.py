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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
import logging
from scraper import scrape_url
from preprocess import clean_text
from topic_model import model_topics
from visualization import generate_wordclouds_html, generate_full_html_page

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This will output to console/Render logs
    ]
)

# Create logger instance
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 1: Define a request model
class URLRequest(BaseModel):
    url: HttpUrl

# Response models for better API documentation
class ProcessResponse(BaseModel):
    success: bool
    html_content: str
    url: str
    num_documents: int
    num_topics: int

class ErrorResponse(BaseModel):
    success: bool
    error: str
    url: str

@app.post("/process/")
async def process_url_json(data: URLRequest):
    """
    Process URL and return JSON response with HTML content.
    This avoids protocol errors that can occur with HTMLResponse.
    """
    try:
        # Convert Pydantic HttpUrl to string
        url_str = str(data.url)
        logger.info(f"🚀 Starting to process URL: {url_str}")
        
        # Step 1: Scraping
        logger.info("📡 Step 1: Starting web scraping...")
        raw_text = scrape_url(url_str, headless=True, timeout=30, max_content_length=8000)
        logger.info(f"✅ Scraping completed. Text length: {len(raw_text)} characters")
        
        # Check if scraping failed
        if raw_text.startswith("[Timeout]") or raw_text.startswith("[Error]"):
            logger.error(f"❌ Scraping failed: {raw_text}")
            raise HTTPException(status_code=400, detail=f"Scraping failed: {raw_text}")
        
        # Step 2: Text cleaning
        logger.info("🧹 Step 2: Cleaning text...")
        docs = clean_text(raw_text)
        logger.info(f"✅ Text cleaning completed. Number of documents: {len(docs)}")
        
        if not docs or len(docs) == 0:
            raise HTTPException(status_code=400, detail="No valid documents found after cleaning")
        
        # Step 3: Dynamic topic modeling based on document count
        logger.info("🔍 Step 3: Running topic modeling...")
        
        # Calculate appropriate number of clusters
        n_docs = len(docs)
        if n_docs == 1:
            n_clusters = 1
            logger.info(f"Single document detected. Using {n_clusters} cluster.")
        elif n_docs < 5:
            n_clusters = n_docs
            logger.info(f"Few documents ({n_docs}). Using {n_clusters} clusters.")
        else:
            n_clusters = min(5, n_docs)
            logger.info(f"Multiple documents ({n_docs}). Using {n_clusters} clusters.")
        
        topics, _ = model_topics(docs, n_clusters=n_clusters)
        logger.info(f"✅ Topic modeling completed. Number of topics: {len(topics) if topics else 0}")
        
        if not topics:
            raise HTTPException(status_code=400, detail="No topics generated from the text")
        
        # Step 4: Generate wordclouds
        logger.info("☁️ Step 4: Generating wordclouds...")
        wordclouds = generate_wordclouds_html(topics)
        logger.info(f"✅ Wordclouds generated. Number of wordclouds: {len(wordclouds) if wordclouds else 0}")
        
        # Step 5: Generate HTML page
        logger.info("📄 Step 5: Generating HTML page...")
        html_page = generate_full_html_page(
            url=url_str,  # Pass string version
            wordclouds=wordclouds,
            topics=topics,
            num_documents=len(docs)
        )
        logger.info("✅ HTML page generation completed")
        
        # Return successful JSON response
        return {
            "success": True,
            "html_content": html_page,
            "url": url_str,
            "num_documents": len(docs),
            "num_topics": len(topics) if topics else 0
        }
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Log the full error details
        url_str = str(data.url) if hasattr(data, 'url') else 'unknown'
        logger.error(f"❌ Error processing URL {url_str}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Raise HTTPException for proper error handling
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

# @app.post("/process/", response_model=ProcessResponse)
# async def process_url_json(data: URLRequest):
#     """
#     Process URL and return JSON response with HTML content.
#     This avoids protocol errors that can occur with HTMLResponse.
#     """
#     try:
#         # Convert Pydantic HttpUrl to string
#         url_str = str(data.url)
#         logger.info(f"🚀 Starting to process URL: {url_str}")
        
#         # Step 1: Scraping
#         logger.info("📡 Step 1: Starting web scraping...")
#         raw_text = scrape_url(url_str, headless=True, timeout=30, max_content_length=8000)
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
        
#         # Return JSON response instead of HTMLResponse
#         return JSONResponse(
#             content={
#                 "success": True,
#                 "html_content": html_page,
#                 "url": url_str,
#                 "num_documents": len(docs),
#                 "num_topics": len(topics) if topics else 0
#             },
#             status_code=200
#         )
        
#     except Exception as e:
#         # Log the full error details
#         url_str = str(data.url) if hasattr(data, 'url') else 'unknown'
#         logger.error(f"❌ Error processing URL {url_str}: {str(e)}")
#         logger.error(f"Error type: {type(e).__name__}")
#         import traceback
#         logger.error(f"Full traceback: {traceback.format_exc()}")
        
#         # Return JSON error response
#         return JSONResponse(
#             content={
#                 "success": False,
#                 "error": str(e),
#                 "url": url_str
#             },
#             status_code=400
#         )

# Updated home page with modified JavaScript
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Topic Analysis Tool</title>
        <style>
            body { 
                font-family: 'Segoe UI', sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0;
            }
            .form-container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                backdrop-filter: blur(10px);
                max-width: 500px;
                width: 90%;
            }
            h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            input[type="url"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 16px;
                margin-bottom: 20px;
                box-sizing: border-box;
            }
            button {
                width: 100%;
                padding: 15px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            button:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h1>🔍 Topic Analysis Tool</h1>
            <form id="urlForm">
                <input type="url" id="urlInput" placeholder="Enter URL to analyze..." required>
                <button type="submit">Analyze Topics</button>
            </form>
        </div>
        
        <script>
                    // Improved script with timeout handling and better UX
            document.getElementById('urlForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('urlInput').value;
                const button = e.target.querySelector('button');
                const originalButtonText = button.textContent;
                
                // Validate URL before processing
                if (!isValidUrl(url)) {
                    showError('Please enter a valid URL');
                    return;
                }
                
                // Create progress indicator
                const progressDiv = createProgressIndicator();
                button.parentNode.insertBefore(progressDiv, button.nextSibling);
                
                button.textContent = '🔄 Starting analysis...';
                button.disabled = true;
                
                // Set up timeout controller
                const controller = new AbortController();
                const timeoutId = setTimeout(() => {
                    controller.abort();
                }, 120000); // 2 minute timeout
                
                let progressInterval;
                
                try {
                    // Start progress animation
                    startProgressAnimation(progressDiv, button);
                    
                    const response = await fetch('/process/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json',
                            'Cache-Control': 'no-cache'
                        },
                        body: JSON.stringify({url: url}),
                        signal: controller.signal
                    });
                    
                    clearTimeout(timeoutId);
                    
                    if (response.ok) {
                        const data = await response.json();
                        if (data.success) {
                            updateProgress(progressDiv, '✅ Complete! Loading results...');
                            
                            // Smooth transition to results
                            setTimeout(() => {
                                document.body.innerHTML = data.html_content;
                            }, 500);
                        } else {
                            throw new Error(data.error || data.detail || 'Failed to analyze URL');
                        }
                    } else {
                        // Handle different HTTP status codes
                        let errorMessage;
                        try {
                            const errorData = await response.json();
                            errorMessage = errorData.detail || errorData.error || `Server error (${response.status})`;
                        } catch {
                            errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                        }
                        throw new Error(errorMessage);
                    }
                    
                } catch (error) {
                    clearTimeout(timeoutId);
                    console.error('Error:', error);
                    
                    let userMessage;
                    if (error.name === 'AbortError') {
                        userMessage = '⏱️ Request timed out. The URL might be taking too long to process. Please try a simpler page or try again later.';
                    } else if (error.message.includes('fetch')) {
                        userMessage = '🌐 Network error. Please check your connection and try again.';
                    } else if (error.message.includes('timeout')) {
                        userMessage = '⏱️ The server is taking too long to respond. Please try again.';
                    } else {
                        userMessage = `❌ ${error.message}`;
                    }
                    
                    showError(userMessage);
                    resetButton(button, originalButtonText);
                    
                } finally {
                    // Clean up
                    if (progressInterval) clearInterval(progressInterval);
                    if (progressDiv && progressDiv.parentNode) {
                        progressDiv.parentNode.removeChild(progressDiv);
                    }
                }
            });
            
            // Helper functions
            function isValidUrl(string) {
                try {
                    new URL(string);
                    return string.startsWith('http://') || string.startsWith('https://');
                } catch (_) {
                    return false;
                }
            }
            
            function createProgressIndicator() {
                const div = document.createElement('div');
                div.style.cssText = `
                    margin: 10px 0;
                    padding: 15px;
                    background: #f0f8ff;
                    border: 1px solid #4a90e2;
                    border-radius: 8px;
                    font-family: monospace;
                    font-size: 14px;
                    color: #2c5aa0;
                `;
                div.innerHTML = `
                    <div style="margin-bottom: 8px;">📊 Processing your URL...</div>
                    <div style="background: #e0e0e0; height: 6px; border-radius: 3px; overflow: hidden;">
                        <div id="progressBar" style="background: #4a90e2; height: 100%; width: 0%; transition: width 0.3s;"></div>
                    </div>
                    <div id="progressText" style="margin-top: 8px; font-size: 12px;">Initializing...</div>
                `;
                return div;
            }
            
            function startProgressAnimation(progressDiv, button) {
                const progressBar = progressDiv.querySelector('#progressBar');
                const progressText = progressDiv.querySelector('#progressText');
                
                const steps = [
                    { width: '10%', text: '🕷️ Scraping content...', buttonText: '🔄 Scraping website...' },
                    { width: '30%', text: '🧹 Cleaning text...', buttonText: '🔄 Processing text...' },
                    { width: '50%', text: '🔍 Analyzing topics...', buttonText: '🔄 Finding topics...' },
                    { width: '70%', text: '☁️ Generating wordclouds...', buttonText: '🔄 Creating visualizations...' },
                    { width: '90%', text: '📄 Building results page...', buttonText: '🔄 Almost done...' }
                ];
                
                let currentStep = 0;
                
                const interval = setInterval(() => {
                    if (currentStep < steps.length) {
                        const step = steps[currentStep];
                        progressBar.style.width = step.width;
                        progressText.textContent = step.text;
                        button.textContent = step.buttonText;
                        currentStep++;
                    } else {
                        clearInterval(interval);
                    }
                }, 8000); // Update every 8 seconds
                
                return interval;
            }
            
            function updateProgress(progressDiv, message) {
                const progressBar = progressDiv.querySelector('#progressBar');
                const progressText = progressDiv.querySelector('#progressText');
                progressBar.style.width = '100%';
                progressText.textContent = message;
            }
            
            function showError(message) {
                // Create or update error message
                let errorDiv = document.getElementById('errorMessage');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.id = 'errorMessage';
                    errorDiv.style.cssText = `
                        margin: 15px 0;
                        padding: 15px;
                        background: #ffe6e6;
                        border: 1px solid #ff4444;
                        border-radius: 8px;
                        color: #cc0000;
                        font-weight: bold;
                    `;
                    document.getElementById('urlForm').appendChild(errorDiv);
                }
                
                errorDiv.textContent = message;
                
                // Auto-hide after 10 seconds
                setTimeout(() => {
                    if (errorDiv && errorDiv.parentNode) {
                        errorDiv.parentNode.removeChild(errorDiv);
                    }
                }, 10000);
            }
            
            function resetButton(button, originalText) {
                setTimeout(() => {
                    button.textContent = originalText;
                    button.disabled = false;
                }, 3000);
            }
        </script>
    </body>
    </html>
    """)
            
            # document.getElementById('urlForm').addEventListener('submit', async (e) => {
            #     e.preventDefault();
            #     const url = document.getElementById('urlInput').value;
            #     const button = e.target.querySelector('button');
                
            #     button.textContent = '🔄 Analyzing...';
            #     button.disabled = true;
                
            #     try {
            #         const response = await fetch('/process/', {
            #             method: 'POST',
            #             headers: {
            #                 'Content-Type': 'application/json',
            #                 'Accept': 'application/json'
            #             },
            #             body: JSON.stringify({url: url})
            #         });
                    
            #         if (response.ok) {
            #             const data = await response.json();
            #             if (data.success) {
            #                 // Replace the page content with the returned HTML
            #                 document.body.innerHTML = data.html_content;
            #             } else {
            #                 throw new Error(data.error || 'Failed to analyze URL');
            #             }
            #         } else {
            #             const errorData = await response.json();
            #             throw new Error(errorData.error || 'Failed to analyze URL');
            #         }
            #     } catch (error) {
            #         console.error('Error:', error);
            #         button.textContent = '❌ Error - Try Again';
            #         button.disabled = false;
            #         setTimeout(() => {
            #             button.textContent = 'Analyze Topics';
            #         }, 2000);
            #     }
            # });


@app.post("/test/")
async def test_endpoint(data: URLRequest):
    return {"received_url": data.url}


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

