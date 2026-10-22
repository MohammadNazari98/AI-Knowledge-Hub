import pytest
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document, DocumentChunk
from documents.services.extractors.processor import DocumentProcessor



@pytest.mark.django_db
def test_user_sees_only_knowledge_bases_from_their_workspaces(client: APIClient) -> None:
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_a = Workspace.objects.create(name="workspace a")
    workspace_a.members.add(user_a)
    
    workspace_b = Workspace.objects.create(name="workspace b")
    workspace_b.members.add(user_b)
    
    kb_a = KnowledgeBase.objects.create(name="Python AI",
                                        workspace=workspace_a, 
                                        created_by=user_a)
    kb_b = KnowledgeBase.objects.create(name="Deep Learning",
                                        workspace=workspace_b,
                                        created_by=user_b)
    
    client.force_login(user_a)
    response = client.get("/api/knowledge-bases/")
    
    assert response.status_code == 200
    
    data = response.data
    
    assert data["count"] == 1
    assert data["results"][0]["id"] == kb_a.id
    assert data["results"][0]["name"] == "Python AI"
    
@pytest.mark.django_db
def test_userA_tries_to_create_knowledge_base_from_workspace_user_B_and_must_return_400_bad_request(client: APIClient) -> None:
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_b = Workspace.objects.create(name="workspace b")
    workspace_b.members.add(user_b)
    
    client.force_login(user_a)
    
    response = client.post("/api/knowledge-bases/", data={
        "name": "Python AI",
        "workspace": workspace_b.pk,
        "created_by": user_a
    })
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["workspace"][0] == "Error validation, workspace chosen not found."

