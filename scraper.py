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
import threading
from functools import wraps

logger = logging.getLogger(__name__)
#########RAM-LIMITED VERSION - NO TIMEOUTS##################
# Global variables for memory tracking
_initial_memory = None
_peak_memory = 0
_memory_limit_mb = 600  # Configurable memory limit
_memory_warning_mb = 480  # Warning threshold

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

def check_memory_status():
    """Check memory status and return action to take"""
    memory = get_memory_usage()
    current_mb = memory['rss_mb']
    
    if current_mb > _memory_limit_mb:
        logger.error(f"🚨 MEMORY LIMIT EXCEEDED: {current_mb:.1f}MB > {_memory_limit_mb}MB - STOPPING")
        return "STOP"
    elif current_mb > _memory_warning_mb:
        logger.warning(f"⚠️ MEMORY WARNING: {current_mb:.1f}MB (approaching {_memory_limit_mb}MB limit)")
        return "WARNING"
    else:
        return "OK"

def force_cleanup():
    """Aggressive memory cleanup"""
    logger.info("🧹 Forcing aggressive memory cleanup...")
    
    # Multiple garbage collection passes
    for i in range(3):
        collected = gc.collect()
        logger.info(f"🗑️ GC pass {i+1}: collected {collected} objects")
    
    log_memory_usage("after aggressive cleanup")

class MemoryMonitoredPageLoad:
    """Monitor page loading and stop if memory limit is reached"""
    
    def __init__(self, driver, url):
        self.driver = driver
        self.url = url
        self.should_stop = False
        self.load_completed = False
        self.error = None
        
    def memory_monitor_thread(self):
        """Background thread to monitor memory during page load"""
        while not self.load_completed and not self.should_stop:
            status = check_memory_status()
            if status == "STOP":
                logger.warning("🛑 Memory limit reached during page load - stopping")
                self.should_stop = True
                try:
                    self.driver.execute_script("window.stop();")
                except:
                    pass
                break
            time.sleep(2)  # Check every 2 seconds
    
    def load_with_memory_monitoring(self):
        """Load page with continuous memory monitoring"""
        # Start memory monitoring thread
        monitor_thread = threading.Thread(target=self.memory_monitor_thread, daemon=True)
        monitor_thread.start()
        
        try:
            # Remove all timeouts - let it run until memory limit or completion
            self.driver.set_page_load_timeout(0)  # Infinite timeout
            self.driver.implicitly_wait(0)
            
            logger.info(f"🌐 Loading page (no timeout limit): {self.url}")
            self.driver.get(self.url)
            
            # Wait for body element without timeout
            start_time = time.time()
            while not self.should_stop:
                try:
                    self.driver.find_element(By.TAG_NAME, "body")
                    break
                except:
                    if time.time() - start_time > 5:  # Just a basic sanity check
                        break
                    time.sleep(0.5)
            
            self.load_completed = True
            
            if self.should_stop:
                logger.warning("⏹️ Page load stopped due to memory limit")
                return False
            else:
                logger.info("✅ Page loaded successfully")
                return True
                
        except Exception as e:
            self.load_completed = True
            self.error = e
            logger.warning(f"⚠️ Page load exception (continuing anyway): {e}")
            return True  # Continue with whatever we have
        
        finally:
            self.load_completed = True

