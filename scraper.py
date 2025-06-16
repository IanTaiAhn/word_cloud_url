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
import gc
import psutil
import tracemalloc
import sys
from functools import wraps

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
    
        
#         # Custom user agent (more recent version)
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
        
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

logger = logging.getLogger(__name__)


#########SUPPOSEDLY ULTRA LIGHTWEIGHT VERSION NOW##################
# Global variables for memory tracking
_initial_memory = None
_peak_memory = 0

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size (actual RAM usage)
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent(),       # Percentage of system RAM
        'available_mb': psutil.virtual_memory().available / 1024 / 1024,
        'total_system_mb': psutil.virtual_memory().total / 1024 / 1024
    }

def log_memory_usage(stage=""):
    """Log current memory usage with optional stage description"""
    global _peak_memory
    
    memory = get_memory_usage()
    current_rss = memory['rss_mb']
    
    if current_rss > _peak_memory:
        _peak_memory = current_rss
    
    if _initial_memory:
        increase = current_rss - _initial_memory
        logger.info(f"🧠 RAM {stage}: {current_rss:.1f}MB (+{increase:.1f}MB) | "
                   f"Peak: {_peak_memory:.1f}MB | "
                   f"System: {memory['percent']:.1f}% | "
                   f"Available: {memory['available_mb']:.0f}MB")
    else:
        logger.info(f"🧠 RAM {stage}: {current_rss:.1f}MB | "
                   f"System: {memory['percent']:.1f}% | "
                   f"Available: {memory['available_mb']:.0f}MB")

def memory_monitor(func):
    """Decorator to monitor memory usage of functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        log_memory_usage(f"BEFORE {func_name}")
        
        try:
            result = func(*args, **kwargs)
            log_memory_usage(f"AFTER {func_name}")
            return result
        except Exception as e:
            log_memory_usage(f"ERROR in {func_name}")
            raise
    return wrapper

def check_memory_limit(limit_mb=500):
    """Check if we're approaching memory limit"""
    memory = get_memory_usage()
    if memory['rss_mb'] > limit_mb:
        logger.warning(f"⚠️ MEMORY LIMIT EXCEEDED: {memory['rss_mb']:.1f}MB > {limit_mb}MB")
        return False
    elif memory['rss_mb'] > limit_mb * 0.8:  # 80% warning
        logger.warning(f"⚠️ MEMORY WARNING: {memory['rss_mb']:.1f}MB (approaching {limit_mb}MB limit)")
    return True

def force_cleanup():
    """Aggressive memory cleanup"""
    logger.info("🧹 Forcing aggressive memory cleanup...")
    
    # Multiple garbage collection passes
    for i in range(3):
        collected = gc.collect()
        logger.info(f"🗑️ GC pass {i+1}: collected {collected} objects")
    
    log_memory_usage("after aggressive cleanup")

