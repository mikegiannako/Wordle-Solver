from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
# import chromedriver_autoinstaller
from time import sleep
import re
import random
import string
import argparse

WORDS_URL = 'https://gist.githubusercontent.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/ca9018b32e963292473841fb55fd5a62176769b5/valid-wordle-words.txt'

# Gets the words from the website specified in word_scrapper.py
from word_scrapper import WordScrapper
import os
words : list[str] = []

# set of letters
letters  = string.ascii_lowercase

# List of a set of characters that can't be used for every letter of the word
filters : list[set[str]] = [set(), set(), set(), set(), set()]
found_letters : list[str] = ['', '', '', '', '']

# List of letters that need to exist in the string
present : set[str] = set()

def regulate_filters(result : list[tuple[str,str]]) -> None:
    global filters
    global present

    # First patching all the letters that are correct to make next checks easier
    for i,res in enumerate(result):
        # As there's only one correct letter, we remove all else
        if res[1] == 'correct':
            filters[i] = set(letters) - {res[0]}
            # if we find a letter we were "searching for" we remove it from the present set
            # as it's in its correct position now
            if res[0] in present: present.remove(res[0])
            found_letters[i] = res[0]

    # Afterwards we check for all the other cases
    for i,res in enumerate(result):
        if res[1] == 'present':
            # if a letter is present, it means it doesn't belong to the specific
            # position it was found but need to be added to the next word(s)
            filters[i].add(res[0])
            present.add(res[0])
        elif res[1] == 'absent':
            for j in range(len(filters)): 
                # There's a chance a letter appears 2 times, one in a correct position
                # and once in a wrong position, so we need to remove it from all the
                # position except the one that's it's correct
                if(result[j][1] != 'correct'): 
                    filters[j].add(res[0])

# Generate the regex by creating a pattern that will recognize 5 letter words and for each letter
# we add all the ones that *aren't* legal to use. In case we have found the correct letter we just
# add every other letter except the correct one.
def generate_regex() -> str:
    global filters

    regex = ''
    for filt in filters:
        regex += f'[^{"".join(filt)}]' if len(filt) > 0 else '.'
    
    return regex

# Find the state of the letters in the #iteration line and returns them in
# a list like such: [('s', 'absent'), ('t', 'absent'), ('e', 'absent'), ('a', 'correct'), ('m', 'absent')]
def find_row_state(browser: WebDriver, iteration : int) -> list[tuple[str, str]]:
    
    # Gets all the rows of the board and selects the one that was just submitted and evaluated
    result : WebElement = browser.find_elements(By.CLASS_NAME, "Row-module_row__pwpBq")[iteration]
    
    # Creates a list with all the letters/tiles of the selected row
    tiles : list[WebElement] = result.find_elements(By.CLASS_NAME, "Tile-module_tile__UWEHN")

    # the 'innerHTML' property is a more convenient way of getting the text of the WebElement in this situation
    # the attribute 'data-state' gives as the information about the tile state ('absent', 'correct', 'present')

    return [(str(tile.get_property('innerHTML')), str(tile.get_attribute('data-state'))) for tile in tiles]

def try_word(browser : WebDriver, word : str) -> None:
    # Finding the text area (which is virtually anywhere)
    text_area = browser.find_element(By.CSS_SELECTOR, 'body')
    
    # Typing the word
    text_area.send_keys(word)
    # Submit the word
    text_area.send_keys(Keys.ENTER)

def find_word(regex : str) -> str:
    global words

    # compiles the regex 
    r = re.compile(regex)
    
    # filters the words that don't match the regex
    words = list(filter(lambda word: r.match(word), words))

    # filters the words that don't have all the letters in the present set
    words = list(filter(lambda word: all([p in word for p in present]), words))
    
    # in case no word matches the regex we catch the error and stop the program
    if len(words) == 0:
        print('No word matches the regex')
        print('The regex was:', regex)
        exit()

    # else, create a copy of the words list where for each word we remove the letters that we know are present or correct
    candidate_letters = list(map(lambda word: ''.join([word[i] for i in range(5) if word[i] not in present and word[i] != found_letters[i]]), words))

    # Then we count the frequency of each letter in the list 
    frequencies = [sum([word.count(letter) for word in candidate_letters]) for letter in letters]
    
    # and choose the element in the list that has the highest sum of frequencies
    # This is done so if the word is not the correct one we extract the maximum amount 
    # of information (aka we get to eliminate more words)
    sorted_by_freq = sorted(words, key=lambda word: sum(frequencies[letters.index(letter)] for letter in set(candidate_letters[words.index(word)])), reverse=True)
    return sorted_by_freq[0]

