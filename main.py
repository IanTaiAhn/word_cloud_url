# main.py (root file)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.scraper import scrape_url
from app.preprocess import clean_text
from app.topic_model import model_topics
from app.visualization import generate_wordclouds

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = Path(__file__).parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.post("/process/")
async def process_url(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return {"error": "Missing URL"}

    raw_text = scrape_url(url)
    docs = clean_text(raw_text)
    topics, _ = model_topics(docs)
    wordclouds = generate_wordclouds(topics)
    return {"topics": topics, "wordclouds": wordclouds}
