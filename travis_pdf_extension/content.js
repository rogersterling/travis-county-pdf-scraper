// Content script that runs on Travis County court pages
console.log('Travis County PDF Downloader - Content Script Loaded');

// Configuration
const DELAY_BETWEEN_CLICKS = 2000; // 2 seconds between clicks
const WAIT_FOR_PAGE_LOAD = 5000; // 5 seconds initial wait

// Function to extract case number from URL or page
function getCaseNumber() {
    // Try to find case number in page content
    const casePatterns = [
        /[CD]-\d+-[A-Z]{2}-\d{2}-\d{6}/g,
        /[CD]-\d+-[A-Z]{2}-\d{2}-\d{5,6}/g
    ];
    
    const pageText = document.body.innerText;
    for (const pattern of casePatterns) {
        const matches = pageText.match(pattern);
        if (matches && matches.length > 0) {
            return matches[0];
        }
    }
    
    // Try to extract from title or headers
    const title = document.title;
    const h1 = document.querySelector('h1');
    const h2 = document.querySelector('h2');
    
    const textToSearch = `${title} ${h1?.innerText || ''} ${h2?.innerText || ''}`;
    for (const pattern of casePatterns) {
        const matches = textToSearch.match(pattern);
        if (matches && matches.length > 0) {
            return matches[0];
        }
    }
    
    return 'UNKNOWN_CASE';
}

// Function to find all PDF download elements
function findPDFElements() {
    const pdfElements = [];
    
    // Strategy 1: Find all images that might be PDF icons
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        const src = img.src || '';
        const alt = img.alt || '';
        const title = img.title || '';
        
        // Check if this looks like a PDF icon
        if (src.includes('icon') || src.includes('pdf') || src.includes('document') ||
            alt.toLowerCase().includes('pdf') || alt.toLowerCase().includes('document') ||
            title.toLowerCase().includes('pdf') || title.toLowerCase().includes('document')) {
            
            // Find the clickable parent
            let clickable = img.closest('a, button, [onclick], td');
            if (clickable) {
                pdfElements.push({
                    element: clickable,
                    type: 'image-icon',
                    info: {src, alt, title}
                });
            } else {
                // The image itself might be clickable
                pdfElements.push({
                    element: img,
                    type: 'image-direct',
                    info: {src, alt, title}
                });
            }
        }
    });
    
    // Strategy 2: Find all links that might download PDFs
    const links = document.querySelectorAll('a');
    links.forEach(link => {
        const href = link.href || '';
        const text = link.innerText || '';
        const onclick = link.onclick ? link.onclick.toString() : '';
        
        if (href.includes('pdf') || href.includes('document') || href.includes('download') ||
            text.toLowerCase().includes('pdf') || text.toLowerCase().includes('document') ||
            onclick.includes('pdf') || onclick.includes('document')) {
            
            pdfElements.push({
                element: link,
                type: 'link',
                info: {href, text, onclick}
            });
        }
    });
    
    // Strategy 3: Find elements with onclick handlers
    const clickables = document.querySelectorAll('[onclick]');
    clickables.forEach(elem => {
        const onclick = elem.onclick ? elem.onclick.toString() : elem.getAttribute('onclick');
        if (onclick && (onclick.includes('pdf') || onclick.includes('document') || onclick.includes('download'))) {
            pdfElements.push({
                element: elem,
                type: 'onclick-handler',
                info: {onclick, tag: elem.tagName}
            });
        }
    });
    
    // Strategy 4: Look in table cells for any clickable content
    const tableCells = document.querySelectorAll('td');
    tableCells.forEach(td => {
        const images = td.querySelectorAll('img');
        const links = td.querySelectorAll('a');
        const buttons = td.querySelectorAll('button');
        
        [...images, ...links, ...buttons].forEach(elem => {
            if (!pdfElements.some(pdf => pdf.element === elem)) {
                // Check if this looks like it might be document-related
                const text = td.innerText || '';
                if (text.toLowerCase().includes('document') || text.toLowerCase().includes('pdf') ||
                    text.toLowerCase().includes('file') || text.toLowerCase().includes('view')) {
                    pdfElements.push({
                        element: elem,
                        type: 'table-cell-element',
                        info: {cellText: text, tag: elem.tagName}
                    });
                }
            }
        });
    });
    
    // Remove duplicates
    const seen = new Set();
    const unique = [];
    pdfElements.forEach(pdf => {
        if (!seen.has(pdf.element)) {
            seen.add(pdf.element);
            unique.push(pdf);
        }
    });
    
    return unique;
}

