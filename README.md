# Travis County PDF Scraper

Automated tools for downloading PDF documents from Travis County court records system.

## Overview

This repository contains two solutions for automatically downloading PDFs from the Travis County Odyssey Portal:

1. **Python Selenium Scraper** - Automated browser scraping with multiple detection strategies
2. **Chrome Extension** - Direct browser integration for reliable PDF downloads

## Features

- 🔍 Multiple PDF detection strategies
- 📥 Automatic download handling
- 📁 Organized file structure by case number
- 🐛 Debug mode with screenshots and HTML capture
- 🔄 Batch processing for multiple cases
- 🌐 Network interception for PDF URL capture

## Installation

### Python Scraper

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the scraper:
```bash
python travis_advanced_pdf_scraper.py
```

### Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `travis_pdf_extension` folder
5. The extension icon will appear in your toolbar

## Usage

### Python Scraper

The scraper will:
1. Navigate to each case URL
2. Detect PDF download elements
3. Click elements to trigger downloads
4. Organize PDFs into folders by case number
5. Generate debug output for troubleshooting

### Chrome Extension

1. Navigate to a Travis County court case page
2. Click the extension icon
3. Use "Analyze Current Page" to detect PDFs
4. Click "Download All PDFs on Page" to download
5. Or use "Process All Cases" for batch processing

## Project Structure

```
├── travis_advanced_pdf_scraper.py    # Main Python scraper with network interception
├── travis_district_court_scraper.py  # Focused scraper for District Court cases
├── travis_pdf_extension/             # Chrome extension files
│   ├── manifest.json                 # Extension configuration
│   ├── content.js                    # Page interaction script
│   ├── background.js                 # Download management
│   ├── popup.html                    # Extension UI
│   └── popup.js                      # UI logic
├── debug_output/                     # Debug files (screenshots, HTML, logs)
└── court_records/                    # Organized downloaded PDFs
```

## Debug Output

The scraper creates debug files for troubleshooting:
- `*_screenshot.png` - Page screenshots
- `*_page.html` - Full page HTML
- `*_clickables.json` - List of clickable elements
- `*_pdf_urls.json` - Extracted PDF URLs
- `*_tables.json` - Table structure data

## Troubleshooting

### No PDFs downloading?
1. Check debug output for page structure
2. Verify you're on the correct case page
3. Try the Chrome extension as an alternative
4. Check browser console for errors

### District Court cases not working?
District Court pages may have different structure. Use the Chrome extension for better success rates.

## Legal Notice

This tool is for legitimate use only. Ensure you have proper authorization to access and download court records. Respect all terms of service and legal restrictions.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please submit pull requests or open issues for bugs and feature requests.