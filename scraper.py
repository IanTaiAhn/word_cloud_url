import requests
from bs4 import BeautifulSoup

def scrape_url(url):
    # response = requests.get(url, verify=False) #TODO Remove this verify=False in production
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    [s.extract() for s in soup(['script', 'style'])]
    text = ' '.join(p.get_text() for p in soup.find_all(['p', 'article', 'main']))
    return text