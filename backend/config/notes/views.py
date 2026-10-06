from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.serializers import Serializer
from .permissions import IsOwnerOrReadOnly
from .pagination import NotePagination


class NoteListAPIView(APIView):
    
    def get(self, request: Request):
        note = Note.objects.all()
        serializer = NoteSerializer(note, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Request):
        serializer = NoteSerializer(data=request.data)
        
        if (serializer.is_valid()):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class NoteDetailAPIView(APIView):
    
    def get(self, request: Request, pk):
        note = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(note)

        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request: Request, pk):
        note = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(note, request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request: Request, pk):
        note = get_object_or_404(Note, pk=pk)
        serializer = NoteSerializer(note, request.data, partial=True)
        if (serializer.is_valid()):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request: Request, pk):
        note = get_object_or_404(Note, pk=pk)
        
        note.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class NoteListGenericAPIView(ListCreateAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    
    
class NoteDetailGenericAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    
    
class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    pagination_class = NotePagination
    filterset_fields = ["category"]
    search_fields = ["title", "content", "category"]
    ordering_fields = ["created_at", "updated_at", "title", "category"]
    
    def get_permissions(self):
        if self.request.method == "GET":
            return [IsOwnerOrReadOnly()]
        return [IsAuthenticated(), IsOwnerOrReadOnly()]
    
    def perform_create(self, serializer: Serializer):
        serializer.save(owner=self.request.user)