// Popup script for user interface
console.log('Popup script loaded');

// Travis County search page URL
const TRAVIS_COUNTY_SEARCH_URL = 'https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29';

// Navigate to Travis County search page
document.getElementById('goToSearch').addEventListener('click', () => {
    chrome.tabs.create({ url: TRAVIS_COUNTY_SEARCH_URL });
    window.close(); // Close the popup after opening the tab
});

// Update status display
function updateStatus(message, isError = false) {
    const statusDiv = document.getElementById('currentStatus');
    statusDiv.textContent = message;
    statusDiv.style.background = isError ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 255, 0, 0.3)';
}

// Load download history
function loadDownloadHistory() {
    chrome.storage.local.get(['downloadHistory', 'caseData'], (result) => {
        const historyDiv = document.getElementById('downloadHistory');
        
        if (result.downloadHistory) {
            const downloads = Object.values(result.downloadHistory).flat();
            const pdfCount = downloads.filter(d => d.filename && d.filename.endsWith('.pdf')).length;
            historyDiv.textContent = `Total PDFs downloaded: ${pdfCount}`;
        }
        
        if (result.caseData) {
            const cases = Object.keys(result.caseData).length;
            historyDiv.textContent += ` | Cases processed: ${cases}`;
        }
    });
}

// Analyze current page
document.getElementById('analyzePage').addEventListener('click', async () => {
    updateStatus('Analyzing page...');
    
    try {
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        
        chrome.tabs.sendMessage(tab.id, {action: 'analyzePage'}, (response) => {
            if (chrome.runtime.lastError) {
                updateStatus('Error: Page not compatible', true);
                return;
            }
            
            if (response && response.success) {
                const analysis = response.analysis;
                const analysisDiv = document.getElementById('analysis');
                
                analysisDiv.innerHTML = `
                    <strong>Case:</strong> ${analysis.caseNumber}<br>
                    <strong>URL:</strong> ${analysis.url.substring(0, 50)}...<br>
                    <strong>Tables:</strong> ${analysis.tables}<br>
                    <strong>Images:</strong> ${analysis.images}<br>
                    <strong>Links:</strong> ${analysis.links}<br>
                    <strong>Buttons:</strong> ${analysis.buttons}<br>
                    <strong>PDF Elements Found:</strong> ${analysis.pdfElements.length}<br>
                    <details>
                        <summary>PDF Elements Details</summary>
                        ${analysis.pdfElements.map(pdf => `
                            <div style="margin: 5px 0; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 3px;">
                                <strong>Type:</strong> ${pdf.type}<br>
                                ${JSON.stringify(pdf.info, null, 2)}
                            </div>
                        `).join('')}
                    </details>
                `;
                
                analysisDiv.style.display = 'block';
                updateStatus(`Analysis complete: ${analysis.pdfElements.length} PDF elements found`);
            }
        });
    } catch (error) {
        updateStatus('Error: ' + error.message, true);
    }
});

// Highlight PDF elements
document.getElementById('highlightPDFs').addEventListener('click', async () => {
    updateStatus('Highlighting PDF elements...');
    
    try {
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        
        chrome.tabs.sendMessage(tab.id, {action: 'highlightPDFs'}, (response) => {
            if (chrome.runtime.lastError) {
                updateStatus('Error: Page not compatible', true);
                return;
            }
            
            if (response && response.success) {
                updateStatus(`Highlighted ${response.count} PDF elements`);
            }
        });
    } catch (error) {
        updateStatus('Error: ' + error.message, true);
    }
});

// Download PDFs from current page
document.getElementById('downloadPDFs').addEventListener('click', async () => {
    updateStatus('Starting PDF downloads...');
    
    try {
        const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
        
        chrome.tabs.sendMessage(tab.id, {action: 'downloadPDFs'}, (response) => {
            if (chrome.runtime.lastError) {
                updateStatus('Error: Page not compatible', true);
                return;
            }
            
            if (response && response.success) {
                updateStatus(`Download complete: ${response.count} PDFs processed`);
                loadDownloadHistory();
            }
        });
    } catch (error) {
        updateStatus('Error: ' + error.message, true);
    }
});

// Process all cases
document.getElementById('processAll').addEventListener('click', async () => {
    updateStatus('Processing all cases...');
    
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
    
    for (let i = 0; i < cases.length; i++) {
        const caseInfo = cases[i];
        updateStatus(`Processing case ${i + 1}/${cases.length}: ${caseInfo.case_number}`);
        
        // Open case in new tab
        const tab = await chrome.tabs.create({url: caseInfo.url, active: false});
        
        // Wait for page to load
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Send download command
        try {
            await new Promise((resolve, reject) => {
                chrome.tabs.sendMessage(tab.id, {action: 'downloadPDFs'}, (response) => {
                    if (chrome.runtime.lastError) {
                        reject(chrome.runtime.lastError);
                    } else {
                        resolve(response);
                    }
                });
            });
        } catch (error) {
            console.error(`Error processing case ${caseInfo.case_number}:`, error);
        }
        
        // Close tab after processing
        await chrome.tabs.remove(tab.id);
        
        // Wait before next case
        if (i < cases.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
    }
    
    updateStatus('All cases processed!');
    loadDownloadHistory();
});

// Toggle analysis display
document.getElementById('toggleAnalysis').addEventListener('click', () => {
    const analysisDiv = document.getElementById('analysis');
    analysisDiv.style.display = analysisDiv.style.display === 'none' ? 'block' : 'none';
});

// Load history on popup open
loadDownloadHistory();

// Listen for updates from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'downloadProgress') {
        updateStatus(`Downloading: ${request.current}/${request.total} for ${request.caseNumber}`);
    } else if (request.action === 'downloadComplete') {
        updateStatus(`Complete: ${request.downloadCount} PDFs from ${request.caseNumber}`);
        loadDownloadHistory();
    }
});