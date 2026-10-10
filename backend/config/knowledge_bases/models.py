from django.db import models
from workspaces.models import Workspace
from django.contrib.auth.models import User


class KnowledgeBase(models.Model):
    name = models.CharField(max_length=150, null=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="knowledge_bases")
    description = models.TextField(null=True, blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_knowledge_bases")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name