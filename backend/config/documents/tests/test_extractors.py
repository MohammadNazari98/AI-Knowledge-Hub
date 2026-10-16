from io import BytesIO
from documents.services.extractors.base import TextExtractor
from documents.services.extractors.txt import TXTExtractor
from documents.services.extractors.pdf import PDFExtractor
from reportlab.pdfgen import canvas 
from documents.services.exceptions import DocumentProcessingError
import pytest



class FakeTextExtractor:
    def extract(self, file: BytesIO) -> str:
        return file.read().decode("utf-8")

def test_fake_extractor_satisfies_text_generator_contract():
    extractor: TextExtractor = FakeTextExtractor()
    result = extractor.extract(BytesIO("سلام دنیا".encode("utf-8")))
    
    assert result == "سلام دنیا"
    
def test_text_extractor_return_text_as_string():
    extractor: TextExtractor = FakeTextExtractor()
    
    result = extractor.extract(BytesIO(b"AI Knowledge Hub"))
    
    assert isinstance(result, str)
    
def test_txt_extractor_returns_text():
    extractor = TXTExtractor()
    file = BytesIO("سلام دنیا".encode("utf-8"))
    
    result = extractor.extract(file)
    assert result == "سلام دنیا"
    assert isinstance(result, str)
    
def test_txt_extractor_handles_utf8_bom():
    extractor = TXTExtractor()
    file = BytesIO(b"\xef\xbb\xbfAI Knowledge Hub")
    
    result = extractor.extract(file)
    assert result == "AI Knowledge Hub"
    assert isinstance(result, str)
    
def test_pdf_extractor_returns_text_from_pdf():
    pdf_file = BytesIO()
    pdf = canvas.Canvas(pdf_file)
    pdf.drawString(50, 250, "AI Knowledge Hub")
    pdf.save()
    
    pdf_file.seek(0)

    extractor = PDFExtractor()
    result = extractor.extract(pdf_file)
    
    assert isinstance(result, str)
    assert "AI Knowledge Hub" in result
    
def test_pdf_extractor_raises_error_for_invalid_pdf():
    extractor = PDFExtractor()
    invalid_file = BytesIO(b"This is not a pdf file.")
    
    with pytest.raises(DocumentProcessingError):
        extractor.extract(invalid_file)
