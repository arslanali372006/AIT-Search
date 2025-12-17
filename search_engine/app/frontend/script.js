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
            updatePlaceholder();
            clearResults();
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
