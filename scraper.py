from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import logging
import time
import os
# from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)

def scrape_url(url):
    """
    Improved scraper with better error handling and debugging
    """
    driver = None
    try:
        logger.info(f"🔍 Starting to scrape: {url}")
        
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return f"[Error] Invalid URL: {url}"
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

        # Use the Service class for modern Selenium
        service = Service(executable_path="/opt/render/project/.render/chromedriver/chromedriver")
        
        logger.info("🚀 Initializing Chrome driver...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        logger.info(f"📡 Loading page: {url}")
        # driver.set_page_load_timeout(30)  # Increased timeout
        # driver.get(url)
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            try:
                driver.get(url)
                break
            except WebDriverException as e:
                if "ssl" in str(e).lower() or "handshake" in str(e).lower():
                    logger.warning(f"🔁 SSL error on attempt {attempt + 1}, retrying...")
                    time.sleep(2)
                else:
                    raise
        
        logger.info("📄 Getting page source...")
        html = driver.page_source
        
        if not html or len(html) < 100:
            return f"[Error] Page returned minimal content: {len(html)} characters"
        
        logger.info(f"✅ Page loaded successfully. HTML length: {len(html)} characters")
        
    except TimeoutException:
        logger.error(f"⏰ Timeout loading page: {url}")
        return f"[Timeout] Page failed to load within 30 seconds: {url}"
    except WebDriverException as e:
        logger.error(f"🚫 WebDriver error: {e}")
        return f"[Error] WebDriver error: {str(e)}"
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return f"[Error] Unexpected error: {str(e)}"
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("🔚 Driver closed successfully")
            except:
                pass

    # Parse with BeautifulSoup
    try:
        logger.info("🍲 Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Try multiple content extraction strategies
        content_text = ""
        
        # Strategy 1: Look for main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and any(word in x.lower() for word in ['content', 'main', 'article', 'post', 'story']))
        
        if main_content:
            logger.info("📝 Found main content area")
            content_text = main_content.get_text(separator=' ', strip=True)
        else:
            # Strategy 2: Get text from common content elements
            logger.info("📝 Using fallback content extraction")
            elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
            content_text = ' '.join([elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)])
        
        # Clean up the text
        content_text = ' '.join(content_text.split())  # Remove extra whitespace
        
        if len(content_text) < 50:
            logger.warning(f"⚠️ Very little content extracted: {len(content_text)} characters")
            # Try getting all text as last resort
            content_text = soup.get_text(separator=' ', strip=True)
            content_text = ' '.join(content_text.split())
        
        logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
        # Return first 10000 characters to avoid overwhelming the topic modeling
        if len(content_text) > 10000:
            content_text = content_text[:10000] + "..."
            logger.info("✂️ Content truncated to 10000 characters")
        
        return content_text
        
    except Exception as e:
        logger.error(f"❌ Error parsing HTML: {e}")
        return f"[Error] Failed to parse HTML: {str(e)}"


# def scrape_url_local(url, headless=True, timeout=30, ignore_ssl=False):
#     """
#     Local version of the web scraper - automatically manages ChromeDriver
    
#     Args:
#         url (str): URL to scrape
#         headless (bool): Run browser in headless mode (default: True)
#         timeout (int): Page load timeout in seconds (default: 30)
#         ignore_ssl (bool): Ignore SSL certificate errors (default: False)
    
#     Returns:
#         str: Extracted text content or error message
#     """
#     driver = None
#     try:
#         logger.info(f"🔍 Starting to scrape: {url}")
        
#         # Validate URL
#         if not url or not url.startswith(('http://', 'https://')):
#             return f"[Error] Invalid URL: {url}"
        
#         # Chrome options for local development
#         chrome_options = Options()
#         if headless:
#             chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-plugins")
#         chrome_options.add_argument("--disable-images")
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         chrome_options.add_experimental_option('useAutomationExtension', False)
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
#         ###more logging
#         chrome_options.add_argument("--enable-logging")
#         chrome_options.add_argument("--v=1")
#         # SSL certificate bypass options (for corporate firewalls)
#         if ignore_ssl:
#             chrome_options.add_argument("--ignore-ssl-errors")
#             chrome_options.add_argument("--ignore-certificate-errors")
#             chrome_options.add_argument("--allow-running-insecure-content")
#             chrome_options.add_argument("--disable-web-security")
#             chrome_options.add_argument("--ignore-certificate-errors-spki-list")
#             chrome_options.add_argument("--ignore-ssl-errors-list")
#             chrome_options.add_argument("--accept-insecure-certs")
#             logger.info("🔓 SSL certificate checking enabled for now")
        
#         # Use ChromeDriverManager to automatically handle driver installation
#         logger.info("🚀 Initializing Chrome driver (auto-managing driver)...")
        
#         # Disable SSL verification for ChromeDriverManager if needed
#         if ignore_ssl:
#             os.environ['WDM_SSL_VERIFY'] = '0'
#             logger.info("🔓 ChromeDriverManager SSL verification disabled")
        
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         # Phase 2: Re-enable SSL verification for everything else
#         os.environ.pop('WDM_SSL_VERIFY', None)
#         os.environ.pop('REQUESTS_CA_BUNDLE', None)
#         os.environ.pop('SSL_CERT_FILE', None)
#         logger.info("🔐 ChromeDriverManager SSL verification re-enabled")

#         # Additional stealth measures
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

#         # Optional: Wait for specific elements if needed
#         try:
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "body"))
#             )
#         except TimeoutException:
#             logger.warning("⚠️ Body element not found within timeout, proceeding anyway")
        
