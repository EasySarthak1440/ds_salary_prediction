import logging
import os
import joblib
from typing import Optional, Tuple, Any
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class ModelInfo:
    model: Any
    columns: Optional[list] = None
    explainer: Optional[Any] = None
    loaded: bool = True
    error: Optional[str] = None


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure structured logging for the application."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger("flask_api")
    return logger


def load_model_safe(model_path: str, logger: Optional[logging.Logger] = None) -> Tuple[Optional[Any], Optional[str]]:
    """Safely load a model from disk with error handling."""
    try:
        if not os.path.exists(model_path):
            error = f"Model file not found: {model_path}"
            if logger:
                logger.error(error)
            return None, error
        model = joblib.load(model_path)
        if logger:
            logger.info(f"Model loaded successfully: {model_path}")
        return model, None
    except Exception as e:
        error = f"Error loading model from {model_path}: {str(e)}"
        if logger:
            logger.error(error)
        return None, error


def align_input_data(
    input_df: pd.DataFrame,
    model_columns: list,
    default_value: Any = 0
) -> pd.DataFrame:
    """Align input DataFrame columns with model's expected columns."""
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = default_value
    return input_df[model_columns]


def validate_prediction_input(
    data: list,
    expected_length: Optional[int] = None
) -> Tuple[bool, Optional[str]]:
    """Validate US model prediction input."""
    if not data:
        return False, "Input data is required"
    if not isinstance(data, list):
        return False, "Input must be a list of numerical values"
    if not all(isinstance(x, (int, float)) for x in data):
        return False, "All input values must be numeric"
    if expected_length and len(data) != expected_length:
        return False, f"Expected {expected_length} features, got {len(data)}"
    return True, None


def validate_india_input(data: dict) -> Tuple[bool, Optional[str]]:
    """Validate India model prediction input."""
    if not data:
        return False, "Input data is required"
    if not isinstance(data, dict):
        return False, "Input must be a dictionary"
    
    valid_skill_keys = {'python', 'sql', 'aws', 'azure', 'llm', 'pytorch', 'spark'}
    valid_seniority = {'na', 'entry', 'mid', 'senior', 'lead', 'manager'}
    
    rating = data.get('rating', data.get('Rating'))
    if rating is not None:
        try:
            r = float(rating)
            if r < 0 or r > 5:
                return False, "Rating must be between 0 and 5"
        except (ValueError, TypeError):
            return False, "Rating must be a number"
    
    yoe = data.get('yoe')
    if yoe is not None:
        try:
            y = int(yoe)
            if y < 0 or y > 50:
                return False, "Years of experience must be between 0 and 50"
        except (ValueError, TypeError):
            return False, "Years of experience must be an integer"
    
    seniority = data.get('seniority', 'na')
    if seniority.lower() not in valid_seniority:
        return False, f"Seniority must be one of: {', '.join(valid_seniority)}"
    
    return True, None


def create_prediction_response(
    prediction: float,
    currency: str,
    market: Optional[str] = None,
    metadata: Optional[dict] = None
) -> dict:
    """Create a standardized prediction response."""
    response = {
        'prediction': round(float(prediction), 2),
        'currency': currency
    }
    if market:
        response['market'] = market
    if metadata:
        response['metadata'] = metadata
    return response


def create_error_response(
    error: str,
    code: int = 400,
    details: Optional[dict] = None
) -> Tuple[dict, int]:
    """Create a standardized error response."""
    response = {'error': error}
    if details:
        response['details'] = details
    return response, code
