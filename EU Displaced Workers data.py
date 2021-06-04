import time
import os
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

startTime = datetime.now()

chromedriver = '' #add here path to chrome driver


chrome_options = Options()
chrome_options.add_argument("headless")

driver = webdriver.Chrome(chromedriver, options=chrome_options, keep_alive=False)
#runs the browser in the background

driver.get("https://www.eurofound.europa.eu/observatories/emcc/erm/factsheets")

region_name_list = ['Europe']
announcement_date_list = []
country_list = []
company_list = []
announcement_type_list = []
sector_list = []
job_creation_list = []
job_reduction_list = []

for i in range (1, 15):

    region_name_list.append('Europe')

    announcement_date_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[1]'''
    date = driver.find_element_by_xpath(announcement_date_path)
    announcement_date_list.append(date.text)

    #country_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[2]'''
    #country = driver.find_element_by_class_name(country_path)
    #country_list.append(country.text)

    company_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[3]'''
    company = driver.find_element_by_xpath(company_path)
    company_list.append(company.text)

    announcement_type_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[4]'''
    type = driver.find_element_by_xpath(announcement_type_path)
    announcement_type_list.append(type.text)

    #sector_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[5]'''
    #sector = driver.find_element_by_xpath(sector_path)
    #sector_list.append(sector.text)

    job_creation_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[6]'''
    job_creation = driver.find_element_by_xpath(job_creation_path)
    job_creation_list.append(job_creation.text)

    job_reduction_path = f'''/html/body/div[3]/main/div/div/div[2]/div/div[3]/div/table/tbody/tr[{i}]/td[7]'''
    job_reduction = driver.find_element_by_xpath(job_reduction_path)
    job_reduction_list.append(job_reduction.text)

allinfo = list(zip(region_name_list, announcement_date_list, company_list, announcement_type_list, job_creation_list, job_reduction_list))

df = pd.DataFrame(allinfo, columns= ['region', 'announcement_date', 'company', 'type', 'job_creation', 'job_reduction'])
df.to_csv('eu_displaced_worked.csv', index=False)
print(f'''Execution Time: {datetime.now()-startTime}''')
print(allinfo)

