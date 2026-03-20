import pandas as pd
import numpy as np
import re
from sklearn.ensemble import RandomForestRegressor
import joblib

def clean_india_data(file_path):
    df = pd.read_csv(file_path)
    
    # 1. Handle missing salaries
    df = df[df['Salary Estimate'] != 'N/A'].copy()
    
    # 2. Extract min and max salary from INR format (e.g., ₹4L - ₹9L)
    def parse_salary(salary_str):
        if pd.isna(salary_str): return None
        # Extract all numbers from the string
        nums = re.findall(r'(\d+)', salary_str)
        if len(nums) >= 2:
            return float(nums[0]), float(nums[1])
        elif len(nums) == 1:
            return float(nums[0]), float(nums[0])
        return None, None

    df[['min_salary', 'max_salary']] = df['Salary Estimate'].apply(lambda x: pd.Series(parse_salary(x)))
    df = df.dropna(subset=['min_salary'])
    df['avg_salary'] = (df['min_salary'] + df['max_salary']) / 2
    
    # 3. Clean Ratings
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(df['Rating'].median() if not df['Rating'].empty else 3.5)
    
    # 4. Extract Job Seniority
    def get_seniority(title):
        title = title.lower()
        if 'sr' in title or 'senior' in title: return 'senior'
        if 'jr' in title or 'junior' in title or 'associate' in title: return 'junior'
        if 'lead' in title or 'principal' in title: return 'lead'
        return 'na'
    
    df['seniority'] = df['Job Title'].apply(get_seniority)
    
    return df

if __name__ == "__main__":
    print("Cleaning Real Indian Job Data...")
    df_cleaned = clean_india_data('india_salary_prediction/data/glassdoor_india_real.csv')
    
    print(f"Cleaned {len(df_cleaned)} records.")
    print(df_cleaned[['Job Title', 'avg_salary', 'seniority']].head())
    
    # Save cleaned data
    df_cleaned.to_csv('india_salary_prediction/data/india_real_cleaned.csv', index=False)
    
    # Simple Modeling for India (Proof of Concept)
    # Features: Rating, Seniority (dummy)
    df_model = df_cleaned[['avg_salary', 'Rating', 'seniority']]
    df_dum = pd.get_dummies(df_model)
    
    X = df_dum.drop('avg_salary', axis=1)
    y = df_dum.avg_salary.values
    
    rf = RandomForestRegressor(n_estimators=100)
    rf.fit(X, y)
    
    # Save the new India-specific model
    joblib.dump(rf, 'india_salary_prediction/model_india.joblib')
    print("New Indian Salary Model saved to india_salary_prediction/model_india.joblib")
