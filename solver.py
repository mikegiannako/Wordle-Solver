from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium import webdriver
from time import sleep
import re
import random

# Gets the words from the website specified in word_scrapper.py
from word_scrapper import get_words
words = get_words()

# set of letters
letters = 'abcdefghijklmnopqrstuvwxyz'

# List of a set of characters that can't be used for every letter of the word
filters = [set(), set(), set(), set(), set()]

# List of letters that need to exist in the string
present = set()

def regulate_filters(result):
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
def generate_regex():
    global filters

    regex = ''
    for filt in filters:
        regex += f'[^{"".join(filt)}]' if len(filt) > 0 else '.'
    
    return regex

# Find the state of the letters in the #iteration line and returns them in
# a list like such: [('s', 'absent'), ('t', 'absent'), ('e', 'absent'), ('a', 'correct'), ('m', 'absent')]
def find_row_state(browser: WebElement, iteration):
    
    # Gets all the rows of the board and selects the one that was just submitted and evaluated
    result : WebElement = browser.find_elements_by_class_name("Row-module_row__dEHfN")[iteration]
    
    # Creates a list with all the letters/tiles of the selected row
    tiles = result.find_elements_by_class_name("Tile-module_tile__3ayIZ")

    # the 'innerHTML' property is a more convenient way of getting the text of the WebElement in this situation
    # the attribute 'data-state' gives as the information about the tile state ('absent', 'correct', 'present')
    return [(tile.get_property('innerHTML'), tile.get_attribute('data-state')) for tile in tiles]

def try_word(browser, word):
    # Finding the text area (which is virtually anywhere)
    text_area = browser.find_element_by_css_selector('body')
    
    # Typing the word
    text_area.send_keys(word)
    # Submit the word
    text_area.send_keys(Keys.ENTER)

def find_word(regex):
    global words

    # compiles the regex
    r = re.compile(regex)
    
    # filters the words that don't match the regex
    words = list(filter(r.match, words))

    # filters the words that don't have all the letters in the present set
    words = list(filter(lambda word: all([p in word for p in present]), words))
    
    # in case no word matches the regex we catch the error and stop the program
    try:
        return random.choice(words)
    except IndexError:
        print(generate_regex(), present)
        quit()

def save_image(browser : WebElement):
    browser.find_element_by_class_name('Board-module_board__lbzlf').screenshot('wordle.png')

def main():
    # You should add a "driver_path" file with the path to your chromedriver.exe
    with open("driver_path", "r") as f:
        driver_path = f.readlines()[0].strip()


    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Initializing the browser
    browser = webdriver.Chrome(executable_path=driver_path, options=options)
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

    # Tries maximum 6 words, break the loop if the word is correct
    for i in range(6):
        # Types and submits the word, the first word will always be 'steam'
        try_word(browser, word := find_word(generate_regex()) if i != 0 else 'steam')

        # Necessary to wait for the page to load because of animations
        # implicitly_wait didn't do the job
        sleep(3)

        # Getting the result of the word typed
        result = find_row_state(browser, i)

        if [res[1] == 'correct' for res in result] == [True] * 5:
            print(f'Iteration {i + 1} is correct\nThe word was {word}')
            break

        # Adjusting the regex based on the results we just got from the most recent word
        regulate_filters(result)

    # Saves the completed puzzle as an image to a file named 'wordle.png' in the current directory
    save_image(browser)

if __name__ == '__main__':
    main()