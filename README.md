# mlens

Binary sentiment classification benchmark trained on the Stanford IMDB dataset (50k reviews).  
Benchmarks every combination of **embedding × classifier**, tracks experiments with MLflow, and serves predictions + LIME explanations via a FastAPI backend. A Vue 3 frontend visualises results and exposes an inference UI.

---

## Embeddings

| Embedding | Status |
|---|---|
| TF-IDF | ✅ |
| Bag of Words | ✅ |
| GloVe | coming soon |
| BERT | coming soon |

## Classifiers

| Classifier | Status |
|---|---|
| Logistic Regression | ✅ |
| SVM | ✅ |
| Random Forest | ✅ |
| LightGBM | ✅ |
| XGBoost | ✅ |
| Naive Bayes | ✅ |
| MLP | coming soon |

---

## Stack

- **Backend** — Python 3.11, FastAPI, scikit-learn, LightGBM, XGBoost
- **Tracking** — MLflow
- **Explainability** — LIME
- **Frontend** — Vue 3 + Vite, nginx
- **Infra** — Docker, GitHub Actions

---

## Getting started

### 1. Install dependencies

```bash
pip install torch==2.10.0+cpu --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 2. Download data

```bash
python run.py download
```

### 3. Train

```bash
# All combinations
python run.py train

# Specific subset
python scripts/train.py --embeddings tfidf bow --classifiers lr svm
```

### 4. Run

```bash
# FastAPI backend
python run.py api

# MLflow UI
python run.py mlflow

# Frontend
cd frontend && npm install && npm run dev
```

### Docker (full stack)

```bash
docker compose up --build
```

---

## Project structure

```
mlens/
├── app/              # FastAPI application
├── frontend/         # Vue 3 SPA
├── scripts/          # Training, evaluation, data download
├── src/              # Embedders and classifiers
├── models/           # Trained .pkl artifacts (not tracked by git)
├── mlruns/           # MLflow tracking (not tracked by git)
├── nginx/            # nginx config
├── docker-compose.yml
└── docker-compose.prod.yml
```

