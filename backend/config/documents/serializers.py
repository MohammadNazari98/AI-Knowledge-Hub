from rest_framework import serializers
from .models import Document, DocumentChunk
from rest_framework.serializers import ValidationError



class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "knowledge_base", "file", "file_type", "status", "content", "created_by", "created_at", "updated_at"]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
    
    def validate_knowledge_base(self, value):
        user = self.context["request"].user
        users_knowledge = value.workspace.members.filter(pk=user.pk).exists()
        if not users_knowledge:
            raise ValidationError("Error knowledge base chosen is invalid.")
        return value
    
    
class DocumentChunkSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(read_only=True)
    document_title = serializers.CharField(source="document.title", read_only=True)
    class Meta:
        model = DocumentChunk
        fields = ["id", "document", "document_title", "content", "index", "score", "created_at"]
        read_only_fields = ["id", "document", "document_title", "content", "index", "score", "created_at"]