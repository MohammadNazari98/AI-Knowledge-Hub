from .pdf import PDFExtractor
from .txt import TXTExtractor
from documents.services.exceptions import DocumentProcessingError
from documents.models import Document
from documents.services.validators import FileValidator



class DocumentProcessor:
    """Coordinate document text extraction."""
    def __init__(self):
        self.extractors = {
            "pdf": PDFExtractor(),
            "txt": TXTExtractor()
        }
        self.validator = FileValidator()
        
    def process(self, document: Document)->str:
        try:
            file_type = document.file_type.lower()
            extractor = self.extractors.get(file_type)
            
            if extractor is None:
                raise DocumentProcessingError(f"Unsupported document type: {file_type}")
            
            self.validator.validate(document.file)
            
            document.status = Document.Status.PROCESSING
            document.save()
            
            result = extractor.extract(document.file)
            
        except DocumentProcessingError as exc:
            document.status = Document.Status.FAILED
            document.content = ''
            document.save()
            raise DocumentProcessingError(
                f"Failed to extract text from document: {exc}"
            ) from exc
        
        document.content = result
        document.status = Document.Status.PROCESSED
        document.save()
        return document.content