@pytest.mark.django_db
def test_user_a_cannot_retrieve_knowledge_base_from_another_users_workspace(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_a = Workspace.objects.create(name="Python AI")
    workspace_a.members.add(user_a)
    
    workspace_b = Workspace.objects.create(name="researcher AI")
    workspace_b.members.add(user_b)
    
    knowledge_a = KnowledgeBase.objects.create(name="Machine Learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    knowledge_b = KnowledgeBase.objects.create(name="Deep Learning",
                                            workspace=workspace_b,
                                            created_by=user_b)
    
    client.force_login(user=user_a)
    response = client.get(f"/api/knowledge-bases/{knowledge_b.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
@pytest.mark.django_db
def test_user_b_cannot_retrieve_knowledge_base_from_another_users_workspace(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    workspace_b = Workspace.objects.create(name="web developer")
    workspace_b.members.add(user_b)
    
    knowledge_a = KnowledgeBase.objects.create(name="Machine Learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    client.force_login(user=user_b)
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
@pytest.mark.django_db
def test_user_b_cannot_update_knowledge_base_from_another_users_workspace(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    workspace_b = Workspace.objects.create(name="web developer")
    workspace_b.members.add(user_b)
    
    knowledge_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    client.force_login(user=user_b)
    
    response = client.patch(f"/api/knowledge-bases/{knowledge_a.id}/", data={
        "name": "Hacked Knowledge Base"
    }, content_type="application/json")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
@pytest.mark.django_db
def test_user_a_cannot_delete_knowledge_base_from_another_users_workspace(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    workspace_b = Workspace.objects.create(name="web developer")
    workspace_b.members.add(user_b)
    
    knowledge_b = KnowledgeBase.objects.create(name="Python & Django", 
                                            workspace=workspace_b,
                                            created_by=user_b)
    
    client.force_login(user=user_a)
    
    response = client.delete(f"/api/knowledge-bases/{knowledge_b.id}/")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert KnowledgeBase.objects.filter(pk=knowledge_b.pk).exists() == True
    
@pytest.mark.django_db
def test_user_a_can_update_knowledge_base_and_must_return_200(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    client.force_login(user=user_a)
    
    response = client.patch(f"/api/knowledge-bases/{knowledge_a.id}/", data={
        "name": "LLM"
    }, content_type="application/json")
    
    assert response.status_code == status.HTTP_200_OK
    assert KnowledgeBase.objects.get(pk=knowledge_a.pk).name == "LLM"
    
@pytest.mark.django_db
def test_user_a_can_create_knowledge_base_and_must_return_201(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    client.force_login(user=user_a)
    
    response = client.post("/api/knowledge-bases/", data={
        "name": "Deep Learning",
        "workspace": workspace_a.pk
    }, content_type="application/json")
    
    assert response.status_code == status.HTTP_201_CREATED
    assert KnowledgeBase.objects.get(pk=response.data["id"]).name == "Deep Learning"
    assert KnowledgeBase.objects.get(pk=response.data["id"]).created_by == user_a
    
@pytest.mark.django_db
def test_user_cannot_move_knowledge_base_to_workspace_they_are_not_member_of(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    workspace_b = Workspace.objects.create(name="AI Team")
    workspace_b.members.add(user_a)
    
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    workspace_c = Workspace.objects.create(name="Web developer")
    workspace_c.members.add(user_b)
    
    knowledge_a = KnowledgeBase.objects.create(name="Deep Learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    client.force_login(user=user_a)
    
    response = client.patch(f"/api/knowledge-bases/{knowledge_a.pk}/", {
        "workspace": workspace_c.pk
    }, content_type="application/json")
    
    knowledge_a.refresh_from_db()
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert knowledge_a.workspace_id == workspace_a.pk
    
@pytest.mark.django_db
def test_user_a_can_delete_knowledge_base_and_must_return_204(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
        
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    client.force_login(user=user_a)
    
    response = client.delete(f"/api/knowledge-bases/{knowledge_a.id}/")
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert KnowledgeBase.objects.filter(pk=knowledge_a.id).exists() == False

@pytest.mark.django_db
def test_user_can_search_the_query_in_the_knowledge_and_return_200(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
            
    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)
    
    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)
    
    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor = DocumentProcessor()
    document_processor.process(document)
    client.force_login(user=user_a)
        
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=هوش مصنوعی")    
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
    
@pytest.mark.django_db
def test_user_cannot_search_empty_the_query_in_the_knowledge_and_return_400(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")

    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)

    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)

    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor = DocumentProcessor()
    document_processor.process(document)
    client.force_login(user=user_a)
    
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=")
        
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    
@pytest.mark.django_db
def test_user_b_cannot_search_the_query_from_another_knowledge_and_return_404(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")

    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)

    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)

    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor = DocumentProcessor()
    document_processor.process(document)
    
    user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
    workspace_b = Workspace.objects.create(name="Python developer")
    workspace_b.members.add(user_b)
    
    knowledge_b = KnowledgeBase.objects.create(name="python expert", 
                                                workspace=workspace_b,
                                                created_by=user_b)
    
    client.force_login(user=user_b)
        
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=هوش مصنوعی")
        
    assert response.status_code == status.HTTP_404_NOT_FOUND
    

@pytest.mark.django_db
def test_user_a_gets_empty_results_when_query_does_not_match_any_chunk(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")

    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)

    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)

    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor = DocumentProcessor()
    document_processor.process(document)
    
    client.force_login(user=user_a)
            
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=توسعه وب")
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
    
@pytest.mark.django_db
def test_user_a_cannot_search_the_query_document_status_processing_in_the_knowledge_and_return_200(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")

    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)

    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)

    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a, status=Document.Status.PROCESSING)
    
    DocumentChunk.objects.create(
        document=document,
        content="هوش مصنوعی در پزشکی",
        index=0,
    )
    client.force_login(user=user_a)
            
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=هوش مصنوعی")
    
    assert response.status_code == status.HTTP_200_OK
    assert document.status == Document.Status.PROCESSING
    assert len(response.data) == 0
    
@pytest.mark.django_db
def test_user_a_search_the_query_by_high_rating_in_the_knowledge_and_return_200(client: APIClient):
    user_a = User.objects.create_user(username="testuserA", password="testpasswordA")

    workspace_a = Workspace.objects.create(name="Data science")
    workspace_a.members.add(user_a)

    knowledge_a = KnowledgeBase.objects.create(name="Deep learning", 
                                            workspace=workspace_a,
                                            created_by=user_a)

    file_uploaded = SimpleUploadedFile("test.txt", "هوش مصنوعی در پزشکی".encode("utf-8"))
    document = Document.objects.create(title="ai basic", knowledge_base=knowledge_a, file=file_uploaded, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor = DocumentProcessor()
    document_processor.process(document)
    
    file_uploaded_2 = SimpleUploadedFile("test.txt", "هوش در پزشکی با یادگیری ماشین".encode("utf-8"))
    document_2 = Document.objects.create(title="medical in machine learning", knowledge_base=knowledge_a, file=file_uploaded_2, file_type=Document.FileType.TXT, created_by=user_a)
    document_processor.process(document_2)
    
    client.force_login(user=user_a)
    
    response = client.get(f"/api/knowledge-bases/{knowledge_a.id}/search/?q=هوش مصنوعی")
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0
    assert response.data[0]['score'] > response.data[1]['score']
    assert response.data[0]["score"] == 2
    assert response.data[1]["score"] == 1