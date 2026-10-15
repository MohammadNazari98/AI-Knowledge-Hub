from rest_framework import serializers
from .models import Document
from rest_framework.serializers import ValidationError



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "knowledge_base", "file", "status", "content", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
    
    def validate_knowledge_base(self, value):
        user = self.context["request"].user
        users_knowledge = value.workspace.members.filter(pk=user.pk).exists()
        if not users_knowledge:
            raise ValidationError("Error knowledge base chosen is invalid.")
        return value