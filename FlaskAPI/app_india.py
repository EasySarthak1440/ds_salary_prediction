from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import pandas as pd
import joblib
import os

from utils import (
    setup_logging,
    load_model_safe,
    validate_india_input,
    align_input_data,
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

current_dir = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(current_dir, '..', 'india_salary_prediction', 'india_ds_model.joblib')
COLUMNS_PATH = os.path.join(current_dir, '..', 'india_salary_prediction', 'india_model_columns.joblib')

india_model = None
india_model_columns = None


def load_models() -> None:
    """Load India model at startup."""
    global india_model, india_model_columns
    
    india_model, error = load_model_safe(MODEL_PATH, logger)
    if india_model:
        india_model_columns, col_error = load_model_safe(COLUMNS_PATH, logger)
        if col_error:
            logger.error(f"Columns file error: {col_error}")
            india_model = None
    else:
        logger.warning("India model files not found - some features may be unavailable")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for container orchestration."""
    status = {
        'status': 'healthy',
        'models': {
            'india_model': india_model is not None,
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
        'message': 'India Salary Prediction API',
        'version': 'v1',
        'endpoints': [
            '/health',
            '/api/v1/predict',
        ]
    }), 200


@app.route('/api/v1/predict', methods=['POST'])
@app.route('/predict_india', methods=['POST'], endpoint='predict_legacy')
@limiter.limit("30 per minute")
def predict():
    """India market salary prediction endpoint."""
    try:
        if not india_model or not india_model_columns:
            logger.error("India Model not loaded")
            return jsonify({'error': 'India Model not loaded'}), 503

        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400
        
        is_valid, error_msg = validate_india_input(data)
        if not is_valid:
            logger.warning(f"Invalid India input: {error_msg}")
            return jsonify({'error': error_msg}), 400

        model_data = {
            'Rating': float(data.get('rating', data.get('Rating', 4.0))),
            'yoe': int(data.get('yoe', 3)),
            'python': 1 if data.get('python') else 0,
            'sql': 1 if data.get('sql') else 0,
            'llm': 1 if data.get('llm') else 0,
            'aws': 1 if data.get('cloud', data.get('aws')) else 0,
            'azure': 1 if data.get('azure') else 0,
            'pytorch': 1 if data.get('ml', data.get('pytorch')) else 0,
            'spark': 1 if data.get('spark') else 0,
            'job_simp': data.get('job_simp', 'data scientist'),
            'seniority': data.get('seniority', 'na'),
        }

        input_df = pd.DataFrame([model_data])
        input_df = pd.get_dummies(input_df)
        input_df = align_input_data(input_df, india_model_columns)
        
        prediction = india_model.predict(input_df)[0]
        
        logger.info(f"India prediction made: {prediction:.2f} LPA")
        
        return jsonify(create_prediction_response(
            prediction,
            currency='INR (Lakhs Per Annum)',
            market='India 2026'
        ))
    except ValueError as e:
        logger.error(f"Value error in India prediction: {e}")
        return jsonify({'error': 'Invalid numeric values in input'}), 400
    except Exception as e:
        logger.error(f"India prediction error: {str(e)}")
        return jsonify({'error': 'Internal prediction error'}), 500


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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