@memory_monitor
def create_driver(headless=True):
    """Create Chrome driver with ultra-minimal memory footprint"""
    log_memory_usage("before driver creation")
    
    chrome_options = uc.ChromeOptions()
    # Better alternatives:
    # essential_args = [
    #     # Core stability (keep these)
    #     "--no-sandbox",
    #     "--disable-dev-shm-usage", 
    #     "--disable-gpu",
    #     "--disable-software-rasterizer",

    #     # Window size - make responsive to content
    #     "--window-size=1024,768",  # Slightly larger for better rendering
    #     "--disable-extensions",
    #     "--disable-plugins",
    #     "--disable-images",

    #     # Memory optimization (improved)
    #     "--memory-pressure-off",
    #     "--max_old_space_size=512",  # Less restrictive
    #     "--disable-background-timer-throttling",
    #     "--disable-renderer-backgrounding",
    #     "--disable-backgrounding-occluded-windows",

    #     # Better feature disabling
    #     "--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess,MediaRouter,DialMediaRouteProvider",
    #     "--disable-background-networking",
    #     "--disable-sync",
    #     "--disable-default-apps",
    #     "--no-first-run",
    #     "--disable-client-side-phishing-detection",
    #     "--disable-component-update",
    #     "--disable-domain-reliability",
    #     "--disable-background-mode",

    #     # Cache optimization (better approach)
    #     "--disk-cache-size=0",  # 0 instead of 1
    #     "--media-cache-size=0",
    #     "--disable-application-cache",
    #     # "--disable-offline-load-stale-cache",

    #     # Process management (safer than single-process)
    #     # "--renderer-process-limit=1",
    #     "--disable-site-isolation-trials",

    #     # Anti-detection improvements for undetected-chromedriver
    #     "--disable-blink-features=AutomationControlled",
    #     # "--exclude-switches=enable-automation,enable-logging",
    #     "--disable-logging",
    #     "--log-level=3",
    #     # "--silent",

    #     # User agent (keep simple)
    #     "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    # ]
    #Old settings...
    # Ultra-minimal Chrome configuration for maximum memory savings
    essential_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--window-size=800,600",  # Even smaller window
        "--disable-extensions",
        "--disable-plugins",
        "--disable-images",
        # "--disable-javascript",  # Disable JS if possible for your use case
        # "--disable-web-security",
        
        Extreme memory optimization
        "--memory-pressure-off",
        "--max_old_space_size=512",  # Very restrictive V8 heap
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-backgrounding-occluded-windows",
        "--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess",
        "--disable-ipc-flooding-protection",
        "--disable-background-networking",
        "--disable-sync",
        "--disable-default-apps",
        "--no-first-run",
        "--disable-client-side-phishing-detection",
        "--disable-component-update",
        "--disable-domain-reliability",
        "--disable-background-mode",
        
        Zero cache
        "--renderer-process-limit=1"
        "--media-cache-size=1",
        "--aggressive-cache-discard",
        "--disable-application-cache",
        
        Process limits
        # "--single-process",  # Use single process (saves RAM but less stable)
        "--disable-site-isolation-trials",
        
        Minimal user agent
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    for arg in essential_args:
        chrome_options.add_argument(arg)
    
    if headless:
        chrome_options.add_argument("--headless=new")  # Use new headless mode
    
    logger.info("🚀 Creating ultra-minimal Chrome driver...")
    
    try:
        driver = uc.Chrome(
            options=chrome_options,
            headless=False,  # Let the argument handle headless
            version_main=None,
            driver_executable_path=None,
            use_subprocess=False,  # Use same process to save memory
            debug=False
        )
        
        log_memory_usage("after driver creation")
        return driver
        
    except Exception as e:
        log_memory_usage("driver creation failed")
        raise

@memory_monitor  
def load_page(driver, url, timeout=20):
    """Load page with memory monitoring"""
    log_memory_usage("before page load")
    
    driver.set_page_load_timeout(timeout)
    driver.implicitly_wait(2)
    
    # Single attempt load - no retries to save memory
    try:
        driver.get(url)
        log_memory_usage("after page load")
        
        # Minimal wait
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except TimeoutException:
            pass
            
        return True
        
    except TimeoutException:
        logger.warning("⏰ Page load timeout - stopping load")
        try:
            driver.execute_script("window.stop();")
        except:
            pass
        return True  # Continue anyway
        
    except Exception as e:
        log_memory_usage("page load error")
        raise

@memory_monitor
def extract_html(driver):
    """Extract HTML with memory monitoring"""
    log_memory_usage("before HTML extraction")
    
    html = driver.page_source
    html_size_mb = len(html) / 1024 / 1024
    
    logger.info(f"📄 HTML extracted: {html_size_mb:.2f}MB ({len(html)} chars)")
    log_memory_usage("after HTML extraction")
    
    return html

@memory_monitor
def parse_content(html, max_length=10000):
    """Parse HTML content with aggressive memory management"""
    log_memory_usage("before HTML parsing")
    
    if not html or len(html) < 50:
        return "[Error] No HTML content"
    
    try:
        # Use html.parser to avoid lxml memory overhead
        soup = BeautifulSoup(html, "html.parser")
        
        # Clear HTML immediately
        html = None
        log_memory_usage("after soup creation")
        
        # Aggressive cleanup - remove everything except essential content
        remove_tags = ["script", "style", "nav", "header", "footer", "aside", 
                      "iframe", "noscript", "form", "svg", "canvas", "video", 
                      "audio", "img", "picture", "source", "track", "embed", 
                      "object", "applet", "link", "meta"]
        
        for tag in remove_tags:
            for element in soup(tag):
                element.decompose()
        
        log_memory_usage("after tag removal")
        
        # Extract only paragraph text - simplest approach
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        
        content_parts = []
        current_length = 0
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 5:  # Only meaningful text
                if current_length + len(text) > max_length:
                    break
                content_parts.append(text)
                current_length += len(text)
        
        # Clear soup
        soup = None
        log_memory_usage("after content extraction")
        
        content = ' '.join(content_parts)
        
        # Final cleanup
        force_cleanup()
        
        return content[:max_length] if content else "[Error] No readable content"
        
    except Exception as e:
        log_memory_usage("HTML parsing error")
        return f"[Error] Parsing failed: {str(e)}"

