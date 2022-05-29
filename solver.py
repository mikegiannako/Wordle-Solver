from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from time import sleep
import re

# Gets the words from the website specified in word_scrapper.py
from word_scrapper import get_words
words = get_words()

def find_result(browser, iteration):
    # Find the state of the letters in the #iteration line and returns them in
    # a list like such: [('s', 'absent'), ('t', 'absent'), ('e', 'absent'), ('a', 'correct'), ('m', 'absent')]

    result: WebElement = browser.execute_script(f"""
                                    return document
                                    .querySelector('game-app')
                                    .shadowRoot
                                    .querySelector('#game')
                                    .querySelector('#board-container')
                                    .querySelector('game-row:nth-child({iteration})')
                                    .shadowRoot
                                    .querySelector('div.row')
                                    """)
    
    return re.findall(r'letter="([a-z])" evaluation="(absent|correct|present)"',result.get_property('innerHTML'))

def try_word(browser):
    # Finding the text area (which is virtually anywhere)
    text_area = browser.find_element_by_css_selector('body')
    
    # Typing the word
    text_area.send_keys('kappa')
    # Submit the word
    text_area.send_keys(Keys.ENTER)

def main():
    # You should add a "driver_path" file with the path to your chromedriver.exe
    with open("driver_path", "r") as f:
        driver_path = f.readlines()[0].strip()

    # Initializing the browser
    browser = webdriver.Chrome(executable_path=driver_path, options=Chrome_Options())
    # Entering the website
    browser.get('https://www.nytimes.com/games/wordle/')
    # Maximizing the browser window
    browser.maximize_window()
    # Waiting for the page to load
    browser.implicitly_wait(2)

    # Finding the reject cookies button
    reject_button = browser.find_element_by_xpath('//*[@id="pz-gdpr-btn-reject"]')
    # and clicking it
    reject_button.click()

    # Clicking anywhere for the tutorial to disappear
    browser.find_element_by_css_selector('body').click()


    for i in range(6):
        # Types and submits the word
        try_word(browser)

        # Necessary to wait for the page to load because of animations
        sleep(3)

        result = find_result(browser, i + 1)
        if all([res[1] == 'correct' for res in result]):
            print(f'Iteration {i + 1} is correct')
            break


if __name__ == '__main__':
    main()
