# AIT Search Engine - Backend API

FastAPI-based REST API for the search engine with semantic search capabilities.

## Features

- **Single-word Search**: Fast exact word matching
- **Multi-word Search**: AND operation across multiple terms
- **Semantic Search**: GloVe-based similarity search
- **Autocomplete**: Real-time word suggestions
- **Preloaded Data**: Fast responses with in-memory data

## API Endpoints

### Base URL: `http://localhost:8000/api`

#### 1. Single-word Search
```bash
POST /api/search/single
{
  "query": "virus",
  "top_k": 10
}
```

#### 2. Multi-word Search
```bash
POST /api/search/multi
{
  "query": "virus vaccine",
  "top_k": 10
}
```

#### 3. Semantic Search
```bash
POST /api/search/semantic
{
  "query": "covid treatment",
  "top_k": 10
}
```

#### 4. Autocomplete
```bash
POST /api/autocomplete
{
  "prefix": "vir",
  "top_n": 10
}
```

#### 5. Statistics
```bash
GET /api/stats
```

## Setup & Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python server.py
```

Or with uvicorn directly:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API:
- **API**: http://localhost:8000/api
- **Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Response Format

All search endpoints return:
```json
[
  {
    "doc_id": "doc_123",
    "score": 0.95
  }
]
```

## Development

- Auto-reload enabled in development mode
- CORS enabled for frontend integration
- Comprehensive error handling
