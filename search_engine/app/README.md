# AIT Search Engine - Application

Complete search engine application with backend API and frontend interface.

## Quick Start (One Command)

### Option 1: Python Launcher (Recommended)
```bash
cd search_engine/app
python run.py
```

This will:
- ✅ Start backend API on port 8000
- ✅ Start frontend server on port 8080
- ✅ Wait for backend to initialize
- ✅ Open browser automatically
- ✅ Handle graceful shutdown with Ctrl+C

### Option 2: Shell Script (Unix/Mac/Linux)
```bash
cd search_engine/app
chmod +x run.sh
./run.sh
```

### Option 3: Manual (Separate Terminals)

**Terminal 1 - Backend:**
```bash
cd search_engine/app/backend
python server.py
```

**Terminal 2 - Frontend:**
```bash
cd search_engine/app/frontend
python -m http.server 8080
```

## Access Points

Once running:
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
app/
├── run.py              # Unified launcher script (Python)
├── run.sh              # Unified launcher script (Shell)
├── backend/
│   ├── server.py       # FastAPI server
│   ├── api.py          # API routes
│   ├── loader.py       # Data preloader
│   └── requirements.txt
└── frontend/
    ├── index.html      # Main UI
    ├── style.css       # Styling
    ├── script.js       # Logic & API calls
    └── README.md
```

## Features

### Backend
- FastAPI REST API
- Preloaded embeddings & GloVe
- 4 search endpoints
- Auto-generated docs
- CORS enabled

### Frontend
- Beautiful gradient UI
- 4 search modes (Semantic, Multi, Single, Autocomplete)
- Real-time statistics
- Live autocomplete
- Responsive design

## Stopping Servers

Press **Ctrl+C** in the terminal running `run.py` or `run.sh` - both servers will stop gracefully.

## Troubleshooting

**Port already in use:**
```bash
# Kill processes on port 8000
lsof -ti:8000 | xargs kill -9

# Kill processes on port 8080
lsof -ti:8080 | xargs kill -9
```

**Backend won't start:**
- Check if virtual environment is activated
- Install dependencies: `pip install -r backend/requirements.txt`
- Verify GloVe files exist in `../../index/glove/`

**Frontend can't connect:**
- Ensure backend is running first
- Check browser console for CORS errors
- Verify API_BASE_URL in script.js matches backend URL