#         logger.info(f"📡 Loading page: {url}")
#         # driver.set_page_load_timeout(timeout)
#         # driver.get(url)

#         # driver.get_log("performance")
#         # Wait for page to load and any dynamic content
#         logger.info("⏳ Waiting for page to fully load...")
#         time.sleep(3)

#         MAX_RETRIES = 3
#         for attempt in range(MAX_RETRIES):
#             try:
#                 driver.get(url)
#                 break
#             except WebDriverException as e:
#                 if "ssl" in str(e).lower() or "handshake" in str(e).lower():
#                     logger.warning(f"🔁 SSL error on attempt {attempt + 1}, retrying...")
#                     time.sleep(2)
#                 else:
#                     raise

#         logger.info("📄 Getting page source...")
#         html = driver.page_source
        
#         if not html or len(html) < 100:
#             return f"[Error] Page returned minimal content: {len(html)} characters"
        
#         logger.info(f"✅ Page loaded successfully. HTML length: {len(html)} characters")
        
#     except TimeoutException:
#         logger.error(f"⏰ Timeout loading page: {url}")
#         return f"[Timeout] Page failed to load within {timeout} seconds: {url}"
#     except WebDriverException as e:
#         logger.error(f"🚫 WebDriver error: {e}")
#         return f"[Error] WebDriver error: {str(e)}"
#     except Exception as e:
#         logger.error(f"❌ Unexpected error: {e}")
#         return f"[Error] Unexpected error: {str(e)}"
#     finally:
#         if driver:
#             try:
#                 driver.quit()
#                 logger.info("🔚 Driver closed successfully")
#             except Exception as e:
#                 logger.warning(f"Warning closing driver: {e}")

#     # Parse with BeautifulSoup
#     try:
#         logger.info("🍲 Parsing HTML with BeautifulSoup...")
#         soup = BeautifulSoup(html, "html.parser")
        
#         # Remove unwanted elements
#         for element in soup(["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript"]):
#             element.decompose()
        
#         # Remove elements with common ad/tracking classes
#         for element in soup.find_all(attrs={"class": lambda x: x and any(
#             word in ' '.join(x).lower() for word in ['ad', 'advertisement', 'tracking', 'cookie', 'popup', 'modal']
#         )}):
#             element.decompose()
        
#         # Try multiple content extraction strategies
#         content_text = ""
        
#         # Strategy 1: Look for main content areas
#         selectors = [
#             'main',
#             'article',
#             '[role="main"]',
#             '.content',
#             '.main-content',
#             '.article-content',
#             '.post-content',
#             '.entry-content',
#             '.story-body',
#             '#content',
#             '#main-content'
#         ]
        
#         main_content = None
#         for selector in selectors:
#             main_content = soup.select_one(selector)
#             if main_content:
#                 logger.info(f"📝 Found main content area with selector: {selector}")
#                 break
        
#         if main_content:
#             content_text = main_content.get_text(separator=' ', strip=True)
#         else:
#             # Strategy 2: Get text from common content elements
#             logger.info("📝 Using fallback content extraction")
#             content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'span'])
#             content_text = ' '.join([
#                 elem.get_text(strip=True) 
#                 for elem in content_elements 
#                 if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 10
#             ])
        
#         # Clean up the text
#         content_text = ' '.join(content_text.split())  # Remove extra whitespace
        
#         if len(content_text) < 50:
#             logger.warning(f"⚠️ Very little content extracted: {len(content_text)} characters")
#             # Try getting all text as last resort
#             content_text = soup.get_text(separator=' ', strip=True)
#             content_text = ' '.join(content_text.split())
        
#         logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
#         # Return first 10000 characters to avoid overwhelming downstream processing
#         if len(content_text) > 10000:
#             content_text = content_text[:10000] + "..."
#             logger.info("✂️ Content truncated to 10000 characters")
        
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"
