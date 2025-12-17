# app/backend/loader.py
"""
Preload all search engine data at startup for fast API responses.
"""
import sys
import os

# Add src directory to path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from semantic import load_all_embeddings, load_glove  # type: ignore
from lexicon import lexicon  # type: ignore
from barrels import barrel_manager  # type: ignore

class SearchEngineLoader:
    """
    Singleton class to load and hold all search engine data in memory.
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
            
        print("🚀 Initializing Search Engine...")
        
        # Load lexicon
        print("📖 Loading lexicon...")
        lexicon.load()
        print(f"✅ Lexicon loaded: {lexicon.size()} words")
        
        # Load GloVe embeddings
        print("🧠 Loading GloVe embeddings (this may take a while)...")
        self.glove = load_glove()
        print(f"✅ GloVe loaded: {len(self.glove)} word vectors")
        
        # Load document embeddings
        print("📚 Loading document embeddings...")
        self.embeddings = load_all_embeddings()
        print(f"✅ Document embeddings loaded: {len(self.embeddings)} documents")
        
        # Store references
        self.lexicon = lexicon
        self.barrel_manager = barrel_manager
        
        self._initialized = True
        print("✅ Search Engine ready!\n")
    
    def get_glove(self):
        return self.glove
    
    def get_embeddings(self):
        return self.embeddings
    
    def get_lexicon(self):
        return self.lexicon
    
    def get_barrel_manager(self):
        return self.barrel_manager


# Global instance
search_engine = SearchEngineLoader()
