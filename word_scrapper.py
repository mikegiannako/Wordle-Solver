def get_words():
    # Read the text from:
    # https://gist.githubusercontent.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/ca9018b32e963292473841fb55fd5a62176769b5/valid-wordle-words.txt 
    # and store it in a variable called words using bs4

    from bs4 import BeautifulSoup
    from urllib.request import urlopen

    url = 'https://gist.githubusercontent.com/dracos/dd0668f281e685bad51479e5acaadb93/raw/ca9018b32e963292473841fb55fd5a62176769b5/valid-wordle-words.txt'
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    words = soup.get_text().split('\n')

    return words


if __name__ == '__main__':
    print("Please run solver.py")