// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State
let currentSearchType = 'semantic';
let autocompleteTimeout = null;

// DOM Elements
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const topKSelect = document.getElementById('topK');
const resultsDiv = document.getElementById('results');
const loadingDiv = document.getElementById('loading');
const resultsHeader = document.getElementById('resultsHeader');
const noResults = document.getElementById('noResults');
const errorMessage = document.getElementById('errorMessage');
const autocompleteSuggestions = document.getElementById('autocompleteSuggestions');
const tabs = document.querySelectorAll('.tab');
const addDocumentSection = document.getElementById('addDocumentSection');
const addDocumentForm = document.getElementById('addDocumentForm');
const cancelAddDocBtn = document.getElementById('cancelAddDoc');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    setupEventListeners();
    updatePlaceholder();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab switching
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            currentSearchType = tab.dataset.type;
            
            if (currentSearchType === 'add-document') {
                showAddDocumentSection();
            } else {
                hideAddDocumentSection();
                updatePlaceholder();
                clearResults();
            }
        });
    });

    // Search button
    searchButton.addEventListener('click', performSearch);

    // Enter key to search
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });

    // Autocomplete on input
    searchInput.addEventListener('input', handleAutocompleteInput);

    // Click outside to close autocomplete
    document.addEventListener('click', (e) => {
        if (!autocompleteSuggestions.contains(e.target) && e.target !== searchInput) {
            autocompleteSuggestions.classList.remove('show');
        }
    });

    // Add document form
    if (addDocumentForm) {
        addDocumentForm.addEventListener('submit', handleAddDocument);
    }

    // Cancel add document
    if (cancelAddDocBtn) {
        cancelAddDocBtn.addEventListener('click', () => {
            // Switch back to semantic search tab
            document.querySelector('.tab[data-type="semantic"]').click();
        });
    }

    // Upload method toggle
    const toggleBtns = document.querySelectorAll('.toggle-btn');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            toggleBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const method = btn.dataset.method;
            if (method === 'form') {
                document.getElementById('addDocumentForm').style.display = 'block';
                document.getElementById('fileUploadSection').style.display = 'none';
            } else {
                document.getElementById('addDocumentForm').style.display = 'none';
                document.getElementById('fileUploadSection').style.display = 'block';
            }
        });
    });

    // File input change
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }

    // Upload file button
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    if (uploadFileBtn) {
        uploadFileBtn.addEventListener('click', handleFileUpload);
    }

    // Cancel file upload
    const cancelFileUpload = document.getElementById('cancelFileUpload');
    if (cancelFileUpload) {
        cancelFileUpload.addEventListener('click', () => {
            document.querySelector('.tab[data-type="semantic"]').click();
        });
    }
}

// Update placeholder based on search type
function updatePlaceholder() {
    const placeholders = {
        'semantic': 'Start typing for suggestions... (Semantic search)',
        'multi': 'Start typing for suggestions... (Multi-word search)',
        'single': 'Start typing for suggestions... (Single-word search)',
        'autocomplete': 'Start typing to see word suggestions...'
    };
    searchInput.placeholder = placeholders[currentSearchType];
}

// Load Statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();
        
        document.getElementById('docCount').textContent = data.total_documents.toLocaleString();
        document.getElementById('wordCount').textContent = data.total_words.toLocaleString();
        document.getElementById('status').textContent = 'Online';
        document.getElementById('status').classList.add('online');
    } catch (error) {
        console.error('Failed to load stats:', error);
        document.getElementById('status').textContent = 'Offline';
        document.getElementById('status').classList.add('offline');
    }
}

// Handle Autocomplete Input
function handleAutocompleteInput(e) {
    const query = e.target.value;
    
    // Allow empty query if there's a trailing space (user wants suggestions for next word)
    if (!query) {
        autocompleteSuggestions.classList.remove('show');
        return;
    }

    // Debounce (reduce delay for better UX)
    clearTimeout(autocompleteTimeout);
    autocompleteTimeout = setTimeout(() => {
        fetchAutocompleteSuggestions(query);
    }, 200);
}

