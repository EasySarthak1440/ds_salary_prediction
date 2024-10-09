from flask import Flask, jsonify, request
import numpy as np
import joblib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_models():
    try:
        file_name = "model_file.joblib"  # Ensure the model file is in this path
        model = joblib.load(file_name)
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return f"Error loading model: {str(e)}"

app = Flask(__name__)

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
