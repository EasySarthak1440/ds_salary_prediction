import json
import pandas as pd
from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import random

def get_jobs_tls(title, location_id, num_jobs):
    print(f"Initializing TLS-SOTA Scraper for {title} in {location_id}...")
    
    # Target URL (Search)
    url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={title}&locT=C&locId={location_id}"
    
    # The 'Secret Sauce': curl_cffi impersonates Chrome 120 TLS fingerprint
    # This bypasses Cloudflare/Turnstile much better than standard requests/Selenium
    session = requests.Session(impersonate="chrome120")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    
    print(f"Requesting: {url}")
    try:
        response = session.get(url, headers=headers, timeout=20)
        response.raise_for_status()
    except Exception as e:
        print(f"Initial request failed: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 2026 Strategy: Look for the __NEXT_DATA__ or JSON-LD script tags
    # This is where the real data is hidden in modern Next.js/React sites like Glassdoor
    scripts = soup.find_all('script', type='application/ld+json')
    print(f"Found {len(scripts)} JSON-LD blocks.")
    
    jobs_data = []
    
    # Option 1: Parse JSON-LD (Search results often have multiple job postings)
    for script in scripts:
        try:
            data = json.loads(script.string)
            # If it's a list of jobs
            if isinstance(data, list):
                for item in data:
                    if item.get('@type') == 'JobPosting':
                        jobs_data.append(process_json_job(item))
            # If it's a single job
            elif data.get('@type') == 'JobPosting':
                jobs_data.append(process_json_job(data))
        except:
            continue

    # Option 2: Extracting from the Apollo/Next.js State (the 'Pro' move)
    if not jobs_data:
        print("Falling back to Apollo State extraction...")
        apollo_script = soup.find('script', id='__NEXT_DATA__')
        if apollo_script:
            try:
                state = json.loads(apollo_script.string)
                # Traverse the deep state to find job objects
                # (Path varies but we can search for job keys)
                # For brevity, we'll try to find any key containing 'job' in the props
                def find_jobs_in_dict(d):
                    if isinstance(d, dict):
                        if 'jobTitle' in d and 'employerName' in d:
                            yield d
                        for v in d.values():
                            yield from find_jobs_in_dict(v)
                    elif isinstance(d, list):
                        for item in d:
                            yield from find_jobs_in_dict(item)
                
                for job in find_jobs_in_dict(state):
                    jobs_data.append({
                        "Job Title": job.get('jobTitle'),
                        "Company": job.get('employerName'),
                        "Location": job.get('locationName'),
                        "Salary": job.get('salaryRange', 'N/A'),
                        "Description": job.get('jobDescriptionPreview', 'N/A')
                    })
            except Exception as e:
                print(f"State extraction failed: {e}")

    df = pd.DataFrame(jobs_data).drop_duplicates()
    return df

def process_json_job(item):
    """Parses standard JSON-LD job format"""
    return {
        "Job Title": item.get('title'),
        "Company": item.get('hiringOrganization', {}).get('name'),
        "Location": item.get('jobLocation', {}).get('address', {}).get('addressLocality'),
        "Salary": item.get('baseSalary', {}).get('value', {}).get('minValue', 'N/A'),
        "Currency": item.get('baseSalary', {}).get('currency', 'INR'),
        "Description": item.get('description', 'N/A')[:200]
    }

if __name__ == "__main__":
    # Bangalore: 1131510
    df = get_jobs_tls("Data Scientist", "1131510", 10)
    
    if not df.empty:
        print(f"Success! Scraped {len(df)} real jobs.")
        print(df.head())
        
        import os
        if not os.path.exists('india_salary_prediction/data'):
            os.makedirs('india_salary_prediction/data')
        df.to_csv('india_salary_prediction/data/glassdoor_jobs_india_tls.csv', index=False)
    else:
        print("Scraper failed to find job data. Cloudflare might have blocked the handshake.")
        # Saving HTML for debugging (without printing it)
        with open("debug_glassdoor.html", "w") as f:
            # We would normally write response.text here if we had it
            f.write("Failed to fetch")