def save_image(browser : WebDriver) -> None:
    browser.find_element(By.CLASS_NAME, 'Board-module_board__jeoPS').screenshot('wordle.png')

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Wordle Solver')
    parser.add_argument('-d', '--driver', type=str, help='Path to the chromedriver')
    parser.add_argument('-w', '--words', type=str, help='Link to list of words to use')
    parser.add_argument('-s', '--start', type=str, help='Starting word')
    parser.add_argument('-hl', '--headless', action='store_true', help='Run the browser in headless mode')
    return parser.parse_args()

def main() -> None:
    global words
    cmd_args : argparse.Namespace = parse_args()

    # You should add a "driver_path" file with the path to your chromedriver.exe
    with open(cmd_args.driver or "driver_path", 'r') as f:
        driver_path = f.readlines()[0].strip()

    words = WordScrapper(cmd_args.words or WORDS_URL).get_words()

    # Downloads the chromedriver.exe if 
    # chromedriver_autoinstaller.install()

    # Setting the options for the browser
    options = Options()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Disabling the notifications
    options.add_argument("--disable-notifications")
    # Disable cert errors
    options.add_argument('--ignore-certificate-errors')
    # Make the browser headless
    if cmd_args.headless:
        options.add_argument("--headless")
    
    # Setting the service for the browser
    service = Service(driver_path)

    # Initializing the browser
    browser = webdriver.Chrome(service=service, options=options)
    # Entering the website
    browser.get('https://www.nytimes.com/games/wordle/')
    # Maximizing the browser window
    browser.maximize_window()
    # Waiting for the page to load
    browser.implicitly_wait(2)

    # If there's a popup about the new terms of service, we close it
    try:
        browser.find_element(By.XPATH, '/html/body/div[2]/div/div/button').click()
        browser.implicitly_wait(2)
    except:
        pass

    try:
        # Finding the reject cookies button and clicking it
        browser.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div/div/div[2]/div[1]/button[3]').click()
        browser.implicitly_wait(2)
    except:
        pass
    
    try:
        # Finding the updated terms of service button and clicking it
        browser.find_element(By.XPATH, '/html/body/div[4]/div/div/button').click()
        browser.implicitly_wait(2)
    except:
        pass

    sleep(1)

    # Clicking on the play button
    play_button = browser.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div/div[2]/button[3]')
    # and clicking it
    play_button.click()

    browser.implicitly_wait(2)

    # Clicking on the X button to close the popup
    try:
        browser.find_element(By.XPATH, '//*[@id="help-dialog"]/div/div/button').click()
    except:
        pass

    # Waiting for the page to load
    sleep(2) # I had to put sleep instead of implicit wait because the implicit
             # wait thought the page was loaded and the first input was sent too fast

    # Tries 6 words, break the loop if the word is correct
    for i in range(6):
        # Types and submits the word, the first word will always be 'steam'
        try_word(browser, word := find_word(generate_regex()) if i != 0 else (cmd_args.start or 'adieu'))

        # Necessary to wait for the page to load because of animations
        # implicitly_wait didn't do the job
        sleep(3)

        # Getting the result of the word typed
        result = find_row_state(browser, i)

        if [res[1] == 'correct' for res in result] == [True] * 5:
            print(f"The word is: {word}")
            break

        # Adjusting the regex based on the results we just got from the most recent word
        regulate_filters(result)
    else:
        print("The word was not found")

    # Scroll down until the whole board is visible
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Saves the completed puzzle as an image to a file named 'wordle.png' in the current directory
    save_image(browser)
    print(f"Screenshot of the wordle saved at: {os.getcwd() + '/wordle.png'}")

    # Closes the browser
    browser.quit()

if __name__ == '__main__':
    main()