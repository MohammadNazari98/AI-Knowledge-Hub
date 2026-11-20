from typing import BinaryIO
from pypdf import PdfReader
from documents.services.exceptions import DocumentProcessingError
from pypdf.errors import PdfReadError, PdfStreamError



class PDFExtractor:
    """extract text from pdf files."""
    def extract(self, file: BinaryIO) -> str:
        try:
            reader = PdfReader(file)
            pages_text = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
                    
            return "\n".join(pages_text)
        except (PdfStreamError, PdfReadError, OSError, ValueError) as exc:
            raise DocumentProcessingError("Unable to extract text from the pdf file.") from exc