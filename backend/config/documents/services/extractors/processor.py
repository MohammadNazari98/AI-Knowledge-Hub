from .pdf import PDFExtractor
from .txt import TXTExtractor
from documents.services.exceptions import DocumentProcessingError
from documents.models import Document, DocumentChunk
from documents.services.validators import FileValidator
from documents.services.chunking import TextChunker
from documents.services.embedding import EmbeddingService
from django.db import transaction



class DocumentProcessor:
    """Coordinate document text extraction."""
    def __init__(self, embedding_service=None):
        self.extractors = {
            "pdf": PDFExtractor(),
            "txt": TXTExtractor()
        }
        self.validator = FileValidator()
        self.embedding_service = (
            embedding_service if embedding_service is not None else EmbeddingService()
        )
        
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
        
        text_chunker = TextChunker()
        chunks = text_chunker.split_text(result)
        
        with transaction.atomic():
            DocumentChunk.objects.filter(document=document).delete()
            DocumentChunk.objects.bulk_create([
                DocumentChunk(
                    document=document,
                    content=chunk,
                    embedding=self.embedding_service.get_embedding(chunk).squeeze(0).tolist(),
                    index=i
                )
                for i, chunk in enumerate(chunks)
            ])
            
        return document.content