class WordScrapper:
    '''This class is used to scrape a basic word file from a website'''
    def __init__(self, url: str) -> None:
        self.url = url

    def get_words(self) -> list[str]:
        from bs4 import BeautifulSoup
        from urllib.request import urlopen

        html = urlopen(self.url)
        soup = BeautifulSoup(html, 'html.parser')
        
        return soup.get_text().split('\n')

if __name__ == '__main__':
    print("Please run solver.py")