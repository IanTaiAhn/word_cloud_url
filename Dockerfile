FROM python:3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --timeout=1000

# Install spaCy model separately
RUN python -m spacy download en_core_web_sm

COPY . .

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
