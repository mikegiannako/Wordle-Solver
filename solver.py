# Enter https://www.nytimes.com/games/wordle/ using selenium
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium import webdriver
from time import sleep

chrome_options = Chrome_Options()

with open("driver_path", "r") as f:
    driver_path = f.readlines()[0]

browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
browser.implicitly_wait(5)

browser.get('https://www.nytimes.com/games/wordle/')
browser.maximize_window()

browser.implicitly_wait(2)

reject_button = browser.find_element_by_xpath('//*[@id="pz-gdpr-btn-reject"]')
reject_button.click()

browser.find_element_by_css_selector('body').click()

sleep(60)