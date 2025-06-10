FROM python:3.12

WORKDIR /app

# Install system dependencies including cmake for hdbscan
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .

# Install heavy packages first
RUN pip install --no-cache-dir torch==2.7.1 --timeout=2000
RUN pip install --no-cache-dir numpy scipy scikit-learn --timeout=2000

# Install remaining requirements
RUN pip install --no-cache-dir -r requirements.txt --timeout=2000

# Install spaCy model
RUN python -m spacy download en_core_web_sm

COPY . .

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
