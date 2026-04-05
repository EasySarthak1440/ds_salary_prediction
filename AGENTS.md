# AGENTS.md

This document provides guidelines for AI agents working in this repository.

## Project Overview

DS Salary Prediction is a full-stack application for predicting Data Scientist salaries in the **US and India markets**. It consists of:
- **Flask Backend** (`FlaskAPI/`): REST APIs for salary predictions
- **React Frontend** (`frontend/`): Vite + TypeScript + Tailwind CSS application
- **Data Science** (`*.py`, `india_salary_prediction/`): Web scraping, data cleaning, ML model training

---

## Build Commands

### Backend (Python/Flask)

```bash
# Install dependencies
pip install -r requirements.txt

# Run US Market API (port 5000)
python FlaskAPI/app.py

# Run India Market API (port 5001)
python FlaskAPI/app_india.py

# Run merged API (both markets)
python FlaskAPI/app_merged.py

# Train India model
python india_salary_prediction/final_train_india.py

# Data cleaning
python data_cleaning.py
```

### Frontend (React/TypeScript)

```bash
cd frontend

# Install dependencies
npm install

# Development server (port 5173)
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

### Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start services in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f flask_api
docker-compose logs -f frontend
```

---

## Lint & Type Check Commands

### Frontend

```bash
cd frontend

# Run ESLint
npm run lint

# Type check (runs automatically with build)
npm run build

# Run single test file (if tests exist)
npx vitest run src/components/ResumeAnalyzer.test.tsx
npx vitest run src/App.test.tsx
```

### Python

```bash
# Format code (install black first if needed)
pip install black
black FlaskAPI/*.py

# Lint code (install flake8 first if needed)
pip install flake8
flake8 FlaskAPI/ --max-line-length=100
```

---

## Git Workflow

### Branch Naming
```bash
# Feature branches
git checkout -b feature/resume-upload
git checkout -b feature/shap-explainability

# Bug fixes
git checkout -b fix/cors-issue
git checkout -b fix/model-loading-error

# Refactoring
git checkout -b refactor/india-api
```

### Commit Messages
```
feat: add resume upload functionality
fix: resolve CORS error on prediction endpoint
refactor: extract model loading to separate module
docs: update API documentation
test: add pytest for India model predictions
```

---

## Environment Variables

Create a `.env` file for local development:

```bash
# Flask API
FLASK_ENV=development
FLASK_DEBUG=1

# API URLs (for frontend)
VITE_US_API_URL=http://localhost:5000
VITE_INDIA_API_URL=http://localhost:5001
```

---

## Code Style Guidelines

### Python Style

**Imports**: Standard library first, then third-party, then local imports
```python
import os
import logging
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import joblib
import pandas as pd
```

**Naming**: snake_case for variables/functions, PascalCase for classes
```python
def load_models():
def train_india_sota():
model_columns = list(X.columns)
```

**Error Handling**: Wrap API routes in try/except, return JSON errors
```python
except Exception as e:
    logger.error(f"Error in prediction: {str(e)}")
    return jsonify({'error': str(e)}), 500
```

**Logging**: Use standard `logging` module with `__name__`
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**Type Hints**: Encouraged for function signatures
```python
def predict(data: list) -> float:
```

**Selenium Error Handling** (for scrapers)
```python
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException
)

try:
    # Selenium operation
except (ElementClickInterceptedException, ElementNotInteractableException) as e:
    print(f"Failed to click job button: {e}")
    time.sleep(2)
```

**Docstrings**: Use for module-level functions and classes

### React/TypeScript Style

**Imports**: React hooks first, then libraries, then local components
```typescript
import React, { useState } from 'react';
import axios from 'axios';
import { DollarSign, Briefcase } from 'lucide-react';
import ResumeAnalyzer from './components/ResumeAnalyzer';
```

**Component Pattern**: Functional components with type annotations
```typescript
const App: React.FC = () => { ... }
```

**State Management**: useState for local state, keep components focused
```typescript
const [activeTab, setActiveTab] = useState<'predict' | 'resume'>('predict');
```

**Styling**: Tailwind CSS utility classes
```tsx
className="flex items-center justify-center gap-2 px-4 py-3 rounded-xl"
```

**Async Operations**: async/await with try/catch/finally, handle loading/error states
```typescript
const handlePredict = async (e: React.FormEvent) => {
  setLoading(true);
  try {
    // API call
  } catch (err: any) {
    console.error(err);
    setError(`Connection failed: ${err.message}`);
  } finally {
    setLoading(false);
  }
};
```

