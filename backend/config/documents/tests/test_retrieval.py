import pytest
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.services.extractors.processor import DocumentProcessor
from documents.services.retrieval import KeywordRetriever, SemanticRetriever
from documents.models import Document, DocumentChunk
import torch



class FakeEmbeddingService:
    def __init__(self):
        self.received_text = None
        self.prefix = None
    def get_embedding(self, text: str, prefix: str = "passage: "):
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        self.received_text = text
        self.prefix = prefix
        return torch.Tensor([[0.1]*384])
            

@pytest.fixture
def workspace(db):
    user = User.objects.create_user("usertestA", password="password")
    workspace = Workspace.objects.create(name="AI team")
    workspace.members.add(user)
    knowledge_base_a = KnowledgeBase.objects.create(name="AI medical",
                                                workspace=workspace,
                                                created_by=user)
    
    file_upload = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی به تشخیص بیماری کمک می‌کند.".encode("utf-8"))
    document = Document.objects.create(title="AI and Medical",
                                    knowledge_base=knowledge_base_a,
                                    file=file_upload,
                                    file_type=Document.FileType.TXT, 
                                    created_by=user)
    
    document_processor = DocumentProcessor(embedding_service=FakeEmbeddingService())
    document_processor.process(document)
    
    file_upload_2 = SimpleUploadedFile("test.txt", 
                                    "هوش مصنوعی تصاویر اشیاها را تشخیص میدهد کادر و برچسب میسازد به این تکنولوژی معروف YOLO گفته میشود.".encode("utf-8"))
    document_2 = Document.objects.create(title="Photo medical analysis",
                                    knowledge_base=knowledge_base_a,
                                    file=file_upload_2,
                                    file_type=Document.FileType.TXT, 
                                    created_by=user)
    document_processor.process(document_2)
    
    knowledge_base_b = KnowledgeBase.objects.create(name="AI researcher",
                                                    workspace=workspace,
                                                    created_by=user)
    
    file_upload_3 = SimpleUploadedFile("test.txt", 
                            "هوش مصنوعی در تشخیص بیماری کاربرد دارد.".encode("utf-8"))
    
    document_3 = Document.objects.create(title="ai paper",
                                    knowledge_base=knowledge_base_b,
                                    file=file_upload_3,
                                    file_type=Document.FileType.TXT, 
                                    created_by=user)
    document_processor.process(document_3)
    
    return user, knowledge_base_a, knowledge_base_b
    
