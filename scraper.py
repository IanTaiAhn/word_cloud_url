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
def scrape_url(url, headless=True, timeout=30):
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
        # if ignore_ssl:
        #     chrome_options.add_argument("--ignore-ssl-errors")
        #     chrome_options.add_argument("--ignore-certificate-errors")
        #     chrome_options.add_argument("--ignore-certificate-errors-spki-list")
        #     chrome_options.add_argument("--ignore-ssl-errors-list")
        #     chrome_options.add_argument("--accept-insecure-certs")
        #     chrome_options.add_argument("--allow-running-insecure-content")
        #     chrome_options.add_argument("--disable-web-security")
        #     logger.info("🔓 SSL certificate checking disabled")
        
        # Disable SSL verification for driver download if needed
        # if ignore_ssl:
        #     os.environ['WDM_SSL_VERIFY'] = '0'
        #     logger.info("🔓 Driver download SSL verification disabled")
        
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
        # if ignore_ssl:
        #     os.environ.pop('WDM_SSL_VERIFY', None)
        #     logger.info("🔐 Driver download SSL verification re-enabled")
        
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

# def scrape_url(url):
#     """
#     Improved scraper with better error handling and debugging
#     """
#     driver = None
#     try:
#         logger.info(f"🔍 Starting to scrape: {url}")
        
#         # Validate URL
#         if not url or not url.startswith(('http://', 'https://')):
#             return f"[Error] Invalid URL: {url}"
        
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-plugins")
#         chrome_options.add_argument("--disable-images")
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
#         chrome_options.binary_location = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"

#         # Use the Service class for modern Selenium
#         service = Service(executable_path="/opt/render/project/.render/chromedriver/chromedriver")
        
#         logger.info("🚀 Initializing Chrome driver...")
#         driver = webdriver.Chrome(service=service, options=chrome_options)
        
#         logger.info(f"📡 Loading page: {url}")
#         # driver.set_page_load_timeout(30)  # Increased timeout
#         # driver.get(url)
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
#         return f"[Timeout] Page failed to load within 30 seconds: {url}"
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
#             except:
#                 pass

#     # Parse with BeautifulSoup
#     try:
#         logger.info("🍲 Parsing HTML with BeautifulSoup...")
#         soup = BeautifulSoup(html, "html.parser")
        
#         # Remove script and style elements
#         for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
#             script.decompose()
        
#         # Try multiple content extraction strategies
#         content_text = ""
        
#         # Strategy 1: Look for main content areas
#         main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=lambda x: x and any(word in x.lower() for word in ['content', 'main', 'article', 'post', 'story']))
        
#         if main_content:
#             logger.info("📝 Found main content area")
#             content_text = main_content.get_text(separator=' ', strip=True)
#         else:
#             # Strategy 2: Get text from common content elements
#             logger.info("📝 Using fallback content extraction")
#             elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div'])
#             content_text = ' '.join([elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)])
        
#         # Clean up the text
#         content_text = ' '.join(content_text.split())  # Remove extra whitespace
        
#         if len(content_text) < 50:
#             logger.warning(f"⚠️ Very little content extracted: {len(content_text)} characters")
#             # Try getting all text as last resort
#             content_text = soup.get_text(separator=' ', strip=True)
#             content_text = ' '.join(content_text.split())
        
#         logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
#         # Return first 10000 characters to avoid overwhelming the topic modeling
#         if len(content_text) > 10000:
#             content_text = content_text[:10000] + "..."
#             logger.info("✂️ Content truncated to 10000 characters")
        
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"


##############similar to the other one below this, I dont really like the wordcloud made...#######################
# def scrape_url_local(url, headless=True, timeout=45, ignore_ssl=False):
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
#         # More advanced prefs
#         # chrome_options.add_experimental_option("prefs", {
#         #     "profile.default_content_setting_values": {
#         #         "notifications": 2,
#         #         "media_stream": 2,
#         #     },
#         #     "profile.managed_default_content_settings": {
#         #         "images": 2
#         #     }
#         # })

