from django.db import models
from django.contrib.auth.models import User



class Workspace(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="workspaces")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    