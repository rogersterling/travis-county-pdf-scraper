# Travis County PDF Downloader Chrome Extension

This Chrome extension automatically downloads PDFs from Travis County court records.

## Installation

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked"
4. Select the `travis_pdf_extension` folder
5. The extension will appear in your toolbar

## Usage

### Method 1: Extension Popup
1. Navigate to a Travis County court case page
2. Click the extension icon in your toolbar
3. Click "Analyze Current Page" to see what PDFs are available
4. Click "Download All PDFs on Page" to download them
5. Or click "Process All Cases" to automatically process all 4 cases

### Method 2: Python Script
Run the advanced scraper:
```bash
python travis_advanced_pdf_scraper.py
```

## Features

### Chrome Extension
- **Automatic PDF Detection**: Finds all clickable PDF elements on the page
- **Visual Feedback**: Highlights elements before clicking
- **Batch Processing**: Can process all 4 cases automatically
- **Page Analysis**: Shows detailed information about the page structure
- **Download Tracking**: Keeps track of all downloaded PDFs

### Python Script (travis_advanced_pdf_scraper.py)
- **Network Interception**: Captures PDF URLs from network traffic
- **Multiple Detection Strategies**: Uses various methods to find PDFs
- **Debug Output**: Saves HTML, screenshots, and clickable elements for analysis
- **Automatic Organization**: Moves PDFs to organized folder structure
- **Comprehensive Logging**: Detailed logs of all operations

## How It Works

### Extension Approach
1. Content script injects into Travis County pages
2. Finds all potential PDF elements using multiple strategies:
   - Images with icon/pdf/document in src/alt/title
   - Links with pdf/document/download in href/text
   - Elements with onclick handlers
   - Table cells with document-related content
3. Clicks each element to trigger download
4. Background script tracks downloads and organizes them

### Python Script Approach
1. Uses Selenium with Chrome DevTools Protocol
2. Captures network logs to find PDF URLs
3. Executes JavaScript to extract PDF links
4. Tries multiple click methods on identified elements
5. Saves debug information for troubleshooting

## Troubleshooting

If PDFs aren't downloading:
1. Check that you're on the correct case page
2. Use "Analyze Current Page" to see if PDFs are detected
3. Use "Highlight PDF Elements" to see what will be clicked
4. Check the browser console for error messages
5. Try the Python script as an alternative

## Case URLs

The extension and script are configured for these specific cases:
- C-1-CR-25-209558 (County Court #3)
- D-1-DC-25-206308 (331st District Court)
- D-1-DC-25-301278 (331st District Court) 
- C-1-CR-25-150156 (County Court #5)

## Notes for Icons

The extension requires icon files (icon16.png, icon48.png, icon128.png). You can:
1. Create simple colored squares in an image editor
2. Use any PDF or legal-themed icons
3. Or use the extension without icons (it will show a default icon)