#         chrome_options.add_argument("--disable-background-networking")
#         chrome_options.add_argument("--disable-background-timer-throttling")
#         chrome_options.add_argument("--disable-client-side-phishing-detection")
#         chrome_options.add_argument("--disable-hang-monitor")
#         chrome_options.add_argument("--disable-popup-blocking")
#         chrome_options.add_argument("--disable-prompt-on-repost")
#         chrome_options.add_argument("--safebrowsing-disable-auto-update")

#         # Additional options for problematic sites
#         chrome_options.add_argument("--disable-background-timer-throttling")
#         chrome_options.add_argument("--disable-backgrounding-occluded-windows")
#         chrome_options.add_argument("--disable-renderer-backgrounding")
#         chrome_options.add_argument("--disable-features=TranslateUI")
#         chrome_options.add_argument("--disable-default-apps")
#         chrome_options.add_argument("--disable-sync")
#         chrome_options.add_argument("--no-first-run")
#         chrome_options.add_argument("--no-default-browser-check")
        
#         # Performance optimizations
#         chrome_options.add_argument("--max_old_space_size=4096")
#         chrome_options.add_argument("--memory-pressure-off")
        
#         # Custom user agent (more recent version)
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
#         # Logging options (optional, can be removed for production)
#         chrome_options.add_argument("--enable-logging")
#         chrome_options.add_argument("--v=1")
        
#         # SSL certificate bypass options
#         if ignore_ssl:
#             chrome_options.add_argument("--ignore-ssl-errors")
#             chrome_options.add_argument("--ignore-certificate-errors")
#             chrome_options.add_argument("--ignore-certificate-errors-spki-list")
#             chrome_options.add_argument("--ignore-ssl-errors-list")
#             chrome_options.add_argument("--accept-insecure-certs")
#             chrome_options.add_argument("--allow-running-insecure-content")
#             chrome_options.add_argument("--disable-web-security")
#             logger.info("🔓 SSL certificate checking disabled")
        
#         # Disable SSL verification for driver download if needed
#         if ignore_ssl:
#             os.environ['WDM_SSL_VERIFY'] = '0'
#             logger.info("🔓 Driver download SSL verification disabled")
        
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
#         if ignore_ssl:
#             os.environ.pop('WDM_SSL_VERIFY', None)
#             logger.info("🔐 Driver download SSL verification re-enabled")
        
#         # Enhanced stealth measures for heavily protected sites
#         stealth_scripts = [
#             "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
#             "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
#             "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
#             "Object.defineProperty(navigator, 'platform', {get: () => 'Win32'})",
#             "Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 4})",
#             "Object.defineProperty(navigator, 'deviceMemory', {get: () => 8})",
#             "Object.defineProperty(screen, 'width', {get: () => 1920})",
#             "Object.defineProperty(screen, 'height', {get: () => 1080})",
#             "window.chrome = { runtime: {} }",
#             "Object.defineProperty(navigator, 'permissions', {get: () => undefined})",
#             "delete navigator.__proto__.webdriver"
#         ]
        
#         for script in stealth_scripts:
#             try:
#                 driver.execute_script(script)
#             except Exception as e:
#                 logger.debug(f"Stealth script failed: {e}")
#                 continue
        
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
        
#         # Adaptive wait based on page complexity and JavaScript rendering
#         try:
#             script_count = len(driver.find_elements(By.TAG_NAME, "script"))
#             if script_count > 20:  # Heavy JavaScript site
#                 logger.info("🔄 Heavy JS site detected, waiting for dynamic content...")
                
#                 # Wait for common JavaScript frameworks to load
#                 js_wait_scripts = [
#                     "return typeof jQuery !== 'undefined'",
#                     "return typeof React !== 'undefined'",
#                     "return typeof Vue !== 'undefined'",
#                     "return typeof angular !== 'undefined'",
#                     "return document.readyState === 'complete'",
#                     "return window.performance.timing.loadEventEnd > 0"
#                 ]
                
