import pytest
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document, DocumentChunk
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.services.extractors.processor import DocumentProcessor
from documents.services.validators import FileValidator
from io import BytesIO
from reportlab.pdfgen import canvas
from documents.services.exceptions import DocumentProcessingError
from types import SimpleNamespace
from unittest.mock import Mock, patch
import torch



class FakeEmbeddingService:
    def get_embedding(self, text, prefix="passage: "):
        assert text.strip()
        assert prefix == "passage: "
        return torch.Tensor([[0.1] * 384])

@pytest.fixture
def fake_embedding_service():
    return FakeEmbeddingService()

@pytest.fixture(autouse=True)
def mock_embedding_service(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        "documents.services.extractors.processor.EmbeddingService",
        FakeEmbeddingService,
    )
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
    document = SimpleNamespace(file_type="malware", file="malware", save=Mock())
    document_processor = DocumentProcessor()
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document=document)

@pytest.mark.django_db
def test_file_type_by_using_mock():
    document_processor = DocumentProcessor()
    
    extractor = Mock()
    
    extractor.extract.return_value = "Hello from mock"
    
    document_processor.extractors["txt"] = extractor
    
    document_processor.validator = Mock()
    
    with patch(
        "documents.services.extractors.processor.DocumentChunk.objects.filter"
    ) as mock_filter, patch(
        "documents.services.extractors.processor.DocumentChunk.objects.bulk_create"
    ) as mock_bulk_create, patch(
        "documents.services.extractors.processor.DocumentChunk"
    ) as mock_chunk:
        mock_filter.return_value.delete.return_value = (0, {})

        document = SimpleNamespace(file_type="txt", file="fake file", save=Mock())
    
        result = document_processor.process(document=document)
    
    assert result == "Hello from mock"
    extractor.extract.assert_called_once_with("fake file")
    
def test_file_type_raise_error_by_using_mock():
    document_processor = DocumentProcessor()
    extractor = Mock()
    extractor.extract.side_effect = DocumentProcessingError()
    
    document_processor.extractors["txt"] = extractor
    
    document_processor.validator = Mock()
    
    document = SimpleNamespace(file_type="txt", file="malware", save=Mock())
    
    with pytest.raises(DocumentProcessingError):        
        document_processor.process(document=document)
    extractor.extract.assert_called_once_with(document.file)
    
@pytest.mark.django_db
def test_text_extractor_processes_when_retrieves_txt_file_and_save_to_database_correctly():
    user = User.objects.create_user(username="usertestA", password="passwordtestA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user)
    knowledge_base = KnowledgeBase.objects.create(name="Python AI", workspace=workspace, created_by=user)
    file = BytesIO(b"Hello, This is a text file.")
    txt_file = SimpleUploadedFile("test_file.txt", content=file.getvalue())
    document = Document.objects.create(title="python expert", knowledge_base=knowledge_base, file=txt_file, file_type=Document.FileType.TXT, created_by=user)
    
    document_processor = DocumentProcessor()
    extractor = Mock()
    extractor.extract.return_value = "Hello, This is a text file."
    document_processor.extractors["txt"] = extractor
    document_processor.process(document=document)
    document.refresh_from_db()
    assert document.content == "Hello, This is a text file."
    assert document.status == document.Status.PROCESSED

@pytest.mark.django_db
def test_text_extractor_processes_when_retrieves_pdf_file_and_save_to_database_correctly():
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
    extractor = Mock()
    extractor.extract.return_value = "This is a text pdf."
    document_processor.extractors["pdf"] = extractor
    document_processor.process(document=document)
    
    document.refresh_from_db()
    
    assert document.content == "This is a text pdf."
    assert document.status == document.Status.PROCESSED
    
def test_text_extractor_processes_when_retrieves_file_unsupported_and_save_to_database_correctly():
    document_processor = DocumentProcessor()
    extractor = Mock()
    extractor.extract.side_effect = DocumentProcessingError()
    
    document_processor.validator = Mock()
    
    document = SimpleNamespace(file_type="txt", file="malware", save=Mock())
    document_processor.extractors["txt"] = extractor
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document=document)
    
    extractor.extract.assert_called_once_with(document.file)
    assert document.status == Document.Status.FAILED
    assert document.content == ''
    
@pytest.mark.django_db
def test_document_processor_sets_failed_status_in_database_when_extraction_fails():
    user = User.objects.create_user(username="usertestA", password="passwordtestA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user)
    knowledge_base = KnowledgeBase.objects.create(name="Python AI", workspace=workspace, created_by=user)
    txt_file = BytesIO(b"This is a text file.")    
    file_uploaded = SimpleUploadedFile(name="test_file.pdf", content=txt_file.getvalue())
    document = Document.objects.create(title="python expert", 
                                    knowledge_base=knowledge_base,
                                    file=file_uploaded,
                                    file_type=Document.FileType.PDF,
                                    created_by=user)
    
    document_processor = DocumentProcessor()
    
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document=document)
    
    document.refresh_from_db()
    
    assert document.status == Document.Status.FAILED
    assert document.content == ''
    