@pytest.mark.django_db
def test_keyword_retriever_orders_chunks_by_matching_terms(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی تشخیص بیماری", knowledge_id=knowledge_base_a.id))

    
    assert len(results) == 2
    assert all(chunk.document.knowledge_base_id == knowledge_base_a.id for chunk in results)
    assert results[0].score >= results[1].score
    
def test_keyword_retriever_term_must_returns_results_by_high_score(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    file_upload = SimpleUploadedFile("test.txt", "پایتون برای توسعه وب استفاده می‌شود.".encode("utf-8"))
    document = Document.objects.create(title="python expert",
                                    knowledge_base=knowledge_base_a,
                                    file=file_upload,
                                    file_type=Document.FileType.TXT, 
                                    created_by=user)
    
    document_processor = DocumentProcessor(embedding_service=FakeEmbeddingService())
    document_processor.process(document)
    
    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی تشخیص بیماری", knowledge_id=knowledge_base_a.id))
    
    assert len(results) == 2
    assert all(chunk.document.knowledge_base.id == knowledge_base_a.id for chunk in results)
    assert results[0].content == "هوش مصنوعی در پزشکی به تشخیص بیماری کمک می\u200cکند."
    assert results[0].content != "پایتون برای توسعه وب استفاده می‌شود."
    

@pytest.mark.django_db
def test_keyword_retriever_gets_results_high_score_by_matching_term(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
        
    file_upload = SimpleUploadedFile("test.txt", "پایتون برای توسعه وب استفاده می‌شود.".encode("utf-8"))
    document = Document.objects.create(title="python expert",
                                    knowledge_base=knowledge_base_a,
                                    file=file_upload,
                                    file_type=Document.FileType.TXT, 
                                    created_by=user)
    
    document_processor = DocumentProcessor(embedding_service=FakeEmbeddingService())
    document_processor.process(document)
    
    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی تشخیص بیماری", knowledge_id=knowledge_base_a.id))
        
    assert results[0].score > results[1].score
    assert all(chunk.document.knowledge_base.id == knowledge_base_a.id for chunk in results)
    
@pytest.mark.django_db
def test_keyword_retriever_returns_results_null_when_no_matching_term(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    retriever = KeywordRetriever()
    results = list(retriever.search(query="", knowledge_id=knowledge_base_a.id))
    assert len(results) == 0
    
@pytest.mark.django_db
def test_keyword_retriever_returns_no_results_when_limit_is_zero(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
        
    retriever = KeywordRetriever()
    results = list(retriever.search(query="", knowledge_id=knowledge_base_a.id, limit=0))
    assert results == []
    
@pytest.mark.django_db
def test_keyword_retriever_returns_no_results_when_limit_is_zero_and_by_matching_term(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
            
    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی تشخیص بیماری", knowledge_id=knowledge_base_a.id, limit=0))
    assert results == []
    
@pytest.mark.django_db
def test_keyword_retriever_returns_only_best_result_when_limit_is_one(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
                
    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی تشخیص بیماری", knowledge_id=knowledge_base_a.id, limit=1))
    
    assert results[0].score == 4
    assert len(results) == 1
    assert results[0].content == "هوش مصنوعی در پزشکی به تشخیص بیماری کمک می\u200cکند."

@pytest.mark.django_db
def test_keyword_retriever_returns_no_results_for_whitespace_query(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace

    retriever = KeywordRetriever()
    results = list(retriever.search(query="   ", knowledge_id=knowledge_base_a.id))

    assert results == []

@pytest.mark.django_db
def test_keyword_retriever_must_return_results_ordered_correctly(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace

    retriever = KeywordRetriever()
    results = list(retriever.search(query="هوش مصنوعی", knowledge_id=knowledge_base_a.id))

    expected_ids = list(
        Document.objects.filter(knowledge_base=knowledge_base_a).order_by("id").values_list("id", flat=True)
    )

    assert [
        chunk.document_id for chunk in results
    ] == expected_ids
    
def test_semantic_retriever_uses_query_prefix(workspace):
    user_a, knowledge_base_a, knowledge_base_b = workspace
    
    embedding_service = FakeEmbeddingService()
    retriever = SemanticRetriever(
        embedding_service=embedding_service
    )
    list(
        retriever.search(
            query="هوش مصنوعی",
            knowledge_id=knowledge_base_a.id
        )
    )
    
    assert embedding_service.received_text == "هوش مصنوعی"
    assert embedding_service.prefix == "query: "
    
def test_semantic_retriever_must_return_results_ordered_correctly(workspace):
    user_a, knowledge_base_a, knowledge_base_b = workspace
    
    retriever = SemanticRetriever()
    
    results = list(retriever.search(query="هوش مصنوعی", knowledge_id=knowledge_base_a.id))
    
    expected_id = list(Document.objects.filter(knowledge_base=knowledge_base_a).order_by("id").values_list("id", flat=True))
    
    assert len(results) == 2
    assert [
        chunk.document_id for chunk in results
    ] == expected_id
    
    
class RankingFakeEmbeddingService:
    def __init__(self):
        self.text = None
        self.prefix = None
        
    def get_embedding(self, text:str, prefix:str = "passage: "):
        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")
        self.text = text
        self.prefix = prefix
        return torch.Tensor([[1.0] + [0.0] * 383])

@pytest.mark.django_db
def test_semantic_retriever_orders_chunks_by_cosine_distance(workspace):
    user_a, knowledge_base_a, knowledge_base_b = workspace
    
    chunks = list(
        DocumentChunk.objects.filter(
            document__knowledge_base=knowledge_base_a
        ).order_by("id")
    )
    
    assert len(chunks) == 2

    vectors = [
        [1.0] + [0.0] * 383,
        [0.0, 1.0] + [0.0] * 382
    ]
    
    retriever = SemanticRetriever(embedding_service=RankingFakeEmbeddingService())
    
    for chunk, vector in zip(chunks, vectors):
        chunk.embedding = vector
        chunk.save(update_fields=["embedding"])
        
    results = list(
        retriever.search(query="هوش مصنوعی", knowledge_id=knowledge_base_a.id)
    )
        
    assert len(results) == 2
    assert results[0].id == chunks[0].id
    
    
@pytest.mark.django_db
def test_semantic_retriever_respects_limit(workspace):
    user_a, knowledge_base_a, knowledge_base_b = workspace

    chunks = list(DocumentChunk.objects.filter(
        document__knowledge_base=knowledge_base_a
    ).order_by("id"))
    
    assert len(chunks) == 2
    
    retriever = SemanticRetriever(embedding_service=RankingFakeEmbeddingService())
        
    results = list(
        retriever.search("هوش مصنوعی", knowledge_id=knowledge_base_a.id, limit=1)
    )
    
    assert len(results) == 1
    
@pytest.mark.django_db
def test_semantic_retriever_return_empty_when_query_is_empty(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    chunks = DocumentChunk.objects.filter(
        document__knowledge_base=knowledge_base_a
    ).order_by("id")
    
    fake_embedding_service = FakeEmbeddingService()
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search("", knowledge_id=knowledge_base_a.id)
    )
    assert len(results) == 0
    
    results = list(
        retriever.search(None, knowledge_id=knowledge_base_a.id)
    )
    
    assert len(results) ==  0
    
    results = list(
        retriever.search(" ", knowledge_id=knowledge_base_a.id)
    )
        
    assert len(results) ==  0
    
    assert fake_embedding_service.received_text is None
    
@pytest.mark.django_db
def test_semantic_retriever_returns_only_selected_knowledge_base(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    fake_embedding_service = FakeEmbeddingService()
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(retriever.search("هوش مصنوعی", knowledge_id=knowledge_base_a.id))
    
    assert all(knowledge_base_a == chunk.document.knowledge_base for chunk in results)
    
@pytest.mark.django_db
def test_semantic_retriever_does_not_return_chunks_from_other_knowledge_base(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    fake_embedding_service = FakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search(query="هوش مصنوعی", knowledge_id=knowledge_base_b.id)
    )
    assert len(results) == 1
    assert all(
        knowledge_base_b == chunk.document.knowledge_base for chunk in results
    )
    
@pytest.mark.django_db
def test_semantic_retriever_return_empty_when_limit_is_zero(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    fake_embedding_service = FakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search("هوش مصنوعی", knowledge_id=knowledge_base_b.id, limit=0)
    )
    
    assert len(results) == 0
    assert fake_embedding_service.received_text is None
    
@pytest.mark.django_db
def test_semantic_retriever_return_empty_when_limit_is_negative(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    fake_embedding_service = FakeEmbeddingService()
        
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search("هوش مصنوعی", knowledge_id=knowledge_base_b.id, limit=-1)
    )
    
    assert len(results) == 0
    assert fake_embedding_service.received_text is None
    
@pytest.mark.django_db
def test_semantic_retriever_returns_chunk_with_embedding_valid(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    chunks = list(
        DocumentChunk.objects.filter(
        document__knowledge_base=knowledge_base_a).order_by("id")
    )
    
    chunks[0].embedding = None
    chunks[0].save(update_fields=["embedding"])
    
    ranking_fake_embedding_service = RankingFakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=ranking_fake_embedding_service)
    
    results = list(
        retriever.search(query="هوش مصنوعی", knowledge_id=knowledge_base_a.id)
    )
    
    assert len(results) == 1
    assert results[0].id == chunks[1].id
    
@pytest.mark.django_db
def test_semantic_retriever_return_chunks_status_successful_correctly(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    chunks = DocumentChunk.objects.filter(
        document__knowledge_base=knowledge_base_a,
    ).order_by("id")
    
    document = chunks[0].document
    
    document.status = Document.Status.FAILED
    document.save(update_fields=["status"])
    
    document.refresh_from_db()
    
    fake_embedding_service = FakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search(query="هوش مصنوعی", 
                        knowledge_id=knowledge_base_a.id)
    )
    assert len(results) == 1
    
@pytest.mark.django_db
def test_semantic_retriever_returns_empty_when_documents_status_is_failed(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
        
    chunks = DocumentChunk.objects.filter(
        document__knowledge_base=knowledge_base_a,
    ).order_by("id")
    
    for chunk in chunks:
        chunk.document.status = Document.Status.FAILED
        chunk.document.save(update_fields=["status"])
        chunk.document.refresh_from_db()
    
    fake_embedding_service = FakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search(query="هوش مصنوعی", 
                        knowledge_id=knowledge_base_a.id)
    )
    assert len(results) == 0
    
@pytest.mark.django_db
def test_semantic_retriever_returns_empty_when_knowledge_base_is_invalid(workspace):
    user, knowledge_base_a, knowledge_base_b = workspace
    
    fake_embedding_service = FakeEmbeddingService()
    
    retriever = SemanticRetriever(embedding_service=fake_embedding_service)
    
    results = list(
        retriever.search(query="هوش مصنوعی", 
                        knowledge_id=99)
    )
    assert len(results) == 0
    assert fake_embedding_service.received_text == "هوش مصنوعی"
    assert fake_embedding_service.prefix == "query: "