// Fetch Autocomplete Suggestions
async function fetchAutocompleteSuggestions(query) {
    try {
        // Split by spaces but keep trailing spaces
        const parts = query.split(/\s+/);
        const hasTrailingSpace = query.endsWith(' ');
        
        // Get the last word being typed
        let lastWord;
        let previousWords;
        
        if (hasTrailingSpace && query.trim().length > 0) {
            // User just typed a space, start fresh for new word
            lastWord = '';
            previousWords = parts.filter(w => w.length > 0);
        } else {
            // User is typing a word
            const trimmedParts = query.trim().split(/\s+/);
            lastWord = trimmedParts[trimmedParts.length - 1];
            previousWords = trimmedParts.slice(0, -1);
        }
        
        // Only autocomplete if last word has at least 1 character
        // or if we just typed a space (show all suggestions)
        if (lastWord.length === 0 && !hasTrailingSpace) {
            autocompleteSuggestions.classList.remove('show');
            return;
        }
        
        // If last word is too short and no trailing space, require at least 2 chars
        if (lastWord.length === 1 && !hasTrailingSpace && previousWords.length === 0) {
            // First word needs at least 2 characters
            if (lastWord.length < 2) {
                autocompleteSuggestions.classList.remove('show');
                return;
            }
        }
        
        const response = await fetch(`${API_BASE_URL}/autocomplete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prefix: lastWord || 'a',  // Default prefix if empty
                top_n: 10
            })
        });

        const data = await response.json();
        displayAutocompleteSuggestions(data.suggestions, previousWords);
    } catch (error) {
        console.error('Autocomplete error:', error);
    }
}

// Display Autocomplete Suggestions
function displayAutocompleteSuggestions(suggestions, previousWords = []) {
    if (suggestions.length === 0) {
        autocompleteSuggestions.classList.remove('show');
        return;
    }

    autocompleteSuggestions.innerHTML = suggestions.map(suggestion => {
        // Build full suggestion with previous words
        const fullSuggestion = previousWords.length > 0 
            ? previousWords.join(' ') + ' ' + suggestion 
            : suggestion;
        
        return `<div class="suggestion-item" onclick="selectSuggestion('${fullSuggestion}')">${fullSuggestion}</div>`;
    }).join('');
    
    autocompleteSuggestions.classList.add('show');
}

// Select Autocomplete Suggestion
function selectSuggestion(suggestion) {
    searchInput.value = suggestion;
    autocompleteSuggestions.classList.remove('show');
    
    // If on autocomplete tab, don't trigger search
    if (currentSearchType !== 'autocomplete') {
        performSearch();
    }
}

// Perform Search
async function performSearch() {
    const query = searchInput.value.trim();
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }

    if (currentSearchType === 'autocomplete') {
        // For autocomplete tab, just show suggestions (already visible)
        return;
    }

    // Hide autocomplete when searching
    autocompleteSuggestions.classList.remove('show');
    
    clearResults();
    showLoading();

    const startTime = performance.now();

    try {
        const endpoint = {
            'semantic': '/search/semantic',
            'multi': '/search/multi',
            'single': '/search/single'
        }[currentSearchType];

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: parseInt(topKSelect.value)
            })
        });

        const data = await response.json();
        const endTime = performance.now();
        const searchTime = Math.round(endTime - startTime);

        hideLoading();
        displayResults(data, searchTime);

    } catch (error) {
        hideLoading();
        showError(`Search failed: ${error.message}`);
    }
}

// Display Results
function displayResults(results, searchTime) {
    if (results.length === 0) {
        noResults.style.display = 'block';
        return;
    }

    resultsHeader.style.display = 'block';
    document.getElementById('resultCount').textContent = `(${results.length})`;
    document.getElementById('searchTime').textContent = searchTime;

    // Create placeholders first
    resultsDiv.innerHTML = results.map(result => {
        const scoreClass = result.score > 0.7 ? 'high' : result.score > 0.4 ? 'medium' : 'low';
        const scoreDisplay = currentSearchType === 'semantic' 
            ? result.score.toFixed(4) 
            : Math.round(result.score);

        return `
            <div class="result-item" id="result-${result.doc_id}">
                <div class="result-header">
                    <span class="doc-id">${result.doc_id}</span>
                    <span class="score ${scoreClass}">Score: ${scoreDisplay}</span>
                </div>
                <div class="result-loading">Loading document details...</div>
            </div>
        `;
    }).join('');
    
    // Fetch document details for each result
    results.forEach(result => fetchDocumentDetails(result.doc_id));
}

// Fetch Document Details
async function fetchDocumentDetails(docId) {
    try {
        const response = await fetch(`${API_BASE_URL}/document/${docId}`);
        const data = await response.json();
        
        const resultElement = document.getElementById(`result-${docId}`);
        if (resultElement) {
            const loadingDiv = resultElement.querySelector('.result-loading');
            if (loadingDiv) {
                loadingDiv.remove();
            }
            
            const detailsHTML = `
                <div class="result-details">
                    <h3 class="result-title">${data.title}</h3>
                    <p class="result-abstract">${data.abstract}</p>
                </div>
            `;
            
            resultElement.insertAdjacentHTML('beforeend', detailsHTML);
        }
    } catch (error) {
        console.error(`Failed to fetch details for ${docId}:`, error);
        const resultElement = document.getElementById(`result-${docId}`);
        if (resultElement) {
            const loadingDiv = resultElement.querySelector('.result-loading');
            if (loadingDiv) {
                loadingDiv.innerHTML = '<em>Could not load document details</em>';
            }
        }
    }
}

// Show Loading
function showLoading() {
    loadingDiv.style.display = 'block';
    resultsDiv.innerHTML = '';
    resultsHeader.style.display = 'none';
    noResults.style.display = 'none';
    errorMessage.style.display = 'none';
}

// Hide Loading
function hideLoading() {
    loadingDiv.style.display = 'none';
}

// Show Error
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// Clear Results
function clearResults() {
    resultsDiv.innerHTML = '';
    resultsHeader.style.display = 'none';
    noResults.style.display = 'none';
    errorMessage.style.display = 'none';
    autocompleteSuggestions.classList.remove('show');
}

// Show Add Document Section
function showAddDocumentSection() {
    // Hide search section
    document.querySelector('.search-section').style.display = 'none';
    document.querySelector('.results-section').style.display = 'none';
    
    // Show add document section
    addDocumentSection.style.display = 'block';
    
    // Clear form
    addDocumentForm.reset();
    document.getElementById('addDocResult').style.display = 'none';
}

// Hide Add Document Section
function hideAddDocumentSection() {
    // Show search section
    document.querySelector('.search-section').style.display = 'block';
    document.querySelector('.results-section').style.display = 'block';
    
    // Hide add document section
    addDocumentSection.style.display = 'none';
}

// Handle Add Document
async function handleAddDocument(e) {
    e.preventDefault();
    
    const title = document.getElementById('docTitle').value.trim();
    const abstract = document.getElementById('docAbstract').value.trim();
    const body = document.getElementById('docBody').value.trim();
    
    if (!title || !abstract) {
        showAddDocError('Title and Abstract are required');
        return;
    }
    
    // Show loading state
    const submitBtn = addDocumentForm.querySelector('.btn-primary');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Adding Document...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/document/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                abstract: abstract,
                body_text: body
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAddDocSuccess(data);
            addDocumentForm.reset();
        } else {
            showAddDocError(data.detail || 'Failed to add document');
        }
    } catch (error) {
        showAddDocError(`Error: ${error.message}`);
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// Show Add Document Success
function showAddDocSuccess(data) {
    const resultDiv = document.getElementById('addDocResult');
    resultDiv.className = 'add-doc-result';
    resultDiv.style.display = 'block';
    
    resultDiv.innerHTML = `
        <h3>✅ Document Added Successfully!</h3>
        <p><strong>Document ID:</strong> ${data.doc_id}</p>
        <p><strong>Tokens:</strong> ${data.details.tokens_count} (${data.details.unique_words} unique)</p>
        <p><strong>Indexing Time:</strong> ${data.details.indexing_time}</p>
        <p><strong>Embedding:</strong> ${data.details.embedding_created ? 'Created' : 'Not created'}</p>
        <p style="margin-top: 15px; font-style: italic;">Your document is now searchable!</p>
    `;
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show Add Document Error
function showAddDocError(message) {
    const resultDiv = document.getElementById('addDocResult');
    resultDiv.className = 'add-doc-result error';
    resultDiv.style.display = 'block';
    
    resultDiv.innerHTML = `
        <h3>❌ Error Adding Document</h3>
        <p>${message}</p>
    `;
    
    // Scroll to result
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Handle File Select
function handleFileSelect(e) {
    const file = e.target.files[0];
    const fileName = document.getElementById('fileName');
    const uploadBtn = document.getElementById('uploadFileBtn');
    
    if (file) {
        fileName.textContent = file.name;
        fileName.classList.add('selected');
        uploadBtn.disabled = false;
    } else {
        fileName.textContent = 'No file selected';
        fileName.classList.remove('selected');
        uploadBtn.disabled = true;
    }
}

// Handle File Upload
async function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        showAddDocError('Please select a file');
        return;
    }

    const uploadBtn = document.getElementById('uploadFileBtn');
    const originalText = uploadBtn.textContent;
    uploadBtn.textContent = 'Processing...';
    uploadBtn.disabled = true;

    try {
        const fileExt = file.name.split('.').pop().toLowerCase();
        let docData;

        if (fileExt === 'json') {
            // Parse JSON file
            const text = await file.text();
            const jsonData = JSON.parse(text);
            
            // Extract title, abstract, body
            docData = {
                title: jsonData.metadata?.title || jsonData.title || file.name,
                abstract: extractText(jsonData.abstract),
                body_text: extractText(jsonData.body_text)
            };
        } else if (fileExt === 'txt') {
            // For TXT files, use filename as title and content as body
            const text = await file.text();
            docData = {
                title: file.name.replace('.txt', ''),
                abstract: text.substring(0, 500), // First 500 chars as abstract
                body_text: text
            };
        } else {
            throw new Error('Unsupported file type. Please use JSON or TXT files.');
        }

        // Send to API
        const response = await fetch(`${API_BASE_URL}/document/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(docData)
        });

        const data = await response.json();

        if (response.ok) {
            showAddDocSuccess(data);
            fileInput.value = '';
            document.getElementById('fileName').textContent = 'No file selected';
            document.getElementById('fileName').classList.remove('selected');
        } else {
            showAddDocError(data.detail || 'Failed to add document');
        }
    } catch (error) {
        showAddDocError(`Error: ${error.message}`);
    } finally {
        uploadBtn.textContent = originalText;
        uploadBtn.disabled = false;
    }
}

// Extract text helper for file upload
function extractText(field) {
    if (!field) return '';
    if (typeof field === 'string') return field;
    if (Array.isArray(field)) {
        return field.map(item => {
            if (typeof item === 'string') return item;
            if (item && item.text) return item.text;
            return '';
        }).join(' ');
    }
    return '';
}
