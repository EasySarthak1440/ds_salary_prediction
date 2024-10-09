import pandas as pd

# Load the dataset
df = pd.read_csv('glassdoor_jobs.csv')

# Salary parsing
# Flag rows with hourly wage
df['hourly'] = df['Salary Estimate'].apply(lambda x: 1 if 'per hour' in x.lower() else 0)

# Remove rows with no salary estimate
df = df[df['Salary Estimate'] != '-1']

# Extract and clean the salary estimates
salary = df['Salary Estimate'].apply(lambda x: x.split('(')[0])
minus_Kd = salary.apply(lambda x: x.replace('K', '').replace('$', ''))

min_hr = minus_Kd.apply(lambda x: x.lower().replace('per hour', '').replace('Per Hour', ''))

# Calculate min, max, and average salary
df['min_salary'] = min_hr.apply(lambda x: float(x.split('-')[0].replace(',', '')) if '-' in x else float(x.replace(',', '')))
df['max_salary'] = min_hr.apply(lambda x: float(x.split('-')[1].replace(',', '')) if '-' in x else float(x.replace(',', '')))
df['avg_salary'] = (df.min_salary + df.max_salary) / 2

# Extract company name
df['company_txt'] = df.apply(lambda x: x['Company Name'] if x['Rating'] == -1 else x['Company Name'][:-3].strip(), axis=1)

# Extract state field
df['job_state'] = df['Location'].apply(lambda x: x.split(',')[1].strip() if isinstance(x, str) and ',' in x else '')
job_state_counts = df['job_state'].value_counts()

# Remove rows with no founded year
# Convert the 'Founded' column to numeric, forcing errors to NaN
df['Founded'] = pd.to_numeric(df['Founded'], errors='coerce')

# Remove rows where 'Founded' is NaN or -1
df = df[(df['Founded'].notna()) & (df['Founded'] != -1)]

# Calculate the age of the company
df['age'] = df['Founded'].apply(lambda x: 2024 - x if x > 0 else -1)

# Parsing of job description for key skills
df['python_yn'] = df['Skills'].apply(lambda x: 1 if 'python' in x.lower() else 0)
df['R_yn'] = df['Skills'].apply(lambda x: 1 if 'r' in x.lower() else 0)
df['spark'] = df['Skills'].apply(lambda x: 1 if 'spark' in x.lower() else 0)
df['cloud'] = df['Skills'].apply(lambda x: 1 if 'aws' in x.lower() or 'azure' in x.lower() else 0)
df['excel'] = df['Skills'].apply(lambda x: 1 if 'excel' or 'microsoft excel' in x.lower() else 0)
df['sql'] = df['Skills'].apply(lambda x: 1 if 'sql' in x.lower() else 0)
df['machine_learning'] = df['Skills'].apply(lambda x: 1 if 'machine learning' in x.lower() else 0)
df['statistics'] = df['Skills'].apply(lambda x: 1 if 'statistics' in x.lower() or 'statistical analysis' in x.lower() else 0)

# Save the cleaned data
df.to_csv('salary_data_cleaned.csv', index=False)

# Display the cleaned data
print(pd.read_csv('salary_data_cleaned.csv').head())
