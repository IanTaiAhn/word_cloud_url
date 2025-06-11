from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup

def scrape_url(url):
    # Setup headless Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    )

    try:
        # Initialize the browser
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(15)

        # Attempt to fetch the page
        driver.get(url)
        html = driver.page_source
        driver.quit()

        # Parse and clean the HTML
        soup = BeautifulSoup(html, 'html.parser')
        for s in soup(['script', 'style']):
            s.decompose()

        # Extract meaningful text
        text = ' '.join(
            p.get_text(strip=True) for p in soup.find_all(['p', 'article', 'main'])
        )

        if not text.strip():
            raise ValueError("No meaningful content extracted from page.")

        return text

    except TimeoutException:
        print(f"[Timeout] Failed to load: {url}")
    except WebDriverException as e:
        print(f"[WebDriver Error] {e}")
    except Exception as e:
        print(f"[Unexpected Error] {e}")
    finally:
        try:
            driver.quit()
        except:
            pass  # driver might already be closed

    return ""  # Return empty string on failure


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
