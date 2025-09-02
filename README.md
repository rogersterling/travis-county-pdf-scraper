# Travis County Court Records Scraper

A comprehensive solution for extracting court records from the Travis County Odyssey Portal, including both PDF downloads and text content extraction to Markdown format.

## 🎯 Purpose

This tool automates the extraction of court records from Travis County's online system, capturing:
- PDF documents (when available)
- Full text content of court proceedings as Markdown files
- Structured case information including parties, events, and case status

## ✨ Features

- **Dual Extraction**: Downloads PDFs when available AND captures page text as Markdown
- **Chrome Extension**: Quick navigation to Travis County search page with PDF download tools
- **Structured Output**: Organized folder structure by case number
- **Comprehensive Logging**: Detailed logs and debug output for troubleshooting
- **Screenshot Capture**: Visual record of each processed page

## 📁 Project Structure

```
├── travis_scraper_with_markdown.py  # Main scraper (recommended)
├── travis_pdf_extension/            # Chrome extension for manual PDF downloads
│   ├── manifest.json
│   ├── content.js
│   ├── background.js
│   ├── popup.html
│   └── popup.js
├── court_records/                   # Output directory
│   └── MANCUSO_GIACOMO_ANGELO/     # Organized by defendant name
│       ├── [CASE-NUMBER]/
│       │   ├── [CASE]_court_record.md    # Extracted text content
│       │   ├── [CASE]_raw_content.json   # Raw JSON data
│       │   └── documents/                # PDFs (if available)
└── debug_output/                    # Screenshots and debug files
```

## 🚀 Quick Start

### Python Scraper (Recommended)

1. **Setup Virtual Environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the Scraper**:
```bash
python travis_scraper_with_markdown.py
```

### Chrome Extension (For Manual PDF Downloads)

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select the `travis_pdf_extension` folder
5. Click the extension icon to navigate to Travis County search

## 📊 Output

### Markdown Files
Each case generates a structured Markdown file containing:
- Case information (type, status, parties)
- Case events timeline
- Party details (defendants, attorneys)
- Full page text content

Example: `D-1-DC-25-206308_court_record.md`

### JSON Files
Raw extracted data in JSON format for programmatic access.

### PDFs
Downloaded to `documents/` subfolder when available on the court page.

## 🔧 Configuration

The scraper is pre-configured with specific case URLs. To modify:

1. Edit the `cases` list in `travis_scraper_with_markdown.py`
2. Add new cases with format:
```python
{
    'case_number': 'CASE-NUMBER',
    'url': 'https://odysseyweb.traviscountytx.gov/...'
}
```

## 📝 Example Output Structure

```
court_records/
└── MANCUSO_GIACOMO_ANGELO/
    ├── C-1-CR-25-209558/
    │   ├── C-1-CR-25-209558_court_record.md
    │   ├── C-1-CR-25-209558_raw_content.json
    │   └── documents/
    │       └── C-1-CR-25-209558.pdf
    └── D-1-DC-25-206308/
        ├── D-1-DC-25-206308_court_record.md
        └── D-1-DC-25-206308_raw_content.json
```

## ⚠️ Important Notes

- District Court cases (D-1-DC-*) often don't have downloadable PDFs but text content is captured
- County Court cases (C-1-CR-*) typically have PDFs available
- The scraper requires Chrome/Chromium browser and ChromeDriver
- All extracted content is saved locally - no data is sent externally

## 🐛 Troubleshooting

### No PDFs Downloaded?
- District Court pages often don't have PDFs - check the Markdown file for text content
- Check `debug_output/` for screenshots to verify page loaded correctly

### ChromeDriver Issues?
- Ensure ChromeDriver version matches your Chrome browser version
- Download from: https://chromedriver.chromium.org/

### Page Not Loading?
- Check internet connection
- Verify the case URLs are still valid
- Review logs in `scraper_with_markdown.log`

## 📜 Legal Notice

This tool is for legitimate use only. Ensure you have proper authorization to access and download court records. Respect all terms of service and legal restrictions.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

## 📄 License

MIT License - See LICENSE file for details