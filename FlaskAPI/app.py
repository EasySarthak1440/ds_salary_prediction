from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_models():
    try:
        import os
        # Get the directory where app.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(current_dir, "model_file.joblib")
        model = joblib.load(file_name)
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return f"Error loading model: {str(e)}"

app = Flask(__name__)
CORS(app) # Enable CORS

@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'Salary Prediction Server is running!'}), 200

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Load model
        model = load_models()
        if isinstance(model, str):
            return jsonify({'error': model}), 500

        # Get data from request
        data = request.json.get('input')

        # Validate input
        if not data or not isinstance(data, list):
            return jsonify({'error': 'Invalid input data format. Expected a list of numerical values.'}), 400

        # Convert data to numpy array
        x_in = np.array(data).reshape(1, -1)

        # Make prediction
        prediction = model.predict(x_in)[0]

        # Prepare response
        response = jsonify({'response': prediction})
        return response, 200
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
