# AIT Search Engine - Frontend

Simple, elegant frontend interface for testing the search engine API.

## Features

- **4 Search Modes**: Semantic, Multi-word, Single-word, Autocomplete
- **Live Statistics**: Shows total documents, words, and server status
- **Real-time Autocomplete**: Type-ahead suggestions
- **Responsive Design**: Works on desktop and mobile
- **Search Metrics**: Shows search time for each query

## Quick Start

### Option 1: Direct File Open
Simply open `index.html` in your browser

### Option 2: Local Server (Recommended)
```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx http-server -p 8080
```

Then visit: http://localhost:8080

## Configuration

Edit `script.js` to change the API endpoint:
```javascript
const API_BASE_URL = 'http://localhost:8000/api';
```

## Usage

1. **Start Backend**: Make sure your FastAPI backend is running on port 8000
2. **Open Frontend**: Open index.html or serve on localhost:8080
3. **Select Search Type**: Click tabs to switch between search modes
4. **Enter Query**: Type your search query
5. **View Results**: Results appear with scores

## Search Examples

- **Semantic**: "covid treatment" → finds similar documents
- **Multi-word**: "virus vaccine" → finds docs with BOTH words
- **Single-word**: "virus" → finds all docs with "virus"
- **Autocomplete**: "vir" → suggests "virus", "viral", etc.

## Tech Stack

- Pure HTML5/CSS3/JavaScript
- No frameworks or dependencies
- Fetch API for HTTP requests
- Modern CSS Grid & Flexbox

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
