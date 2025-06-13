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
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

logger = logging.getLogger(__name__)

#########same as the great local version################
# def scrape_url(url, headless=True, timeout=30):
#     """
#     Local version of the web scraper using undetected-chrome for better stealth
    
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
        
#         # Configure undetected-chrome options
#         chrome_options = uc.ChromeOptions()
        
#         # Basic stealth options
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-plugins")
#         chrome_options.add_argument("--disable-images")
#         chrome_options.add_argument("--disable-web-security")
#         chrome_options.add_argument("--allow-running-insecure-content")
        
#         # Enhanced stealth options for undetected-chrome
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--disable-features=VizDisplayCompositor")
#         chrome_options.add_argument("--disable-ipc-flooding-protection")
        
#         # Note: undetected-chrome handles these automatically, so we don't need to set them manually
#         # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         # chrome_options.add_experimental_option('useAutomationExtension', False)
        
#         # Custom user agent (more recent version)
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
#         # Logging options (optional, can be removed for production)
#         chrome_options.add_argument("--enable-logging")
#         chrome_options.add_argument("--v=1")
        
#         # SSL certificate bypass options
#         # if ignore_ssl:
#         #     chrome_options.add_argument("--ignore-ssl-errors")
#         #     chrome_options.add_argument("--ignore-certificate-errors")
#         #     chrome_options.add_argument("--ignore-certificate-errors-spki-list")
#         #     chrome_options.add_argument("--ignore-ssl-errors-list")
#         #     chrome_options.add_argument("--accept-insecure-certs")
#         #     chrome_options.add_argument("--allow-running-insecure-content")
#         #     chrome_options.add_argument("--disable-web-security")
#         #     logger.info("🔓 SSL certificate checking disabled")
        
#         # Disable SSL verification for driver download if needed
#         # if ignore_ssl:
#         #     os.environ['WDM_SSL_VERIFY'] = '0'
#         #     logger.info("🔓 Driver download SSL verification disabled")
        
#         logger.info("🚀 Initializing undetected Chrome driver...")
        
#         # Use undetected-chrome driver with proper configuration
#         driver = uc.Chrome(
#             options=chrome_options,
#             headless=headless,  # Let uc handle headless mode properly
#             version_main=None,  # Auto-detect Chrome version
#             driver_executable_path=None,  # Let uc manage the driver
#             use_subprocess=True,  # Better process management
#             debug=False  # Set to True for debugging
#         )
        
#         # Clean up environment variables after driver initialization
#         # if ignore_ssl:
#         #     os.environ.pop('WDM_SSL_VERIFY', None)
#         #     logger.info("🔐 Driver download SSL verification re-enabled")
        
#         # Additional stealth measures (undetected-chrome handles most of this automatically)
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
#         driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
#         driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
#         # Set more generous timeouts for challenging sites
#         driver.set_page_load_timeout(timeout)
#         driver.implicitly_wait(5)  # Reduced implicit wait
        
#         logger.info(f"📡 Loading page: {url}")
        
#         # Enhanced retry logic with multiple strategies
#         MAX_RETRIES = 3
#         page_loaded = False
        
#         for attempt in range(MAX_RETRIES):
#             try:
#                 logger.info(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES}")
                
#                 # Strategy 1: Normal page load
#                 if attempt == 0:
#                     driver.get(url)
#                 # Strategy 2: Stop page load early and continue
#                 elif attempt == 1:
#                     logger.info("🛑 Trying early stop strategy...")
#                     driver.set_page_load_timeout(15)  # Shorter timeout
#                     try:
#                         driver.get(url)
#                     except TimeoutException:
#                         logger.info("⏹️ Stopping page load early...")
#                         driver.execute_script("window.stop();")
#                         time.sleep(2)
#                 # Strategy 3: JavaScript navigation
#                 else:
#                     logger.info("🔧 Trying JavaScript navigation...")
#                     driver.get("about:blank")
#                     time.sleep(1)
#                     driver.execute_script(f"window.location.href = '{url}';")
#                     time.sleep(10)
                
#                 page_loaded = True
#                 break
                
