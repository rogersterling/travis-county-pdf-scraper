#!/usr/bin/env python3
"""
Enhanced Travis County Scraper that captures both PDFs and page content as Markdown
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper_with_markdown.log'),
        logging.StreamHandler()
    ]
)

class TravisCountyScraperWithMarkdown:
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
        
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        prefs = {
            "download.default_directory": str(self.downloads_dir),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        return webdriver.Chrome(options=chrome_options)
    
    def extract_page_content_to_markdown(self, driver, case_number):
        """Extract page content and convert to Markdown format"""
        logging.info(f"Extracting page content for case {case_number}")
        
        # JavaScript to extract structured content from the page
        extract_script = """
        function extractPageContent() {
            let content = {
                title: document.title,
                url: window.location.href,
                timestamp: new Date().toISOString(),
                caseInfo: {},
                events: [],
                parties: [],
                allText: []
            };
            
            // Extract case information from header/summary tables
            const infoTables = document.querySelectorAll('table');
            infoTables.forEach(table => {
                const rows = table.querySelectorAll('tr');
                rows.forEach(row => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 2) {
                        const label = cells[0].innerText.trim();
                        const value = cells[1].innerText.trim();
                        if (label && value) {
                            content.caseInfo[label.replace(':', '')] = value;
                        }
                    }
                });
            });
            
            // Extract case events from the main table
            const eventTable = document.querySelector('.roa-table, table');
            if (eventTable) {
                const headers = [];
                const headerRow = eventTable.querySelector('thead tr, tr:first-child');
                if (headerRow) {
                    headerRow.querySelectorAll('th, td').forEach(cell => {
                        headers.push(cell.innerText.trim());
                    });
                }
                
                const dataRows = eventTable.querySelectorAll('tbody tr, tr:not(:first-child)');
                dataRows.forEach(row => {
                    const event = {};
                    const cells = row.querySelectorAll('td');
                    cells.forEach((cell, index) => {
                        if (headers[index]) {
                            event[headers[index]] = cell.innerText.trim();
                        }
                    });
                    if (Object.keys(event).length > 0) {
                        content.events.push(event);
                    }
                });
            }
            
            // Extract party information
            const partyElements = document.querySelectorAll('[class*="party"], [id*="party"]');
            partyElements.forEach(elem => {
                const text = elem.innerText.trim();
                if (text && text.length > 0) {
                    content.parties.push(text);
                }
            });
            
            // Get all text content for fallback
            const allTextElements = document.querySelectorAll('p, div, span, td, li');
            allTextElements.forEach(elem => {
                const text = elem.innerText?.trim();
                if (text && text.length > 5) {
                    content.allText.push(text);
                }
            });
            
            // Remove duplicates from allText
            content.allText = [...new Set(content.allText)];
            
            return content;
        }
        
        return extractPageContent();
        """
        
        try:
            content = driver.execute_script(extract_script)
            
            # Create Markdown content
            markdown = f"# Court Case: {case_number}\n\n"
            markdown += f"**URL:** {content.get('url', 'N/A')}\n\n"
            markdown += f"**Extracted:** {content.get('timestamp', datetime.now().isoformat())}\n\n"
            markdown += "---\n\n"
            
            # Add case information
            if content.get('caseInfo'):
                markdown += "## Case Information\n\n"
                for key, value in content['caseInfo'].items():
                    markdown += f"- **{key}:** {value}\n"
                markdown += "\n"
            
            # Add case events
            if content.get('events'):
                markdown += "## Case Events\n\n"
                markdown += "| Date | Event | Description | Additional Info |\n"
                markdown += "|------|-------|-------------|----------------|\n"
                for event in content['events']:
                    # Try to extract common fields
                    date = event.get('Date', event.get('Filed Date', event.get('Event Date', '')))
                    event_type = event.get('Event', event.get('Type', event.get('Action', '')))
                    desc = event.get('Description', event.get('Text', event.get('Comment', '')))
                    info = event.get('Party', event.get('Judge', event.get('Amount', '')))
                    
                    markdown += f"| {date} | {event_type} | {desc} | {info} |\n"
                markdown += "\n"
            
            # Add parties if found
            if content.get('parties'):
                markdown += "## Parties Involved\n\n"
                for party in content['parties']:
                    markdown += f"- {party}\n"
                markdown += "\n"
            
            # Add raw text content as fallback
            if content.get('allText'):
                markdown += "## Full Page Content\n\n"
                markdown += "```\n"
                for text in content['allText'][:100]:  # Limit to first 100 unique text blocks
                    if len(text) > 10:  # Only include meaningful text
                        markdown += f"{text}\n\n"
                markdown += "```\n"
            
            # Save Markdown file
            case_dir = self.output_dir / case_number
            case_dir.mkdir(parents=True, exist_ok=True)
            
            markdown_file = case_dir / f"{case_number}_court_record.md"
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            
            logging.info(f"Saved Markdown file: {markdown_file}")
            
            # Also save raw JSON for reference
            json_file = case_dir / f"{case_number}_raw_content.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Saved raw JSON: {json_file}")
            
            return markdown_file
            
        except Exception as e:
            logging.error(f"Error extracting content for {case_number}: {e}")
            return None
    
    def find_and_download_pdfs(self, driver, case_number):
        """Try to find and click PDF download elements"""
        pdf_count = 0
        
        # Look for clickable PDF elements
        selectors = [
            "img[src*='icon']",
            "img[src*='pdf']",
            "img[src*='document']",
            "a[href*='pdf']",
            "button img",
            "td img"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    logging.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements[:5]:  # Limit to first 5 to avoid over-clicking
                        try:
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].click();", element)
                            pdf_count += 1
                            time.sleep(2)
                        except:
                            pass
            except:
                continue
        
        return pdf_count
    
    def scrape_case(self, driver, case):
        """Scrape a single case - both PDFs and content"""
        case_number = case['case_number']
        url = case['url']
        
        logging.info(f"\n{'='*60}")
        logging.info(f"Processing case: {case_number}")
        
        try:
            # Navigate to case page
            driver.get(url)
            time.sleep(5)  # Wait for page to load
            
            # Wait for main content
            wait = WebDriverWait(driver, 20)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
                logging.info("Page loaded successfully")
            except TimeoutException:
                logging.warning("Timeout waiting for page load, continuing anyway")
            
            # Extract page content to Markdown (do this for ALL pages)
            markdown_file = self.extract_page_content_to_markdown(driver, case_number)
            if markdown_file:
                logging.info(f"✅ Markdown content saved for {case_number}")
            else:
                logging.warning(f"❌ Failed to save Markdown for {case_number}")
            
            # Try to download PDFs
            pdf_count = self.find_and_download_pdfs(driver, case_number)
            if pdf_count > 0:
                logging.info(f"Clicked {pdf_count} potential PDF elements")
                time.sleep(5)  # Wait for downloads
            else:
                logging.info("No PDF elements found on this page")
            
            # Take screenshot for reference
            screenshot_dir = Path("debug_output")
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_file = screenshot_dir / f"{case_number}_screenshot.png"
            driver.save_screenshot(str(screenshot_file))
            logging.info(f"Screenshot saved: {screenshot_file}")
            
        except Exception as e:
            logging.error(f"Error processing case {case_number}: {e}")
    
    def run(self):
        """Main execution"""
        logging.info("Starting Travis County Scraper with Markdown Extraction")
        logging.info(f"Output directory: {self.output_dir}")
        
        driver = self.setup_driver()
        
        try:
            for case in self.cases:
                self.scrape_case(driver, case)
                time.sleep(2)
            
            logging.info(f"\n{'='*60}")
            logging.info("SCRAPING COMPLETE")
            logging.info(f"Check {self.output_dir} for Markdown files and any PDFs")
            
        finally:
            driver.quit()
            logging.info("Driver closed")

if __name__ == "__main__":
    scraper = TravisCountyScraperWithMarkdown()
    scraper.run()