// Function to highlight an element (for visual feedback)
function highlightElement(element) {
    const originalBorder = element.style.border;
    element.style.border = '3px solid red';
    element.style.backgroundColor = 'yellow';
    
    setTimeout(() => {
        element.style.border = originalBorder;
        element.style.backgroundColor = '';
    }, 1000);
}

// Function to click an element using multiple methods
async function clickElement(element) {
    return new Promise((resolve) => {
        try {
            // Scroll into view
            element.scrollIntoView({behavior: 'smooth', block: 'center'});
            
            // Highlight for visual feedback
            highlightElement(element);
            
            setTimeout(() => {
                // Try different click methods
                try {
                    // Method 1: Regular click
                    element.click();
                    console.log('Clicked with regular click');
                } catch (e) {
                    try {
                        // Method 2: Dispatch click event
                        const clickEvent = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        element.dispatchEvent(clickEvent);
                        console.log('Clicked with dispatched event');
                    } catch (e2) {
                        // Method 3: Focus and simulate Enter key
                        element.focus();
                        const enterEvent = new KeyboardEvent('keypress', {
                            key: 'Enter',
                            keyCode: 13,
                            bubbles: true
                        });
                        element.dispatchEvent(enterEvent);
                        console.log('Clicked with Enter key');
                    }
                }
                resolve();
            }, 500);
        } catch (error) {
            console.error('Error clicking element:', error);
            resolve();
        }
    });
}

// Function to download all PDFs
async function downloadAllPDFs() {
    console.log('Starting PDF download process...');
    
    const caseNumber = getCaseNumber();
    console.log('Case number:', caseNumber);
    
    // Find all PDF elements
    const pdfElements = findPDFElements();
    console.log(`Found ${pdfElements.length} potential PDF elements`);
    
    // Send info to background script
    chrome.runtime.sendMessage({
        action: 'startDownload',
        caseNumber: caseNumber,
        elementCount: pdfElements.length
    });
    
    // Click each element with delay
    let downloadCount = 0;
    for (let i = 0; i < pdfElements.length; i++) {
        const pdf = pdfElements[i];
        console.log(`Clicking element ${i + 1}/${pdfElements.length}:`, pdf.info);
        
        await clickElement(pdf.element);
        downloadCount++;
        
        // Send progress update
        chrome.runtime.sendMessage({
            action: 'downloadProgress',
            current: i + 1,
            total: pdfElements.length,
            caseNumber: caseNumber
        });
        
        // Wait between clicks
        if (i < pdfElements.length - 1) {
            await new Promise(resolve => setTimeout(resolve, DELAY_BETWEEN_CLICKS));
        }
    }
    
    // Send completion message
    chrome.runtime.sendMessage({
        action: 'downloadComplete',
        caseNumber: caseNumber,
        downloadCount: downloadCount
    });
    
    return downloadCount;
}

// Function to analyze page and send debug info
function analyzePage() {
    const analysis = {
        url: window.location.href,
        title: document.title,
        caseNumber: getCaseNumber(),
        tables: document.querySelectorAll('table').length,
        images: document.querySelectorAll('img').length,
        links: document.querySelectorAll('a').length,
        buttons: document.querySelectorAll('button').length,
        pdfElements: findPDFElements().map(pdf => ({
            type: pdf.type,
            info: pdf.info,
            html: pdf.element.outerHTML.substring(0, 200)
        }))
    };
    
    console.log('Page Analysis:', analysis);
    
    // Send to background script
    chrome.runtime.sendMessage({
        action: 'pageAnalysis',
        analysis: analysis
    });
    
    return analysis;
}

// Listen for messages from popup or background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'downloadPDFs') {
        downloadAllPDFs().then(count => {
            sendResponse({success: true, count: count});
        });
        return true; // Keep message channel open for async response
    } else if (request.action === 'analyzePage') {
        const analysis = analyzePage();
        sendResponse({success: true, analysis: analysis});
        return true;
    } else if (request.action === 'highlightPDFs') {
        const pdfElements = findPDFElements();
        pdfElements.forEach(pdf => highlightElement(pdf.element));
        sendResponse({success: true, count: pdfElements.length});
    }
});

// Auto-run analysis on page load
setTimeout(() => {
    console.log('Auto-analyzing page...');
    analyzePage();
}, WAIT_FOR_PAGE_LOAD);