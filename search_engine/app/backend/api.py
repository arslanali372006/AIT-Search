# app/backend/api.py
"""
API route handlers for the search engine.
"""
import sys
import os

# Add src directory to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from search import single_word_search, multi_word_search, autocomplete_words  # type: ignore
from semantic import semantic_search_query  # type: ignore
from loader import search_engine

router = APIRouter()

# Request/Response Models
class SearchResponse(BaseModel):
    doc_id: str
    score: float

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 10

class AutocompleteRequest(BaseModel):
    prefix: str
    top_n: Optional[int] = 10

class AutocompleteResponse(BaseModel):
    suggestions: List[str]


@router.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Search Engine API is running",
        "endpoints": {
            "single_word": "/search/single",
            "multi_word": "/search/multi",
            "semantic": "/search/semantic",
            "autocomplete": "/autocomplete"
        }
    }


@router.post("/search/single", response_model=List[SearchResponse])
async def single_word_search_endpoint(request: SearchRequest):
    """
    Single-word search: Returns documents containing the exact word.
    """
    try:
        word = request.query.strip().lower()
        if not word:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = single_word_search(word)
        
        if not results:
            return []
        
        # Return top_k results
        return [
            SearchResponse(doc_id=doc_id, score=float(score))
            for doc_id, score in results[:request.top_k]
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/search/multi", response_model=List[SearchResponse])
async def multi_word_search_endpoint(request: SearchRequest):
    """
    Multi-word search: Returns documents containing ALL words (AND search).
    """
    try:
        query = request.query.strip().lower()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        results = multi_word_search(query)
        
        if not results:
            return []
        
        return [
            SearchResponse(doc_id=doc_id, score=float(score))
            for doc_id, score in results[:request.top_k]
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.post("/search/semantic", response_model=List[SearchResponse])
async def semantic_search_endpoint(request: SearchRequest):
    """
    Semantic search: Returns documents with similar meaning using GloVe embeddings.
    """
    try:
        query = request.query.strip().lower()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get preloaded data
        glove = search_engine.get_glove()
        embeddings = search_engine.get_embeddings()
        
        results = semantic_search_query(
            query,
            top_k=request.top_k,
            glove=glove,
            preloaded_embeddings=embeddings
        )
        
        if not results:
            return []
        
        return [
            SearchResponse(doc_id=doc_id, score=float(score))
            for doc_id, score in results
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search error: {str(e)}")


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete_endpoint(request: AutocompleteRequest):
    """
    Autocomplete: Returns word suggestions based on prefix.
    """
    try:
        prefix = request.prefix.strip().lower()
        if not prefix:
            raise HTTPException(status_code=400, detail="Prefix cannot be empty")
        
        suggestions = autocomplete_words(prefix, top_n=request.top_n)
        
        return AutocompleteResponse(suggestions=suggestions)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocomplete error: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    Get search engine statistics.
    """
    try:
        lexicon = search_engine.get_lexicon()
        embeddings = search_engine.get_embeddings()
        glove = search_engine.get_glove()
        
        return {
            "total_words": lexicon.size(),
            "total_documents": len(embeddings),
            "glove_vectors": len(glove),
            "status": "operational"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@router.get("/document/{doc_id}")
async def get_document(doc_id: str):
    """
    Get document details by ID.
    """
    import json
    from pathlib import Path
    
    try:
        # Try to find the document in sample_data
        base_dir = Path(__file__).parent.parent.parent / "sample_data"
        doc_file = base_dir / f"{doc_id}.json"
        
        if not doc_file.exists():
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract relevant fields
        title = data.get("metadata", {}).get("title", "No title")
        
        # Extract abstract
        abstract_parts = data.get("abstract", [])
        if isinstance(abstract_parts, list):
            abstract = " ".join([part.get("text", "") for part in abstract_parts if isinstance(part, dict)])
        else:
            abstract = str(abstract_parts) if abstract_parts else ""
        
        return {
            "doc_id": doc_id,
            "paper_id": data.get("paper_id", doc_id),
            "title": title,
            "abstract": abstract[:500] if abstract else "No abstract available"  # Limit to 500 chars
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")
