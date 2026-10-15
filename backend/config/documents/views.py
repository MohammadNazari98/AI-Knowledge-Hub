from django.shortcuts import render
from .models import Document
from rest_framework.viewsets import ModelViewSet
from .serializers import DocumentSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer


class DocumentAPIViewSet(ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(knowledge_base__workspace__members=self.request.user).order_by("-created_at")
    
    def perform_create(self, serializer: Serializer):
        serializer.save(created_by=self.request.user)