#                 for i, script in enumerate(js_wait_scripts):
#                     try:
#                         WebDriverWait(driver, 5).until(lambda d: d.execute_script(script))
#                         logger.info(f"✅ JS framework check {i+1} passed")
#                         break
#                     except TimeoutException:
#                         continue
                
#                 # Additional wait for dynamic content
#                 time.sleep(8)
                
#                 # Try to trigger any lazy loading
#                 try:
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
#                     time.sleep(2)
#                     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#                     time.sleep(2)
#                     driver.execute_script("window.scrollTo(0, 0);")
#                     time.sleep(1)
#                 except Exception as e:
#                     logger.debug(f"Scroll trigger failed: {e}")
                
#             else:
#                 time.sleep(3)
#         except Exception as e:
#             logger.debug(f"Adaptive wait failed: {e}")
#             time.sleep(5)
        
#         # Check if page content has loaded by looking for indicators
#         content_indicators = [
#             "return document.body.innerText.length > 100",
#             "return document.querySelectorAll('p').length > 3",
#             "return document.querySelectorAll('article').length > 0",
#             "return document.querySelector('main') !== null"
#         ]
        
#         content_loaded = False
#         for indicator in content_indicators:
#             try:
#                 if driver.execute_script(indicator):
#                     content_loaded = True
#                     logger.info("✅ Content presence confirmed")
#                     break
#             except Exception:
#                 continue
        
#         if not content_loaded:
#             logger.warning("⚠️ No content indicators found, page may be blocked or still loading")
#             # Try one more aggressive wait
#             time.sleep(5)
        
#         # Scroll to load lazy content (optional)
#         try:
#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(1)
#             driver.execute_script("window.scrollTo(0, 0);")
#         except Exception as e:
#             logger.warning(f"Scroll operation failed: {e}")
        
#         logger.info("📄 Getting page source...")
#         html = driver.page_source
        
#         # Debug: Check what we actually got
#         if html:
#             logger.info(f"✅ Page source length: {len(html)} characters")
            
#             # Quick check for common blocking patterns
#             html_lower = html.lower()
#             blocking_patterns = [
#                 'access denied',
#                 'blocked',
#                 'captcha',
#                 'unusual traffic',
#                 'please enable javascript',
#                 'bot detection',
#                 'cloudflare',
#                 'please verify you are human'
#             ]
            
#             blocking_found = [pattern for pattern in blocking_patterns if pattern in html_lower]
#             if blocking_found:
#                 logger.warning(f"🚫 Potential blocking detected: {blocking_found}")
            
#             # Check for minimal content (could indicate blocking)
#             visible_text = BeautifulSoup(html, "html.parser").get_text(strip=True)
#             if len(visible_text) < 200:
#                 logger.warning(f"⚠️ Very little visible text: {len(visible_text)} characters")
                
#                 # Try to get more information about the page state
#                 try:
#                     page_title = driver.title
#                     current_url = driver.current_url
#                     logger.info(f"Page title: {page_title}")
#                     logger.info(f"Current URL: {current_url}")
                    
#                     # Check if we were redirected
#                     if current_url != url:
#                         logger.warning(f"🔄 Redirected from {url} to {current_url}")
                        
#                 except Exception as e:
#                     logger.debug(f"Could not get page info: {e}")
        
#         if not html or len(html) < 100:
#             return f"[Error] Page returned minimal content: {len(html) if html else 0} characters"
        
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
        
#         # Enhanced content extraction strategies for protected sites
#         content_text = ""
        
