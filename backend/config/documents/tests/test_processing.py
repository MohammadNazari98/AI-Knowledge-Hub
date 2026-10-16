import pytest
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.services.extractors.processor import DocumentProcessor
from io import BytesIO
from reportlab.pdfgen import canvas
from documents.services.exceptions import DocumentProcessingError
from types import SimpleNamespace



@pytest.mark.django_db    
def test_text_extractor_processes_when_retrieves_txt_file_and_return_str_text_correctly():
    user = User.objects.create_user(username="usertestA", password="passwordtestA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user)
    knowledge_base = KnowledgeBase.objects.create(name="Python AI", workspace=workspace, created_by=user)
    uploaded_file = SimpleUploadedFile("test_file.txt", content=b"Hello world!")
    document = Document.objects.create(title="python expert", knowledge_base=knowledge_base, file=uploaded_file, file_type=Document.FileType.TXT, created_by=user)
    
    document_processor = DocumentProcessor()
    text_extracted = document_processor.process(document=document)
    
    assert text_extracted == "Hello world!"
    
@pytest.mark.django_db
def test_text_extractor_processes_when_retrieves_pdf_file_and_return_str_text_correctly():
    user = User.objects.create_user(username="usertestA", password="passwordtestA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user)
    knowledge_base = KnowledgeBase.objects.create(name="Python AI", workspace=workspace, created_by=user)
    pdf_file = BytesIO()
    pdf = canvas.Canvas(pdf_file)
    pdf.drawString(50, 250, "This is a text pdf.")
    pdf.save()
    pdf_file.seek(0)
    file_uploaded = SimpleUploadedFile(name="python_expert.pdf", content=pdf_file.getvalue())
    document = Document.objects.create(title="python expert", 
                                    knowledge_base=knowledge_base,
                                    file=file_uploaded,
                                    file_type=Document.FileType.PDF,
                                    created_by=user)
    
    document_processor = DocumentProcessor()
    text_extracted = document_processor.process(document=document)
    
    assert text_extracted == "This is a text pdf.\n"
    
def test_text_extractor_processes_when_retrieves_file_unsupported_and_return_error_correctly():
    document = SimpleNamespace(file_type="malware")
    document_processor = DocumentProcessor()
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document=document)