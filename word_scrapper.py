def get_words():
    # Read the text from https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt using bs4
    # and store it in a variable called words

    from bs4 import BeautifulSoup
    from urllib.request import urlopen

    url = 'https://www-cs-faculty.stanford.edu/~knuth/sgb-words.txt'
    html = urlopen(url)
    soup = BeautifulSoup(html, 'html.parser')

    words = soup.get_text().split('\n')

    return words


if __name__ == '__main__':
    print("Please run solver.py")