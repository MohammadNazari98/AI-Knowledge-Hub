from pathlib import Path
from documents.models import Document
from .exceptions import DocumentProcessingError
from django.core.files.uploadedfile import UploadedFile



class FileValidator:
    
    MAX_FILE_SIZE = 10 * 2 ** 20
    
    def validate_extension(self, filename: str) -> bool:
        allowed_extension = Document.FileType.values
        extension = Path(filename).suffix.strip(".").lower()
        if extension not in allowed_extension:
            raise DocumentProcessingError(f"Error {filename} doesn't match extensions such as txt and pdf")
        
        return True
    
    def validate_size(self, file_size: int) -> bool:                
        if file_size > self.MAX_FILE_SIZE:
            raise DocumentProcessingError(f"Error {file_size}, cannot accepted because must be lower than <10MB.")
        return True
    
    def validate_content(self, file: UploadedFile) -> bool:
        extension = Path(file.name).suffix.strip(".").lower()
        if extension == "pdf":
            file.seek(0)
            signature = file.read(5)
            file.seek(0)
            if signature != b"%PDF-":
                raise DocumentProcessingError(f"Error, Invalid PDF file content.")
        elif extension == "txt":
            file.seek(0)
            content = file.read()
            try:
                content.decode("utf-8-sig")
            except UnicodeDecodeError as exc:
                raise DocumentProcessingError(
                    "Invalid TXT file encoding."
                ) from exc
            finally:
                file.seek(0)
        return True
                
    def validate(self, file: UploadedFile) -> bool:
        self.validate_extension(file.name)
        self.validate_size(file.size)
        self.validate_content(file)
        return True