print("=== Testing imports one by one ===")

try:
    from fastapi import FastAPI
    print("✓ FastAPI imported")
except Exception as e:
    print(f"✗ FastAPI failed: {e}")

try:
    from fastapi.middleware.cors import CORSMiddleware
    print("✓ CORSMiddleware imported")
except Exception as e:
    print(f"✗ CORSMiddleware failed: {e}")

try:
    from pydantic import BaseModel, HttpUrl
    print("✓ Pydantic imported")
except Exception as e:
    print(f"✗ Pydantic failed: {e}")

try:
    from scraper import scrape_url
    print("✓ scraper imported")
except Exception as e:
    print(f"✗ scraper failed: {e}")

try:
    from preprocess import clean_text
    print("✓ preprocess imported")
except Exception as e:
    print(f"✗ preprocess failed: {e}")

try:
    from topic_model import model_topics
    print("✓ topic_model imported")
except Exception as e:
    print(f"✗ topic_model failed: {e}")

try:
    from visualization import generate_wordclouds, test_wordcloud_generation, generate_wordclouds_html
    print("✓ visualization imported")
except Exception as e:
    print(f"✗ visualization failed: {e}")

print("=== All tests complete ===")