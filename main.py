# # Put this at the VERY TOP of app/main.py
# print("=== SCRIPT STARTED ===")

# import sys
# import os

# print(f"Python path: {sys.path}")
# print(f"Current directory: {os.getcwd()}")
# print(f"PORT env var: {os.environ.get('PORT', 'NOT SET')}")

# try:
#     from fastapi import FastAPI
#     print("✓ FastAPI imported")
# except Exception as e:
#     print(f"✗ FastAPI import failed: {e}")
#     sys.exit(1)

# try:    
#     import uvicorn
#     print("✓ Uvicorn imported")
# except Exception as e:
#     print(f"✗ Uvicorn import failed: {e}")
#     sys.exit(1)

# print("=== CREATING APP ===")
# app = FastAPI()
# print("✓ App created")

# @app.get("/")
# def root():
#     return {"message": "Hello World"}

# print("✓ Routes defined")
####################################
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel, HttpUrl
# print("✓ FastAPI imports successful")

# from scraper import scrape_url
# print("✓ scraper import successful")

# from preprocess import clean_text
# print("✓ preprocess import successful")

# from topic_model import model_topics
# print("✓ topic_model import successful")

# from visualization import generate_wordclouds, test_wordcloud_generation, generate_wordclouds_html
# print("✓ visualization import successful")
###############################################
# ##testing...##
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
from scraper import scrape_url
from preprocess import clean_text
from topic_model import model_topics
from visualization import generate_wordclouds_html, generate_full_html_page

app = FastAPI()

# Add CORS middleware immediately after creating the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://iantaiahn.github.io"],  # Replace with your actual GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 1: Define a request model
class URLRequest(BaseModel):
    url: HttpUrl


# If you prefer HTML word clouds (much lighter):
@app.post("/process_small/")
async def process_url_html(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    topics, _ = model_topics(docs, n_clusters=5)
    wordclouds = generate_wordclouds_html(topics)
    
    return {
        "wordclouds": wordclouds,
        "topics": topics,
        "num_documents": len(docs)
    }

# Updated endpoint that returns complete HTML page
@app.post("/process/", response_class=HTMLResponse)
async def process_url_html(data: URLRequest):
    try:
        # Your existing processing
        raw_text = scrape_url(data.url)
        docs = clean_text(raw_text)
        topics, _ = model_topics(docs, n_clusters=5)
        wordclouds = generate_wordclouds_html(topics)
        
        # Generate complete HTML page
        html_page = generate_full_html_page(
            url=data.url,
            wordclouds=wordclouds,
            topics=topics,
            num_documents=len(docs)
        )
        
        return HTMLResponse(content=html_page, status_code=200)
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial; padding: 20px; text-align: center;">
            <h1>❌ Error Processing URL</h1>
            <p>Sorry, we couldn't process the URL: <strong>{data.url}</strong></p>
            <p>Error: {str(e)}</p>
            <a href="/" style="color: #007bff;">← Try Another URL</a>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)


# Optional: Add a simple form page for URL input
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
            document.getElementById('urlForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('urlInput').value;
                const button = e.target.querySelector('button');
                
                button.textContent = '🔄 Analyzing...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/process/', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    
                    if (response.ok) {
                        const html = await response.text();
                        document.body.innerHTML = html;
                    } else {
                        throw new Error('Failed to analyze URL');
                    }
                } catch (error) {
                    button.textContent = '❌ Error - Try Again';
                    button.disabled = false;
                    setTimeout(() => {
                        button.textContent = 'Analyze Topics';
                    }, 2000);
                }
            });
        </script>
    </body>
    </html>
    """)

@app.post("/test/")
async def test_endpoint(data: URLRequest):
    return {"received_url": data.url}

