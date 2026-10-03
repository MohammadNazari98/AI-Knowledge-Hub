from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .models import Note
from .serializers import NoteSerializer



class NoteListAPIView(APIView):
    
    def get(self, request: Request):
        note = Note.objects.all()
        serializer = NoteSerializer(note, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request: Request):
        serializer = NoteSerializer(data=request.data)
        
        if (serializer.is_valid()):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)