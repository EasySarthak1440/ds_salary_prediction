import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

def train_india_sota():
    df = pd.read_csv('india_salary_prediction/data/india_585_cleaned.csv')
    
    # Selecting the best features mined from your scrape
    features = ['Rating', 'yoe', 'python', 'sql', 'aws', 'azure', 'llm', 'pytorch', 'spark', 'job_simp', 'seniority']
    
    # Feature Engineering: One-Hot Encoding for categorical data
    X = df[features]
    X = pd.get_dummies(X)
    y = df['avg_salary'].values
    
    # Save the feature columns for the API to match
    model_columns = list(X.columns)
    joblib.dump(model_columns, 'india_salary_prediction/india_model_columns.joblib')
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest Regressor (The Gold Standard for this data)
    rf = RandomForestRegressor(n_estimators=200, random_state=42)
    rf.fit(X_train, y_train)
    
    # Evaluate
    score = rf.score(X_test, y_test)
    print(f"Model Training Complete! R^2 Score on Test Data: {score:.2f}")
    
    # Save Model
    joblib.dump(rf, 'india_salary_prediction/india_ds_model.joblib')
    print("Model saved to india_salary_prediction/india_ds_model.joblib")

if __name__ == "__main__":
    train_india_sota()
