# Claude Code Usage Guide - Travis County Court Records Scraper

## Overview

This project provides automated extraction of court records from Travis County's Odyssey Portal. The main script (`travis_scraper_with_markdown.py`) captures both PDFs and text content, converting court pages into structured Markdown files.

## Primary Use Case

Extracting court case information for:
- **Defendant**: MANCUSO, GIACOMO ANGELO
- **Cases**: 4 cases (2 County Court, 2 District Court)
- **Output**: Markdown files with structured text + PDFs when available

## Key Features

### What It Does
✅ Extracts full page text content as Markdown (works for ALL cases)  
✅ Downloads PDFs when available (mainly County Court cases)  
✅ Creates organized folder structure by case number  
✅ Captures screenshots for verification  
✅ Saves both formatted Markdown and raw JSON  

### What We Learned
- **County Court cases** (C-1-CR-*): Usually have downloadable PDFs
- **District Court cases** (D-1-DC-*): Often NO PDFs, but text content is captured successfully
- The Markdown extraction ensures you get case information even when PDFs aren't available

## Quick Commands

### Run the Main Scraper
```bash
# Activate virtual environment
source venv/bin/activate

# Run the scraper
python travis_scraper_with_markdown.py
```

### Install Chrome Extension
```bash
# Directory to load in Chrome
/Users/samgaddis/dev/APD/travis_pdf_extension/
```

## Output Structure

```
court_records/
└── MANCUSO_GIACOMO_ANGELO/
    ├── C-1-CR-25-209558/          # County Court Case
    │   ├── C-1-CR-25-209558_court_record.md
    │   ├── C-1-CR-25-209558_raw_content.json
    │   └── documents/
    │       └── *.pdf (if available)
    │
    └── D-1-DC-25-206308/          # District Court Case
        ├── D-1-DC-25-206308_court_record.md
        └── D-1-DC-25-206308_raw_content.json
        └── documents/ (usually empty for District Court)
```

## Markdown File Contents

Each `.md` file contains:
- **Case Information**: Type, status, defendant details
- **Case Events**: Timeline of court proceedings
- **Parties Involved**: Defendants, attorneys, state representatives
- **Full Page Content**: Complete text extracted from the page

## Adding New Cases

Edit `travis_scraper_with_markdown.py` and add to the `cases` list:

```python
{
    'case_number': 'YOUR-CASE-NUMBER',
    'url': 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=...'
}
```

## Troubleshooting

### Issue: No PDFs Downloaded
**Solution**: Check if it's a District Court case (D-1-DC-*). These often don't have PDFs, but the Markdown file will have all the text content.

### Issue: Page Not Loading
**Solution**: 
1. Check screenshots in `debug_output/` folder
2. Verify URLs are still valid
3. Check `scraper_with_markdown.log` for errors

### Issue: ChromeDriver Error
**Solution**: Ensure ChromeDriver matches your Chrome version. Download from https://chromedriver.chromium.org/

## Chrome Extension Usage

The extension provides:
1. **Quick Navigation**: Click icon → "Go to Travis County Search"
2. **PDF Detection**: Analyze page to find downloadable PDFs
3. **Batch Processing**: Process multiple cases automatically

### To Load Extension:
1. Chrome → `chrome://extensions/`
2. Enable Developer Mode
3. Load Unpacked → Select `travis_pdf_extension` folder
4. Click extension icon to use

## Important Files

- `travis_scraper_with_markdown.py` - Main scraper (USE THIS)
- `travis_pdf_extension/` - Chrome extension for manual downloads
- `requirements.txt` - Python dependencies (just selenium)
- `court_records/` - All extracted data goes here
- `debug_output/` - Screenshots and debug files

## Success Metrics

From our testing:
- ✅ 4/4 cases had Markdown files created successfully
- ✅ 2/4 cases had PDFs (County Court cases)
- ✅ 2/4 cases had no PDFs but full text captured (District Court)
- ✅ 100% success rate for text extraction

## Notes

- The scraper works best with County Court cases for PDFs
- District Court cases rarely have PDFs but text is always captured
- Each run creates new screenshots in `debug_output/`
- Markdown files provide complete case information even without PDFs