**Accessibility**: Include ARIA attributes for interactive elements
```tsx
<button
  onClick={handleClick}
  aria-label="Close modal"
  aria-expanded={isOpen}
>
  Close
</button>
```

---

## API Design

### Response Format
```python
# Success
return jsonify({'response': prediction}), 200

# Error
return jsonify({'error': 'Invalid input'}), 400
```

### Input Validation & Alignment (India Model Example)
```python
input_df = pd.DataFrame([data])
input_df = pd.get_dummies(input_df)

# Align with training columns
for col in model_columns:
    if col not in input_df.columns:
        input_df[col] = 0

input_df = input_df[model_columns]
prediction = model.predict(input_df)[0]
```

### CORS
Enable CORS for all Flask apps: `flask_cors.CORS(app)`

### Port Convention
- US API: 5000
- India API: 5001
- Merged API: any

---

## File Organization

| Type | Location |
|------|----------|
| Flask API | `FlaskAPI/` |
| India market code | `india_salary_prediction/` |
| React components | `frontend/src/components/` |
| ML models (`.joblib`) | Alongside training scripts |
| Data files | `data/` subdirectories |
| Python tests | `tests/` |
| GitHub Actions | `.github/workflows/` |

### Key Files
- `FlaskAPI/utils.py` - Shared utilities (logging, validation, model loading)
- `.env.example` - Environment variable template

---

## Model & Data Conventions

- Feature columns: `*_model_columns.joblib`
- Serialization: `joblib.dump()` / `joblib.load()`
- Encoding: `pd.get_dummies()`, align columns with training
- US model features: [rating, age, skills...] (60+ after encoding)
- India model features: Rating, yoe, python, sql, aws, azure, llm, pytorch, spark, job_simp, seniority

---

## Performance Guidelines

### Model Loading
Cache models at module level to avoid repeated loading:
```python
# Load once when module imports
model = joblib.load(model_path)
model_columns = joblib.load(columns_path)
```

### Production Deployment
Use Gunicorn with worker count based on CPU cores:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

---

## Security Guidelines

- **Input Sanitization**: Validate all API inputs before processing
- **Rate Limiting**: Flask-Limiter is enabled with defaults (100/min, 10/sec)
- **Environment Variables**: Never commit secrets to git
- **CORS**: Restrict origins in production: `CORS(app, origins=['https://yourdomain.com'])`

### Rate Limiting
Rate limiting is enabled via Flask-Limiter. Configure in `.env`:
```bash
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_SECOND=10
```

---

## API Versioning

APIs support versioning via `/api/v1/` prefix:

| Endpoint | Legacy | Versioned | Rate Limit |
|----------|--------|-----------|-------------|
| US Predict | `/predict` | `/api/v1/predict` | 30/min |
| India Predict | `/predict_india` | `/api/v1/predict` | 30/min |
| US Explain | - | `/api/v1/explain` | 20/min |
| Health | `/health` | `/api/v1/health` | No limit |

---

## Health Check Endpoints

All APIs expose `/health` for container orchestration:

```bash
curl http://localhost:5000/health
# Returns: {"status": "healthy", "models": {"us_model": true}, "version": "1.0.0"}
```

---

## Testing

### Current State
- Python tests in `tests/test_models.py` (pytest)
- Frontend tests in `frontend/src/App.test.ts` (Vitest)
- Manual testing at `http://localhost:5173`

### Python Tests (pytest)
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestIndiaModel::test_prediction_returns_float
```

### Frontend Tests (Vitest)
```bash
cd frontend

# Run all tests
npm run test:run

# Watch mode
npm run test

# Run specific test file
npx vitest run src/App.test.ts
```

---

## ChromeDriver Setup

Required for `glassdoor_scraper.py`:

1. Download ChromeDriver matching your Chrome version
2. Place in project root or add to PATH
3. Current path in code: `chromedriver.exe` (update for Linux: `chromedriver`)

```python
from selenium.webdriver.chrome.service import Service

service = Service(executable_path="chromedriver")
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Model not found | Ensure `model_file.joblib` exists in `FlaskAPI/` |
| CORS errors | Verify `CORS(app)` is enabled |
| India model errors | Check `india_model_columns.joblib` matches training |
| ChromeDriver error | Verify Chrome version matches driver version |
| Port conflict | Use `lsof -i :5000` to find and kill processes |

---

## Development Workflow

1. **Start backend**: `python FlaskAPI/app.py` (and/or `app_india.py`)
2. **Start frontend**: `cd frontend && npm run dev`
3. **Make changes** to code
4. **Lint**: `npm run lint` and `black <file>.py`
5. **Test** manually or with curl
6. **Build** for production: `npm run build`
