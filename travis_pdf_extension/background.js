// Background service worker for managing downloads and storage
console.log('Travis County PDF Downloader - Background Script Loaded');

// Travis County search page URL
const TRAVIS_COUNTY_SEARCH_URL = 'https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29';

// Storage for tracking downloads
let downloadTracker = {};
let caseData = {};

// Note: Since we have a popup defined in manifest.json, clicking the icon will show the popup
// To navigate to Travis County, users can click the button in the popup
// Or we can add a listener for when popup opens to check if we should navigate

// Initialize storage
chrome.storage.local.get(['downloadHistory', 'caseData'], (result) => {
    if (result.downloadHistory) {
        downloadTracker = result.downloadHistory;
    }
    if (result.caseData) {
        caseData = result.caseData;
    }
});

// Listen for download events
chrome.downloads.onCreated.addListener((downloadItem) => {
    console.log('Download started:', downloadItem);
    
    // Track PDF downloads
    if (downloadItem.filename && downloadItem.filename.endsWith('.pdf')) {
        const timestamp = new Date().toISOString();
        if (!downloadTracker[timestamp]) {
            downloadTracker[timestamp] = [];
        }
        downloadTracker[timestamp].push({
            id: downloadItem.id,
            filename: downloadItem.filename,
            url: downloadItem.url,
            startTime: downloadItem.startTime
        });
        
        // Save to storage
        chrome.storage.local.set({downloadHistory: downloadTracker});
    }
});

// Listen for download completion
chrome.downloads.onChanged.addListener((downloadDelta) => {
    if (downloadDelta.state && downloadDelta.state.current === 'complete') {
        console.log('Download completed:', downloadDelta.id);
        
        // Get download details
        chrome.downloads.search({id: downloadDelta.id}, (downloads) => {
            if (downloads.length > 0) {
                const download = downloads[0];
                console.log('Completed download details:', download);
                
                // Organize the download if it's a PDF
                if (download.filename.endsWith('.pdf')) {
                    organizeDownload(download);
                }
            }
        });
    }
});

// Function to organize downloads into folders
function organizeDownload(download) {
    // Extract case number from filename or use stored case data
    let caseNumber = 'UNKNOWN_CASE';
    
    // Try to extract case number from filename
    const casePattern = /[CD]-\d+-[A-Z]{2}-\d{2}-\d{6}/;
    const match = download.filename.match(casePattern);
    if (match) {
        caseNumber = match[0];
    } else if (Object.keys(caseData).length > 0) {
        // Use the most recent case number
        const recentCase = Object.keys(caseData).sort().pop();
        caseNumber = recentCase;
    }
    
    // Create organized filename
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const newFilename = `court_records/MANCUSO_GIACOMO_ANGELO/${caseNumber}/documents/${caseNumber}_${timestamp}.pdf`;
    
    // Note: Chrome extensions can't directly move files to custom folders
    // This would need to be handled by the Python script or manual organization
    console.log('Suggested organization:', {
        original: download.filename,
        suggested: newFilename,
        caseNumber: caseNumber
    });
}

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Received message:', request);
    
    if (request.action === 'startDownload') {
        // Store case data
        caseData[request.caseNumber] = {
            startTime: new Date().toISOString(),
            elementCount: request.elementCount,
            tabId: sender.tab.id
        };
        chrome.storage.local.set({caseData: caseData});
        
        // Update badge
        chrome.action.setBadgeText({text: '...'});
        chrome.action.setBadgeBackgroundColor({color: '#FFA500'});
        
    } else if (request.action === 'downloadProgress') {
        // Update badge with progress
        const progress = `${request.current}/${request.total}`;
        chrome.action.setBadgeText({text: progress});
        
    } else if (request.action === 'downloadComplete') {
        // Update case data
        if (caseData[request.caseNumber]) {
            caseData[request.caseNumber].endTime = new Date().toISOString();
            caseData[request.caseNumber].downloadCount = request.downloadCount;
            chrome.storage.local.set({caseData: caseData});
        }
        
        // Update badge
        chrome.action.setBadgeText({text: '✓'});
        chrome.action.setBadgeBackgroundColor({color: '#00FF00'});
        
        // Clear badge after 3 seconds
        setTimeout(() => {
            chrome.action.setBadgeText({text: ''});
        }, 3000);
        
    } else if (request.action === 'pageAnalysis') {
        // Store page analysis
        const tabId = sender.tab.id;
        chrome.storage.local.set({
            [`analysis_${tabId}`]: request.analysis
        });
    }
    
    sendResponse({received: true});
});

// Function to process all cases
async function processAllCases() {
    const cases = [
        {
            case_number: 'C-1-CR-25-209558',
            url: 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=CEBF1977E83D029FB838EC851CA65EC3EB4F31A744BCCEA7046A65DC68AE790E00BF1662E8A8D403CE15AFD0300FB30E5B4D86BD975F1C1F1F581EDEAA834198EC48D90BA8A1375CCDE7FD3A78A7ACD4&isAuthenticated=False&mode=portalembed'
        },
        {
            case_number: 'D-1-DC-25-206308',
            url: 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=E4FF1E55FF9EFC69467A3AE9A879DC0D44F8C3085A018FC27C575782FACE0241825B8C17A7D0F6CF7D07973694EE795EC838623AA08C25643633BA8FD08AC7A4956C4D9A57344EE1727BAB37BB31A8B6&isAuthenticated=False&mode=portalembed'
        },
        {
            case_number: 'D-1-DC-25-301278',
            url: 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=DA38C924478946FB60DF9981B9A33C73EBDE1F5AA0649DC79B04AB31043D16D07F00FE3C12CA1B1D24DA1BAE18F47E7F6F3CE25F3D1EC1397C9ECDC891BC079EAD2008800C7CF018A2A3EC7B71913564&isAuthenticated=False&mode=portalembed'
        },
        {
            case_number: 'C-1-CR-25-150156',
            url: 'https://odysseyweb.traviscountytx.gov/app/RegisterOfActions/?id=2467947BC1F96D9A79E0C3C34B57BACE9AB8E29EC8B1EC5114B0D8CA8CCC463855CD4153A78810A6EB4816F389F88288FC0C1339E9D5C0299FE86F87112175E8311EFF1C7B4EF0A9DA27672A63C50160&isAuthenticated=False&mode=portalembed'
        }
    ];
    
    for (const caseInfo of cases) {
        // Open case in new tab
        const tab = await chrome.tabs.create({url: caseInfo.url, active: false});
        
        // Wait for page to load
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Send download command
        try {
            const response = await chrome.tabs.sendMessage(tab.id, {action: 'downloadPDFs'});
            console.log(`Case ${caseInfo.case_number} processed:`, response);
        } catch (error) {
            console.error(`Error processing case ${caseInfo.case_number}:`, error);
        }
        
        // Wait before next case
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
    
    console.log('All cases processed');
}