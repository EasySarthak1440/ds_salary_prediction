import pandas as pd
import numpy as np
import random

# Setting the seed for reproducibility
random.seed(42)
np.random.seed(42)

def generate_mock_data(num_records=500):
    cities = ['Bangalore', 'Pune', 'Mumbai', 'Gurgaon', 'Hyderabad', 'Chennai', 'Noida', 'Remote']
    job_titles = ['Data Scientist', 'Senior Data Scientist', 'SDE-2 (Data Science)', 'Lead Data Scientist', 'AI Engineer', 'ML Engineer', 'Data Science Associate']
    industries = ['FinTech', 'HealthTech', 'E-commerce', 'Consulting', 'Service-based', 'SaaS', 'MAANG']
    sectors = ['Information Technology', 'Finance', 'Manufacturing', 'Retail', 'Education']
    ownership = ['Company - Private', 'Company - Public', 'Startup', 'Subsidiary or Business Segment']
    sizes = ['1 to 50 Employees', '51 to 200 Employees', '201 to 500 Employees', '501 to 1000 Employees', '1001 to 5000 Employees', '5001 to 10000 Employees', '10000+ Employees']
    revenues = ['Unknown / Non-Applicable', '₹1 to ₹5 billion (INR)', '₹5 to ₹10 billion (INR)', '₹10+ billion (INR)', '₹100 to ₹500 million (INR)']

    data = []
    for _ in range(num_records):
        title = random.choice(job_titles)
        location = random.choice(cities)
        rating = round(random.uniform(3.0, 5.0), 1)
        company = f"Company_{random.randint(1, 100)}"
        size = random.choice(sizes)
        founded = random.randint(1970, 2024)
        owner_type = random.choice(ownership)
        industry = random.choice(industries)
        sector = random.choice(sectors)
        revenue = random.choice(revenues)
        
        # Salary logic for 2026 India (in Lakhs per Annum)
        base = 8 # Entry level
        if 'Senior' in title or 'Lead' in title: base += 10
        if 'Lead' in title: base += 15
        if 'SDE-2' in title: base += 8
        if location == 'Bangalore': base += 3
        if industry == 'MAANG': base += 12
        if industry == 'Startup': base += 5 # High risk, high pay
        
        # Random noise
        base += random.randint(-2, 10)
        
        min_salary = base
        max_salary = base + random.randint(5, 15)
        avg_salary = (min_salary + max_salary) / 2
        
        salary_estimate = f"₹{min_salary}L - ₹{max_salary}L (Employer est.)"
        
        # Description and Skills
        desc = "Exciting role in Data Science using Python, SQL, and Cloud."
        python_yn = 1 if random.random() > 0.1 else 0
        spark = 1 if random.random() > 0.6 else 0
        cloud = 1 if random.random() > 0.4 else 0
        ml = 1 if random.random() > 0.2 else 0
        stats = 1 if random.random() > 0.3 else 0
        
        data.append({
            "Job Title": title,
            "Salary Estimate": salary_estimate,
            "Job Description": desc,
            "Rating": rating,
            "Company Name": company,
            "Location": location,
            "Size": size,
            "Founded": founded,
            "Type of ownership": owner_type,
            "Industry": industry,
            "Sector": sector,
            "Revenue": revenue,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "avg_salary": avg_salary,
            "python_yn": python_yn,
            "spark": spark,
            "cloud": cloud,
            "machine_learning": ml,
            "statistics": stats,
            "age": 2026 - founded
        })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    df = generate_mock_data(500)
    import os
    if not os.path.exists('india_salary_prediction/data'):
        os.makedirs('india_salary_prediction/data')
    df.to_csv('india_salary_prediction/data/glassdoor_jobs_india_cleaned.csv', index=False)
    print("Generated 500 Indian DS job records for 2026 in india_salary_prediction/data/glassdoor_jobs_india_cleaned.csv")
