# Chrome Extension Installation Guide

## 📦 How to Install the Travis County PDF Downloader Extension

### Step 1: Locate the Extension Files
The Chrome extension is located in the `travis_pdf_extension` folder. The full path is:
```
/Users/samgaddis/dev/APD/travis_pdf_extension/
```

### Step 2: Open Chrome Extension Manager
1. Open Google Chrome
2. Click the three dots menu (⋮) in the top-right corner
3. Go to **More tools** → **Extensions**
4. OR simply type `chrome://extensions/` in the address bar

### Step 3: Enable Developer Mode
1. In the Extensions page, look for the **Developer mode** toggle in the top-right corner
2. Turn it **ON** (the toggle should be blue)

### Step 4: Load the Extension
1. Click the **Load unpacked** button that appears after enabling Developer mode
2. Navigate to the extension folder:
   - Go to: `/Users/samgaddis/dev/APD/`
   - Select the `travis_pdf_extension` folder
   - Click **Select** or **Open**

### Step 5: Verify Installation
- The extension should now appear in your extensions list
- You'll see "Travis County PDF Downloader" with version 1.0
- A new icon will appear in your Chrome toolbar (puzzle piece area)

## 🚀 How to Use the Extension

### Quick Access to Travis County Search
1. **Click the extension icon** in your toolbar
2. Click **"🔍 Go to Travis County Search"** button
3. You'll be taken directly to the Travis County court records search page

### On Travis County Court Pages
When you're on a court case page:
1. Click the extension icon
2. Use the available tools:
   - **Analyze Current Page** - See what PDFs are available
   - **Highlight PDF Elements** - Visually identify clickable PDF icons
   - **Download All PDFs on Page** - Automatically click all PDF elements
   - **Process All Cases** - Batch process multiple cases

## 📁 Extension Files Explained

The extension consists of these files in `travis_pdf_extension/`:
- `manifest.json` - Extension configuration
- `background.js` - Handles downloads and navigation
- `content.js` - Interacts with web pages
- `popup.html` - The UI you see when clicking the icon
- `popup.js` - Controls the popup behavior

## ⚙️ Features

### Automatic Navigation
- Clicking the extension icon shows a popup with quick access to Travis County search
- The "Go to Travis County Search" button takes you directly to the search page

### PDF Detection & Download
- Automatically finds PDF elements on court pages
- Clicks elements to trigger downloads
- Tracks download progress
- Works on all Travis County court case pages

### Batch Processing
- Can process all 4 MANCUSO cases automatically
- Shows progress in the extension badge

## 🔧 Troubleshooting

### Extension Not Loading?
- Make sure Developer mode is ON
- Check that you selected the `travis_pdf_extension` folder (not the parent folder)
- Try reloading the extension with the refresh button

### Icon Not Visible?
- Click the puzzle piece icon in Chrome toolbar
- Pin the "Travis County PDF Downloader" extension

### PDFs Not Downloading?
1. Make sure you're on a Travis County court case page
2. Try "Analyze Current Page" first to detect PDFs
3. Check Chrome's download settings (Settings → Downloads)
4. Look for blocked popups or download warnings

## 📝 Notes

- The extension only works on `https://odysseyweb.traviscountytx.gov/*` pages
- Downloaded PDFs go to your default Chrome Downloads folder
- The extension needs permissions for downloads, tabs, and storage

## 🔄 Updating the Extension

If you make changes to the extension files:
1. Go to `chrome://extensions/`
2. Find "Travis County PDF Downloader"
3. Click the refresh icon (↻)
4. The changes will take effect immediately