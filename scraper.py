from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# sets the path for chromedriver
# def scrape_url(url):
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument("--disable-extensions")
#     chrome_options.add_argument("--disable-plugins")
#     chrome_options.add_argument("--disable-images")
#     chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

#     # Modern Selenium 4.x way to specify ChromeDriver path
#     service = Service(executable_path="/opt/render/project/.render/chromedriver/chromedriver")
    
#     driver = webdriver.Chrome(
#         service=service,
#         options=chrome_options
#     )

#     try:
#         driver.set_page_load_timeout(15)
#         driver.get(url)
#         html = driver.page_source
#     except TimeoutException:
#         return "[Timeout] Page failed to load"
#     except Exception as e:
#         return f"[Error] {str(e)}"
#     finally:
#         driver.quit()

#     soup = BeautifulSoup(html, "html.parser")
#     for s in soup(["script", "style"]):
#         s.decompose()
#     return ' '.join(p.get_text(strip=True) for p in soup.find_all(["p", "article", "main"]))

# Alternative version that uses PATH (if you prefer)
def scrape_url(url):
    """
    This version relies on chromedriver being in PATH
    (which it will be with your export PATH command)
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

    # Let Selenium find chromedriver from PATH
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.set_page_load_timeout(15)
        driver.get(url)
        html = driver.page_source
    except TimeoutException:
        return "[Timeout] Page failed to load"
    except Exception as e:
        return f"[Error] {str(e)}"
    finally:
        driver.quit()

    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style"]):
        s.decompose()
    return ' '.join(p.get_text(strip=True) for p in soup.find_all(["p", "article", "main"]))