def scrape_url(url, headless=True, timeout=20, max_content_length=8000):
    """
    Ultra-memory-efficient web scraper with detailed RAM monitoring
    """
    global _initial_memory, _peak_memory
    
    # Start memory tracking
    _initial_memory = get_memory_usage()['rss_mb']
    _peak_memory = _initial_memory
    
    logger.info(f"🔍 Starting scrape: {url}")
    log_memory_usage("INITIAL")
    
    # Check if we have enough memory to start
    if not check_memory_limit(400):  # Conservative limit
        return "[Error] Insufficient memory to start scraping"
    
    driver = None
    try:
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return f"[Error] Invalid URL: {url}"
        
        # Create driver
        driver = create_driver(headless)
        
        if not check_memory_limit(450):
            return "[Error] Memory limit exceeded after driver creation"
        
        # Load page
        if not load_page(driver, url, timeout):
            return "[Error] Failed to load page"
            
        if not check_memory_limit(480):
            logger.warning("⚠️ Memory critical - extracting content quickly")
        
        # Extract HTML
        html = extract_html(driver)
        
        # Close driver immediately
        driver.quit()
        driver = None
        log_memory_usage("after driver quit")
        
        # Force cleanup
        force_cleanup()
        
        # Parse content
        content = parse_content(html, max_content_length)
        
        # Clear HTML
        html = None
        force_cleanup()
        
        log_memory_usage("FINAL")
        logger.info(f"✅ Scrape complete. Peak memory: {_peak_memory:.1f}MB")
        
        return content
        
    except Exception as e:
        log_memory_usage("ERROR")
        logger.error(f"❌ Scraping error: {e}")
        return f"[Error] {str(e)}"
        
    finally:
        if driver:
            try:
                driver.quit()
                log_memory_usage("driver cleanup in finally")
            except:
                pass
        
        # Final aggressive cleanup
        force_cleanup()

# # Utility function to monitor system resources
# def log_system_resources():
#     """Log comprehensive system resource information"""
#     memory = psutil.virtual_memory()
#     cpu_percent = psutil.cpu_percent(interval=1)
    
#     logger.info(f"💻 SYSTEM RESOURCES:")
#     logger.info(f"   RAM: {memory.used/1024/1024:.0f}MB / {memory.total/1024/1024:.0f}MB "
#                f"({memory.percent:.1f}% used)")
#     logger.info(f"   Available RAM: {memory.available/1024/1024:.0f}MB")
#     logger.info(f"   CPU: {cpu_percent:.1f}%")
    
#     # Process-specific info
#     process = psutil.Process(os.getpid())
#     logger.info(f"   This process: {process.memory_info().rss/1024/1024:.1f}MB "
#                f"({process.memory_percent():.1f}% of system)")

# # Example usage with comprehensive monitoring
# if __name__ == "__main__":
#     # Setup logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(levelname)s - %(message)s'
#     )
    
#     # Log initial system state
#     log_system_resources()
    
#     # Test scraping with monitoring
#     test_url = "https://example.com"
#     result = scrape_url(test_url, headless=True, max_content_length=5000)
    
#     print(f"Result length: {len(result)} characters")
#     print(f"First 200 chars: {result[:200]}")
    
#     # Final system state
#     log_system_resources()



##########memory saving code or so it said...###############
# def scrape_url(url, headless=True, timeout=30, max_content_length=15000):
#     """
#     Memory-optimized version of the web scraper using undetected-chrome
    
