import pytest
from documents.services.validators import FileValidator
from documents.services.exceptions import DocumentProcessingError
from django.core.files.uploadedfile import SimpleUploadedFile



@pytest.mark.parametrize(
    "filename",
    ["report.txt",
    "report.pdf",
    "python.pdf",
    "test.txt",
    "REPORT.PDF",
    "Notepad.TXT"]
)
def test_validate_extension_accepts_supported_extensions(filename):    
    assert FileValidator().validate_extension(filename)
    
@pytest.mark.parametrize(
    "filename",
    ["image.png",
    "malware.exe",
    "clickme.apk",
    "readme",
    "README"
    ".report"]
)
def test_validate_file_invalid_and_raise_error_validation(filename):
    with pytest.raises(DocumentProcessingError):
        FileValidator().validate_extension(filename)
        
@pytest.mark.parametrize("file_size",[10*1024*1024, 5*1024*1024, 0, 9*1024*1024])
def test_validate_file_size_valid_accepted_file_size(file_size):
    assert FileValidator().validate_size(file_size)
    
@pytest.mark.parametrize("file_size", [1+10*1024*1024, 20*1024*1024])
def test_validate_file_size_invalid_and_raise_error_validation(file_size):
    with pytest.raises(DocumentProcessingError):
        assert FileValidator().validate_size(file_size)
        
        
def test_validates_file_uploaded_and_must_validate_valid_correctly():
    file_upload = SimpleUploadedFile("file_uploaded_test.txt", b"this is a test.")
    
    file_validator = FileValidator()
    
    assert file_validator.validate(file_upload)
    
def test_validates_file_uploaded_invalid_and_must_raise_error():
    file_upload_invalid = SimpleUploadedFile("file_uploaded_test.exe", b"this is a test.")
    
    file_validator = FileValidator()
    
    with pytest.raises(DocumentProcessingError):
        file_validator.validate(file_upload_invalid)
        
def test_rejects_pdf_with_invalid_content():
    file_upload = SimpleUploadedFile(
        "malware.pdf",
        b"This is not a PDF"
    )
    with pytest.raises(DocumentProcessingError):
        FileValidator().validate(file_upload)