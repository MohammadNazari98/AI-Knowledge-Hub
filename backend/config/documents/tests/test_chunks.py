import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document, DocumentChunk
from django.db import IntegrityError






@pytest.fixture
def document(db):
    user = User.objects.create_user(
        username="chunk_test_user",
        password="test_password",
    )

    workspace = Workspace.objects.create(name="Chunk Test Workspace")
    workspace.members.add(user)

    knowledge_base = KnowledgeBase.objects.create(
        name="Chunk Test Knowledge Base",
        workspace=workspace,
        created_by=user,
    )

    uploaded_file = SimpleUploadedFile(
        "chunk_test.txt",
        b"Sample document content",
    )

    return Document.objects.create(
        title="Chunk Test Document",
        knowledge_base=knowledge_base,
        file=uploaded_file,
        file_type=Document.FileType.TXT,
        created_by=user,
    )
    
def test_documents_chunks_are_ordered_by_index(document):
    DocumentChunk.objects.create(document=document,
                                content="first chunks",
                                index=0)
    DocumentChunk.objects.create(document=document,
                                content="second chunks",
                                index=1)
    DocumentChunk.objects.create(document=document,
                                content="third chunks",
                                index=2)
    
    chunks = DocumentChunk.objects.all()
    assert [chunk.index for chunk in chunks] == [0, 1, 2]
    
    
@pytest.mark.django_db
def test_document_chunk_index_must_be_unique_per_document(document):
    DocumentChunk.objects.create(document=document,
                                content="first chunks",
                                index=0)    
    
    with pytest.raises(IntegrityError):
        DocumentChunk.objects.create(document=document,
                                content="second chunks",
                                index=0)
        
@pytest.mark.django_db
def test_deleting_document_deletes_its_chunks(document):
    DocumentChunk.objects.create(document=document,
                                    content="first chunks",
                                    index=0)
    DocumentChunk.objects.create(document=document,
                                content="second chunks",
                                index=1)
    DocumentChunk.objects.create(document=document,
                                content="third chunks",
                                index=2)
    
    document.delete()
    assert DocumentChunk.objects.filter(content="chunks").count() == 0
    assert not DocumentChunk.objects.filter(document__pk=document.pk).exists() 