# Data Science Salary Prediction Project (Multi-Market)

**A comprehensive, end-to-End Data Science project** featuring web scraping, automated data cleaning, exploratory data analysis (EDA), state-of-the-art machine learning models, and a professional React-based frontend for predicting Data Scientist salaries in the **US and India (2026)**.

---

## 🚀 Project Overview

This project provides a robust solution for estimating salaries in the Data Science field by analyzing real-world job postings. It features:

- **US Market Model**: Trained on Glassdoor US data with specialized feature engineering.
- **India Market Model (2026)**: A state-of-the-art (SOTA) model specifically tuned for the rapidly growing Indian tech landscape, including modern skills like LLMs, GenAI, and cloud platforms.
- **Full Stack Architecture**: Professional React frontend with a high-performance Flask backend.

---

## 📂 Folder Structure

```text
ds_salary_prediction/
├── FlaskAPI/                 # Python Flask Backend
│   ├── app.py                # US Market API (Port 5000)
│   ├── app_india.py          # India Market API (Port 5001)
│   ├── model_file.joblib     # Serialized US model
│   └── wsgi.py               # Production entrypoint
├── frontend/                 # Modern React Frontend (Vite + Tailwind CSS)
│   ├── src/                  # React components and logic
│   └── package.json          # Node dependencies
├── india_salary_prediction/  # Research & Development for India Market
│   ├── data/                 # Raw and cleaned India datasets
│   ├── deep_cleaning_india.py # Specialized cleaning pipeline
│   ├── final_train_india.py  # Model training script
│   └── india_ds_model.joblib # SOTA India model (2026)
├── data_cleaning.py          # Legacy/US cleaning scripts
├── eda.ipynb                 # In-depth analysis and modeling notebooks
├── glassdoor_scraper.py      # Selenium-based web scraper
└── requirements.txt          # Python dependencies
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
- **Python 3.11+**
- **Node.js (v18+)**
- **ChromeDriver** (matching your Chrome version)

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/EasySarthak1440/ds_salary_prediction.git
cd ds_salary_prediction

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🚦 How to Run

### Step 1: Start the Backend(s)
To enable full functionality, run both APIs (or the one you need):
```bash
# Terminal 1: US API
python FlaskAPI/app.py

# Terminal 2: India API
python FlaskAPI/app_india.py
```

### Step 2: Start the Frontend
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## 🧠 Machine Learning Details

### US Model
- **Algorithm**: Random Forest Regressor (Optimized via GridSearchCV).
- **Features**: Company rating, size, industry, revenue, and extracted skills (Python, R, Spark, AWS, Excel).
- **Metric**: Achieved a competitive Mean Absolute Error (MAE).

### India 2026 SOTA Model
- **Algorithm**: Advanced Ensemble Model (XGBoost/Random Forest).
- **New Features**: Modern industry requirements including **LLM/Generative AI**, **Cloud Computing (Azure/GCP)**, and **Advanced Analytics (Tableau/PowerBI)**.
- **Optimization**: Features a deep cleaning pipeline to handle the specific formatting of the Indian job market.

---

## 💻 Technologies Used

- **Frontend**: React 19, Vite, Tailwind CSS (v4), Lucide Icons, Axios.
- **Backend**: Flask, Flask-CORS, Gunicorn.
- **Data Science**: Scikit-learn, Pandas, NumPy, Selenium, Joblib.
- **Development**: TypeScript, Python, Git.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

**Developed by [Sarthak Kelkar](https://github.com/EasySarthak1440)**