#     Args:
#         url (str): URL to scrape
#         headless (bool): Run browser in headless mode (default: True)
#         timeout (int): Page load timeout in seconds (default: 30)
#         max_content_length (int): Maximum content length to return (default: 15000)
    
#     Returns:
#         str: Extracted text content or error message
#     """
#     driver = None
#     try:
#         logger.info(f"🔍 Starting to scrape: {url}")
        
#         # Validate URL
#         if not url or not url.startswith(('http://', 'https://')):
#             return f"[Error] Invalid URL: {url}"
        
#         # Configure memory-optimized Chrome options
#         chrome_options = uc.ChromeOptions()
        
#         # Basic options
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--disable-gpu")
#         chrome_options.add_argument("--window-size=1366,768")  # Smaller window
#         chrome_options.add_argument("--disable-extensions")
#         chrome_options.add_argument("--disable-plugins")
#         chrome_options.add_argument("--disable-images")
#         chrome_options.add_argument("--disable-web-security")
#         chrome_options.add_argument("--allow-running-insecure-content")
        
#         # Memory optimization flags
#         chrome_options.add_argument("--memory-pressure-off")
#         chrome_options.add_argument("--max_old_space_size=512")  # Limit V8 heap
#         chrome_options.add_argument("--disable-background-timer-throttling")
#         chrome_options.add_argument("--disable-renderer-backgrounding")
#         chrome_options.add_argument("--disable-backgrounding-occluded-windows")
#         chrome_options.add_argument("--disable-features=TranslateUI,VizDisplayCompositor")
#         chrome_options.add_argument("--disable-ipc-flooding-protection")
#         chrome_options.add_argument("--disable-background-networking")
#         chrome_options.add_argument("--disable-sync")
#         chrome_options.add_argument("--disable-default-apps")
#         chrome_options.add_argument("--no-first-run")
#         chrome_options.add_argument("--disable-client-side-phishing-detection")
#         chrome_options.add_argument("--disable-component-update")
#         chrome_options.add_argument("--disable-domain-reliability")
        
#         # Reduce cache and storage
#         chrome_options.add_argument("--disk-cache-size=0")
#         chrome_options.add_argument("--media-cache-size=0")
#         chrome_options.add_argument("--aggressive-cache-discard")
        
#         # Stealth options
#         chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#         chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        
#         logger.info("🚀 Initializing memory-optimized Chrome driver...")
        
#         # Use undetected-chrome driver
#         driver = uc.Chrome(
#             options=chrome_options,
#             headless=headless,
#             version_main=None,
#             driver_executable_path=None,
#             use_subprocess=True,
#             debug=False
#         )
        
#         # Reduced stealth measures (only essential ones)
#         driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
#         # Set timeouts
#         driver.set_page_load_timeout(timeout)
#         driver.implicitly_wait(3)  # Reduced wait time
        
#         logger.info(f"📡 Loading page: {url}")
        
#         # Simplified retry logic - max 2 attempts to save memory
#         MAX_RETRIES = 2
#         page_loaded = False
        
#         for attempt in range(MAX_RETRIES):
#             try:
#                 logger.info(f"🔄 Attempt {attempt + 1}/{MAX_RETRIES}")
                
#                 if attempt == 0:
#                     driver.get(url)
#                 else:
#                     # Early stop strategy only
#                     driver.set_page_load_timeout(15)
#                     try:
#                         driver.get(url)
#                     except TimeoutException:
#                         driver.execute_script("window.stop();")
#                         time.sleep(1)  # Reduced wait
                
#                 page_loaded = True
#                 break
                
#             except TimeoutException:
#                 if attempt < MAX_RETRIES - 1:
#                     time.sleep(2)  # Reduced retry delay
#                     continue
#                 else:
#                     try:
#                         driver.execute_script("window.stop();")
#                         page_loaded = True
#                         break
#                     except:
#                         pass
                        
#             except WebDriverException as e:
#                 if attempt < MAX_RETRIES - 1:
#                     logger.warning(f"🔁 Error on attempt {attempt + 1}: {str(e)[:50]}")
#                     time.sleep(2)
#                 else:
#                     raise
        
#         if not page_loaded:
#             return f"[Error] Failed to load page after {MAX_RETRIES} attempts: {url}"
        
