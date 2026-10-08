from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import WorkspaceSerializer
from rest_framework.serializers import Serializer
from .models import Workspace


class workspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Workspace.objects.filter(members=self.request.user).distinct().order_by("id")
    
    def perform_create(self, serializer: Serializer):
        workspace = serializer.save()
        workspace.members.add(self.request.user)