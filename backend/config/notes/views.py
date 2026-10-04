from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer
from django.shortcuts import get_object_or_404



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