#         # Simplified wait strategy
#         try:
#             WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#         except TimeoutException:
#             pass  # Continue anyway
        
#         # Minimal additional wait
#         time.sleep(1)
        
#         logger.info("📄 Getting page source...")
#         html = driver.page_source
        
#         # Early validation and memory cleanup
#         if not html or len(html) < 100:
#             if driver:
#                 driver.quit()
#             return f"[Error] Page returned minimal content"
        
#         # Close driver immediately after getting HTML to free memory
#         driver.quit()
#         driver = None
        
#         logger.info(f"✅ Page loaded. HTML length: {len(html)} characters")
        
#         # Force garbage collection
#         gc.collect()
        
#     except Exception as e:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#         logger.error(f"❌ Error during page load: {e}")
#         return f"[Error] {str(e)}"

#     # Memory-efficient HTML parsing
#     try:
#         logger.info("🍲 Parsing HTML with BeautifulSoup...")
        
#         # Use lxml parser for better memory efficiency if available, fallback to html.parser
#         try:
#             soup = BeautifulSoup(html, "lxml")
#         except:
#             soup = BeautifulSoup(html, "html.parser")
        
#         # Clear the original HTML from memory
#         html = None
#         gc.collect()
        
#         # Aggressively remove unwanted elements first
#         unwanted_tags = ["script", "style", "nav", "header", "footer", "aside", 
#                         "iframe", "noscript", "form", "svg", "canvas", "video", "audio"]
#         for tag in unwanted_tags:
#             for element in soup(tag):
#                 element.decompose()
        
#         # Remove unwanted classes/IDs (simplified patterns)
#         unwanted_patterns = ['ad', 'advertisement', 'cookie', 'popup', 'modal', 'sidebar']
        
#         for element in soup.find_all(attrs={"class": lambda x: x and any(
#             pattern in ' '.join(x).lower() for pattern in unwanted_patterns
#         )}):
#             element.decompose()
        
#         # Streamlined content extraction
#         content_text = ""
        
#         # Primary content selectors (reduced list)
#         content_selectors = [
#             'main', 'article', '[role="main"]', '.content', '.main-content', 
#             '.article-content', '#content'
#         ]
        
#         main_content = None
#         for selector in content_selectors:
#             elements = soup.select(selector)
#             if elements:
#                 main_content = max(elements, key=lambda x: len(x.get_text(strip=True)))
#                 break
        
#         if main_content and len(main_content.get_text(strip=True)) > 100:
#             content_text = main_content.get_text(separator=' ', strip=True)
#         else:
#             # Simplified fallback - just get paragraph content
#             paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
#             content_text = ' '.join([
#                 p.get_text(strip=True) 
#                 for p in paragraphs 
#                 if p.get_text(strip=True) and len(p.get_text(strip=True)) > 10
#             ])
        
#         # Clear soup from memory
#         soup = None
#         gc.collect()
        
#         # Clean and limit content length early
#         if content_text:
#             content_text = ' '.join(content_text.split())  # Clean whitespace
            
#             # Truncate early to save memory
#             if len(content_text) > max_content_length:
#                 content_text = content_text[:max_content_length] + "..."
#         else:
#             return "[Error] No readable content found"
        
#         logger.info(f"✅ Content extracted. Length: {len(content_text)} characters")
#         return content_text
        
#     except Exception as e:
#         logger.error(f"❌ Error parsing HTML: {e}")
#         return f"[Error] Failed to parse HTML: {str(e)}"
#     finally:
#         # Final cleanup
#         gc.collect()


# # Additional utility function for batch processing with memory management
# def scrape_urls_batch(urls, headless=True, timeout=30, delay_between_requests=2):
#     """
#     Memory-efficient batch scraping with cleanup between requests
#     """
#     results = []
    
#     for i, url in enumerate(urls):
#         logger.info(f"Processing {i+1}/{len(urls)}: {url}")
        
#         result = scrape_url(url, headless=headless, timeout=timeout)
#         results.append({'url': url, 'content': result})
        
#         # Force garbage collection between requests
#         gc.collect()
        
#         # Small delay to prevent overwhelming target servers
#         if delay_between_requests > 0 and i < len(urls) - 1:
#             time.sleep(delay_between_requests)
    
#     return results