#             except TimeoutException as te:
#                 logger.warning(f"⏰ Timeout on attempt {attempt + 1}: {str(te)[:100]}")
#                 if attempt < MAX_RETRIES - 1:
#                     time.sleep(3)
#                     continue
#                 else:
#                     # Last attempt - try to stop loading and proceed
#                     try:
#                         driver.execute_script("window.stop();")
#                         logger.info("🛑 Stopped page loading, attempting to extract content...")
#                         page_loaded = True
#                         break
#                     except:
#                         pass
                        
#             except WebDriverException as e:
#                 error_msg = str(e).lower()
#                 if ("ssl" in error_msg or "handshake" in error_msg or "certificate" in error_msg):
#                     logger.warning(f"🔁 SSL/Certificate error on attempt {attempt + 1}, retrying...")
#                     time.sleep(3)
#                 elif "net::" in error_msg:
#                     logger.warning(f"🔁 Network error on attempt {attempt + 1}, retrying...")
#                     time.sleep(5)
#                 else:
#                     if attempt < MAX_RETRIES - 1:
#                         logger.warning(f"🔁 WebDriver error on attempt {attempt + 1}: {str(e)[:100]}")
#                         time.sleep(3)
#                     else:
#                         raise
        
#         if not page_loaded:
#             return f"[Error] Failed to load page after {MAX_RETRIES} attempts: {url}"
        
#         # Wait for basic page structure with multiple fallbacks
#         wait_strategies = [
#             # Strategy 1: Wait for body
#             lambda: WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "body"))),
#             # Strategy 2: Wait for any content
#             lambda: WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "p"))),
#             # Strategy 3: Wait for document ready
#             lambda: WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
#         ]
        
#         content_ready = False
#         for i, strategy in enumerate(wait_strategies):
#             try:
#                 strategy()
#                 logger.info(f"✅ Content ready (strategy {i + 1})")
#                 content_ready = True
#                 break
#             except TimeoutException:
#                 logger.warning(f"⚠️ Wait strategy {i + 1} timed out")
#                 continue
        
#         if not content_ready:
#             logger.warning("⚠️ All wait strategies failed, proceeding anyway")
        
#         # Adaptive wait based on page complexity
#         try:
#             script_count = len(driver.find_elements(By.TAG_NAME, "script"))
#             if script_count > 20:  # Heavy JavaScript site
#                 logger.info("🔄 Heavy JS site detected, waiting longer...")
#                 time.sleep(5)
#             else:
#                 time.sleep(2)
#         except:
#             time.sleep(3)
        
#         # Scroll to load lazy content (optional)
#         try:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(1)
#             driver.execute_script("window.scrollTo(0, 0);")
#         except Exception as e:
#             logger.warning(f"Scroll operation failed: {e}")
        
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
#         unwanted_tags = ["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript", "form"]
#         for tag in unwanted_tags:
#             for element in soup(tag):
#                 element.decompose()
        
#         # Remove elements with common ad/tracking classes and IDs
#         unwanted_patterns = ['ad', 'advertisement', 'tracking', 'cookie', 'popup', 'modal', 
#                            'sidebar', 'comment', 'social', 'share', 'newsletter']
        
#         for element in soup.find_all(attrs={"class": lambda x: x and any(
#             pattern in ' '.join(x).lower() for pattern in unwanted_patterns
#         )}):
#             element.decompose()
            
#         for element in soup.find_all(attrs={"id": lambda x: x and any(
#             pattern in x.lower() for pattern in unwanted_patterns
#         )}):
#             element.decompose()
        
#         # Enhanced content extraction strategies
#         content_text = ""
        
#         # Strategy 1: Look for structured content areas (prioritized order)
#         content_selectors = [
#             'main article',
#             'main',
#             'article',
#             '[role="main"]',
#             '.content',
#             '.main-content',
#             '.article-content',
#             '.post-content',
#             '.entry-content',
#             '.story-body',
#             '.article-body',
#             '#content',
#             '#main-content',
#             '.text-content'
#         ]
        
#         main_content = None
#         used_selector = None
        
