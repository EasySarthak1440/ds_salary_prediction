import pytest
import os
import sys
import joblib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIndiaModel:
    @pytest.fixture
    def model_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'india_salary_prediction', 'india_ds_model.joblib')

    @pytest.fixture
    def columns_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'india_salary_prediction', 'india_model_columns.joblib')

    @pytest.fixture
    def model(self, model_path):
        if not os.path.exists(model_path):
            pytest.skip("Model file not found")
        return joblib.load(model_path)

    @pytest.fixture
    def model_columns(self, columns_path):
        if not os.path.exists(columns_path):
            pytest.skip("Model columns file not found")
        return joblib.load(columns_path)

    def test_model_file_exists(self, model_path):
        assert os.path.exists(model_path), f"Model file not found at {model_path}"

    def test_columns_file_exists(self, columns_path):
        assert os.path.exists(columns_path), f"Columns file not found at {columns_path}"

    def test_model_is_fitted(self, model):
        assert hasattr(model, 'predict'), "Model must have predict method"

    def test_prediction_returns_float(self, model, model_columns):
        input_data = {
            'Rating': 4.0,
            'yoe': 5,
            'python': 1,
            'sql': 1,
            'aws': 1,
            'azure': 0,
            'llm': 1,
            'pytorch': 0,
            'spark': 0,
            'job_simp_data scientist': 1,
            'seniority_na': 1
        }

        input_df = pd.DataFrame([input_data])
        for col in model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model_columns]

        prediction = model.predict(input_df)
        assert isinstance(prediction[0], (float, np.floating)), "Prediction must be a float"

    def test_prediction_is_positive(self, model, model_columns):
        input_data = {
            'Rating': 4.0,
            'yoe': 5,
            'python': 1,
            'sql': 1,
            'aws': 1,
            'azure': 0,
            'llm': 1,
            'pytorch': 0,
            'spark': 0,
            'job_simp_data scientist': 1,
            'seniority_na': 1
        }

        input_df = pd.DataFrame([input_data])
        for col in model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model_columns]

        prediction = model.predict(input_df)
        assert prediction[0] > 0, "Salary prediction should be positive"

    def test_more_experience_higher_salary(self, model, model_columns):
        base_input = {
            'Rating': 4.0,
            'yoe': 3,
            'python': 1,
            'sql': 1,
            'aws': 1,
            'azure': 0,
            'llm': 0,
            'pytorch': 0,
            'spark': 0,
            'job_simp_data scientist': 1,
            'seniority_na': 1
        }

        input_df_low = pd.DataFrame([base_input])
        for col in model_columns:
            if col not in input_df_low.columns:
                input_df_low[col] = 0
        input_df_low = input_df_low[model_columns]

        base_input['yoe'] = 8
        input_df_high = pd.DataFrame([base_input])
        for col in model_columns:
            if col not in input_df_high.columns:
                input_df_high[col] = 0
        input_df_high = input_df_high[model_columns]

        pred_low = model.predict(input_df_low)[0]
        pred_high = model.predict(input_df_high)[0]

        assert pred_high >= pred_low, "More experience should result in higher or equal salary"

    def test_model_columns_is_list(self, model_columns):
        assert isinstance(model_columns, list), "Model columns must be a list"
        assert len(model_columns) > 0, "Model columns must not be empty"


class TestUSModel:
    @pytest.fixture
    def model_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, 'FlaskAPI', 'model_file.joblib')

    @pytest.fixture
    def model(self, model_path):
        if not os.path.exists(model_path):
            pytest.skip("US Model file not found")
        return joblib.load(model_path)

    def test_model_file_exists(self, model_path):
        assert os.path.exists(model_path), f"Model file not found at {model_path}"

    def test_model_is_fitted(self, model):
        assert hasattr(model, 'predict'), "Model must have predict method"

    def test_prediction_shape(self, model):
        sample_input = np.array([[4.2, 0, 49, 0, 0, 0, 0, 0, 160, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]])
        prediction = model.predict(sample_input)
        assert prediction.shape == (1,), "Prediction should return shape (1,)"
