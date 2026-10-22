from rest_framework.viewsets import ModelViewSet
from workspaces.models import Workspace
from .models import KnowledgeBase
from .serializers import KnowledgeBaseSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import Serializer
from rest_framework.decorators import action
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from documents.services.retrieval import KeywordRetriever
from documents.serializers import DocumentChunkSerializer


class KnowledgeBaseAPIViewSet(ModelViewSet):
    serializer_class = KnowledgeBaseSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_queryset(self):
        return KnowledgeBase.objects.filter(workspace__members=self.request.user).distinct().order_by("-created_at", "-id")
    
    def perform_create(self, serializer: Serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def search(self, request: HttpRequest, pk: int=None):
        query = request.GET.get("q","")
        keyword_retrieval = KeywordRetriever()
        results = list(keyword_retrieval.search(knowledge_id=pk, query=query))

        serializer = DocumentChunkSerializer(results, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)