#         # Check if we got blocked or paywalled
#         page_text = soup.get_text().lower()
#         blocked_indicators = [
#             'please enable javascript',
#             'subscription required',
#             'paywall',
#             'sign in to continue',
#             'subscribe to continue',
#             'login required',
#             'access denied',
#             'blocked',
#             'bot detection',
#             'unusual traffic'
#         ]
        
#         is_blocked = any(indicator in page_text for indicator in blocked_indicators)
#         if is_blocked:
#             logger.warning("🚫 Site appears to be blocking/paywalling content")
        
#         # Strategy 1: Look for JSON-LD structured data (common in news sites)
#         json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
#         json_content = ""
        
#         for script in json_ld_scripts:
#             try:
#                 import json
#                 data = json.loads(script.string)
                
#                 # Extract article content from JSON-LD
#                 def extract_from_jsonld(obj):
#                     content = ""
#                     if isinstance(obj, dict):
#                         # Common JSON-LD article properties
#                         for key in ['articleBody', 'text', 'description', 'headline', 'name']:
#                             if key in obj and isinstance(obj[key], str):
#                                 content += obj[key] + " "
                        
#                         # Recursive search in nested objects
#                         for value in obj.values():
#                             if isinstance(value, (dict, list)):
#                                 content += extract_from_jsonld(value)
#                     elif isinstance(obj, list):
#                         for item in obj:
#                             content += extract_from_jsonld(item)
#                     return content
                
#                 json_content += extract_from_jsonld(data)
                
#             except (json.JSONDecodeError, Exception) as e:
#                 logger.debug(f"Failed to parse JSON-LD: {e}")
#                 continue
        
#         if json_content.strip():
#             logger.info("📄 Found content in JSON-LD structured data")
#             content_text = json_content.strip()
        
#         # Strategy 2: Look for meta tags with article content
#         if not content_text or len(content_text) < 200:
#             meta_content = ""
#             meta_selectors = [
#                 'meta[property="og:description"]',
#                 'meta[name="description"]',
#                 'meta[property="article:summary"]',
#                 'meta[name="twitter:description"]'
#             ]
            
#             for selector in meta_selectors:
#                 meta_tag = soup.select_one(selector)
#                 if meta_tag and meta_tag.get('content'):
#                     meta_content += meta_tag.get('content') + " "
            
#             if meta_content.strip():
#                 logger.info("📄 Found content in meta tags")
#                 content_text = meta_content.strip()
        
#         # Strategy 3: Enhanced content area detection for news sites
#         if not content_text or len(content_text) < 200:
#             # News-specific selectors (including NYTimes patterns)
#             news_selectors = [
#                 'section[name="articleBody"]',
#                 '.StoryBodyCompanionColumn',
#                 '.ArticleBody-articleBody',
#                 '[data-module="ArticleBody"]',
#                 '.story-body',
#                 '.article-body',
#                 '.entry-content',
#                 '.post-content',
#                 '.content-body',
#                 'main article',
#                 'main section',
#                 'article section',
#                 '[role="main"] article',
#                 '.paywall-article',
#                 '.story-content'
#             ]
            
#             main_content = None
#             used_selector = None
            
#             for selector in news_selectors:
#                 elements = soup.select(selector)
#                 if elements:
#                     # Choose the element with most paragraph content
#                     best_element = max(elements, key=lambda x: len(x.find_all('p')))
#                     if len(best_element.find_all('p')) > 2:  # Must have multiple paragraphs
#                         main_content = best_element
#                         used_selector = selector
#                         logger.info(f"📝 Found news content with selector: {selector}")
#                         break
            
#             if main_content:
#                 content_text = main_content.get_text(separator=' ', strip=True)
        
#         # Strategy 4: Paragraph aggregation with intelligent filtering
#         if not content_text or len(content_text) < 200:
#             logger.info("📝 Using intelligent paragraph aggregation")
            
#             # Find all paragraphs
#             all_paragraphs = soup.find_all('p')
            
#             # Filter paragraphs by quality indicators
#             quality_paragraphs = []
#             for p in all_paragraphs:
#                 p_text = p.get_text(strip=True)
                
