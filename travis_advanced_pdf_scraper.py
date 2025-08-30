#!/usr/bin/env python3
"""
Advanced Travis County PDF Scraper with Network Interception and Enhanced Detection
This scraper uses multiple strategies to download PDFs from Travis County court records.
"""

import os
import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_scraper.log'),
        logging.StreamHandler()
    ]
)

class AdvancedPDFScraper:
    def __init__(self):
        self.cases = [
            {
                'case_number': 'C-1-CR-25-209558',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=CEBF1977E83D029FB838EC851CA65EC3EB4F31A744BCCEA7046A65DC68AE790E00BF1662E8A8D403CE15AFD0300FB30E5B4D86BD975F1C1F1F581EDEAA834198EC48D90BA8A1375CCDE7FD3A78A7ACD4&isAuthenticated=False&mode=portalembed'
            },
            {
                'case_number': 'D-1-DC-25-206308',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=E4FF1E55FF9EFC69467A3AE9A879DC0D44F8C3085A018FC27C575782FACE0241825B8C17A7D0F6CF7D07973694EE795EC838623AA08C25643633BA8FD08AC7A4956C4D9A57344EE1727BAB37BB31A8B6&isAuthenticated=False&mode=portalembed'
            },
            {
                'case_number': 'D-1-DC-25-301278',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=DA38C924478946FB60DF9981B9A33C73EBDE1F5AA0649DC79B04AB31043D16D07F00FE3C12CA1B1D24DA1BAE18F47E7F6F3CE25F3D1EC1397C9ECDC891BC079EAD2008800C7CF018A2A3EC7B71913564&isAuthenticated=False&mode=portalembed'
            },
            {
                'case_number': 'C-1-CR-25-150156',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=2467947BC1F96D9A79E0C3C34B57BACE9AB8E29EC8B1EC5114B0D8CA8CCC463855CD4153A78810A6EB4816F389F88288FC0C1339E9D5C0299FE86F87112175E8311EFF1C7B4EF0A9DA27672A63C50160&isAuthenticated=False&mode=portalembed'
            }
        ]
        
        self.downloads_dir = Path.home() / "Downloads"
        self.output_dir = Path("court_records/MANCUSO_GIACOMO_ANGELO")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track download progress
        self.download_tracker = {}
        self.network_logs = []
        
    def setup_driver(self):
        """Setup Chrome driver with advanced options for PDF downloads and network logging"""
        chrome_options = Options()
        
        # Enable logging and network capture
        chrome_options.add_experimental_option('perfLoggingPrefs', {
            'enableNetwork': True,
            'enablePage': False
        })
        
        # Set up downloads
        prefs = {
            "download.default_directory": str(self.downloads_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Enable DevTools Protocol
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        
        # Additional options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": "Mozilla/5.0"}})
        
        return driver
    
    def capture_network_logs(self, driver):
        """Capture network logs to find PDF URLs"""
        logs = driver.get_log("performance")
        for log in logs:
            try:
                message = json.loads(log["message"])
                method = message.get("message", {}).get("method", "")
                
                if "Network.responseReceived" in method:
                    response = message["message"]["params"]["response"]
                    url = response.get("url", "")
                    mime_type = response.get("mimeType", "")
                    
                    if "pdf" in mime_type.lower() or url.endswith(".pdf"):
                        logging.info(f"Found PDF URL: {url}")
                        self.network_logs.append({
                            "url": url,
                            "mimeType": mime_type,
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                continue
    
    def extract_pdf_urls_from_page(self, driver):
        """Extract PDF URLs directly from page using JavaScript"""
        pdf_urls = []
        
        # Try to extract all links that might be PDFs
        js_script = """
        var pdfUrls = [];
        
        // Find all links
        var links = document.querySelectorAll('a');
        links.forEach(function(link) {
            var href = link.href;
            if (href && (href.includes('pdf') || href.includes('document') || href.includes('download'))) {
                pdfUrls.push({url: href, text: link.innerText, onclick: link.onclick ? link.onclick.toString() : ''});
            }
        });
        
        // Find all elements with onclick handlers
        var clickables = document.querySelectorAll('[onclick]');
        clickables.forEach(function(elem) {
            var onclick = elem.onclick ? elem.onclick.toString() : elem.getAttribute('onclick');
            if (onclick && (onclick.includes('pdf') || onclick.includes('document') || onclick.includes('download'))) {
                pdfUrls.push({onclick: onclick, html: elem.outerHTML});
            }
        });
        
        // Find all images that might be icons
        var images = document.querySelectorAll('img');
        images.forEach(function(img) {
            if (img.src && (img.src.includes('icon') || img.src.includes('pdf') || img.src.includes('document'))) {
                var parent = img.closest('a, button, [onclick]');
                if (parent) {
                    pdfUrls.push({
                        imgSrc: img.src,
                        parentHref: parent.href || '',
                        parentOnclick: parent.onclick ? parent.onclick.toString() : '',
                        parentHTML: parent.outerHTML
                    });
                }
            }
        });
        
        return pdfUrls;
        """
        
        try:
            urls = driver.execute_script(js_script)
            logging.info(f"Extracted {len(urls)} potential PDF URLs/elements")
            return urls
        except Exception as e:
            logging.error(f"Error extracting PDF URLs: {e}")
            return []
    
    def find_and_click_pdf_icons(self, driver, case_number):
        """Enhanced method to find and click PDF icons using multiple strategies"""
        clicked_count = 0
        
        # Strategy 1: Look for any clickable elements in table rows
        selectors = [
            "img[src*='icon']",
            "img[src*='pdf']",
            "img[src*='document']",
            "img[src*='file']",
            "img[alt*='PDF']",
            "img[alt*='Document']",
            "img[title*='PDF']",
            "img[title*='Document']",
            "button img",
            "a img",
            "[onclick] img",
            "td img",
            "td a",
            "td button",
            ".icon",
            ".pdf-icon",
            ".document-icon",
            "[class*='icon']",
            "[class*='pdf']",
            "[class*='document']",
            "svg",
            "i[class*='icon']",
            "i[class*='pdf']",
            "span[class*='icon']",
            "[role='button'] img",
            "[role='link'] img"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logging.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for idx, element in enumerate(elements):
                        try:
                            # Scroll element into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            
                            # Highlight element for debugging
                            driver.execute_script("arguments[0].style.border='3px solid red'", element)
                            
                            # Try different click methods
                            try:
                                # Method 1: Regular click
                                element.click()
                                clicked_count += 1
                                logging.info(f"Clicked element {idx+1} with regular click")
                            except:
                                try:
                                    # Method 2: JavaScript click
                                    driver.execute_script("arguments[0].click();", element)
                                    clicked_count += 1
                                    logging.info(f"Clicked element {idx+1} with JS click")
                                except:
                                    try:
                                        # Method 3: Action chains
                                        ActionChains(driver).move_to_element(element).click().perform()
                                        clicked_count += 1
                                        logging.info(f"Clicked element {idx+1} with action chains")
                                    except Exception as e:
                                        logging.warning(f"Could not click element {idx+1}: {e}")
                            
                            # Wait for potential download
                            time.sleep(2)
                            
                            # Capture network logs after click
                            self.capture_network_logs(driver)
                            
                        except Exception as e:
                            logging.warning(f"Error clicking element {idx+1}: {e}")
                            
            except Exception as e:
                continue
        
        # Strategy 2: Use JavaScript to find and trigger all clickable elements
        js_click_script = """
        var clicked = 0;
        
        // Find all images and try to click their parent elements
        var images = document.querySelectorAll('img');
        images.forEach(function(img, index) {
            if (img.src && (img.src.includes('icon') || img.src.includes('pdf') || img.src.includes('document'))) {
                var clickTarget = img.closest('a, button, td, [onclick]') || img;
                try {
                    clickTarget.click();
                    clicked++;
                    console.log('Clicked element ' + index);
                } catch(e) {
                    console.log('Failed to click element ' + index + ': ' + e);
                }
            }
        });
        
        return clicked;
        """
        
        try:
            js_clicked = driver.execute_script(js_click_script)
            clicked_count += js_clicked
            logging.info(f"JavaScript clicked {js_clicked} additional elements")
        except Exception as e:
            logging.error(f"JavaScript click script failed: {e}")
        
        return clicked_count
    
    def wait_for_downloads(self, case_number, timeout=30):
        """Wait for PDF downloads to complete"""
        start_time = time.time()
        found_pdfs = []
        
        while time.time() - start_time < timeout:
            # Check for any PDF files in downloads
            pdf_files = list(self.downloads_dir.glob(f"*{case_number}*.pdf"))
            pdf_files.extend(list(self.downloads_dir.glob("*.pdf")))
            
            # Remove duplicates and temp files
            pdf_files = [f for f in pdf_files if not f.name.endswith('.crdownload')]
            
            if pdf_files:
                for pdf in pdf_files:
                    if pdf not in found_pdfs:
                        found_pdfs.append(pdf)
                        logging.info(f"Found new PDF: {pdf.name}")
            
            # Check if downloads are still in progress
            temp_files = list(self.downloads_dir.glob("*.crdownload"))
            if not temp_files and len(found_pdfs) > 0:
                break
            
            time.sleep(1)
        
        return found_pdfs
    
    def organize_pdfs(self, case_number, pdf_files):
        """Organize downloaded PDFs into proper folders"""
        case_dir = self.output_dir / case_number / "documents"
        case_dir.mkdir(parents=True, exist_ok=True)
        
        organized_count = 0
        for pdf in pdf_files:
            if pdf.exists():
                # Create unique filename if needed
                dest_name = pdf.name
                dest_path = case_dir / dest_name
                
                # Handle duplicates
                counter = 1
                while dest_path.exists():
                    stem = pdf.stem
                    dest_name = f"{stem}_{counter}.pdf"
                    dest_path = case_dir / dest_name
                    counter += 1
                
                try:
                    shutil.move(str(pdf), str(dest_path))
                    organized_count += 1
                    logging.info(f"Moved {pdf.name} to {dest_path}")
                except Exception as e:
                    logging.error(f"Error moving {pdf.name}: {e}")
        
        return organized_count
    
    def dump_page_info(self, driver, case_number):
        """Dump page HTML and take screenshot for debugging"""
        debug_dir = Path("debug_output")
        debug_dir.mkdir(exist_ok=True)
        
        # Save HTML
        html_file = debug_dir / f"{case_number}_page.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logging.info(f"Saved HTML to {html_file}")
        
        # Take screenshot
        screenshot_file = debug_dir / f"{case_number}_screenshot.png"
        driver.save_screenshot(str(screenshot_file))
        logging.info(f"Saved screenshot to {screenshot_file}")
        
        # Extract and log all clickable elements
        clickables = driver.execute_script("""
            var elements = [];
            document.querySelectorAll('img, button, a, [onclick]').forEach(function(elem) {
                elements.push({
                    tag: elem.tagName,
                    class: elem.className,
                    id: elem.id,
                    src: elem.src || '',
                    href: elem.href || '',
                    onclick: elem.onclick ? elem.onclick.toString() : '',
                    text: elem.innerText || elem.alt || elem.title || ''
                });
            });
            return elements;
        """)
        
        # Save clickable elements info
        clickables_file = debug_dir / f"{case_number}_clickables.json"
        with open(clickables_file, 'w') as f:
            json.dump(clickables, f, indent=2)
        logging.info(f"Saved {len(clickables)} clickable elements to {clickables_file}")
    
    def scrape_case(self, driver, case):
        """Scrape PDFs for a single case"""
        case_number = case['case_number']
        url = case['url']
        
        logging.info(f"\n{'='*60}")
        logging.info(f"Processing case: {case_number}")
        logging.info(f"URL: {url}")
        
        try:
            # Navigate to case page
            driver.get(url)
            time.sleep(5)  # Initial wait for page load
            
            # Wait for specific elements that indicate page is loaded
            wait = WebDriverWait(driver, 20)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                logging.info("Page loaded, table found")
            except TimeoutException:
                logging.warning("Timeout waiting for table, continuing anyway")
            
            # Dump page info for debugging
            self.dump_page_info(driver, case_number)
            
            # Extract PDF URLs from JavaScript
            pdf_urls = self.extract_pdf_urls_from_page(driver)
            if pdf_urls:
                with open(f"debug_output/{case_number}_pdf_urls.json", 'w') as f:
                    json.dump(pdf_urls, f, indent=2)
            
            # Try to click PDF icons
            clicked = self.find_and_click_pdf_icons(driver, case_number)
            logging.info(f"Clicked {clicked} potential PDF elements")
            
            # Wait for downloads
            if clicked > 0:
                logging.info("Waiting for downloads...")
                pdf_files = self.wait_for_downloads(case_number)
                
                if pdf_files:
                    organized = self.organize_pdfs(case_number, pdf_files)
                    logging.info(f"Successfully organized {organized} PDFs for case {case_number}")
                    self.download_tracker[case_number] = organized
                else:
                    logging.warning(f"No PDFs downloaded for case {case_number}")
                    self.download_tracker[case_number] = 0
            else:
                logging.warning(f"No clickable elements found for case {case_number}")
                self.download_tracker[case_number] = 0
            
            # Save network logs for this case
            if self.network_logs:
                network_log_file = f"debug_output/{case_number}_network.json"
                with open(network_log_file, 'w') as f:
                    json.dump(self.network_logs, f, indent=2)
                logging.info(f"Saved network logs to {network_log_file}")
            
        except Exception as e:
            logging.error(f"Error processing case {case_number}: {e}")
            self.download_tracker[case_number] = 0
    
    def run(self):
        """Main execution method"""
        logging.info("Starting Advanced PDF Scraper")
        logging.info(f"Downloads directory: {self.downloads_dir}")
        logging.info(f"Output directory: {self.output_dir}")
        
        driver = self.setup_driver()
        
        try:
            for case in self.cases:
                self.scrape_case(driver, case)
                time.sleep(2)  # Brief pause between cases
            
            # Summary
            logging.info(f"\n{'='*60}")
            logging.info("SCRAPING COMPLETE")
            logging.info("Summary:")
            total_pdfs = 0
            for case_num, count in self.download_tracker.items():
                logging.info(f"  {case_num}: {count} PDFs")
                total_pdfs += count
            logging.info(f"Total PDFs downloaded: {total_pdfs}")
            
            # Check for any remaining PDFs in downloads folder
            remaining_pdfs = list(self.downloads_dir.glob("*.pdf"))
            if remaining_pdfs:
                logging.info(f"\nFound {len(remaining_pdfs)} PDFs still in Downloads folder:")
                for pdf in remaining_pdfs:
                    logging.info(f"  - {pdf.name}")
            
        finally:
            driver.quit()
            logging.info("Driver closed")

if __name__ == "__main__":
    scraper = AdvancedPDFScraper()
    scraper.run()