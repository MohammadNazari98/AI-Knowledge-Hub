from typing import List




class TextChunker:
    """Split text into overlapping character-based chunks."""
    
    def __init__(self, chunk_size: int = 300, chunk_overlap=50):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")
        
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")
        
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        
    def split_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
        
        chunks = []
        step = self.chunk_size - self.chunk_overlap
        
        for start in range(0, len(text), step):
            chunk = text[start: start+self.chunk_size]
            
            if chunk.strip():
                chunks.append(chunk)
                
            if start + self.chunk_size >= len(text):
                break
            
        return chunks