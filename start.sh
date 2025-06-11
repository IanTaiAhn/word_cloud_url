#!/usr/bin/env bash
export PATH=$PATH:/opt/render/project/.render/chrome/opt/google/chrome:/opt/render/project/.render/chromedriver

# Start your Python app here
uvicorn main:app --host 0.0.0.0 --port $PORT