#                 # Skip short paragraphs
#                 if len(p_text) < 30:
#                     continue
                
#                 # Skip paragraphs with unwanted patterns
#                 unwanted_patterns = [
#                     'cookie', 'subscribe', 'sign up', 'newsletter', 'advertisement',
#                     'follow us', 'share this', 'related:', 'see also:', 'read more:',
#                     'terms of service', 'privacy policy', 'copyright', '© 20'
#                 ]
                
#                 if any(pattern in p_text.lower() for pattern in unwanted_patterns):
#                     continue
                
#                 # Look for quality indicators
#                 quality_indicators = [
#                     len(p_text) > 50,  # Substantial length
#                     '.' in p_text,     # Contains sentences
#                     not p_text.isupper(),  # Not all caps
#                     not p_text.startswith('http'),  # Not a URL
#                 ]
                
#                 if sum(quality_indicators) >= 3:
#                     quality_paragraphs.append(p_text)
            
#             if quality_paragraphs:
#                 content_text = ' '.join(quality_paragraphs)
#                 logger.info(f"📝 Aggregated {len(quality_paragraphs)} quality paragraphs")
        
#         # Strategy 5: Fallback to main content containers
#         if not content_text or len(content_text) < 200:
#             logger.info("📝 Using fallback content container detection")
            
#             # Look for containers with substantial paragraph content
#             containers = soup.find_all(['div', 'section', 'article'], 
#                                      attrs={'class': lambda x: x and not any(
#                                          pattern in ' '.join(x).lower() 
#                                          for pattern in ['sidebar', 'footer', 'header', 'nav', 'ad', 'comment']
#                                      )})
            
#             best_container = None
#             max_content_score = 0
            
#             for container in containers:
#                 paragraphs = container.find_all('p')
#                 total_text = sum(len(p.get_text(strip=True)) for p in paragraphs)
#                 paragraph_count = len([p for p in paragraphs if len(p.get_text(strip=True)) > 30])
                
#                 # Content score based on text length and paragraph count
#                 content_score = total_text + (paragraph_count * 100)
                
#                 if content_score > max_content_score:
#                     max_content_score = content_score
#                     best_container = container
            
#             if best_container and max_content_score > 500:
#                 content_text = best_container.get_text(separator=' ', strip=True)
#                 logger.info(f"📝 Using best container (score: {max_content_score})")
        
#         # Final fallback: Extract all meaningful text
#         if not content_text or len(content_text) < 100:
#             logger.info("📝 Using final fallback extraction")
#             content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'span'])
#             content_text = ' '.join([
#                 elem.get_text(strip=True) 
#                 for elem in content_elements 
#                 if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 20
#             ])
        
#         # Clean up the text
#         content_text = ' '.join(content_text.split())  # Remove extra whitespace
#         content_text = content_text.replace('\n', ' ').replace('\r', ' ')
        
#         # Quality check with better error messages
#         if len(content_text) < 100:
#             logger.error(f"⚠️ Very limited content extracted: {len(content_text)} characters")
            
#             # Provide diagnostic information
#             diagnostic_info = []
            
#             if is_blocked:
#                 diagnostic_info.append("Site appears to be blocking access")
            
#             # Check page source characteristics
#             if html:
#                 if len(html) < 1000:
#                     diagnostic_info.append("Very small page source")
#                 if 'javascript' in html.lower() and html.lower().count('<script') > 10:
#                     diagnostic_info.append("Heavy JavaScript rendering detected")
#                 if any(pattern in html.lower() for pattern in ['cloudflare', 'captcha', 'verify']):
#                     diagnostic_info.append("Bot protection detected")
            
#             # Check soup characteristics
#             if soup:
#                 paragraph_count = len(soup.find_all('p'))
#                 div_count = len(soup.find_all('div'))
#                 script_count = len(soup.find_all('script'))
                
