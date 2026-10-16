from .pdf import PDFExtractor
from .txt import TXTExtractor
from documents.services.exceptions import DocumentProcessingError
from documents.models import Document



class DocumentProcessor:
    """Coordinate document text extraction."""
    def __init__(self):
        self.extractors = {
            "pdf": PDFExtractor(),
            "txt": TXTExtractor()
        }
        
    def process(self, document: Document)->str:
        file_type = document.file_type.lower()
        extractor = self.extractors.get(file_type)
        
        if extractor is None:
            raise DocumentProcessingError(f"Unsupported document type: {file_type}")
        
        return extractor.extract(document.file)