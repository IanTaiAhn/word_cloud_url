from fastapi import FastAPI
from pydantic import BaseModel
from app.scraper import scrape_url
from app.preprocess import clean_text
from app.topic_model import model_topics
from app.visualization import generate_wordclouds

app = FastAPI()

# Step 1: Define a request model
class URLRequest(BaseModel):
    url: str

# Step 2: Use it in the route
@app.post("/process/")
async def process_url(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    topics, _ = model_topics(docs)
    wordclouds = generate_wordclouds(topics)

    return {"topics": topics, "wordclouds": wordclouds}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/test/")
async def test_endpoint(data: URLRequest):
    return {"received_url": data.url}