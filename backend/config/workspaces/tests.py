from django.test import TestCase
from django.contrib.auth.models import User
from .models import Workspace
from rest_framework import status



class WorkspaceModelTests(TestCase):
    
    def test_workspace_can_have_multiple_members(self):
        user1 = User.objects.create_user(username="usertest", password="passwordtest")
        user2 = User.objects.create_user(username="usertest2", password="passwordtest2")
        
        workspace_1 = Workspace.objects.create(name="AI_team")
        
        workspace_1.members.add(user1, user2)
        
        self.assertEqual(workspace_1.members.count(), 2)
        self.assertIn(user1, workspace_1.members.all())
        self.assertIn(user2, workspace_1.members.all())
        
    def test_user_can_belong_to_multiple_workspaces(self):
        user1 = User.objects.create_user(username="usertest", password="passwordtest")
        user2 = User.objects.create_user(username="usertest2", password="passwordtest2")
        
        workspace_1 = Workspace.objects.create(name="AI_team")
        workspace_2 = Workspace.objects.create(name="Personal")
        
        workspace_1.members.add(user1, user2)
        
        workspace_2.members.add(user2)
        
        self.assertEqual(user2.workspaces.count(), 2)
        self.assertIn(workspace_1, user2.workspaces.all())
        self.assertIn(workspace_2, user2.workspaces.all())
        
class WorkspaceAPITests(TestCase):
    def setUp(self):
        self.user_A = User.objects.create_user("testuserA", password="testpasswordA")
        self.client.force_login(user=self.user_A)        
        
        self.url = "/api/workspaces/"
    
    def test_user_can_create_workspaces_when_user_is_authenticated(self):
        response = self.client.post(self.url, {
            "name": "AI Team"
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "AI Team")
        workspace = Workspace.objects.get(name="AI Team")
        
        self.assertIn(workspace, self.user_A.workspaces.all())
    
    def test_userA_cannot_see_workspace_userB_and_must_return_get_404(self):
        response = self.client.post(self.url, data={
            "name": "AI Team"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()
        
        self.user_B = User.objects.create_user("testuserB", password="testpasswordB")
        self.client.force_login(user=self.user_B)
        
        workspace = Workspace.objects.get(name="AI Team")
        response = self.client.get(self.url+f"{workspace.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_userB_only_sees_own_workspaces(self):
        self.client.post(self.url, data={
            "name": "AI Team"
        })
        self.client.post(self.url, data={
            "name": "Personal"
        })
        self.client.logout()
        user_B = User.objects.create_user("testuserB", password="testpasswordB")
        self.client.force_login(user=user_B)
        response = self.client.post(self.url, data={
            "name": "personal"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        own_workspace = Workspace.objects.get(members=user_B)
        self.assertIn(own_workspace, user_B.workspaces.all())
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["name"], "personal")
        self.assertEqual(response.data["count"], 1)
        
    def tearDown(self):
        self.client.logout()
        self.user_A = None
        self.url = None