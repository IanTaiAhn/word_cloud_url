from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

def scrape_url(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

    driver = webdriver.Chrome(
        executable_path="/opt/render/project/.render/chromedriver/chromedriver",
        options=chrome_options
    )

    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        html = driver.page_source
    except TimeoutException:
        return "[Timeout] Page failed to load"
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style"]):
        s.decompose()
    return ' '.join(p.get_text(strip=True) for p in soup.find_all(["p", "article", "main"]))


# def scrape_url(url):
#     headers = {
#         'User-Agent': (
#             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#             'AppleWebKit/537.36 (KHTML, like Gecko) '
#             'Chrome/114.0.0.0 Safari/537.36'
#         ),
#         'Accept-Language': 'en-US,en;q=0.9',
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     }

#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()  # Raises HTTPError for bad responses (4xx/5xx)
#     except requests.exceptions.RequestException as e:
#         print(f"Request failed: {e}")
#         return ""

#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Remove script and style elements
#     for s in soup(['script', 'style']):
#         s.decompose()

#     # Extract text
#     text = ' '.join(p.get_text(strip=True) for p in soup.find_all(['p', 'article', 'main']))
#     return text
