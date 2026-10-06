from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Note
        fields = "__all__"
        
    def validate_title(self, value: str): 
        if len(value.strip()) < 5: 
            raise serializers.ValidationError("Title must be at least 5 characters long.")
        return value
    
    def validate_category(self, value: str):
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Category must be at least 1 characters long.")
        return value
    
    def validate(self, attrs):
        if attrs["title"].strip().lower() == attrs["category"].strip().lower():
            raise serializers.ValidationError("Title and category cannot be the same.")
        
        return attrs