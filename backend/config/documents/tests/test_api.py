import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from documents.models import Document
from knowledge_bases.models import KnowledgeBase
from workspaces.models import Workspace
from django.core.files.uploadedfile import SimpleUploadedFile



@pytest.mark.django_db
def test_user_a_can_sees_list_documents_from_owner_workspace(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user_a)
    knowledge_base = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base,
                                    file="media/documents/python-basics.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    client.force_login(user=user_a)
    response = client.get("/api/documents/")
    assert response.status_code == status.HTTP_200_OK
    
@pytest.mark.django_db
def test_user_b_can_sees_document_user_a_from_owner_workspace_a(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    user_b = User.objects.create_user("testuserB", "testpasswordB")
    
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user_a)
    workspace.members.add(user_b)
    knowledge_base = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base,
                                    file="media/documents/python-basics.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    client.force_login(user=user_b)
    response = client.get(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_200_OK
    assert Document.objects.filter(knowledge_base__workspace__members=user_a).exists()
    assert Document.objects.filter(knowledge_base__workspace__members=user_b).exists()
    
@pytest.mark.django_db
def test_user_illegal_cannot_sees_their_documents_in_the_workspace_and_must_return_404(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    user_b = User.objects.create_user("testuserB", "testpasswordB")
    user_c = User.objects.create_user("testuserC", "testpasswordC")
    
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user_a)
    workspace.members.add(user_b)
    knowledge_base = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base,
                                    file="media/documents/python-basics.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    client.force_login(user_c)
    response = client.get(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["detail"] == "No Document matches the given query."

@pytest.mark.django_db
def test_user_illegal_anonymous_cannot_sees_their_documents_and_must_return_403(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    
    workspace = Workspace.objects.create(name="Python AI")
    workspace.members.add(user_a)
    knowledge_base = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base,
                                    file="media/documents/python-basics.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    response = client.get(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
@pytest.mark.django_db
def test_user_a_cannot_creates_a_new_document_in_another_knowledge_base_and_must_return_400(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    
    user_b = User.objects.create_user("testuserB", "testpasswordB")    
    workspace_b = Workspace.objects.create(name="Software development")
    workspace_b.members.add(user_b)
    knowledge_base_b = KnowledgeBase.objects.create(name="python developer", 
                                                workspace=workspace_b,
                                                created_by=user_b)
    
    client.force_login(user=user_a)
    
    uploaded_file = SimpleUploadedFile("python-basics.pdf", b"test content", content_type="application/pdf")
    response = client.post("/api/documents/", data={
        "title": "Python basics", 
        "knowledge_base": knowledge_base_b.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF,
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
@pytest.mark.django_db
def test_user_a_creates_a_new_document_in_the_knowledge_and_must_return_201(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    client.force_login(user=user_a)
    uploaded_file = SimpleUploadedFile("python-basics.pdf", b"test content", content_type="application/pdf")
    response = client.post("/api/documents/", data={
        "title": "Python basics", 
        "knowledge_base": knowledge_base_a.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF,
    })
    assert response.status_code == status.HTTP_201_CREATED
    
@pytest.mark.django_db
def test_user_a_creates_a_new_document_in_workspace_a_through_on_user_b_payload_and_must_return_201(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    user_b = User.objects.create_user("testuserB", "testpasswordB")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    workspace_a.members.add(user_b)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    client.force_login(user=user_a)
    uploaded_file = SimpleUploadedFile("python-basics.pdf", b"test content", content_type="application/pdf")
    response = client.post("/api/documents/", data={
        "title": "Python basics", 
        "knowledge_base": knowledge_base_a.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF,
        "created_by": user_b
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert Document.objects.get(title="Python basics").created_by == user_a
    assert Document.objects.get(title="Python basics").created_by != user_b
    assert knowledge_base_a.documents.get(title="Python basics").created_by == user_a
    assert knowledge_base_a.documents.get(title="Python basics").created_by != user_b
    
    
@pytest.mark.django_db
def test_user_a_updates_document_from_knowledge_a_to_knowledge_b_and_must_return_400(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    
    user_b = User.objects.create_user("testuserB", "testpasswordB")    
    workspace_b = Workspace.objects.create(name="Software development")
    workspace_b.members.add(user_b)
    knowledge_base_b = KnowledgeBase.objects.create(name="python developer", 
                                                workspace=workspace_b,
                                                created_by=user_b)
    api_client = APIClient()
    api_client.force_authenticate(user=user_a)
    uploaded_file = SimpleUploadedFile("python-basics.pdf", b"test content", content_type="application/pdf")
    response = api_client.post("/api/documents/", data={
        "title": "Python basics", 
        "knowledge_base": knowledge_base_a.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF,
        "created_by": user_b
    })
    response = api_client.patch(f"/api/documents/{response.data["id"]}/", data={
        "knowledge_base": knowledge_base_b.id,
    }, format="multipart")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    document = Document.objects.get(title="Python basics")
    assert document.knowledge_base == knowledge_base_a
    
@pytest.mark.django_db
def test_user_b_cannot_deletes_document_from_another_knowledge_a_and_must_return_404(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/python-basics.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    user_b = User.objects.create_user("testuserB", "testpasswordB")    
    workspace_b = Workspace.objects.create(name="Software development")
    workspace_b.members.add(user_b)
    
    client.force_login(user=user_b)

    response = client.delete(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Document.objects.filter(title="RAG").exists()
    
@pytest.mark.django_db
def test_user_b_cannot_updates_document_a_and_must_return_404(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/LLM.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    user_b = User.objects.create_user("testuserB", "testpasswordB")    
    workspace_b = Workspace.objects.create(name="Software development")
    workspace_b.members.add(user_b)
    client.force_login(user=user_b)
    response = client.patch(f"/api/documents/{document.id}/", data={
        "title": "update title"
    })
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Document.objects.filter(title="RAG").exists()
    
@pytest.mark.django_db
def test_user_a_can_deletes_document_from_knowledge_a_and_must_return_204(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/RAG.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    client.force_login(user=user_a)

    response = client.delete(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Document.objects.filter(title="RAG").exists()
    
@pytest.mark.django_db
def test_user_a_can_retrieves_document_access_and_must_return_200(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/RAG.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    client.force_login(user=user_a)
    response = client.get(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "RAG"
    
@pytest.mark.django_db
def test_user_cannot_retrieve_document_and_must_return_404(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/RAG.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    user_b = User.objects.create_user("testuserB", "testpasswordB")   
    workspace_b = Workspace.objects.create(name="Researcher AI")
    workspace_b.members.add(user_b)
    
    client.force_login(user_b)
    response = client.get(f"/api/documents/{document.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    

@pytest.mark.django_db
def test_user_can_edit_document_and_must_return_200(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    document = Document.objects.create(title="RAG", 
                                    knowledge_base=knowledge_base_a,
                                    file="media/documents/RAG.pdf",
                                    file_type=Document.FileType.PDF,
                                    created_by=user_a)
    
    api_client = APIClient()
    api_client.force_authenticate(user_a)
    response = api_client.patch(f"/api/documents/{document.id}/", data={
        "title": "Advanced RAG"
    }, format="json")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data["title"] == "Advanced RAG"
    
@pytest.mark.django_db
def test_user_can_creates_document_and_should_not_duplicate_document(client: APIClient):
    user_a = User.objects.create_user("testuserA", "testpasswordA")
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    knowledge_base_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                                workspace=workspace_a,
                                                created_by=user_a)
    
    client.force_login(user_a)
    
    uploaded_file = SimpleUploadedFile("python_expert.pdf", content=b"test content", content_type="application/pdf")
    response = client.post(f"/api/documents/", data={
        "title": "Python expert",
        "knowledge_base": knowledge_base_a.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF
    }, format="multipart")
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["title"] == "Python expert"
    
    uploaded_file = SimpleUploadedFile("python_expert.pdf", content=b"test content", content_type="application/pdf")
    response = client.post(f"/api/documents/", data={
        "title": "Python expert",
        "knowledge_base": knowledge_base_a.id,
        "file": uploaded_file,
        "file_type": Document.FileType.PDF
    }, format="multipart")
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert knowledge_base_a.documents.count() == 1