@pytest.mark.django_db
def test_document_processor_sets_processing_status_in_database_when_extract_file_pdf():
    user = User.objects.create_user(username="usertestA", password="passwordtestA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user)
    knowledge_base = KnowledgeBase.objects.create(
        name="Python AI",
        workspace=workspace,
        created_by=user,
    )

    pdf_file = BytesIO()
    pdf = canvas.Canvas(pdf_file)
    pdf.drawString(50, 250, "This is a test PDF file.")
    pdf.save()
    pdf_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="test_file.pdf",
        content=pdf_file.getvalue(),
    )

    document = Document.objects.create(
        title="python expert",
        knowledge_base=knowledge_base,
        file=uploaded_file,
        file_type=Document.FileType.PDF,
        created_by=user,
    )

    document_processor = DocumentProcessor()
    extractor = Mock()

    def extract_and_check_status(file):
        document.refresh_from_db()
        assert document.status == Document.Status.PROCESSING
        return "This is a test PDF file.\n"

    extractor.extract.side_effect = extract_and_check_status
    document_processor.extractors["pdf"] = extractor

    result = document_processor.process(document)

    document.refresh_from_db()

    assert result == "This is a test PDF file.\n"
    assert document.status == Document.Status.PROCESSED
    extractor.extract.assert_called_once_with(document.file)
    
    
@pytest.mark.django_db
def test_document_processor_saves_empty_content_for_pdf_without_text():
    user = User.objects.create_user(
        username="empty_pdf_user",
        password="passwordtestA",
    )
    workspace = Workspace.objects.create(name="Empty PDF Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="Empty PDF Knowledge Base",
        workspace=workspace,
        created_by=user,
    )

    pdf_file = BytesIO()
    pdf = canvas.Canvas(pdf_file)
    pdf.save()
    pdf_file.seek(0)

    uploaded_file = SimpleUploadedFile(
        name="empty.pdf",
        content=pdf_file.getvalue(),
    )

    document = Document.objects.create(
        title="Empty PDF",
        knowledge_base=knowledge_base,
        file=uploaded_file,
        file_type=Document.FileType.PDF,
        created_by=user,
    )

    processor = DocumentProcessor()
    result = processor.process(document)

    document.refresh_from_db()

    assert result == ""
    assert document.content == ""
    assert document.status == Document.Status.PROCESSED
    