#                 diagnostic_info.append(f"Elements found: {paragraph_count} paragraphs, {div_count} divs, {script_count} scripts")
            
#             error_msg = f"[Error] Minimal content extracted: {len(content_text)} characters."
#             if diagnostic_info:
#                 error_msg += f" Diagnostics: {'; '.join(diagnostic_info)}"
            
#             return error_msg
        
#         logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
#         # Return first 20000 characters (increased for news articles)
#         if len(content_text) > 20000:
#             content_text = content_text[:20000] + "..."
#             logger.info("✂️ Content truncated to 20000 characters")
        
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"


# #############Works still but I don't like the wordcloud output#################
# def scrape_url_local(url, headless=True, timeout=45, ignore_ssl=False):
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
        
#         # Additional options for problematic sites
#         chrome_options.add_argument("--disable-background-timer-throttling")
#         chrome_options.add_argument("--disable-backgrounding-occluded-windows")
#         chrome_options.add_argument("--disable-renderer-backgrounding")
#         chrome_options.add_argument("--disable-features=TranslateUI")
#         chrome_options.add_argument("--disable-default-apps")
#         chrome_options.add_argument("--disable-sync")
#         chrome_options.add_argument("--no-first-run")
#         chrome_options.add_argument("--no-default-browser-check")
        
#         # Performance optimizations
#         chrome_options.add_argument("--max_old_space_size=4096")
#         chrome_options.add_argument("--memory-pressure-off")
        
#         # Custom user agent (more recent version)
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
#         # Logging options (optional, can be removed for production)
#         chrome_options.add_argument("--enable-logging")
#         chrome_options.add_argument("--v=1")
        
#         # SSL certificate bypass options
#         if ignore_ssl:
#             chrome_options.add_argument("--ignore-ssl-errors")
#             chrome_options.add_argument("--ignore-certificate-errors")
#             chrome_options.add_argument("--ignore-certificate-errors-spki-list")
#             chrome_options.add_argument("--ignore-ssl-errors-list")
#             chrome_options.add_argument("--accept-insecure-certs")
#             chrome_options.add_argument("--allow-running-insecure-content")
#             chrome_options.add_argument("--disable-web-security")
#             logger.info("🔓 SSL certificate checking disabled")
        
#         # Disable SSL verification for driver download if needed
#         if ignore_ssl:
#             os.environ['WDM_SSL_VERIFY'] = '0'
#             logger.info("🔓 Driver download SSL verification disabled")
        
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
#         if ignore_ssl:
#             os.environ.pop('WDM_SSL_VERIFY', None)
#             logger.info("🔐 Driver download SSL verification re-enabled")
        
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
        
#         # Enhanced content extraction strategies for protected sites
#         content_text = ""
        
#         # Check if we got blocked or paywalled
#         page_text = soup.get_text().lower()
#         blocked_indicators = [
#             'please enable javascript',
#             'subscription required',
#             'paywall',
#             'sign in to continue',
#             'subscribe to continue',
#             'login required',
#             'access denied',
#             'blocked',
#             'bot detection',
#             'unusual traffic'
#         ]
        
#         is_blocked = any(indicator in page_text for indicator in blocked_indicators)
#         if is_blocked:
#             logger.warning("🚫 Site appears to be blocking/paywalling content")
        
#         # Strategy 1: Look for JSON-LD structured data (common in news sites)
#         json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
#         json_content = ""
        
#         for script in json_ld_scripts:
#             try:
#                 import json
#                 data = json.loads(script.string)
                
#                 # Extract article content from JSON-LD
#                 def extract_from_jsonld(obj):
#                     content = ""
#                     if isinstance(obj, dict):
#                         # Common JSON-LD article properties
#                         for key in ['articleBody', 'text', 'description', 'headline', 'name']:
#                             if key in obj and isinstance(obj[key], str):
#                                 content += obj[key] + " "
                        
