# -*- coding: utf-8 -*-
"""
@author: Sarthak (Modified)
"""

from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import pandas as pd


def get_jobs(keyword, num_jobs, verbose, path, slp_time):
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''

    # Setup Chrome driver
    service = Service(executable_path=path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1120, 1000)

    url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={keyword}"
    driver.get(url)
    jobs = []

    while len(jobs) < num_jobs:
        time.sleep(slp_time)

        # Close sign-up pop-up if it appears
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "selected"))
            ).click()
        except:
            pass

        try:
            driver.find_element(By.CLASS_NAME, "modal_closeIcon").click()
        except:
            pass

        job_buttons = driver.find_elements(By.CSS_SELECTOR, "li[class*='JobsList_jobListItem']")
        if not job_buttons:
            print("No more job listings found.")
            break

        for job_button in job_buttons:
            print(f"Progress: {len(jobs)}/{num_jobs}")
            if len(jobs) >= num_jobs:
                break

            try:
                job_button.click()
                time.sleep(1)
            except ElementClickInterceptedException:
                continue

            try:
                job_title = job_button.find_element(By.XPATH, './/a[contains(@class,"JobCard_jobTitle")]').text
            except NoSuchElementException:
                job_title = "N/A"

            try:
                company_name = job_button.find_element(By.XPATH, './/div[contains(@class,"EmployerProfile")]').text
            except NoSuchElementException:
                company_name = "N/A"

            try:
                location = job_button.find_element(By.XPATH, './/div[contains(@class,"JobCard_location")]').text
            except NoSuchElementException:
                location = "N/A"

            try:
                job_description = driver.find_element(By.XPATH, './/div[@data-test="jobDescriptionContent"]').text
            except NoSuchElementException:
                job_description = "N/A"

            try:
                rating = job_button.find_element(By.XPATH, './/span[contains(@class,"rating")]').text
            except NoSuchElementException:
                rating = "N/A"

            try:
                salary_estimate = job_button.find_element(By.XPATH, './/div[contains(@class,"JobCard_salaryEstimate")]').text
            except NoSuchElementException:
                salary_estimate = "N/A"

            # Employer details
            def safe_find(text):
                try:
                    return driver.find_element(By.XPATH, f'.//span[text()="{text}"]/following-sibling::*').text
                except NoSuchElementException:
                    return "N/A"

            size = safe_find("Size")
            founded = safe_find("Founded")
            type_of_ownership = safe_find("Type")
            industry = safe_find("Industry")
            sector = safe_find("Sector")
            revenue = safe_find("Revenue")

            if verbose:
                print(f"Title: {job_title}, Company: {company_name}, Location: {location}")
                print(f"Salary: {salary_estimate}, Rating: {rating}")
                print(f"Size: {size}, Founded: {founded}, Ownership: {type_of_ownership}, Industry: {industry}")
                print("------------------------------------------------------")

            jobs.append({
                "Job Title": job_title,
                "Salary Estimate": salary_estimate,
                "Job Description": job_description,
                "Rating": rating,
                "Company Name": company_name,
                "Location": location,
                "Size": size,
                "Founded": founded,
                "Type of ownership": type_of_ownership,
                "Industry": industry,
                "Sector": sector,
                "Revenue": revenue
            })

        try:
            driver.find_element(By.XPATH, './/button[@data-test="pagination-next"]').click()
        except NoSuchElementException:
            print(f"Reached end of pages. Collected {len(jobs)} jobs.")
            break

    driver.quit()
    return pd.DataFrame(jobs)


if __name__ == "__main__":
    df = get_jobs(
        keyword="data scientist",
        num_jobs=10,
        verbose=True,
        path="chromedriver.exe",  
        slp_time=5
    )

    df.to_csv('glassdoor_jobs.csv', index=False)
    print("Scraping completed. Data saved to 'glassdoor_jobs.csv'")
