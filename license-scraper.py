from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.chrome.service import Service
from scraper_functions import clean_folder, read_pdf
import os
from time import sleep
import csv

# Paths  
output_path = './outputs/final.csv'
driver_path = './chromedriver'
url = 'https://www.armedicalboard.org/public/directory/lookup.aspx'
download_path = './inputs/medical_licenses'

# Clean paths
clean_folder(download_path)
clean_folder(os.path.split(output_path)[0])

# Add header for the first row of data
headers = [['Name', 'City', 'License number', 'Original issue date', 'Board minutes?', 'Board orders?', 'Board minutes and orders?', 'Board minutes links']]
with open(output_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerows(headers)
    f.close()

# Initiate driver 
chrome_options = Options()
#chrome_options.add_argument("--headless")
profile = {"download.default_directory" : download_path}
chrome_options.add_experimental_option("prefs", profile)
s = Service(driver_path)
driver = webdriver.Chrome(service=s, options=chrome_options)
driver.get(url)

# Submit search 
submit_button = driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_btnDirSearch')
submit_button.click()

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
        is_orders_and_minutes = is_board_orders and is_board_minutes

        # Get name, city, license number, original issue date, board minutes, board actions
        license_info = [driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResults_ctrl0_lblPhyname').get_attribute('innerHTML'),
                        driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsMail_ctrl0_lblCity').get_attribute('innerHTML'),
                        driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsLicInfo_ctrl0_lblLicnumInfo').get_attribute('innerHTML'),
                        driver.find_element(By.ID,'ctl00_MainContentPlaceHolder_lvResultsLicInfo_ctrl0_lblORdateInfo').get_attribute('innerHTML'),
                        is_board_minutes, 
                        is_board_orders,
                        is_orders_and_minutes]

        # View board minutes and append url
        if is_board_minutes:
            board_minute_link = driver.find_element(By.ID, 'ctl00_MainContentPlaceHolder_lkbtnBoardMinutes')
            driver.execute_script(board_minute_link.get_attribute('href'))

            # get pdf file name
            pdf_filename = 'Master_DetailedVerif'
            

            if download_counter == 0:
                pdf_filename = pdf_filename + '.pdf'
            else: 
                pdf_filename = pdf_filename + '(' + str(download_counter), ').pdf'
            
            output_path = os.path.join(download_path, pdf_filename)

            # delay to ensure pdf downloads 
            while not os.path.exists(output_path):
                sleep(.1)

        # Close tab and switch to main tab 
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Write to file  
        with open(output_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerows([license_info])
            f.close()

        license_counter += 1 

        # Slight delay 
        sleep(.1)

    # Go to next page and update counter 
    if next_page:
        driver.execute_script(next_page_link)

    sleep(.1)
    print(license_counter)

# TODO: Read 100 pages and download pds, then call the script again for another 100 pages. Repeat till end
    
# Script ran successfully  
print('Success!') 