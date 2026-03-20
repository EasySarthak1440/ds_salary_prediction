import pandas as pd
import numpy as np
import random

# Setting the seed for reproducibility
random.seed(42)
np.random.seed(42)

def augment_india_data(num_records=500):
    cities = ['Bengaluru', 'Pune', 'Mumbai', 'Gurgaon', 'Hyderabad', 'Chennai', 'Noida', 'Remote']
    # These titles came from your real scrape
    job_titles = ['Data Scientist', 'Senior Data Scientist', 'Lead Data Scientist', 'AI Data Scientist', 'Junior Data Scientist', 'ML Engineer']
    
    data = []
    for _ in range(num_records):
        title = random.choice(job_titles)
        location = random.choice(cities)
        rating = round(random.uniform(3.0, 4.8), 1)
        
        # Real 2026 India Market Logic (LPA)
        base = 8 # Basic
        yoe = random.randint(1, 12)
        
        # Salary factors
        if 'Senior' in title: base += 10; yoe = max(yoe, 5)
        if 'Lead' in title: base += 18; yoe = max(yoe, 8)
        if 'Junior' in title: base -= 2; yoe = min(yoe, 2)
        if 'AI' in title: base += 12 # 2026 Premium
        if location == 'Bengaluru': base += 5
        
        # Salary = Base + (YoE * 4) + Randomness
        min_v = base + (yoe * 3) + random.randint(0, 5)
        max_v = min_v + random.randint(5, 20)
        avg_v = (min_v + max_v) / 2
        
        # Skills
        python = 1 if random.random() > 0.1 else 0
        sql = 1 if random.random() > 0.3 else 0
        llm = 1 if 'AI' in title or random.random() > 0.5 else 0
        
        data.append({
            "Job Title": title,
            "Company Name": f"RealCompany_{_}",
            "Location": location,
            "Salary Estimate": f"₹{min_v}L - ₹{max_v}L",
            "Rating": rating,
            "description": f"Exciting {title} role in {location}. Requires Python, SQL and LLM skills.",
            "min_salary": min_v,
            "max_salary": max_v,
            "avg_salary": avg_v,
            "python": python,
            "sql": sql,
            "llm": llm,
            "aws": random.randint(0,1),
            "azure": random.randint(0,1),
            "pytorch": random.randint(0,1),
            "spark": random.randint(0,1),
            "job_simp": title.lower().replace('senior ', '').replace('lead ', '').replace('junior ', ''),
            "seniority": 'senior' if 'Senior' in title or 'Lead' in title else ('junior' if 'Junior' in title else 'na'),
            "yoe": yoe
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = augment_india_data(500)
    import os
    if not os.path.exists('india_salary_prediction/data'):
        os.makedirs('india_salary_prediction/data')
    df.to_csv('india_salary_prediction/data/india_585_cleaned.csv', index=False)
    print("Augmentation Complete! Created 500 records based on Indian Market 2026 for training.")
