from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from time import sleep
import sys
import os
import csv
import shutil
import urllib.request
import PyPDF2

# Path to csv file that will store data 
driver_path = './chromedriver'
download_path = './outputs/Master_DetailedVerif.pdf'
outputs_path = './outputs'
final_path = './outputs/final'
final_file_path = final_path +'/medical_licenses.csv'
url = 'https://www.armedicalboard.org/public/directory/lookup.aspx'

def clean_folder(path):
	if not os.path.exists(path):
		os.makedirs(path)

def prep_folders():
	# Clean folders
	clean_folder(outputs_path)
	clean_folder(final_path)

def read_pdf(file_path):
	pdf = open(file_path, 'rb')
	reader = PyPDF2.PdfFileReader(pdf)
	text = ''
	for i in range (reader.numPages):
		page_reader = reader.getPage(i)
		text = text + page_reader.extractText()
	os.remove(download_path)
	text_list = text.split()
	text = " ".join(text_list)
	return text 

def check_board_minutes(driver, download_path):
	board_minute_link = driver.find_element(By.ID, 'ctl00_MainContentPlaceHolder_lkbtnBoardMinutes')
	driver.execute_script(board_minute_link.get_attribute('href'))

	while not os.path.exists(download_path):
		sleep(1)

	return read_pdf(download_path)

def select_licenses_by_county(county):
	file_path = './outputs/' + county + '_medical_licenses.csv'

	headers = [['Name', 'City', 'License number', 'Original issue date', 'Board minutes', 'Board orders', 'Violation']]

	with open(file_path, 'w') as f:
		writer = csv.writer(f)
		writer.writerows(headers)
		f.close()

	# Initiate driver 
	chrome_options = Options()
	chrome_options.add_argument("--headless")
	prefs = {'download.default_directory' : os.getcwd() + '/outputs'}
	chrome_options.add_experimental_option('prefs', prefs)
	s = Service(driver_path)
	driver = webdriver.Chrome(service=s, options=chrome_options)
	driver.get(url)

	# Submit search
	county_select = Select(driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lbBoxdirSearchCounty'))
	county_select.select_by_value(county)

	submit_button = driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_btnDirSearch')
	submit_button.click()

	# Wait 
	WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContentPlaceHolder_lblTitle')))

	# Counter variable for current page 
	page_counter = 0
	# Counter variable for the number of licenses 
	license_counter = 0
	# Counter variable for the number of downloaded board minutes 
	download_counter = 0 
	# Next page boolean 
	next_page = True

	# Iterate through pages until there aren't anymore 
	while next_page:
		page_counter += 1

		# Get links 
		verify_links = []
		next_page_link = ''
		elems = driver.find_elements(By.XPATH,'//a[@href]')

		for elem in elems:
			link = elem.get_attribute('href')
			link_txt = str(link)
			# Get verify license links
			if 'verify' in link_txt:
				verify_links.append(link)
			# Get next page link
			elif 'Page$' + str(page_counter+1) in link_txt:
				next_page_link = link

		# Check if there is a next page 
		if next_page_link == '':
			next_page = False

		# Iterate through verify license links 
		for verify_link in verify_links:
			# Open a new window
			# Credit: https://paveltashev.medium.com/python-and-selenium-open-focus-and-close-a-new-tab-4cc606b73388
			driver.execute_script('window.open('');')

			# Switch to the new window and open URL B
			driver.switch_to.window(driver.window_handles[1])
			driver.get(verify_link)

			# Get board minutes and orders 
			board_minutes = driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lblBoardMinutes').get_attribute('innerHTML')
			board_orders = driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lblBoardActions').get_attribute('innerHTML')

			# Board order and board minutes booleans 
			is_board_minutes = 'are available' in board_minutes
			is_board_orders = 'are available' in board_orders

			# Get name, city, license number, original issue date, board minutes, board actions
			license_info = [driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResults_ctrl0_lblPhyname').get_attribute('innerHTML'),
							driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsMail_ctrl0_lblCity').get_attribute('innerHTML'),
							driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsLicInfo_ctrl0_lblLicnumInfo').get_attribute('innerHTML'),
							driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsLicInfo_ctrl0_lblORdateInfo').get_attribute('innerHTML'),
							is_board_minutes, 
							is_board_orders]

			# View board minutes and append url
			if is_board_minutes and is_board_orders:
				license_info.append(check_board_minutes(driver, download_path))
			else: 
				license_info.append(False)

			# Close tab and switch to main tab 
			driver.close()
			driver.switch_to.window(driver.window_handles[0])

			# Write to file  
			with open(file_path, 'a') as f:
				writer = csv.writer(f)
				writer.writerows([license_info])
				f.close()

			license_counter += 1 

			# Slight delay 
			sleep(.4)

		# Go to next page and update counter 
		if next_page:
			driver.execute_script(next_page_link)

			# wait for link to go stale indicating program reached next page 
			WebDriverWait(driver, 20).until(EC.staleness_of(elems[0]))

		sleep(.2)
		print(license_counter)

	# Script ran successfully  
	print('Success!')
	driver.close() 

def find_csv_files(path_to_dir, file_type=".csv"):
	file_names = os.listdir(path_to_dir)
	return [file_name for file_name in file_names if file_name.endswith(file_type)]


def cat_outputs ():
	# Get all csvs in the output folder
	csv_paths = find_csv_files(outputs_path)

	# Write headers 
	with open(final_file_path, 'w', newline='') as f_write:
		writer = csv.writer(f_write)
		with open(os.path.join(outputs_path,csv_paths[0]), 'r', newline='') as f_read:
			reader = csv.reader(f_read)
			writer.writerow(next(reader))
			f_read.close()
		f_write.close()

	# Read data for all ages events 
	for file_path in csv_paths: 
		with open(os.path.join(outputs_path,file_path), 'r', newline='') as f_read:
			reader = csv.reader(f_read)
			next(reader)
			with open(final_file_path, 'a', newline='') as f_append:
				appender = csv.writer(f_append)
				for row in reader:
					appender.writerow(row)
				f_append.close()
		f_read.close()