from rest_framework.test import APITestCase
from .models import Note
from django.contrib.auth.models import User

class NoteAPITestCase(APITestCase):
    url = "/api/notes-viewset/"
    
    def test_get_list_notes_and_return_be_200_code_status(self):
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
    def test_get_note_detail_and_return_note_and_be_200_code_status(self):
        note = Note.objects.create(
            title = "Test note",
            content = "Test content",
            category = "Testing"
        )
        response = self.client.get(self.url+f"{note.id}/")
        self.assertEqual(response.status_code, 200)
        
    def test_return_be_404_code_status_when_note_id_is_invalid(self):
        invalid_id = 9999
        response = self.client.get(self.url+f"{invalid_id}/")
        self.assertEqual(response.status_code, 404)
    
    def test_try_to_enter_create_note_and_return_must_be_403_status_code(self):        
        response = self.client.post(self.url,None)
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, '{"detail":"Authentication credentials were not provided."}')
        
    def test_create_note_when_user_is_authenticated_and_return_201(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user=user)
        
        data = {"title":"testtitle","content":"testcontent", "category":"testcategory"}
        response = self.client.post(self.url, data, format="json")
        
        self.assertEqual(response.status_code, 201)
        
    def test_create_note_by_authenticated_user_and_assign_owner(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)
        
        response = self.client.post(self.url,{
            "title": "Testing API",
            "content": "Testing create endpoint",
            "category": "Testing",
        }, format="json")
        
        note = Note.objects.get(pk=response.data["id"])
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(note.owner, user)
        
        self.assertEqual(note.owner.username, "testuser")
        
    def test_create_note_invalid_and_must_return_400_when_data_is_invalid(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)
        
        response = self.client.post(self.url,{
            "title": None,
            "content": None,
            "category": None,
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        
    def test_create_note_and_must_return_400_when_title_equal_category(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)
        
        response = self.client.post(self.url,{
            "title": "testtitle",
            "content": "testcontent",
            "category": "testtitle",
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        
    def test_update_note_by_owner_user_and_must_return_200(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)
        
        note = Note.objects.create(title="testtitle", 
                                content="testcontent",
                                category="testcategory",
                                owner=user)
        
        
        response = self.client.put(self.url+f"{note.id}/",{
            "title": "testtitle updated",
            "content": "testcontent",
            "category": "testcategory",
        }, format="json")
        
        self.assertEqual(response.status_code, 200)
        
        note.refresh_from_db()
        
        self.assertEqual(note.title, "testtitle updated")
        self.assertEqual(note.content, "testcontent")
        self.assertEqual(note.category, "testcategory")
        
    
    def test_update_note_and_must_return_403_when_user_is_not_authenticated(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        
        note = Note.objects.create(title="testtitle", 
                                content="testcontent",
                                category="testcategory",
                                owner=user)
        
        response = self.client.put(self.url+f"{note.id}/",{
                    "title": "testtitle updated",
                    "content": "testcontent",
                    "category": "testcategory",
                }, format="json")
        
        self.assertEqual(response.status_code, 403)
        
    def test_delete_note_and_must_return_204(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(user)
        
        note = Note.objects.create(title="testtitle", 
                                content="testcontent",
                                category="testcategory",
                                owner=user)
        
        response = self.client.delete(self.url+f"{note.id}/")
        
        self.assertEqual(response.status_code, 204)
        
    def test_try_to_delete_note_and_must_return_403_when_user_is_not_authenticated(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        
        note = Note.objects.create(title="testtitle", 
                                content="testcontent",
                                category="testcategory",
                                owner=user)
        
        response = self.client.delete(self.url + f"{note.id}/")
        
        self.assertEqual(response.status_code, 403)
        
    def test_try_to_update_note_userA_by_userB_and_must_return_403(self):
        userA = User.objects.create_user(username="testuserA", password="testpasswordA")
        self.client.force_login(userA)
        note = Note.objects.create(title="testtitle",
                                content="testcontent",
                                category="testcategory",
                                owner=userA)
        
        note.refresh_from_db()
        self.client.logout()
        
        userB = User.objects.create_user(username="testuserB", password="testpasswordB")
        self.client.force_login(userB)
        
        response = self.client.put(self.url+f"{note.id}/", {
            "title": "testtitle updated",
            "content": "testcontent",
            "category": "testcategory"
        })
        
        self.assertEqual(response.status_code, 403)
        
    def test_try_to_delete_note_userA_by_userB_and_must_return_403(self):
        userA = User.objects.create_user(username="testuserA", password="testpasswordA")
        self.client.force_login(userA)
        note = Note.objects.create(title="testtitle",
                                content="testcontent",
                                category="testcategory",
                                owner=userA)
        
        note.refresh_from_db()
        self.client.logout()
        
        userB = User.objects.create_user(username="testuserB", password="testpasswordB")
        self.client.force_login(userB)
        
        response = self.client.delete(self.url+f"{note.id}/")
        
        self.assertEqual(response.status_code, 403)
        
    def test_filter_notes_by_category(self):
        Note.objects.create(
            title="Python Basics",
            content="Python content",
            category="Programming",
        )

        Note.objects.create(
            title="RAG Introduction",
            content="RAG content",
            category="AI",
        )

        Note.objects.create(
            title="CNN Introduction",
            content="CNN content",
            category="AI",
        )
        
        response = self.client.get(self.url+"?category=AI")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)
        
    def test_search_notes(self):
        Note.objects.create(
            title="Python Basics",
            content="Python content",
            category="Programming",
        )

        Note.objects.create(
            title="RAG Introduction",
            content="RAG content",
            category="AI",
        )

        Note.objects.create(
            title="CNN Introduction",
            content="CNN content",
            category="AI",
        )
        response = self.client.get(self.url+"?search=RAG")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        
    def test_order_notes_by_created_at_descending(self):
        note1 = Note.objects.create(
            title="Python Basics",
            content="Python content",
            category="Programming",
        )

        note2 = Note.objects.create(
            title="RAG Introduction",
            content="RAG content",
            category="AI",
        )

        note3 = Note.objects.create(
            title="CNN Introduction",
            content="CNN content",
            category="AI",
        )
        response = self.client.get(self.url+"?ordering=-created_at")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["id"], note3.id)
        
    def test_pagination_must_not_exceed_max_page_size(self):
        for i in range(6):
            Note.objects.create(title=f"Test note {i}",
                                content=f"content {i}",
                                category=f"category {i}")
            
        response = self.client.get(self.url+"?page_size=6")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 4)