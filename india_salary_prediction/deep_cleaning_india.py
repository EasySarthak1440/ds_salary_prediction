import pandas as pd
import numpy as np
import re

def clean_deep_india(file_path):
    df = pd.read_csv(file_path)
    
    # 0. Drop Scraping Glitch Duplicates (Important!)
    df = df.drop_duplicates(subset=['description']).copy()
    
    # 1. Salary Cleaning (LPA)
    def parse_salary(x):
        if pd.isna(x) or x == 'N/A': return None, None
        nums = re.findall(r'(\d+)', x.replace(',', ''))
        if len(nums) >= 2:
            min_v, max_v = float(nums[0]), float(nums[1])
            # 2026 India Logic: If both are < 200, assume they are Lakhs (LPA). 
            # If they are very small (e.g. < 5), they might be Monthly Lakhs or Monthly Thousands.
            # Most Glassdoor India entries are in 'L' (Lakhs). 
            # If a job says 50,000 - 100,000, it's monthly thousands.
            if 'per month' in x.lower() or max_v < 10: 
                min_v *= 12
                max_v *= 12
            return min_v, max_v
        elif len(nums) == 1:
            val = float(nums[0])
            if 'per month' in x.lower() or val < 10: val *= 12
            return val, val
        return None, None

    df[['min_salary', 'max_salary']] = df['Salary Estimate'].apply(lambda x: pd.Series(parse_salary(x)))
    df = df.dropna(subset=['min_salary']).copy()
    df['avg_salary'] = (df['min_salary'] + df['max_salary']) / 2
    
    # 2. Skill Mining from Description
    df['description'] = df['description'].fillna('').str.lower()
    df['python'] = df['description'].apply(lambda x: 1 if 'python' in x else 0)
    df['sql'] = df['description'].apply(lambda x: 1 if 'sql' in x else 0)
    df['aws'] = df['description'].apply(lambda x: 1 if 'aws' in x else 0)
    df['azure'] = df['description'].apply(lambda x: 1 if 'azure' in x else 0)
    df['llm'] = df['description'].apply(lambda x: 1 if 'llm' in x or 'large language' in x or 'generative ai' in x else 0)
    df['pytorch'] = df['description'].apply(lambda x: 1 if 'pytorch' in x or 'tensorflow' in x else 0)
    df['spark'] = df['description'].apply(lambda x: 1 if 'spark' in x else 0)
    
    # 3. Job Simplification
    def simplify_title(title):
        title = title.lower()
        if 'data scientist' in title: return 'data scientist'
        if 'machine learning' in title or 'ml' in title: return 'mle'
        if 'data analyst' in title: return 'analyst'
        if 'manager' in title or 'lead' in title or 'head' in title: return 'manager/lead'
        return 'other'
    
    df['job_simp'] = df['Job Title'].apply(simplify_title)
    
    # 4. Seniority
    def get_seniority(title):
        title = title.lower()
        if 'sr' in title or 'senior' in title or 'lead' in title or 'principal' in title: return 'senior'
        if 'jr' in title or 'junior' in title or 'intern' in title: return 'junior'
        return 'na'
    
    df['seniority'] = df['Job Title'].apply(get_seniority)
    
    # 6. Extract Years of Experience (YoE) - CRITICAL for India
    def extract_yoe(x):
        # Look for patterns like "3-5 years", "10+ years", "min 2 years"
        # Handles ranges by taking the minimum
        match = re.search(r'(\d+)(?:\s*-\s*\d+)?\s*years?', x)
        if match:
            return float(match.group(1))
        return 2.0 # Assume 2 years as default
    
    df['yoe'] = df['description'].apply(extract_yoe)
    
    return df

if __name__ == "__main__":
    print("Mining features from 585 Indian Jobs...")
    df_cleaned = clean_deep_india('india_salary_prediction/data/glassdoor_india_585_jobs.csv')
    
    print(f"Extraction Complete. Cleaned {len(df_cleaned)} valid salary records.")
    output_path = 'india_salary_prediction/data/india_585_cleaned.csv'
    df_cleaned.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")
    
    # Quick Summary
    print("\n--- Average Salary by Seniority (LPA) ---")
    print(df_cleaned.groupby('seniority')['avg_salary'].mean())
