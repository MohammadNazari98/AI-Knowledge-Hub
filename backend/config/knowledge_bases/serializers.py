from rest_framework import serializers
from rest_framework.serializers import ValidationError
from workspaces.models import Workspace
from .models import KnowledgeBase




class KnowledgeBaseSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = KnowledgeBase
        fields = ["id", "name", "workspace", "description", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
        
    def validate_workspace(self, value):
        user = self.context["request"].user
        user_workspace = value.members.filter(pk=user.id).exists()
        
        if not user_workspace:
            raise ValidationError("Error validation, workspace chosen not found.")
        return value        