@memory_monitor
def create_driver(headless=True):
    """Create Chrome driver with ultra-minimal memory footprint"""
    log_memory_usage("before driver creation")
    
    chrome_options = uc.ChromeOptions()
    
    # Ultra-minimal Chrome configuration for maximum memory savings
    # essential_args = [
    #     "--no-sandbox",
    #     "--disable-dev-shm-usage",
    #     "--disable-gpu",
    #     "--disable-software-rasterizer",
    #     "--window-size=800,600",
    #     "--disable-extensions",
    #     "--disable-plugins",
    #     "--disable-images",
        
    #     # Extreme memory optimization
    #     "--memory-pressure-off",
    #     "--max_old_space_size=512",  # Very restrictive V8 heap
    #     "--disable-background-timer-throttling",
    #     "--disable-renderer-backgrounding",
    #     "--disable-backgrounding-occluded-windows",
    #     "--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess",
    #     "--disable-ipc-flooding-protection",
    #     "--disable-background-networking",
    #     "--disable-sync",
    #     "--disable-default-apps",
    #     "--no-first-run",
    #     "--disable-client-side-phishing-detection",
    #     "--disable-component-update",
    #     "--disable-domain-reliability",
    #     "--disable-background-mode",
        
    #     # Zero cache and minimal processes
    #     "--renderer-process-limit=1",
    #     "--media-cache-size=1",
    #     "--aggressive-cache-discard",
    #     "--disable-application-cache",
    #     "--disable-site-isolation-trials",
        
    #     # Remove all timeouts at browser level
    #     "--disable-hang-monitor",
    #     "--disable-prompt-on-repost",
        
    #     # Minimal user agent
    #     "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    # ]
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
        
        # Extreme memory optimization
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
        
        # Zero cache
        "--renderer-process-limit=1"
        "--media-cache-size=1",
        "--aggressive-cache-discard",
        "--disable-application-cache",
        
        # Process limits
        # "--single-process",  # Use single process (saves RAM but less stable)
        "--disable-site-isolation-trials",
        
        # Minimal user agent
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]
    
    for arg in essential_args:
        chrome_options.add_argument(arg)
    
    if headless:
        chrome_options.add_argument("--headless=new")
    
    logger.info("🚀 Creating ultra-minimal Chrome driver...")
    
    try:
        driver = uc.Chrome(
            options=chrome_options,
            headless=False,
            version_main=None,
            driver_executable_path=None,
            use_subprocess=False,
            debug=False
        )
        
        log_memory_usage("after driver creation")
        return driver
        
    except Exception as e:
        log_memory_usage("driver creation failed")
        raise

@memory_monitor  
def load_page_with_memory_limit(driver, url):
    """Load page with only memory-based stopping condition"""
    log_memory_usage("before page load")
    
    # Check memory before starting
    status = check_memory_status()
    if status == "STOP":
        return False
    
    # Use memory-monitored page loading
    loader = MemoryMonitoredPageLoad(driver, url)
    success = loader.load_with_memory_monitoring()
    
    log_memory_usage("after page load")
    return success