@pytest.mark.django_db
def test_document_processor_rejects_pdf_with_invalid_content():
    user = User.objects.create_user(
            username="empty_pdf_user",
            password="passwordtestA",
        )
    workspace = Workspace.objects.create(name="Empty PDF Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="Empty PDF Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    uploaded_file = SimpleUploadedFile("malware.pdf", b"This is not a pdf", content_type="application/pdf")
    
    document = Document.objects.create(title="HACKED",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.PDF,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document)
        
    document.refresh_from_db()
    
    assert document.status == Document.Status.FAILED
    assert document.content == ''
    
    
@pytest.mark.django_db
def test_document_processor_does_not_extract_invalid_pdf():
    user = User.objects.create_user(
                username="invaliduserA",
                password="passwordtestA",
            )
    workspace = Workspace.objects.create(name="Invalid PDF Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="Invalid PDF Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    uploaded_file = SimpleUploadedFile("malware.pdf", b"This is not a real pdf file", content_type="application/pdf")
    
    document = Document.objects.create(title="Invalid PDF",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.PDF,
            created_by=user)
    
    document_processor = DocumentProcessor()
    extractor = Mock()
    document_processor.extractors["pdf"] = extractor
    with pytest.raises(DocumentProcessingError):
        document_processor.process(document)
        
    document.refresh_from_db()
    assert document.status == Document.Status.FAILED
    assert document.content == ''
    extractor.extract.assert_not_called()
    
@pytest.mark.django_db
def test_document_processor_does_not_extract_oversized_txt():
    user = User.objects.create_user(
                    username="testuserA",
                    password="passwordtestA",
                )
    workspace = Workspace.objects.create(name="test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    oversized_content = b'A'*(FileValidator.MAX_FILE_SIZE+1)
    uploaded_file = SimpleUploadedFile("malware.txt",oversized_content)
    
    document = Document.objects.create(title="test deep learning",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    extractor = Mock()
    
    document_processor.extractors["txt"] = extractor
    
    with pytest.raises(DocumentProcessingError): 
        document_processor.process(document)
        
    assert document.status == Document.Status.FAILED
    assert document.content == ''
    extractor.extract.assert_not_called()

@pytest.mark.django_db
def test_validate_content_rejects_invalid_txt_encoding():
    user = User.objects.create_user(
                        username="testuserA",
                        password="passwordtestA",
                    )
    workspace = Workspace.objects.create(name="test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    
    uploaded_file = SimpleUploadedFile("test.txt",b"\xff\xfe\xfa")
    
    document = Document.objects.create(title="test deep learning",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    with pytest.raises(DocumentProcessingError, match="Invalid TXT file encoding"):
        document_processor.process(document=document)

@pytest.mark.django_db
def test_document_processor_saves_chunks_after_successful_processing():
    user = User.objects.create_user(
                            username="testuserA",
                            password="passwordtestA",
                        )
    workspace = Workspace.objects.create(name="test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    uploaded_file = SimpleUploadedFile("test.txt",b"This is a text file for integration testing")
    
    document = Document.objects.create(title="test deep learning",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    result = document_processor.process(document=document)
    
    document.refresh_from_db()
    chunks = list(document.chunks.all())
    
    assert document.status == Document.Status.PROCESSED
    assert result == "This is a text file for integration testing"
    assert document.chunks.count() > 0
    assert [chunk.index for chunk in chunks ] == list(range(len(chunks)))
    assert "".join(
        chunk.content for chunk in chunks
    )[:len("This is a text file for integration testing")] == "This is a text file for integration testing"
    
    
@pytest.mark.django_db
def test_document_processor_replaces_existing_chunks_when_reprocessed():
    user = User.objects.create_user(
                                username="testuserA",
                                password="passwordtestA",
                            )
    workspace = Workspace.objects.create(name="test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    uploaded_file = SimpleUploadedFile("test.txt",b"This is a text file for integration testing")
    
    document = Document.objects.create(title="test deep learning",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    result = document_processor.process(document=document)
    
    document.refresh_from_db()
    
    first_chunks = list(document.chunks.all())
    first_count = len(first_chunks)
    first_contents = [chunk.content for chunk in first_chunks]
    first_chunks_indices = [chunk.index for chunk in DocumentChunk.objects.filter(document=document)]
    
    result_2 = document_processor.process(document=document)
    
    document.refresh_from_db()
    
    second_chunks = list(document.chunks.all())
    second_count = len(second_chunks)
    second_contents = [chunk.content for chunk in second_chunks]
    second_chunks_indices = [chunk.index for chunk in DocumentChunk.objects.filter(document=document)]
    
    assert first_count == second_count
    assert first_contents == second_contents
    assert first_chunks_indices == second_chunks_indices
    assert result == result_2
    
@pytest.mark.django_db
def test_document_processor_removes_old_chunks_when_extracted_content_is_empty():
    user = User.objects.create_user(
                                username="testuserA",
                                password="passwordtestA",
                            )
    workspace = Workspace.objects.create(name="test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )
    
    uploaded_file = SimpleUploadedFile("test.txt",b"This is a text file for integration testing")
    
    document = Document.objects.create(title="test deep learning",
            knowledge_base=knowledge_base,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=user)
    
    document_processor = DocumentProcessor()
    
    result = document_processor.process(document=document)
    
    document.refresh_from_db()
    
    chunks = DocumentChunk.objects.filter(document=document)
    
    assert chunks.count() > 0
    assert [chunk.index for chunk in chunks] == [0]
    
    uploaded_file_2 = SimpleUploadedFile("test.txt",b"")
    
    document.file = uploaded_file_2
    document.file_type = Document.FileType.TXT
    
    document_processor = DocumentProcessor()
    
    result = document_processor.process(document=document)
    
    document.refresh_from_db()
    
    chunks = DocumentChunk.objects.filter(document=document)
    assert chunks.count() == 0
    assert not chunks.exists()

@pytest.mark.django_db
def test_document_processor_saves_embedding_for_each_chunk():
    user = User.objects.create_user(
        username="embedding_test_user",
        password="passwordtestA",
    )
    workspace = Workspace.objects.create(name="Embedding Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="Embedding Knowledge Base",
        workspace=workspace,
        created_by=user,
    )

    uploaded_file = SimpleUploadedFile(
        "embedding.txt",
        b"Artificial intelligence helps diagnose diseases.",
    )

    document = Document.objects.create(
        title="Embedding Test",
        knowledge_base=knowledge_base,
        file=uploaded_file,
        file_type=Document.FileType.TXT,
        created_by=user,
    )

    processor = DocumentProcessor()

    processor.process(document)

    chunks = list(document.chunks.order_by("index"))

    assert chunks
    assert all(chunk.embedding is not None for chunk in chunks)
    assert all(
        chunk.embedding == [0.1] * 384
        for chunk in chunks
    )