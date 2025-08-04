"""Vector store for document storage and retrieval."""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from collections import defaultdict

from ..config import settings


class VectorStore:
    """Manages document vector storage and retrieval."""
    
    def __init__(self):
        """Initialize the vector store with ChromaDB."""
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        self.client = chromadb.Client(Settings(
            persist_directory=settings.VECTOR_STORE_PATH,
            anonymized_telemetry=False
        ))
        
        self.collection = self.client.get_or_create_collection(
            name="sec_filings",
            embedding_function=self.embedding_function
        )
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Add processed documents to the vector store."""
        if not documents:
            return
            
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        ids = [f"{doc['metadata']['filing_id']}_{doc['metadata'].get('chunk_index', 0)}" for doc in documents]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(
        self,
        query: str,
        filter_metadata: Optional[Dict] = None,
        limit: int = 5
    ) -> Dict:
        """Enhanced search with filtering and deduplication."""
        where = self._build_where_clause(filter_metadata)
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit * 2,  # Get more results for filtering
            where=where
        )
        
        # Process and deduplicate results
        processed_results = self._process_results(results, limit)
        
        return processed_results
    
    def _build_where_clause(self, filter_metadata: Optional[Dict]) -> Optional[Dict]:
        """Build ChromaDB where clause from filter metadata."""
        if not filter_metadata:
            return None
            
        conditions = []
        
        for key, value in filter_metadata.items():
            if isinstance(value, dict) and "$in" in value:
                # Handle $in operator
                conditions.append({
                    "$or": [
                        {key: v} for v in value["$in"]
                    ]
                })
            else:
                conditions.append({key: value})
        
        if len(conditions) == 1:
            return conditions[0]
        
        return {"$and": conditions}
    
    def _process_results(
        self,
        results: Dict,
        limit: int
    ) -> Dict:
        """Process and deduplicate search results."""
        if not results['documents'] or not results['documents'][0]:
            return {"documents": [[]], "metadatas": [[]]}
        
        # Combine results and deduplicate
        processed = []
        seen_contents = set()
        
        for doc, metadata in zip(
            results['documents'][0],
            results['metadatas'][0]
        ):
            # Use first 100 chars as signature for deduplication
            content_sig = doc[:100]
            if content_sig not in seen_contents:
                seen_contents.add(content_sig)
                
                # Parse metrics from strings if present
                if metadata.get('has_metrics') == 'true':
                    currency_amounts = [float(x) for x in metadata.get('currency_amounts', '').split(',') if x]
                    percentages = [float(x) for x in metadata.get('percentages', '').split(',') if x]
                    metadata['metrics_summary'] = f"Found {len(currency_amounts)} currency amounts and {len(percentages)} percentage values"
                
                processed.append((doc, metadata))
                
            if len(processed) >= limit:
                break
        
        # Unzip processed results
        docs, metas = zip(*processed) if processed else ([], [])
        
        return {
            "documents": [list(docs)],
            "metadatas": [list(metas)]
        }
