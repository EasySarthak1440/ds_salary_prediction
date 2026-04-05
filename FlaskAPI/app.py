from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import numpy as np
import joblib
import logging
import os

from utils import (
    setup_logging,
    load_model_safe,
    validate_prediction_input,
    create_prediction_response,
)

logger = setup_logging()

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "10 per second"],
    storage_uri="memory://"
)

US_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_file.joblib")
EXPECTED_FEATURES = 106

us_model = None
us_explainer = None


def load_models() -> None:
    """Load models at startup."""
    global us_model, us_explainer
    
    us_model, error = load_model_safe(US_MODEL_PATH, logger)
    if us_model:
        try:
            import shap
            us_explainer = shap.TreeExplainer(us_model)
            logger.info("SHAP explainer initialized")
        except ImportError:
            logger.warning("SHAP not available, explain endpoint will be disabled")
            us_explainer = None


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    status = {
        'status': 'healthy',
        'models': {
            'us_model': us_model is not None,
        },
        'version': '1.0.0'
    }
    return jsonify(status), 200


@app.route('/api/v1/health', methods=['GET'])
def health_check_v1():
    """Versioned health check endpoint."""
    return health_check()


@app.route('/', methods=['GET'])
def home():
    """API home endpoint with available routes."""
    return jsonify({
        'message': 'Salary Prediction API',
        'version': 'v1',
        'endpoints': [
            '/health',
            '/api/v1/predict',
            '/api/v1/explain',
        ]
    }), 200


@app.route('/api/v1/predict', methods=['POST'])
@app.route('/predict', methods=['POST'], endpoint='predict_legacy')
@limiter.limit("30 per minute")
def predict():
    """US market salary prediction endpoint."""
    try:
        if not us_model:
            logger.error("US Model not loaded")
            return jsonify({'error': 'US Model not loaded'}), 503

        data = request.json.get('input')
        
        is_valid, error_msg = validate_prediction_input(data, EXPECTED_FEATURES)
        if not is_valid:
            logger.warning(f"Invalid input: {error_msg}")
            return jsonify({'error': error_msg}), 400

        x_in = np.array(data).reshape(1, -1)
        prediction = us_model.predict(x_in)[0]
        
        logger.info(f"Prediction made: {prediction:.2f}")
        
        return jsonify(create_prediction_response(
            prediction,
            currency='USD (Thousands Per Annum)',
            market='US'
        ))
    except ValueError as e:
        logger.error(f"Value error in prediction: {e}")
        return jsonify({'error': 'Invalid numeric values in input'}), 400
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': 'Internal prediction error'}), 500


@app.route('/api/v1/explain', methods=['POST'])
@limiter.limit("20 per minute")
def explain():
    """SHAP-based explanation for US predictions."""
    try:
        if not us_explainer:
            return jsonify({'error': 'Explainability not available'}), 503

        data = request.json.get('input')
        
        is_valid, error_msg = validate_prediction_input(data, EXPECTED_FEATURES)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        x_in = np.array(data).reshape(1, -1)
        shap_values = us_explainer.shap_values(x_in)
        
        sv = shap_values[0] if isinstance(shap_values, list) else shap_values
        
        explanation = [
            {'feature_index': i, 'shap_value': float(val)}
            for i, val in enumerate(sv)
        ]
        
        logger.info("Explanation generated")
        
        return jsonify({
            'explanation': explanation,
            'base_value': float(us_explainer.expected_value) if hasattr(us_explainer, 'expected_value') else None
        })
    except Exception as e:
        logger.error(f"Explanation error: {str(e)}")
        return jsonify({'error': 'Error generating explanation'}), 500


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429


@app.errorhandler(500)
def internal_error_handler(e):
    """Handle internal server errors."""
    logger.error(f"Internal error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    load_models()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
