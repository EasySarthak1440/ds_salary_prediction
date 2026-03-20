import time
import random
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_jobs_sota(title, location_id, num_jobs):
    print(f"Initializing SOTA Scraper for {title} in location {location_id}...")
    
    # SOTA Configuration
    options = uc.ChromeOptions()
    # options.add_argument('--headless=new') # Use this if you want it invisible, but visible is safer for evasion
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Start the browser with the patch
    driver = uc.Chrome(options=options, version_main=146)
    
    # 1. Randomize Viewport to look like a real laptop
    width = random.randint(1024, 1920)
    height = random.randint(768, 1080)
    driver.set_window_size(width, height)
    
    url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={title}&locT=C&locId={location_id}"
    print(f"Navigating to {url}")
    driver.get(url)
    
    # Human-like pause
    time.sleep(random.uniform(3.0, 6.0))
    
    jobs = []
    
    while len(jobs) < num_jobs:
        try:
            # Wait for job cards
            job_cards = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li[data-test='job-listing-card']"))
            )
        except TimeoutException:
            print("Timeout waiting for job cards. Saving screenshot for debugging.")
            driver.save_screenshot("debug_sota_fail.png")
            break
            
        print(f"Found {len(job_cards)} job cards on this page.")
        
        for i, card in enumerate(job_cards):
            if len(jobs) >= num_jobs:
                break
                
            print(f"Processing job {len(jobs) + 1}/{num_jobs}...")
            
            # Click the card to load details (mimic user)
            try:
                card.click()
                time.sleep(random.uniform(1.0, 3.0)) # Read the job description time
                
                # Check for "Close" popup (Glassdoor loves these)
                try:
                    close_btn = driver.find_element(By.CSS_SELECTOR, "button.CloseButton")
                    close_btn.click()
                    print("Closed popup.")
                    time.sleep(1)
                except:
                    pass
                
                # Extract Data using robust selectors
                try:
                    job_title = driver.find_element(By.CSS_SELECTOR, "div[data-test='job-title']").text
                except: job_title = "N/A"
                
                try:
                    company = driver.find_element(By.CSS_SELECTOR, "div[data-test='employer-name']").text.split('\n')[0]
                except: company = "N/A"
                
                try:
                    location = driver.find_element(By.CSS_SELECTOR, "div[data-test='location']").text
                except: location = "N/A"
                
                try:
                    # Salary is often missing or in different places
                    salary = driver.find_element(By.CSS_SELECTOR, "div[data-test='salary-range']").text
                except: 
                    salary = "N/A"
                    
                try:
                    desc = driver.find_element(By.CSS_SELECTOR, "div.JobDetails_jobDescription__uW_fK").text
                except: desc = "N/A"

                jobs.append({
                    "Job Title": job_title,
                    "Company": company,
                    "Location": location,
                    "Salary": salary,
                    "Description": desc[:100] + "..." # Truncate for display
                })
                
            except Exception as e:
                print(f"Error processing card {i}: {str(e)}")
                continue
        
        # Pagination (simplified for this demo)
        if len(jobs) < num_jobs:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "button[data-test='pagination-next']")
                if next_btn.is_enabled():
                    next_btn.click()
                    time.sleep(random.uniform(4.0, 8.0))
                else:
                    break
            except:
                print("No next button found.")
                break
                
    driver.quit()
    return pd.DataFrame(jobs)

if __name__ == "__main__":
    # Bangalore
    df = get_jobs_sota("Data Scientist", "1131510", 5)
    print(df)
    
    import os
    if not os.path.exists('india_salary_prediction/data'):
        os.makedirs('india_salary_prediction/data')
    df.to_csv('india_salary_prediction/data/glassdoor_jobs_india_sota.csv', index=False)
