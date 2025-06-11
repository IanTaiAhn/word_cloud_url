from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import logging

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
        driver.set_page_load_timeout(30)  # Increased timeout
        driver.get(url)
        
        # Wait a moment for any dynamic content
        import time
        time.sleep(2)
        
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

# # Test function to verify scraper works
# def test_scraper():
#     """Test the scraper with a simple page"""
#     test_urls = [
#         "https://httpbin.org/html",
#         "https://example.com",
#         "https://www.google.com"
#     ]
    
#     for url in test_urls:
#         print(f"\n🧪 Testing: {url}")
#         result = scrape_url(url)
#         print(f"Result length: {len(result)}")
#         print(f"First 200 chars: {result[:200]}...")
#         if result.startswith("[Error]") or result.startswith("[Timeout]"):
#             print(f"❌ Failed: {result}")
#         else:
#             print("✅ Success")

# if __name__ == "__main__":
#     test_scraper()

##Old##
# Alternative version that uses PATH (if you prefer)
# def scrape_url(url):
#     """
#     This version relies on chromedriver being in PATH
#     (which it will be with your export PATH command)
#     """
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

#     # Let Selenium find chromedriver from PATH
#     driver = webdriver.Chrome(options=chrome_options)

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



##OLDest##
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