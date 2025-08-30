#!/usr/bin/env python3
"""
Focused scraper for District Court cases that uses JavaScript injection
to directly trigger PDF downloads.
"""

import os
import time
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class DistrictCourtScraper:
    def __init__(self):
        # Focus on District Court cases only
        self.cases = [
            {
                'case_number': 'D-1-DC-25-206308',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=E4FF1E55FF9EFC69467A3AE9A879DC0D44F8C3085A018FC27C575782FACE0241825B8C17A7D0F6CF7D07973694EE795EC838623AA08C25643633BA8FD08AC7A4956C4D9A57344EE1727BAB37BB31A8B6&isAuthenticated=False&mode=portalembed'
            },
            {
                'case_number': 'D-1-DC-25-301278',
                'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=DA38C924478946FB60DF9981B9A33C73EBDE1F5AA0649DC79B04AB31043D16D07F00FE3C12CA1B1D24DA1BAE18F47E7F6F3CE25F3D1EC1397C9ECDC891BC079EAD2008800C7CF018A2A3EC7B71913564&isAuthenticated=False&mode=portalembed'
            }
        ]
        
        self.downloads_dir = Path.home() / "Downloads"
        
    def setup_driver(self):
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
    
    def inject_pdf_finder_script(self, driver):
        """Inject a script that finds and clicks all PDF-related elements"""
        script = """
        // Find and click all potential PDF elements
        function findAndClickPDFs() {
            var clicked = [];
            
            // Strategy 1: Look for all images in table cells
            var tableCells = document.querySelectorAll('td');
            tableCells.forEach(function(td) {
                var images = td.querySelectorAll('img');
                images.forEach(function(img) {
                    // Check if image might be a document icon
                    if (!clicked.includes(img)) {
                        try {
                            // Try clicking the image
                            img.click();
                            clicked.push(img);
                            console.log('Clicked image:', img.src);
                            
                            // Also try clicking parent elements
                            var parent = img.parentElement;
                            if (parent && parent.tagName === 'A') {
                                parent.click();
                                console.log('Clicked parent link');
                            }
                        } catch(e) {
                            console.log('Error clicking image:', e);
                        }
                    }
                });
                
                // Also look for any links in the cell
                var links = td.querySelectorAll('a');
                links.forEach(function(link) {
                    if (!clicked.includes(link)) {
                        try {
                            link.click();
                            clicked.push(link);
                            console.log('Clicked link:', link.href);
                        } catch(e) {}
                    }
                });
            });
            
            // Strategy 2: Find elements by text content
            var allElements = document.querySelectorAll('*');
            allElements.forEach(function(elem) {
                var text = elem.innerText || elem.textContent || '';
                if (text.toLowerCase().includes('view') || 
                    text.toLowerCase().includes('document') ||
                    text.toLowerCase().includes('pdf')) {
                    if (!clicked.includes(elem) && elem.tagName !== 'BODY' && elem.tagName !== 'HTML') {
                        try {
                            elem.click();
                            clicked.push(elem);
                            console.log('Clicked element with text:', text);
                        } catch(e) {}
                    }
                }
            });
            
            // Strategy 3: Force click on ALL images
            var allImages = document.querySelectorAll('img');
            allImages.forEach(function(img, index) {
                if (!clicked.includes(img)) {
                    try {
                        // Create a mouse event
                        var evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        img.dispatchEvent(evt);
                        clicked.push(img);
                        console.log('Force clicked image ' + index);
                    } catch(e) {}
                }
            });
            
            return clicked.length;
        }
        
        // Run the function multiple times with delays
        var totalClicked = 0;
        totalClicked += findAndClickPDFs();
        
        setTimeout(function() {
            totalClicked += findAndClickPDFs();
            console.log('Total elements clicked: ' + totalClicked);
        }, 2000);
        
        return totalClicked;
        """
        
        return driver.execute_script(script)
    
    def extract_table_data(self, driver):
        """Extract table data to understand structure"""
        script = """
        var tables = document.querySelectorAll('table');
        var tableData = [];
        
        tables.forEach(function(table, tableIndex) {
            var rows = table.querySelectorAll('tr');
            var tableInfo = {
                tableIndex: tableIndex,
                rowCount: rows.length,
                rows: []
            };
            
            rows.forEach(function(row, rowIndex) {
                var cells = row.querySelectorAll('td, th');
                var rowInfo = {
                    rowIndex: rowIndex,
                    cells: []
                };
                
                cells.forEach(function(cell) {
                    var cellInfo = {
                        text: cell.innerText || cell.textContent || '',
                        images: [],
                        links: []
                    };
                    
                    // Check for images
                    var images = cell.querySelectorAll('img');
                    images.forEach(function(img) {
                        cellInfo.images.push({
                            src: img.src,
                            alt: img.alt,
                            title: img.title
                        });
                    });
                    
                    // Check for links
                    var links = cell.querySelectorAll('a');
                    links.forEach(function(link) {
                        cellInfo.links.push({
                            href: link.href,
                            text: link.innerText
                        });
                    });
                    
                    rowInfo.cells.push(cellInfo);
                });
                
                if (rowIndex < 20) { // Limit to first 20 rows
                    tableInfo.rows.push(rowInfo);
                }
            });
            
            tableData.push(tableInfo);
        });
        
        return tableData;
        """
        
        return driver.execute_script(script)
    
    def scrape_case(self, driver, case):
        case_number = case['case_number']
        url = case['url']
        
        logging.info(f"\nProcessing case: {case_number}")
        
        try:
            driver.get(url)
            time.sleep(7)  # Wait for page to fully load
            
            # Take screenshot
            screenshot_path = f"debug_output/{case_number}_district_screenshot.png"
            driver.save_screenshot(screenshot_path)
            logging.info(f"Screenshot saved: {screenshot_path}")
            
            # Extract table data
            table_data = self.extract_table_data(driver)
            with open(f"debug_output/{case_number}_tables.json", 'w') as f:
                json.dump(table_data, f, indent=2)
            logging.info(f"Found {len(table_data)} tables on page")
            
            # Count images before clicking
            img_count = len(driver.find_elements(By.TAG_NAME, "img"))
            logging.info(f"Found {img_count} images on page")
            
            # Inject and run PDF finder script
            clicked = self.inject_pdf_finder_script(driver)
            logging.info(f"Clicked {clicked} elements")
            
            # Wait for potential downloads
            time.sleep(10)
            
            # Check for any new PDFs in downloads
            pdf_files = list(self.downloads_dir.glob("*.pdf"))
            recent_pdfs = [f for f in pdf_files if time.time() - f.stat().st_mtime < 60]
            
            if recent_pdfs:
                logging.info(f"Found {len(recent_pdfs)} recent PDFs")
                for pdf in recent_pdfs:
                    logging.info(f"  - {pdf.name}")
            else:
                logging.info("No PDFs downloaded")
            
        except Exception as e:
            logging.error(f"Error processing case {case_number}: {e}")
    
    def run(self):
        driver = self.setup_driver()
        
        try:
            for case in self.cases:
                self.scrape_case(driver, case)
                time.sleep(3)
        finally:
            driver.quit()
            logging.info("Scraping complete")

if __name__ == "__main__":
    scraper = DistrictCourtScraper()
    scraper.run()