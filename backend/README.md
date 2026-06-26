# Predictive Project Backend

Production-grade FastAPI backend with ML for road degradation prediction.

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- (Optional) Virtual environment

## Step 1: Database

**Option A - SQLite (quick start, no setup):**
```bash
set USE_SQLITE=1   # Windows
# export USE_SQLITE=1  # macOS/Linux
```

**Option B - PostgreSQL:**
```bash
# Using psql
psql -U postgres -c "CREATE DATABASE predictive_db;"

# Or using createdb
createdb -U postgres predictive_db
```

## Step 2: Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env if your PostgreSQL credentials differ
```

## Step 4: Train ML Model

```bash
cd backend
python ml/train.py
```

Output: `ml/model.pkl` (XGBoost or RandomForest, whichever performs better)

## Step 5: Start Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`.

- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Step 6: Seed Data (Optional)

If the database is empty, the backend auto-seeds 50 sample roads on startup. To manually seed:

```bash
python seed_data.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /roads | List all roads |
| GET | /roads/{id} | Get road by ID |
| GET | /roads/{id}/predictions | Get predictions for road |
| POST | /roads | Create road |
| POST | /predict/{road_id} | Run ML prediction |
| GET | /predict/{road_id} | Get predictions (generates if none) |
| GET | /digital-twin/{road_id} | Get digital twin |
| GET | /digital-twin | Get all digital twins |
| GET | /dashboard/stats | Dashboard statistics |

## CORS

Allowed origins: `localhost:5173`, `localhost:3000`, `localhost:8080`

## Connect Frontend

Update the frontend store to call these APIs instead of in-memory data. Base URL: `http://localhost:8000`.