#                         # Recursive search in nested objects
#                         for value in obj.values():
#                             if isinstance(value, (dict, list)):
#                                 content += extract_from_jsonld(value)
#                     elif isinstance(obj, list):
#                         for item in obj:
#                             content += extract_from_jsonld(item)
#                     return content
                
#                 json_content += extract_from_jsonld(data)
                
#             except (json.JSONDecodeError, Exception) as e:
#                 logger.debug(f"Failed to parse JSON-LD: {e}")
#                 continue
        
#         if json_content.strip():
#             logger.info("📄 Found content in JSON-LD structured data")
#             content_text = json_content.strip()
        
#         # Strategy 2: Look for meta tags with article content
#         if not content_text or len(content_text) < 200:
#             meta_content = ""
#             meta_selectors = [
#                 'meta[property="og:description"]',
#                 'meta[name="description"]',
#                 'meta[property="article:summary"]',
#                 'meta[name="twitter:description"]'
#             ]
            
#             for selector in meta_selectors:
#                 meta_tag = soup.select_one(selector)
#                 if meta_tag and meta_tag.get('content'):
#                     meta_content += meta_tag.get('content') + " "
            
#             if meta_content.strip():
#                 logger.info("📄 Found content in meta tags")
#                 content_text = meta_content.strip()
        
#         # Strategy 3: Enhanced content area detection for news sites
#         if not content_text or len(content_text) < 200:
#             # News-specific selectors (including NYTimes patterns)
#             news_selectors = [
#                 'section[name="articleBody"]',
#                 '.StoryBodyCompanionColumn',
#                 '.ArticleBody-articleBody',
#                 '[data-module="ArticleBody"]',
#                 '.story-body',
#                 '.article-body',
#                 '.entry-content',
#                 '.post-content',
#                 '.content-body',
#                 'main article',
#                 'main section',
#                 'article section',
#                 '[role="main"] article',
#                 '.paywall-article',
#                 '.story-content'
#             ]
            
#             main_content = None
#             used_selector = None
            
#             for selector in news_selectors:
#                 elements = soup.select(selector)
#                 if elements:
#                     # Choose the element with most paragraph content
#                     best_element = max(elements, key=lambda x: len(x.find_all('p')))
#                     if len(best_element.find_all('p')) > 2:  # Must have multiple paragraphs
#                         main_content = best_element
#                         used_selector = selector
#                         logger.info(f"📝 Found news content with selector: {selector}")
#                         break
            
#             if main_content:
#                 content_text = main_content.get_text(separator=' ', strip=True)
        
#         # Strategy 4: Paragraph aggregation with intelligent filtering
#         if not content_text or len(content_text) < 200:
#             logger.info("📝 Using intelligent paragraph aggregation")
            
#             # Find all paragraphs
#             all_paragraphs = soup.find_all('p')
            
#             # Filter paragraphs by quality indicators
#             quality_paragraphs = []
#             for p in all_paragraphs:
#                 p_text = p.get_text(strip=True)
                
#                 # Skip short paragraphs
#                 if len(p_text) < 30:
#                     continue
                
#                 # Skip paragraphs with unwanted patterns
#                 unwanted_patterns = [
#                     'cookie', 'subscribe', 'sign up', 'newsletter', 'advertisement',
#                     'follow us', 'share this', 'related:', 'see also:', 'read more:',
#                     'terms of service', 'privacy policy', 'copyright', '© 20'
#                 ]
                
#                 if any(pattern in p_text.lower() for pattern in unwanted_patterns):
#                     continue
                
#                 # Look for quality indicators
#                 quality_indicators = [
#                     len(p_text) > 50,  # Substantial length
#                     '.' in p_text,     # Contains sentences
#                     not p_text.isupper(),  # Not all caps
#                     not p_text.startswith('http'),  # Not a URL
#                 ]
                
