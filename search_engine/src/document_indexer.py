# src/document_indexer.py
"""
Dynamic document indexer for adding new documents to the search engine.
Handles indexing without blocking search operations.
"""
import json
import os
from typing import Dict, List
from datetime import datetime
import numpy as np

from tokenizer_module import Tokenizer
from lexicon import lexicon
from barrels import barrel_manager


class DocumentIndexer:
    """
    Handles dynamic indexing of new documents.
    Updates lexicon, forward index, barrels, and embeddings.
    """
    
    def __init__(self):
        self.tokenizer = Tokenizer(remove_stopwords=True)
        self.base_dir = os.path.dirname(__file__)
        self.data_dir = os.path.join(self.base_dir, "..", "sample_data")
        self.tokenized_dir = os.path.join(self.base_dir, "..", "data", "tokenized")
        self.embeddings_dir = os.path.join(self.base_dir, "..", "data", "embeddings")
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.tokenized_dir, exist_ok=True)
        os.makedirs(self.embeddings_dir, exist_ok=True)
    
    def extract_text(self, field):
        """Extract text from various field formats."""
        if isinstance(field, str):
            return field
        if isinstance(field, list):
            return " ".join([item.get("text", "") for item in field if isinstance(item, dict)])
        return ""
    
    def generate_doc_id(self) -> str:
        """Generate a unique document ID."""
        # Find the highest existing doc_X.json number
        existing_docs = [f for f in os.listdir(self.data_dir) if f.startswith("doc_") and f.endswith(".json")]
        
        if not existing_docs:
            return "doc_1"
        
        # Extract numbers and find max
        numbers = []
        for doc in existing_docs:
            try:
                num = int(doc.replace("doc_", "").replace(".json", ""))
                numbers.append(num)
            except ValueError:
                continue
        
        next_num = max(numbers) + 1 if numbers else 1
        return f"doc_{next_num}"
    
    def save_document(self, doc_data: Dict, doc_id: str = None) -> str:
        """Save document to sample_data directory."""
        if not doc_id:
            doc_id = self.generate_doc_id()
        
        # Save to sample_data
        doc_path = os.path.join(self.data_dir, f"{doc_id}.json")
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2)
        
        return doc_id
    
    def tokenize_document(self, doc_data: Dict, doc_id: str) -> List[str]:
        """Tokenize document and save tokens."""
        # Extract text from document
        title = self.extract_text(doc_data.get("metadata", {}).get("title", ""))
        abstract = self.extract_text(doc_data.get("abstract", []))
        body = self.extract_text(doc_data.get("body_text", []))
        
        full_text = " ".join([title, abstract, body])
        
        # Tokenize
        tokens = self.tokenizer.tokenize(full_text)
        
        # Save tokenized document
        tokenized_path = os.path.join(self.tokenized_dir, f"{doc_id}.json")
        with open(tokenized_path, 'w', encoding='utf-8') as f:
            json.dump({"tokens": tokens}, f, indent=2)
        
        return tokens
    
    def update_lexicon(self, tokens: List[str]) -> Dict[str, int]:
        """Update lexicon with new words and return word IDs."""
        word_ids = {}
        new_words = []
        
        for token in tokens:
            # Check if word already exists
            word_id = lexicon.get_id(token)
            
            if word_id == 0:  # New word
                # Add to lexicon
                new_word_id = lexicon._next_id
                lexicon.word_to_id[token] = new_word_id
                lexicon.id_to_word[new_word_id] = token
                lexicon._next_id += 1
                word_ids[token] = new_word_id
                new_words.append(token)
            else:
                word_ids[token] = word_id
        
        # Save updated lexicon if there are new words
        if new_words:
            lexicon.save()
            print(f"Added {len(new_words)} new words to lexicon")
        
        return word_ids
    
    def update_barrels(self, doc_id: str, tokens: List[str], word_ids: Dict[str, int]):
        """Update barrels with new document."""
        # Count word positions
        word_positions = {}
        for position, token in enumerate(tokens):
            if token not in word_positions:
                word_positions[token] = []
            word_positions[token].append(position)
        
        # Update barrels
        failed_updates = 0
        for token, positions in word_positions.items():
            word_id = word_ids.get(token)
            if word_id:
                try:
                    # Get barrel for this word
                    barrel_id = barrel_manager.get_barrel_id(word_id)
                    barrel_data = barrel_manager.load_barrel(barrel_id)
                    
                    # Check if word exists and convert old format to new if needed
                    if word_id not in barrel_data:
                        # New word - use dict format
                        barrel_data[word_id] = {}
                    elif isinstance(barrel_data[word_id], list):
                        # Old format (list of doc IDs) - convert to dict format
                        old_docs = barrel_data[word_id]
                        barrel_data[word_id] = {doc: [] for doc in old_docs}
                    
                    # Add document with positions
                    barrel_data[word_id][doc_id] = positions
                    
                    # Save barrel
                    barrel_manager.save_barrel(barrel_id, barrel_data)
                except Exception as e:
                    print(f"⚠️  Failed to update barrel for word '{token}': {str(e)[:100]}")
                    failed_updates += 1
        
        if failed_updates > 0:
            print(f"⚠️  {failed_updates} barrel updates failed, but document was added")
        print(f"Updated barrels with {len(word_positions) - failed_updates}/{len(word_positions)} unique words")
    
    def generate_embedding(self, doc_id: str, tokens: List[str], glove_embeddings) -> bool:
        """Generate and save document embedding."""
        try:
            # Get vectors for tokens that exist in GloVe
            vectors = [glove_embeddings[t] for t in tokens if t in glove_embeddings]
            
            if not vectors:
                print(f"Warning: No GloVe vectors found for document tokens")
                return False
            
            # Average the vectors
            doc_vector = np.mean(vectors, axis=0)
            
            # Save embedding
            embedding_path = os.path.join(self.embeddings_dir, f"{doc_id}.npy")
            np.save(embedding_path, doc_vector)
            
            return True
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return False
    
    def index_document(self, doc_data: Dict, doc_id: str = None, glove_embeddings=None) -> Dict:
        """
        Index a new document completely.
        Returns status information.
        """
        start_time = datetime.now()
        
        try:
            # 1. Save document
            doc_id = self.save_document(doc_data, doc_id)
            print(f"Saved document: {doc_id}")
            
            # 2. Tokenize
            tokens = self.tokenize_document(doc_data, doc_id)
            print(f"Tokenized: {len(tokens)} tokens")
            
            # 3. Update lexicon
            word_ids = self.update_lexicon(tokens)
            
            # 4. Update barrels (inverted index)
            self.update_barrels(doc_id, tokens, word_ids)
            
            # 5. Generate embedding if GloVe is provided
            embedding_created = False
            if glove_embeddings:
                embedding_created = self.generate_embedding(doc_id, tokens, glove_embeddings)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "doc_id": doc_id,
                "tokens_count": len(tokens),
                "unique_words": len(set(tokens)),
                "new_words_added": len([t for t in tokens if lexicon.get_id(t) > 0]),
                "embedding_created": embedding_created,
                "indexing_time": duration,
                "message": f"Document indexed successfully in {duration:.2f} seconds"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to index document: {str(e)}"
            }


# Global indexer instance
document_indexer = DocumentIndexer()
