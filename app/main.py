from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from app.scraper import scrape_url
from app.preprocess import clean_text
from app.topic_model import model_topics
from app.visualization import generate_wordclouds, test_wordcloud_generation, generate_wordclouds_html

app = FastAPI()

# Step 1: Define a request model
class URLRequest(BaseModel):
    url: HttpUrl

# Step 2: Use it in the route
@app.post("/process/")
async def process_url(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    # topics, _ = model_topics(docs)
    # wordclouds = generate_wordclouds(topics)

    # return {"topics": topics, "wordclouds": wordclouds}
    return {"cleaned_text": docs}

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/test/")
async def test_endpoint(data: URLRequest):
    return {"received_url": data.url}

# here to test the web scrape and filtering with spacy...
@app.post("/filter_text/")
async def process_url(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    # topics, _ = model_topics(docs)
    # wordclouds = generate_wordclouds(topics)

    # return {"topics": topics, "wordclouds": wordclouds}
    return {"cleaned_text": docs}

#TODO This failed when I wasn't able to get any clusters since there wasn't enough data
@app.post("/topics/")
async def process_url(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    topics, _ = model_topics(docs)
    # wordclouds = generate_wordclouds(topics)

    # return {"topics": topics, "wordclouds": wordclouds}
    return {"topics": topics}


@app.post("/wordcloud/")
async def process_url(data: URLRequest):
    raw_text = scrape_url(data.url)
    docs = clean_text(raw_text)
    topics, _ = model_topics(docs)
    # wordclouds = test_wordcloud_generation()
    # wordclouds = generate_wordclouds(topics)
    wordclouds = generate_wordclouds_html(topics)


    return {"wordclouds": wordclouds}
    # return {"cleaned_text": docs}