#                 if sum(quality_indicators) >= 3:
#                     quality_paragraphs.append(p_text)
            
#             if quality_paragraphs:
#                 content_text = ' '.join(quality_paragraphs)
#                 logger.info(f"📝 Aggregated {len(quality_paragraphs)} quality paragraphs")
        
#         # Strategy 5: Fallback to main content containers
#         if not content_text or len(content_text) < 200:
#             logger.info("📝 Using fallback content container detection")
            
#             # Look for containers with substantial paragraph content
#             containers = soup.find_all(['div', 'section', 'article'], 
#                                      attrs={'class': lambda x: x and not any(
#                                          pattern in ' '.join(x).lower() 
#                                          for pattern in ['sidebar', 'footer', 'header', 'nav', 'ad', 'comment']
#                                      )})
            
#             best_container = None
#             max_content_score = 0
            
#             for container in containers:
#                 paragraphs = container.find_all('p')
#                 total_text = sum(len(p.get_text(strip=True)) for p in paragraphs)
#                 paragraph_count = len([p for p in paragraphs if len(p.get_text(strip=True)) > 30])
                
#                 # Content score based on text length and paragraph count
#                 content_score = total_text + (paragraph_count * 100)
                
#                 if content_score > max_content_score:
#                     max_content_score = content_score
#                     best_container = container
            
#             if best_container and max_content_score > 500:
#                 content_text = best_container.get_text(separator=' ', strip=True)
#                 logger.info(f"📝 Using best container (score: {max_content_score})")
        
#         # Final fallback: Extract all meaningful text
#         if not content_text or len(content_text) < 100:
#             logger.info("📝 Using final fallback extraction")
#             content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'span'])
#             content_text = ' '.join([
#                 elem.get_text(strip=True) 
#                 for elem in content_elements 
#                 if elem.get_text(strip=True) and len(elem.get_text(strip=True)) > 20
#             ])
        
#         # Clean up the text
#         content_text = ' '.join(content_text.split())  # Remove extra whitespace
#         content_text = content_text.replace('\n', ' ').replace('\r', ' ')
        
#         # Quality check
#         if len(content_text) < 100:
#             logger.error(f"⚠️ Very limited content extracted: {len(content_text)} characters")
#             if is_blocked:
#                 return f"[Error] Site appears to be blocking access. Content length: {len(content_text)} characters"
#             else:
#                 return f"[Error] Minimal content extracted: {len(content_text)} characters. Page may have heavy client-side rendering."
        
#         logger.info(f"✅ Content extracted successfully. Length: {len(content_text)} characters")
        
#         # Return first 20000 characters (increased for news articles)
#         if len(content_text) > 20000:
#             content_text = content_text[:20000] + "..."
#             logger.info("✂️ Content truncated to 20000 characters")
        
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"



# ######GREAT WORKING LOCAL VERSION(blocked by paywalls.. or modern bots)#############
# def scrape_url_local(url, headless=True, timeout=30, ignore_ssl=False):
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
#         if ignore_ssl:
#             chrome_options.add_argument("--ignore-ssl-errors")
#             chrome_options.add_argument("--ignore-certificate-errors")
#             chrome_options.add_argument("--ignore-certificate-errors-spki-list")
#             chrome_options.add_argument("--ignore-ssl-errors-list")
#             chrome_options.add_argument("--accept-insecure-certs")
#             chrome_options.add_argument("--allow-running-insecure-content")
#             chrome_options.add_argument("--disable-web-security")
#             logger.info("🔓 SSL certificate checking disabled")
        
#         # Disable SSL verification for driver download if needed
#         if ignore_ssl:
#             os.environ['WDM_SSL_VERIFY'] = '0'
#             logger.info("🔓 Driver download SSL verification disabled")
        
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
#         if ignore_ssl:
#             os.environ.pop('WDM_SSL_VERIFY', None)
#             logger.info("🔐 Driver download SSL verification re-enabled")
        
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
