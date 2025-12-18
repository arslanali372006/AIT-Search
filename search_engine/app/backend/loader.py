# app/backend/loader.py
"""
Lazy-loading search engine for optimal performance.
"""
import sys
import os
import numpy as np
from pathlib import Path

# Add src directory to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from semantic import load_glove  # type: ignore
from lexicon import lexicon  # type: ignore
from barrels import barrel_manager  # type: ignore

class SearchEngineLoader:
    """
    Fast lazy-loading search engine - loads embeddings on-demand.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SearchEngineLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        print("🚀 Initializing Search Engine (Fast Mode)...")
        
        # Load lexicon (fast)
        print("📖 Loading lexicon...")
        lexicon.load()
        print(f"✅ Lexicon loaded: {lexicon.size()} words")
        
        # Load GloVe embeddings (needed for semantic search)
        print("🧠 Loading GloVe embeddings...")
        self.glove = load_glove()
        print(f"✅ GloVe loaded: {len(self.glove)} word vectors")
        
        # Use lazy loading for document embeddings
        self.embeddings_dir = Path(__file__).parent.parent.parent / "data" / "embeddings"
        self.embeddings_cache = {}  # Cache for loaded embeddings
        if self.embeddings_dir.exists():
            doc_count = len(list(self.embeddings_dir.glob("*.npy")))
            print(f"📁 Found {doc_count} document embeddings (will load on-demand)")
        else:
            print(f"⚠️  No embeddings found at {self.embeddings_dir}")
            print(f"   Run 'python src/main.py' to build embeddings for all documents")
        
        # Store references
        self.lexicon = lexicon
        self.barrel_manager = barrel_manager
        
        self._initialized = True
        print("✅ Search Engine ready! (startup time: <5 seconds)\n")
    
    def get_glove(self):
        return self.glove
    
    def get_embedding(self, doc_id: str):
        """Load embedding on-demand and cache it"""
        if doc_id in self.embeddings_cache:
            return self.embeddings_cache[doc_id]
        
        # Load from disk
        embedding_path = self.embeddings_dir / f"{doc_id}.npy"
        if embedding_path.exists():
            embedding = np.load(str(embedding_path))
            self.embeddings_cache[doc_id] = embedding
            return embedding
        return None
    
    def get_all_doc_ids(self):
        """Get list of all document IDs (fast - just filenames)"""
        return [f.stem for f in self.embeddings_dir.glob("*.npy")]
    
    def get_embeddings(self):
        """Legacy method - returns cached embeddings"""
        return self.embeddings_cache
    
    def get_lexicon(self):
        return self.lexicon
    
    def get_barrel_manager(self):
        return self.barrel_manager
    
    def get_total_documents(self):
        """Count total documents dynamically"""
        return len(list(self.embeddings_dir.glob("*.npy")))


# Global instance
search_engine = SearchEngineLoader()