@memory_monitor
def extract_html_with_memory_check(driver):
    """Extract HTML with continuous memory monitoring"""
    log_memory_usage("before HTML extraction")
    
    # Check memory before extraction
    status = check_memory_status()
    if status == "STOP":
        logger.error("🚨 Cannot extract HTML - memory limit reached")
        return None
    
    try:
        html = driver.page_source
        html_size_mb = len(html) / 1024 / 1024
        
        logger.info(f"📄 HTML extracted: {html_size_mb:.2f}MB ({len(html)} chars)")
        log_memory_usage("after HTML extraction")
        
        # Check memory after extraction
        status = check_memory_status()
        if status == "STOP":
            logger.warning("🚨 Memory limit reached after HTML extraction")
            return html[:len(html)//2]  # Return half the content
        
        return html
        
    except Exception as e:
        log_memory_usage("HTML extraction error")
        logger.error(f"HTML extraction failed: {e}")
        return None

@memory_monitor
def parse_content_with_memory_monitoring(html, max_length=10000):
    """Parse HTML content with continuous memory monitoring"""
    log_memory_usage("before HTML parsing")
    
    if not html or len(html) < 50:
        return "[Error] No HTML content"
    
    # Check memory before parsing
    status = check_memory_status()
    if status == "STOP":
        return "[Error] Memory limit reached before parsing"
    
    try:
        # Use html.parser to avoid lxml memory overhead
        soup = BeautifulSoup(html, "html.parser")
        
        # Clear HTML immediately
        html = None
        log_memory_usage("after soup creation")
        
        # Check memory after soup creation
        status = check_memory_status()
        if status == "STOP":
            soup = None
            force_cleanup()
            return "[Error] Memory limit reached during parsing"
        
        # Aggressive cleanup - remove everything except essential content
        remove_tags = ["script", "style", "nav", "header", "footer", "aside", 
                      "iframe", "noscript", "form", "svg", "canvas", "video", 
                      "audio", "img", "picture", "source", "track", "embed", 
                      "object", "applet", "link", "meta"]
        
        for tag in remove_tags:
            for element in soup(tag):
                element.decompose()
        
        log_memory_usage("after tag removal")
        
        # Check memory after cleanup
        status = check_memory_status()
        if status == "STOP":
            soup = None
            force_cleanup()
            return "[Error] Memory limit reached during tag removal"
        
        # Extract only paragraph text - simplest approach
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        
        content_parts = []
        current_length = 0
        
        for i, p in enumerate(paragraphs):
            # Check memory every 50 paragraphs
            if i % 50 == 0:
                status = check_memory_status()
                if status == "STOP":
                    logger.warning("🚨 Memory limit reached during content extraction")
                    break
            
            text = p.get_text(strip=True)
            if text and len(text) > 5:
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

def scrape_url(url, headless=True, max_content_length=8000, memory_limit_mb=600):
    """
    Ultra-memory-efficient web scraper with NO TIMEOUTS - only RAM-based limits
    """
    global _initial_memory, _peak_memory, _memory_limit_mb, _memory_warning_mb
    
    # Set memory limits
    _memory_limit_mb = memory_limit_mb
    _memory_warning_mb = int(memory_limit_mb * 0.8)
    
    # Start memory tracking
    _initial_memory = get_memory_usage()['rss_mb']
    _peak_memory = _initial_memory
    
    logger.info(f"🔍 Starting scrape (NO TIMEOUT): {url}")
    logger.info(f"🎯 Memory limit: {_memory_limit_mb}MB, Warning: {_memory_warning_mb}MB")
    log_memory_usage("INITIAL")
    
    # Check if we have enough memory to start
    status = check_memory_status()
    if status == "STOP":
        return "[Error] Insufficient memory to start scraping"
    
    driver = None
    try:
        # Validate URL
        if not url or not url.startswith(('http://', 'https://')):
            return f"[Error] Invalid URL: {url}"
        
        # Create driver
        driver = create_driver(headless)
        
        status = check_memory_status()
        if status == "STOP":
            return "[Error] Memory limit exceeded after driver creation"
        
        # Load page with memory monitoring (no timeout)
        if not load_page_with_memory_limit(driver, url):
            return "[Error] Failed to load page or memory limit reached"
            
        status = check_memory_status()
        if status == "STOP":
            return "[Error] Memory limit reached after page load"
        
        # Extract HTML with memory monitoring
        html = extract_html_with_memory_check(driver)
        
        # Close driver immediately
        driver.quit()
        driver = None
        log_memory_usage("after driver quit")
        
        if not html:
            return "[Error] Could not extract HTML content"
        
        # Force cleanup before parsing
        force_cleanup()
        
        # Parse content with memory monitoring
        content = parse_content_with_memory_monitoring(html, max_content_length)
        
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

# # Convenience function with different memory limits
# def scrape_url_conservative(url, **kwargs):
#     """Scrape with conservative 400MB memory limit"""
#     return scrape_url(url, memory_limit_mb=400, **kwargs)

# def scrape_url_aggressive(url, **kwargs):
#     """Scrape with aggressive 800MB memory limit"""
#     return scrape_url(url, memory_limit_mb=800, **kwargs)



# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException
# from bs4 import BeautifulSoup
# import logging
# import time
# import os
# from webdriver_manager.chrome import ChromeDriverManager
# import undetected_chromedriver as uc
# import gc
# import psutil
# import tracemalloc
# import sys
# import threading
# from functools import wraps

# logger = logging.getLogger(__name__)
# #########SUPPOSEDLY ULTRA LIGHTWEIGHT VERSION NOW##################
# # Global variables for memory tracking
# _initial_memory = None
# _peak_memory = 0

# def get_memory_usage():
#     """Get current memory usage in MB"""
#     process = psutil.Process(os.getpid())
#     memory_info = process.memory_info()
#     return {
#         'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size (actual RAM usage)
#         'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
#         'percent': process.memory_percent(),       # Percentage of system RAM
#         'available_mb': psutil.virtual_memory().available / 1024 / 1024,
#         'total_system_mb': psutil.virtual_memory().total / 1024 / 1024
#     }

# def log_memory_usage(stage=""):
#     """Log current memory usage with optional stage description"""
#     global _peak_memory
    
#     memory = get_memory_usage()
#     current_rss = memory['rss_mb']
    
#     if current_rss > _peak_memory:
#         _peak_memory = current_rss
    
#     if _initial_memory:
#         increase = current_rss - _initial_memory
#         logger.info(f"🧠 RAM {stage}: {current_rss:.1f}MB (+{increase:.1f}MB) | "
#                    f"Peak: {_peak_memory:.1f}MB | "
#                    f"System: {memory['percent']:.1f}% | "
#                    f"Available: {memory['available_mb']:.0f}MB")
#     else:
#         logger.info(f"🧠 RAM {stage}: {current_rss:.1f}MB | "
#                    f"System: {memory['percent']:.1f}% | "
#                    f"Available: {memory['available_mb']:.0f}MB")

# def memory_monitor(func):
#     """Decorator to monitor memory usage of functions"""
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         func_name = func.__name__
#         log_memory_usage(f"BEFORE {func_name}")
        
#         try:
#             result = func(*args, **kwargs)
#             log_memory_usage(f"AFTER {func_name}")
#             return result
#         except Exception as e:
#             log_memory_usage(f"ERROR in {func_name}")
#             raise
#     return wrapper

# def check_memory_limit(limit_mb=500):
#     """Check if we're approaching memory limit"""
#     memory = get_memory_usage()
#     if memory['rss_mb'] > limit_mb:
#         logger.warning(f"⚠️ MEMORY LIMIT EXCEEDED: {memory['rss_mb']:.1f}MB > {limit_mb}MB")
#         return False
#     elif memory['rss_mb'] > limit_mb * 0.8:  # 80% warning
#         logger.warning(f"⚠️ MEMORY WARNING: {memory['rss_mb']:.1f}MB (approaching {limit_mb}MB limit)")
#     return True

# def force_cleanup():
#     """Aggressive memory cleanup"""
#     logger.info("🧹 Forcing aggressive memory cleanup...")
    
#     # Multiple garbage collection passes
#     for i in range(3):
#         collected = gc.collect()
#         logger.info(f"🗑️ GC pass {i+1}: collected {collected} objects")
    
#     log_memory_usage("after aggressive cleanup")

# @memory_monitor
# def create_driver(headless=True):
#     """Create Chrome driver with ultra-minimal memory footprint"""
#     log_memory_usage("before driver creation")
    
#     chrome_options = uc.ChromeOptions()
    
#     # Ultra-minimal Chrome configuration for maximum memory savings
#     essential_args = [
#         "--no-sandbox",
#         "--disable-dev-shm-usage",
#         "--disable-gpu",
#         "--disable-software-rasterizer",
#         "--window-size=800,600",  # Even smaller window
#         "--disable-extensions",
#         "--disable-plugins",
#         "--disable-images",
#         # "--disable-javascript",  # Disable JS if possible for your use case
#         # "--disable-web-security",
        
#         # Extreme memory optimization
#         "--memory-pressure-off",
#         "--max_old_space_size=512",  # Very restrictive V8 heap
#         "--disable-background-timer-throttling",
#         "--disable-renderer-backgrounding",
#         "--disable-backgrounding-occluded-windows",
#         "--disable-features=TranslateUI,VizDisplayCompositor,AudioServiceOutOfProcess",
#         "--disable-ipc-flooding-protection",
#         "--disable-background-networking",
#         "--disable-sync",
#         "--disable-default-apps",
#         "--no-first-run",
#         "--disable-client-side-phishing-detection",
#         "--disable-component-update",
#         "--disable-domain-reliability",
#         "--disable-background-mode",
        
#         # Zero cache
#         "--renderer-process-limit=1"
#         "--media-cache-size=1",
#         "--aggressive-cache-discard",
#         "--disable-application-cache",
        
#         # Process limits
#         # "--single-process",  # Use single process (saves RAM but less stable)
#         "--disable-site-isolation-trials",
        
#         # Minimal user agent
#         "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
#     ]
    
#     for arg in essential_args:
#         chrome_options.add_argument(arg)
    
#     if headless:
#         chrome_options.add_argument("--headless=new")  # Use new headless mode
    
#     logger.info("🚀 Creating ultra-minimal Chrome driver...")
    
#     try:
#         driver = uc.Chrome(
#             options=chrome_options,
#             headless=False,  # Let the argument handle headless
#             version_main=None,
#             driver_executable_path=None,
#             use_subprocess=False,  # Use same process to save memory
#             debug=False
#         )
        
#         log_memory_usage("after driver creation")
#         return driver
        
#     except Exception as e:
#         log_memory_usage("driver creation failed")
#         raise

# @memory_monitor  
# def load_page(driver, url, timeout=20):
#     """Load page with memory monitoring"""
#     log_memory_usage("before page load")
    
#     driver.set_page_load_timeout(timeout)
#     driver.implicitly_wait(2)
    
#     # Single attempt load - no retries to save memory
#     try:
#         driver.get(url)
#         log_memory_usage("after page load")
        
#         # Minimal wait
#         try:
#             WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#         except TimeoutException:
#             pass
            
#         return True
        
#     except TimeoutException:
#         logger.warning("⏰ Page load timeout - stopping load")
#         try:
#             driver.execute_script("window.stop();")
#         except:
#             pass
#         return True  # Continue anyway
        
#     except Exception as e:
#         log_memory_usage("page load error")
#         raise

# @memory_monitor
# def extract_html(driver):
#     """Extract HTML with memory monitoring"""
#     log_memory_usage("before HTML extraction")
    
#     html = driver.page_source
#     html_size_mb = len(html) / 1024 / 1024
    
#     logger.info(f"📄 HTML extracted: {html_size_mb:.2f}MB ({len(html)} chars)")
#     log_memory_usage("after HTML extraction")
    
#     return html

# @memory_monitor
# def parse_content(html, max_length=10000):
#     """Parse HTML content with aggressive memory management"""
#     log_memory_usage("before HTML parsing")
    
#     if not html or len(html) < 50:
#         return "[Error] No HTML content"
    
#     try:
#         # Use html.parser to avoid lxml memory overhead
#         soup = BeautifulSoup(html, "html.parser")
        
#         # Clear HTML immediately
#         html = None
#         log_memory_usage("after soup creation")
        
#         # Aggressive cleanup - remove everything except essential content
#         remove_tags = ["script", "style", "nav", "header", "footer", "aside", 
#                       "iframe", "noscript", "form", "svg", "canvas", "video", 
#                       "audio", "img", "picture", "source", "track", "embed", 
#                       "object", "applet", "link", "meta"]
        
#         for tag in remove_tags:
#             for element in soup(tag):
#                 element.decompose()
        
#         log_memory_usage("after tag removal")
        
#         # Extract only paragraph text - simplest approach
#         paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3'])
        
#         content_parts = []
#         current_length = 0
        
#         for p in paragraphs:
#             text = p.get_text(strip=True)
#             if text and len(text) > 5:  # Only meaningful text
#                 if current_length + len(text) > max_length:
#                     break
#                 content_parts.append(text)
#                 current_length += len(text)
        
#         # Clear soup
#         soup = None
#         log_memory_usage("after content extraction")
        
#         content = ' '.join(content_parts)
        
#         # Final cleanup
#         force_cleanup()
        
#         return content[:max_length] if content else "[Error] No readable content"
        
#     except Exception as e:
#         log_memory_usage("HTML parsing error")
#         return f"[Error] Parsing failed: {str(e)}"

# def scrape_url(url, headless=True, timeout=20, max_content_length=8000):
#     """
#     Ultra-memory-efficient web scraper with detailed RAM monitoring
#     """
#     global _initial_memory, _peak_memory
    
#     # Start memory tracking
#     _initial_memory = get_memory_usage()['rss_mb']
#     _peak_memory = _initial_memory
    
#     logger.info(f"🔍 Starting scrape: {url}")
#     log_memory_usage("INITIAL")
    
#     # Check if we have enough memory to start
#     if not check_memory_limit(400):  # Conservative limit
#         return "[Error] Insufficient memory to start scraping"
    
#     driver = None
#     try:
#         # Validate URL
#         if not url or not url.startswith(('http://', 'https://')):
#             return f"[Error] Invalid URL: {url}"
        
#         # Create driver
#         driver = create_driver(headless)
        
#         if not check_memory_limit(450):
#             return "[Error] Memory limit exceeded after driver creation"
        
#         # Load page
#         if not load_page(driver, url, timeout):
#             return "[Error] Failed to load page"
            
#         if not check_memory_limit(480):
#             logger.warning("⚠️ Memory critical - extracting content quickly")
        
#         # Extract HTML
#         html = extract_html(driver)
        
#         # Close driver immediately
#         driver.quit()
#         driver = None
#         log_memory_usage("after driver quit")
        
#         # Force cleanup
#         force_cleanup()
        
#         # Parse content
#         content = parse_content(html, max_content_length)
        
#         # Clear HTML
#         html = None
#         force_cleanup()
        
#         log_memory_usage("FINAL")
#         logger.info(f"✅ Scrape complete. Peak memory: {_peak_memory:.1f}MB")
        
#         return content
        
#     except Exception as e:
#         log_memory_usage("ERROR")
#         logger.error(f"❌ Scraping error: {e}")
#         return f"[Error] {str(e)}"
        
#     finally:
#         if driver:
#             try:
#                 driver.quit()
#                 log_memory_usage("driver cleanup in finally")
#             except:
#                 pass
        
#         # Final aggressive cleanup
#         force_cleanup()
