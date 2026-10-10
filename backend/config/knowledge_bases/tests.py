from django.test import TestCase
from django.contrib.auth.models import User
from .models import KnowledgeBase
from workspaces.models import Workspace
from django.db.models.deletion import ProtectedError



class KnowledgeBaseModelTest(TestCase):
    
    def setUp(self):
        self.user_1 = User.objects.create_user(username="usertestA", password="passwordtestA")
        self.client.force_login(user=self.user_1)        
        self.workspace = Workspace.objects.create(name="AI team")
        self.workspace.members.add(self.user_1)
    
    def test_knowledge_base_belongs_to_workspace(self):
        
        self.assertIn(self.user_1, self.workspace.members.all())
        
        knowledge_base = KnowledgeBase.objects.create(name="test knowledge base", 
                                    workspace=self.workspace,
                                    created_by=self.user_1)

        self.assertEqual(knowledge_base.name, "test knowledge base")
        self.assertEqual(knowledge_base.workspace, self.workspace)
        self.assertEqual(knowledge_base.created_by, self.user_1)
    
    def test_delete_workspace_and_It_must_delete_belongs_to_knowledge_bases(self):
        self.assertIn(self.user_1, self.workspace.members.all())
        
        knowledge_base = KnowledgeBase.objects.create(name="knowledge base test",
                                                    workspace=self.workspace,
                                                    created_by=self.user_1)
        
        self.assertEqual(knowledge_base.name, "knowledge base test")
        self.assertEqual(knowledge_base.workspace, self.workspace)
        self.assertEqual(knowledge_base.created_by, self.user_1)
        
        self.workspace.delete()
        
        self.assertFalse(Workspace.objects.filter(pk=self.workspace.id).exists())
        self.assertFalse(KnowledgeBase.objects.filter(pk=knowledge_base.id).exists())
        
    def test_knowledge_base_return_str(self):
        knowledge_base = KnowledgeBase.objects.create(name="Knowledge test", 
                                                    workspace=self.workspace,
                                                    created_by=self.user_1)
        self.assertEqual(str(knowledge_base), "Knowledge test")
        
    def test_knowledge_base_None_description_and_must_create_successful(self):
        knowledge_base = KnowledgeBase.objects.create(name="Knowledge test", 
                                                    workspace=self.workspace,
                                                    description="",
                                                    created_by=self.user_1)
        self.assertEqual(knowledge_base.description, "")
        
        
    def test_delete_user_with_knowledge_base_raises_protected_error(self):
        self.assertIn(self.user_1, self.workspace.members.all())
                
        knowledge_base = KnowledgeBase.objects.create(name="knowledge base test",
                                                    workspace=self.workspace,
                                                    created_by=self.user_1)
        
        self.assertEqual(knowledge_base.name, "knowledge base test")
        self.assertEqual(knowledge_base.workspace, self.workspace)
        self.assertEqual(knowledge_base.created_by, self.user_1)
        
        with self.assertRaises(ProtectedError):
            self.user_1.delete()
        
        self.assertTrue(KnowledgeBase.objects.filter(pk=knowledge_base.id).exists())
        self.assertTrue(User.objects.filter(pk=self.user_1.id).exists())
        self.assertTrue(self.workspace.members.filter(pk=self.user_1.id).exists())