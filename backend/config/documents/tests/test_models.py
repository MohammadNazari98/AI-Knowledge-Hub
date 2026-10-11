from django.test import TestCase
from django.contrib.auth.models import User
from workspaces.models import Workspace
from knowledge_bases.models import KnowledgeBase
from documents.models import Document
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile


class DocumentModelTest(TestCase):
    
    def setUp(self):
        self.user_a = User.objects.create_user(username="testuserA", password="testpasswordA")
        self.workspace_a = Workspace.objects.create(name="AI team")
        self.workspace_a.members.add(self.user_a)
        self.knowledge_a = KnowledgeBase.objects.create(name="Data science", workspace=self.workspace_a, created_by=self.user_a)
    
    def test_documents_belongs_to_knowledge_base(self):
        document = Document.objects.create(title="test title", 
                                        knowledge_base=self.knowledge_a,
                                        file="documents/test.txt",
                                        file_type=Document.FileType.TXT,
                                        created_by=self.user_a)
        
        self.assertEqual(document.title, "test title")
        self.assertEqual(document.knowledge_base, self.knowledge_a)
        self.assertEqual(document.status, Document.Status.UPLOADED)
        
    def test_document_rejects_unsupported_file_extension(self):
        uploaded_file = SimpleUploadedFile("malware.exe", 
                                        b"test content", 
                                        content_type="application/octet-stream")
        
        document = Document(
            title="invalid document",
            knowledge_base=self.knowledge_a,
            file=uploaded_file,
            created_by=self.user_a,
        )
        
        with self.assertRaises(ValidationError):
            document.full_clean()
            
    def test_document_rejects_mismatched_file_type(self):
        uploaded_file = SimpleUploadedFile("report.pdf", 
                                        b"content test",
                                        content_type="application/pdf")
        
        document = Document(
            title="Test PDF",
            knowledge_base=self.knowledge_a,
            file=uploaded_file,
            file_type=Document.FileType.TXT,
            created_by=self.user_a,
        )
        
        with self.assertRaises(ValidationError):
            document.full_clean()
            
    def test_document_rejects_blank_title(self):
        uploaded_file = SimpleUploadedFile(
                                    "report.txt",
                                    b"content test",
                                    content_type="text/plain")
                
        document = Document(
            title="      ",
            knowledge_base=self.knowledge_a,
            file=uploaded_file,
            file_type=Document.FileType.PDF,
            created_by=self.user_a,
        )
        
        with self.assertRaises(ValidationError):
            document.full_clean()
            
    def test_document_title_must_be_unique_within_knowledge_base(self):
        uploaded_file = SimpleUploadedFile("python_basic.pdf", b"Test content", content_type="application/pdf")
        Document.objects.create(title="Python basics", 
                                knowledge_base=self.knowledge_a,
                                file=uploaded_file,
                                file_type=Document.FileType.PDF,
                                created_by=self.user_a)
        
        uploaded_file_2 = SimpleUploadedFile("python_basic_2.pdf", b"Test content", content_type="application/pdf")
        document_2 = Document(title="Python basics", 
                            knowledge_base=self.knowledge_a,
                            file=uploaded_file_2,
                            file_type=Document.FileType.PDF,
                            created_by=self.user_a)
        
        with self.assertRaises(ValidationError):
            document_2.full_clean()
            
    def test_same_title_allowed_in_different_knowledge_bases(self):
        uploaded_file = SimpleUploadedFile("python_basics.pdf", b"content test", content_type="application/pdf")
        document_a = Document.objects.create(title="Python basics", 
                                            knowledge_base=self.knowledge_a, 
                                            file=uploaded_file,
                                            file_type=Document.FileType.PDF,
                                            created_by=self.user_a)

        user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
        workspace_b = Workspace.objects.create(name="AI team 2")
        workspace_b.members.add(user_b)
        knowledge_b = KnowledgeBase.objects.create(name="Python AI", 
                                                workspace=workspace_b,
                                                created_by=user_b)
        uploaded_file_b = SimpleUploadedFile("python_basics_2.pdf", b"content test", content_type="application/pdf")
        document_b = Document.objects.create(title="Python basics", 
                                            knowledge_base=knowledge_b, 
                                            file=uploaded_file_b,
                                            file_type=Document.FileType.PDF,
                                            created_by=user_b)

        self.assertTrue(Document.objects.filter(title="Python basics", knowledge_base=self.knowledge_a).exists())
        self.assertTrue(Document.objects.filter(title="Python basics", knowledge_base=knowledge_b).exists())
        
    def test_user_a_creates_a_new_document_owner_and_must_belongs_to_user_a(self):
        uploaded_file = SimpleUploadedFile("python_advanced.pdf", b"test content", content_type="application/pdf")
        document_a = Document.objects.create(title="Python advanced", 
                                            knowledge_base=self.knowledge_a, 
                                            file=uploaded_file,
                                            file_type=Document.FileType.PDF,
                                            created_by=self.user_a)
        self.assertIn(document_a, self.knowledge_a.documents.filter(created_by=self.user_a))
        self.assertEqual(document_a.created_by, self.user_a)
    
    def test_members_a_can_see_documents_in_workspace_a(self):
        uploaded_file = SimpleUploadedFile("python_basics.pdf", b"content test", content_type="application/pdf")
        document_a = Document.objects.create(title="Python basics", 
                                            knowledge_base=self.knowledge_a, 
                                            file=uploaded_file,
                                            file_type=Document.FileType.PDF,
                                            created_by=self.user_a)
        
        user_b = User.objects.create_user(username="testuserB", password="testpasswordB")
        self.workspace_a.members.add(user_b)
        
        self.assertEqual(document_a.knowledge_base.workspace.members.count(), 2)
        self.assertTrue(document_a.knowledge_base.workspace.members.filter(pk=self.user_a.pk).exists())
        self.assertTrue(document_a.knowledge_base.workspace.members.filter(pk=user_b.pk).exists())
        
    def test_user_c_cannot_see_documents_in_workspace_a(self):
        uploaded_file = SimpleUploadedFile("python_basics.pdf", b"content test", content_type="application/pdf")
        document_a = Document.objects.create(title="Python basics", 
                                        knowledge_base=self.knowledge_a, 
                                        file=uploaded_file,
                                        file_type=Document.FileType.PDF,
                                        created_by=self.user_a)
        
        user_c = User.objects.create_user(username="testuserC", password="testpasswordC")
        self.assertFalse(document_a.knowledge_base.workspace.members.filter(pk=user_c.pk).exists())