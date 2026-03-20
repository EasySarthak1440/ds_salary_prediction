from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib
import os

app = Flask(__name__)
CORS(app)

# Load the SOTA India Model
current_dir = os.path.dirname(os.path.abspath(__file__))
# Note: Going up to root then to india_salary_prediction
model_path = os.path.join(current_dir, '..', 'india_salary_prediction', 'india_ds_model.joblib')
columns_path = os.path.join(current_dir, '..', 'india_salary_prediction', 'india_model_columns.joblib')

model = joblib.load(model_path)
model_columns = joblib.load(columns_path)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'SOTA India Salary Prediction Server (2026) is active!'}), 200

@app.route('/predict_india', methods=['POST'])
def predict():
    try:
        data = request.json
        # Input format expected:
        # { "Rating": 4.0, "yoe": 5, "python": 1, "sql": 1, "llm": 1, ... }
        
        # Create a DataFrame for the input
        input_df = pd.DataFrame([data])
        
        # Ensure categorical columns are dummy encoded
        input_df = pd.get_dummies(input_df)
        
        # Align with training columns
        for col in model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        
        input_df = input_df[model_columns]
        
        # Predict
        prediction = model.predict(input_df)[0]
        
        return jsonify({
            'prediction_lpa': round(prediction, 2),
            'currency': 'INR (Lakhs Per Annum)',
            'market': 'India 2026'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Running on port 5001 to avoid conflict with US API
    app.run(port=5001, debug=True)
