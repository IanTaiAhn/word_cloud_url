"""
scraper.py - Selenium scraping logic and Chrome driver management
"""
import os
import time
import psutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from typing import Callable, Optional


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass


def get_chrome_options() -> Options:
    """
    Get optimized Chrome options for minimal RAM usage
    
    Returns:
        Options: Configured Chrome options
    """
    chrome_options = uc.ChromeOptions()
    
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
        "--disable-site-isolation-trials",
        
        # Minimal user agent
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    ]

    for arg in essential_args:
        chrome_options.add_argument(arg)

    return chrome_options


def create_driver() -> webdriver.Chrome:
    """
    Create a new WebDriver instance with RAM optimization
    
    Returns:
        webdriver.Chrome: Configured Chrome driver
        
    Raises:
        ScrapingError: If driver creation fails
    """
    try:

        # Disable SSL verification for ChromeDriverManager if needed
        os.environ['WDM_SSL_VERIFY'] = '0'

        # service = Service(ChromeDriverManager().install())
        driver = uc.Chrome(options=get_chrome_options())
        
        # Phase 2: Re-enable SSL verification for everything else
        os.environ.pop('WDM_SSL_VERIFY', None)
        os.environ.pop('REQUESTS_CA_BUNDLE', None)
        os.environ.pop('SSL_CERT_FILE', None)

        # Set timeouts to prevent hanging
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
    
        return driver
    except Exception as e:
        raise ScrapingError(f"Failed to create Chrome driver: {str(e)}")


def get_memory_usage() -> float:
    """
    Get current memory usage in MB
    
    Returns:
        float: Memory usage in megabytes
    """
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def extract_page_content(driver: webdriver.Chrome, url: str) -> dict:
    """
    Extract content from a webpage using Selenium
    
    Args:
        driver: Selenium WebDriver instance
        url: URL to scrape
        
    Returns:
        dict: Extracted content data
        
    Raises:
        ScrapingError: If content extraction fails
    """
    try:
        # Navigate to URL
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extract basic content
        title = driver.title
        page_source = driver.page_source
        
        # You can add more sophisticated extraction logic here
        # For example: extract specific elements, handle dynamic content, etc.
        
        # Example: Extract all text content
        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except:
            body_text = ""
        
        # Example: Extract all links
        try:
            links = [link.get_attribute('href') for link in driver.find_elements(By.TAG_NAME, "a")]
            links = [link for link in links if link]  # Filter out None values
        except:
            links = []
        
        return {
            'title': title,
            'url': url,
            'content_length': len(page_source),
            'body_text': body_text[:1000],  # First 1000 chars
            'text_length': len(body_text),
            'links_count': len(links),
            'links': links[:10],  # First 10 links
            'extracted_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise ScrapingError(f"Failed to extract content from {url}: {str(e)}")


def scrape_url_with_progress(
    url: str, 
    progress_callback: Callable[[str, int, str], None],
    job_id: str
) -> dict:
    """
    Main scraping function with progress updates
    
    Args:
        url: URL to scrape
        progress_callback: Function to call for progress updates
        job_id: Unique job identifier
        
    Returns:
        dict: Scraping results
        
    Raises:
        ScrapingError: If scraping fails
    """
    driver = None
    start_time = time.time()
    
    try:
        progress_callback('processing', 10, 'Initializing Chrome browser...')
        
        # Create driver
        driver = create_driver()
        progress_callback('processing', 20, f'Loading URL: {url}')
        
        # Extract content with progress updates
        progress_callback('processing', 40, 'Page loaded, extracting content...')
        
        content_data = extract_page_content(driver, url)
        
        progress_callback('processing', 60, 'Analyzing page structure...')
        
        # Simulate additional processing steps (customize as needed)
        time.sleep(1)  # Replace with your actual processing logic
        progress_callback('processing', 80, 'Processing extracted content...')
        
        # Add any additional processing here
        # For example: text analysis, data cleaning, etc.
        
        progress_callback('processing', 95, 'Finalizing results...')
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare final result
        result = {
            'success': True,
            'data': content_data,
            'processing_time_seconds': round(processing_time, 2),
            'memory_used_mb': round(get_memory_usage(), 2),
            'html_content': f'''
                <div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h1>✅ Scraping Complete!</h1>
                    <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h2>📊 Results Summary</h2>
                        <p><strong>Title:</strong> {content_data['title']}</p>
                        <p><strong>URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
                        <p><strong>Content Length:</strong> {content_data['content_length']:,} characters</p>
                        <p><strong>Text Length:</strong> {content_data['text_length']:,} characters</p>
                        <p><strong>Links Found:</strong> {content_data['links_count']}</p>
                        <p><strong>Processing Time:</strong> {processing_time:.2f} seconds</p>
                        <p><strong>Memory Used:</strong> {get_memory_usage():.1f} MB</p>
                    </div>
                    <div style="background: #f9f9f9; padding: 15px; border-radius: 8px;">
                        <h3>📄 Content Preview</h3>
                        <p style="font-style: italic; color: #666;">First 500 characters:</p>
                        <div style="background: white; padding: 10px; border-left: 4px solid #007acc;">
                            {content_data['body_text'][:500]}{'...' if len(content_data['body_text']) > 500 else ''}
                        </div>
                    </div>
                </div>
            '''
        }
        
        progress_callback('completed', 100, 'Scraping completed successfully!')
        return result
        
    except ScrapingError:
        raise  # Re-raise scraping errors as-is
    except Exception as e:
        raise ScrapingError(f"Unexpected error during scraping: {str(e)}")
        
    finally:
        # CRITICAL: Always quit driver to free RAM
        if driver:
            try:
                driver.quit()
                progress_callback('processing', 100, 'Browser closed, memory freed')
            except:
                pass  # Driver might already be closed


def validate_url(url: str) -> bool:
    """
    Basic URL validation
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if URL appears valid
    """
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    return url.startswith(('http://', 'https://')) and '.' in url