#         for selector in content_selectors:
#             elements = soup.select(selector)
#             if elements:
#                 # Choose the element with most text content
#                 main_content = max(elements, key=lambda x: len(x.get_text(strip=True)))
#                 used_selector = selector
#                 logger.info(f"📝 Found main content with selector: {selector}")
#                 break
        
#         if main_content and len(main_content.get_text(strip=True)) > 100:
#             content_text = main_content.get_text(separator=' ', strip=True)
#         else:
#             # Strategy 2: Extract from paragraph-heavy containers
#             logger.info("📝 Using paragraph-based content extraction")
#             potential_containers = soup.find_all(['div', 'section'], 
#                                                attrs={'class': lambda x: x and not any(
#                                                    pattern in ' '.join(x).lower() 
#                                                    for pattern in unwanted_patterns
#                                                )})
            
#             best_container = None
#             max_paragraph_count = 0
            
#             for container in potential_containers:
#                 paragraph_count = len(container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
#                 if paragraph_count > max_paragraph_count:
#                     max_paragraph_count = paragraph_count
#                     best_container = container
            
#             if best_container and max_paragraph_count > 3:
#                 content_text = best_container.get_text(separator=' ', strip=True)
#                 logger.info(f"📝 Using container with {max_paragraph_count} paragraphs")
#             else:
#                 # Strategy 3: Fallback to common content elements
#                 logger.info("📝 Using fallback content extraction")
#                 content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote'])
#                 content_text = ' '.join([
#                     elem.get_text(strip=True) 
#                     for elem in content_elements 
#                     if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 15
#                 ])
        
#         # Clean up the text
#         content_text = ' '.join(content_text.split())  # Remove extra whitespace
#         content_text = content_text.replace('\n', ' ').replace('\r', ' ')
        
#         if len(content_text) < 100:
#             logger.warning(f"⚠️ Limited content extracted: {len(content_text)} characters")
#             # Final fallback: get all text
#             content_text = soup.get_text(separator=' ', strip=True)
#             content_text = ' '.join(content_text.split())
        
#         logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
#         # Return first 15000 characters (increased limit)
#         if len(content_text) > 15000:
#             content_text = content_text[:15000] + "..."
#             logger.info("✂️ Content truncated to 15000 characters")
        
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"

