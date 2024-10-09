import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    ElementNotInteractableException
)

def get_jobs(title, num_jobs, verbose, path, sleep_time):
    # Set up the webdriver
    service = Service(executable_path=path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    options.add_argument("--headless")
    url = f"https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={title}"
    driver.get(url)
    
    jobs = []
    first=True

    while len(jobs) < num_jobs:  # If true, should be still looking for new jobs.

        time.sleep(sleep_time)

        # Going through each job on this page
        job_buttons = driver.find_elements(By.CSS_SELECTOR, "li[class*='JobsList_jobListItem__wjTHv JobsList_dividerWithSelected__nlvH7']")
        if not job_buttons:  # If no job buttons found, break the loop
            print("No more job listings found.")
            break

        for job_button in job_buttons:
            print("Progress: {}/{}".format(len(jobs), num_jobs))
            if len(jobs) >= num_jobs:
                break

            # Retry clicking the job button
            for _ in range(3):
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", job_button)
                    if first:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_button)).click()
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//button[@class="CloseButton"]'))
                        ).click()
                        first=False
                    else:
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job_button)).click()
                    time.sleep(1)
                    break
                except (ElementClickInterceptedException, ElementNotInteractableException) as e:
                    print(f"Failed to click job button: {e}")
                    time.sleep(2)

            collected_successfully = False

            while not collected_successfully:
                    company_name = job_button.find_element(By.XPATH, './/span[@class="EmployerProfile_compactEmployerName__LE242"]').text
                    
                    location = job_button.find_element(By.XPATH, './/div[@class="JobCard_location__rCz3x"]').text
                    
                    job_title = job_button.find_element(By.XPATH, './/a[@class="JobCard_jobTitle___7I6y"]').text
                    
                    try:
                        rating = job_button.find_element(By.XPATH, './/div[@class="EmployerProfile_ratingContainer__ul0Ef"]').text
                    except NoSuchElementException:
                        rating = -1
                        
                    try:
                        salary_estimate = job_button.find_element(By.XPATH, './/div[@class="JobCard_salaryEstimate__arV5J"]').text
                    except NoSuchElementException:
                        salary_estimate = -1
                        
                    job_description = job_button.find_element(By.XPATH, './/div[@class="JobCard_jobDescriptionSnippet__yWW8q"]/div').text
                    
                    try:
                        skills = job_button.find_element(By.XPATH, './/div[@class="JobCard_jobDescriptionSnippet__yWW8q"]/div[2]').text
                    except NoSuchElementException:
                        skills = -1
                        
                    collected_successfully = True

            
            try:
                size = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Size"]/following-sibling::*').text
            except NoSuchElementException:
                size = -1
            
            try:
                founded = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Founded"]/following-sibling::*').text
            except NoSuchElementException:
                founded = -1
            
            try:
                type_of_ownership = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Type"]/following-sibling::*').text
            except NoSuchElementException:
                type_of_ownership = -1
            
            try:
                industry = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Industry"]/following-sibling::*').text
            except NoSuchElementException:
                industry = -1
            
            try:
                sector = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Sector"]/following-sibling::*').text
            except NoSuchElementException:
                sector = -1
            
            try:
                revenue = driver.find_element(By.XPATH, './/div[@class="JobDetails_overviewItem__cAsry"]//span[text()="Revenue"]/following-sibling::*').text
            except NoSuchElementException:
                revenue = -1
                

            if verbose:
                print("Job Title: {}".format(job_title))
                print("Salary Estimate: {}".format(salary_estimate))
                print("Job Description: {}".format(job_description[:500]))
                print("Skills: {}".format(skills))
                print("Rating: {}".format(rating))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))
                print("Size: {}".format(size))
                print("Founded: {}".format(founded))
                print("Type of Ownership: {}".format(type_of_ownership))
                print("Industry: {}".format(industry))
                print("Sector: {}".format(sector))
                print("Revenue: {}".format(revenue))
                print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")

            jobs.append({"Job Title" : job_title,
            "Salary Estimate" : salary_estimate,
            "Job Description" : job_description,
            "Skills" : skills,
            "Rating" : rating,
            "Company Name" : company_name,
            "Location" : location,
            "Size" : size,
            "Founded" : founded,
            "Type of ownership" : type_of_ownership,
            "Industry" : industry,
            "Sector" : sector,
            "Revenue" : revenue})
            
            
        try:
            driver.find_element(By.XPATH, './/button[@data-test="load-more"]').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break


    driver.quit()

    # Convert the list of job dictionaries to a DataFrame
    df = pd.DataFrame(jobs)
    return df

path = "E:/Profile_Data/Desktop/ds_salary_proj-master/ds_salary_proj-master - Copy/ds_salary_proj-master/chromedriver.exe"
df = get_jobs('data scientist', 10, False, path, 15)

# Save the DataFrame to a CSV file
#df.to_csv('glassdoor_jobs.csv', index=False)
#print("Saved jobs to glassdoor_jobs.csv")
