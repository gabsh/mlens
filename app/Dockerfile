FROM python:3.11-slim
WORKDIR /app

COPY requirements.prod.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgomp1 \
    && pip install --no-cache-dir -r requirements.prod.txt \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"
COPY . .
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
