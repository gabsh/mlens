# mlens

Binary sentiment classification benchmark trained on the Stanford IMDB dataset (50k reviews).  
Benchmarks every combination of **embedding × classifier**, tracks experiments with MLflow, and serves predictions + LIME explanations via a FastAPI backend. A Vue 3 frontend visualises results and exposes an inference UI.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          VPS (k3s)                              │
│                                                                 │
│   Internet ──► Traefik :443 ──► TLS termination                 │
│                    │            cert-manager (Let's Encrypt)    │
│                    │                                            │
│                    ▼                                            │
│          ┌─────────────────┐                                    │
│          │  Frontend ×1    │                                    │
│          │  nginx          │                                    │
│          │  Vue 3 SPA      │                                    │
│          └────────┬────────┘                                    │
│                   │ /api/*                                      │
│                   ▼                                             │
│          ┌─────────────────┐                                    │
│          │  FastAPI ×1     │                                    │
│          │  scikit-learn   │                                    │
│          │  LIME           │                                    │
│          └────────┬────────┘                                    │
│                   │                                             │
│          hostPath volumes (read-only)                           │
│          ├── models/   (.pkl artifacts)                         │
│          └── mlruns/   (MLflow tracking)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Prediction pipeline (per request):**
```
Raw text
  │
  ├─► clean_text() — lowercase, strip HTML, remove stopwords
  │
  ├─► Embedder.transform() — TF-IDF / BoW / GloVe / BERT
  │
  └─► Classifier.predict_proba() — LR / SVM / RF / LightGBM / XGBoost / NB / MLP
```

**Explanation pipeline (LIME):**
```
Raw text
  │
  ├─► Generate 500 perturbed variants (random word masking)
  ├─► predict_fn() × 500 forwards → probability matrix (500, 2)
  ├─► LinearRegression(presence_matrix, proba) → coefficients
  └─► Top 10 words by |coefficient| → feature importances
```

---

## Stack

| Layer | Technology |
|---|---|
| **Embeddings** | TF-IDF · Bag of Words · GloVe · BERT |
| **Classifiers** | LR · SVM · RF · LightGBM · XGBoost · Naive Bayes · MLP |
| **Tracking** | MLflow (dev only) |
| **Explainability** | LIME |
| **Backend** | FastAPI + scikit-learn (Python 3.11) |
| **Frontend** | Vue 3 + Vite, served by nginx |
| **Orchestration** | Kubernetes — k3s (prod) |
| **Ingress** | Traefik + cert-manager (Let's Encrypt) |
| **Image registry** | Docker Hub (`gabinn/mlens-*`) |
| **CI/CD** | GitHub Actions → Docker Hub → k3s rollout |

---

## Evolution

**v1 — Docker Compose**  
Single-server setup with `docker-compose.prod.yml`. An external nginx-edge-proxy container handled SSL termination and hostname routing via a shared Docker network (`proxy-network`). MLflow ran as a service in production.

**v2 — Kubernetes (current)**  
Migrated to k3s on the same VPS as FSight. Traefik replaces nginx-edge-proxy as the cluster-wide ingress controller. cert-manager replaces Certbot for TLS. Images are built and pushed to Docker Hub via GitHub Actions, then pulled by k3s on deploy. MLflow removed from production — metrics are read directly from the `mlruns/` filesystem, saving ~700 MB RAM on the VPS.

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
# All combinations (also generates models/roc_curves.json)
python run.py train

# Specific subset
python scripts/train.py --embeddings tfidf bow --classifiers lr svm
```

### 4. Run locally

```bash
# FastAPI backend
python run.py api

# MLflow UI (dev only)
python run.py mlflow

# Frontend
cd frontend && npm install && npm run dev

# Full stack via Docker Compose
docker compose -f docker-compose.old.yml up --build
```

### Deploy to VPS

```bash
# Sync models and mlruns to VPS
rsync -avz -e "ssh -p 2222" ./models/ ubuntu@57.131.48.179:~/mlens/models/
rsync -avz -e "ssh -p 2222" ./mlruns/ ubuntu@57.131.48.179:~/mlens/mlruns/

# Push to main — CI/CD builds images, pushes to Docker Hub, applies k8s manifests
git push origin main
```

---

## Project structure

```
mlens/
├── app/                    # FastAPI application + routers
├── frontend/               # Vue 3 SPA
├── k8s/                    # Kubernetes manifests (namespace, deployments, ingress)
├── scripts/                # Training and data download
├── src/                    # Embedders and classifiers
├── models/                 # Trained .pkl artifacts (not tracked by git)
├── mlruns/                 # MLflow tracking (not tracked by git)
├── nginx/                  # nginx config (used by k8s ConfigMap and dev compose)
├── docker-compose.old.yml  # Dev stack (FastAPI + Frontend + MLflow)
└── .github/workflows/      # CI/CD — build → push → k3s rollout
```