# ######GREAT WORKING LOCAL VERSION(blocked by paywalls.. or modern bots)#############
def scrape_url_local(url, headless=True, timeout=30, ignore_ssl=False):
    """
    Local version of the web scraper using undetected-chrome for better stealth
    
    Args:
        url (str): URL to scrape
        headless (bool): Run browser in headless mode (default: True)
        timeout (int): Page load timeout in seconds (default: 30)
        ignore_ssl (bool): Ignore SSL certificate errors (default: False)
    
    Returns:
        str: Extracted text content or error message
    """
    driver = None
    try:
        logger.info(f"🔍 Starting to scrape: {url}")
        
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return f"[Error] Invalid URL: {url}"
        
        # Configure undetected-chrome options
        chrome_options = uc.ChromeOptions()
        
        # Basic stealth options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Enhanced stealth options for undetected-chrome
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # Note: undetected-chrome handles these automatically, so we don't need to set them manually
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Custom user agent (more recent version)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        # Logging options (optional, can be removed for production)
        chrome_options.add_argument("--enable-logging")
        chrome_options.add_argument("--v=1")
        
        # SSL certificate bypass options
        if ignore_ssl:
            chrome_options.add_argument("--ignore-ssl-errors")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--ignore-certificate-errors-spki-list")
            chrome_options.add_argument("--ignore-ssl-errors-list")
            chrome_options.add_argument("--accept-insecure-certs")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-web-security")
            logger.info("🔓 SSL certificate checking disabled")
        
        # Disable SSL verification for driver download if needed
        if ignore_ssl:
            os.environ['WDM_SSL_VERIFY'] = '0'
            logger.info("🔓 Driver download SSL verification disabled")
        
        logger.info("🚀 Initializing undetected Chrome driver...")
        
        # Use undetected-chrome driver with proper configuration
        driver = uc.Chrome(
            options=chrome_options,
            headless=headless,  # Let uc handle headless mode properly
            version_main=None,  # Auto-detect Chrome version
            driver_executable_path=None,  # Let uc manage the driver
            use_subprocess=True,  # Better process management
            debug=False  # Set to True for debugging
        )
        
        # Clean up environment variables after driver initialization
        if ignore_ssl:
            os.environ.pop('WDM_SSL_VERIFY', None)
            logger.info("🔐 Driver download SSL verification re-enabled")
        
        # Additional stealth measures (undetected-chrome handles most of this automatically)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
        
        # Set more generous timeouts for challenging sites
        driver.set_page_load_timeout(timeout)
        driver.implicitly_wait(5)  # Reduced implicit wait
        
        logger.info(f"📡 Loading page: {url}")
        
        # Enhanced retry logic with multiple strategies
        MAX_RETRIES = 3
        page_loaded = False
        
        for attempt in range(MAX_RETRIES):
            try:
                logger.info(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES}")
                
                # Strategy 1: Normal page load
                if attempt == 0:
                    driver.get(url)
                # Strategy 2: Stop page load early and continue
                elif attempt == 1:
                    logger.info("🛑 Trying early stop strategy...")
                    driver.set_page_load_timeout(15)  # Shorter timeout
                    try:
                        driver.get(url)
                    except TimeoutException:
                        logger.info("⏹️ Stopping page load early...")
                        driver.execute_script("window.stop();")
                        time.sleep(2)
                # Strategy 3: JavaScript navigation
                else:
                    logger.info("🔧 Trying JavaScript navigation...")
                    driver.get("about:blank")
                    time.sleep(1)
                    driver.execute_script(f"window.location.href = '{url}';")
                    time.sleep(10)
                
                page_loaded = True
                break
                
            except TimeoutException as te:
                logger.warning(f"⏰ Timeout on attempt {attempt + 1}: {str(te)[:100]}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(3)
                    continue
                else:
                    # Last attempt - try to stop loading and proceed
                    try:
                        driver.execute_script("window.stop();")
                        logger.info("🛑 Stopped page loading, attempting to extract content...")
                        page_loaded = True
                        break
                    except:
                        pass
                        
            except WebDriverException as e:
                error_msg = str(e).lower()
                if ("ssl" in error_msg or "handshake" in error_msg or "certificate" in error_msg):
                    logger.warning(f"🔁 SSL/Certificate error on attempt {attempt + 1}, retrying...")
                    time.sleep(3)
                elif "net::" in error_msg:
                    logger.warning(f"🔁 Network error on attempt {attempt + 1}, retrying...")
                    time.sleep(5)
                else:
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(f"🔁 WebDriver error on attempt {attempt + 1}: {str(e)[:100]}")
                        time.sleep(3)
                    else:
                        raise
        
        if not page_loaded:
            return f"[Error] Failed to load page after {MAX_RETRIES} attempts: {url}"
        
        # Wait for basic page structure with multiple fallbacks
        wait_strategies = [
            # Strategy 1: Wait for body
            lambda: WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.TAG_NAME, "body"))),
            # Strategy 2: Wait for any content
            lambda: WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "p"))),
            # Strategy 3: Wait for document ready
            lambda: WebDriverWait(driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
        ]
        
        content_ready = False
        for i, strategy in enumerate(wait_strategies):
            try:
                strategy()
                logger.info(f"✅ Content ready (strategy {i + 1})")
                content_ready = True
                break
            except TimeoutException:
                logger.warning(f"⚠️ Wait strategy {i + 1} timed out")
                continue
        
        if not content_ready:
            logger.warning("⚠️ All wait strategies failed, proceeding anyway")
        
        # Adaptive wait based on page complexity
        try:
            script_count = len(driver.find_elements(By.TAG_NAME, "script"))
            if script_count > 20:  # Heavy JavaScript site
                logger.info("🔄 Heavy JS site detected, waiting longer...")
                time.sleep(5)
            else:
                time.sleep(2)
        except:
            time.sleep(3)
        
        # Scroll to load lazy content (optional)
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
        except Exception as e:
            logger.warning(f"Scroll operation failed: {e}")
        
        logger.info("📄 Getting page source...")
        html = driver.page_source
        
        if not html or len(html) < 100:
            return f"[Error] Page returned minimal content: {len(html)} characters"
        
        logger.info(f"✅ Page loaded successfully. HTML length: {len(html)} characters")
        
    except TimeoutException:
        logger.error(f"⏰ Timeout loading page: {url}")
        return f"[Timeout] Page failed to load within {timeout} seconds: {url}"
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
            except Exception as e:
                logger.warning(f"Warning closing driver: {e}")

    # Parse with BeautifulSoup
    try:
        logger.info("🍲 Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        unwanted_tags = ["script", "style", "nav", "header", "footer", "aside", "iframe", "noscript", "form"]
        for tag in unwanted_tags:
            for element in soup(tag):
                element.decompose()
        
        # Remove elements with common ad/tracking classes and IDs
        unwanted_patterns = ['ad', 'advertisement', 'tracking', 'cookie', 'popup', 'modal', 
                           'sidebar', 'comment', 'social', 'share', 'newsletter']
        
        for element in soup.find_all(attrs={"class": lambda x: x and any(
            pattern in ' '.join(x).lower() for pattern in unwanted_patterns
        )}):
            element.decompose()
            
        for element in soup.find_all(attrs={"id": lambda x: x and any(
            pattern in x.lower() for pattern in unwanted_patterns
        )}):
            element.decompose()
        
        # Enhanced content extraction strategies
        content_text = ""
        
        # Strategy 1: Look for structured content areas (prioritized order)
        content_selectors = [
            'main article',
            'main',
            'article',
            '[role="main"]',
            '.content',
            '.main-content',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.story-body',
            '.article-body',
            '#content',
            '#main-content',
            '.text-content'
        ]
        
        main_content = None
        used_selector = None
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Choose the element with most text content
                main_content = max(elements, key=lambda x: len(x.get_text(strip=True)))
                used_selector = selector
                logger.info(f"📝 Found main content with selector: {selector}")
                break
        
        if main_content and len(main_content.get_text(strip=True)) > 100:
            content_text = main_content.get_text(separator=' ', strip=True)
        else:
            # Strategy 2: Extract from paragraph-heavy containers
            logger.info("📝 Using paragraph-based content extraction")
            potential_containers = soup.find_all(['div', 'section'], 
                                               attrs={'class': lambda x: x and not any(
                                                   pattern in ' '.join(x).lower() 
                                                   for pattern in unwanted_patterns
                                               )})
            
            best_container = None
            max_paragraph_count = 0
            
            for container in potential_containers:
                paragraph_count = len(container.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
                if paragraph_count > max_paragraph_count:
                    max_paragraph_count = paragraph_count
                    best_container = container
            
            if best_container and max_paragraph_count > 3:
                content_text = best_container.get_text(separator=' ', strip=True)
                logger.info(f"📝 Using container with {max_paragraph_count} paragraphs")
            else:
                # Strategy 3: Fallback to common content elements
                logger.info("📝 Using fallback content extraction")
                content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote'])
                content_text = ' '.join([
                    elem.get_text(strip=True) 
                    for elem in content_elements 
                    if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 15
                ])
        
        # Clean up the text
        content_text = ' '.join(content_text.split())  # Remove extra whitespace
        content_text = content_text.replace('\n', ' ').replace('\r', ' ')
        
        if len(content_text) < 100:
            logger.warning(f"⚠️ Limited content extracted: {len(content_text)} characters")
            # Final fallback: get all text
            content_text = soup.get_text(separator=' ', strip=True)
            content_text = ' '.join(content_text.split())
        
        logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
        # Return first 15000 characters (increased limit)
        if len(content_text) > 15000:
            content_text = content_text[:15000] + "..."
            logger.info("✂️ Content truncated to 15000 characters")
        
        return content_text
        
    except Exception as e:
        logger.error(f"❌ Error parsing HTML: {e}")
        return f"[Error] Failed to parse HTML: {str(e)}"
