import pytest
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.services.extractors.processor import DocumentProcessor
from documents.services.retrieval import KeywordRetriever
from documents.models import Document, DocumentChunk



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
    
    document_processor = DocumentProcessor()
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
    
    document_processor = DocumentProcessor()
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
    
    document_processor = DocumentProcessor()
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