from rest_framework.viewsets import ModelViewSet
from workspaces.models import Workspace
from .models import KnowledgeBase
from .serializers import KnowledgeBaseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer


class KnowledgeBaseAPIViewSet(ModelViewSet):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        return KnowledgeBase.objects.filter(workspace__members=self.request.user).distinct().order_by("-created_at", "-id")
    
    def perform_create(self, serializer: Serializer):
        serializer.save(created_by=self.request.user)