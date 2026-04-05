from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
import logging
import PyPDF2
import shap

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Load Models ---
current_dir = os.path.dirname(os.path.abspath(__file__))

# US Model
try:
    us_model_path = os.path.join(current_dir, "model_file.joblib")
    us_model = joblib.load(us_model_path)
    # Pre-calculate SHAP explainer for US model (might be slow on startup)
    # Using TreeExplainer for Random Forest
    us_explainer = shap.TreeExplainer(us_model)
    logger.info("US Model loaded successfully.")
except Exception as e:
    logger.error(f"Error loading US model: {e}")
    us_model = None
    us_explainer = None

# India Model
try:
    india_model_path = os.path.join(
        current_dir, "..", "india_salary_prediction", "india_ds_model.joblib"
    )
    india_columns_path = os.path.join(
        current_dir, "..", "india_salary_prediction", "india_model_columns.joblib"
    )

    if os.path.exists(india_model_path) and os.path.exists(india_columns_path):
        india_model = joblib.load(india_model_path)
        india_model_columns = joblib.load(india_columns_path)
        logger.info("India Model loaded successfully.")
    else:
        logger.warning(f"India model files not found at {india_model_path}")
        india_model = None
        india_model_columns = None
except Exception as e:
    logger.error(f"Error loading India model: {e}")
    india_model = None
    india_model_columns = None


# --- Helper Functions ---


def parse_pdf(file_stream):
    try:
        reader = PyPDF2.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        return ""


def extract_skills(text):
    # Simple keyword matching for demo
    skills_db = {
        "python": "Python",
        "sql": "SQL",
        "aws": "AWS",
        "excel": "Excel",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "spark": "Spark",
        "hadoop": "Hadoop",
        "tableau": "Tableau",
        "power bi": "Power BI",
        "sas": "SAS",
        "java": "Java",
        "c++": "C++",
        "r": "R",
    }
    found_skills = []
    text_lower = text.lower()
    for key, val in skills_db.items():
        if key in text_lower:
            found_skills.append(val)
    return list(set(found_skills))


# --- Routes ---


@app.route("/", methods=["GET"])
def home():
    return (
        jsonify(
            {
                "message": "Unified Salary Prediction API (US & India)",
                "endpoints": [
                    "/predict_us",
                    "/predict_india",
                    "/parse_resume",
                    "/explain_us",
                    "/skill_gap",
                ],
            }
        ),
        200,
    )


@app.route("/predict_us", methods=["POST"])
def predict_us():
    try:
        if not us_model:
            return jsonify({"error": "US Model not loaded"}), 503

        data = request.json.get("input")  # Expects list of numerical values
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # Reshape for single prediction
        x_in = np.array(data).reshape(1, -1)
        prediction = us_model.predict(x_in)[0]

        return jsonify(
            {"prediction": round(prediction, 2), "currency": "USD (Thousands Per Annum)"}
        )
    except Exception as e:
        logger.error(f"US Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/predict_india", methods=["POST"])
def predict_india():
    try:
        if not india_model:
            return jsonify({"error": "India Model not loaded"}), 503

        data = request.json  # Expects dict: { "rating": 4.0, ... }
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        # Mapping common frontend keys to model keys
        model_data = {}
        model_data["Rating"] = data.get("rating", data.get("Rating", 4.0))
        model_data["yoe"] = data.get("yoe", 3)
        model_data["python"] = 1 if data.get("python") else 0
        model_data["sql"] = 1 if data.get("sql") else 0
        model_data["llm"] = 1 if data.get("llm") else 0
        model_data["aws"] = 1 if data.get("cloud", data.get("aws")) else 0
        model_data["azure"] = 1 if data.get("azure") else 0
        model_data["pytorch"] = (
            1 if data.get("ml", data.get("pytorch")) else 0
        )  # Map 'ml' from UI to 'pytorch'
        model_data["spark"] = 1 if data.get("spark") else 0
        model_data["job_simp"] = data.get("job_simp", "data scientist")
        model_data["seniority"] = data.get("seniority", "na")

        input_df = pd.DataFrame([model_data])

        # Handle categorical encoding
        input_df = pd.get_dummies(input_df)

        # Align columns
        for col in india_model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[india_model_columns]

        prediction = india_model.predict(input_df)[0]

        return jsonify(
            {
                "prediction_lpa": round(prediction, 2),
                "currency": "INR (Lakhs Per Annum)",
                "market": "India 2026",
            }
        )
    except Exception as e:
        logger.error(f"India Prediction Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/parse_resume", methods=["POST"])
def parse_resume():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        text = parse_pdf(file)
        skills = extract_skills(text)
        return jsonify({"text_snippet": text[:500] + "...", "extracted_skills": skills})


@app.route("/explain_us", methods=["POST"])
def explain_us():
    try:
        if not us_explainer:
            return jsonify({"error": "US Explainer not initialized"}), 503

        data = request.json.get("input")
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        x_in = np.array(data).reshape(1, -1)
        shap_values = us_explainer.shap_values(x_in)

        # Extract values
        explanation = []
        if isinstance(shap_values, list):  # Classification output sometimes
            sv = shap_values[0]
        else:
            sv = shap_values

        for i, val in enumerate(sv[0]):
            explanation.append({"feature_index": i, "shap_value": float(val)})

        return jsonify({"explanation": explanation})

    except Exception as e:
        logger.error(f"Explanation Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/skill_gap", methods=["POST"])
def skill_gap():
    # Simple logic: suggest skills not in user's profile
    current_skills = request.json.get("skills", [])
    current_skills = [s.lower() for s in current_skills]

    # Define high-value skills (could be dynamic later)
    high_value_skills = [
        {"name": "Python", "value_add": "$10k"},
        {"name": "AWS", "value_add": "$15k"},
        {"name": "Spark", "value_add": "$12k"},
        {"name": "Deep Learning", "value_add": "$20k"},
        {"name": "SQL", "value_add": "$8k"},
    ]

    suggestions = []
    for skill in high_value_skills:
        if skill["name"].lower() not in current_skills:
            suggestions.append(skill)

    return jsonify({"suggestions": suggestions})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
