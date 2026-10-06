from rest_framework.permissions import BasePermission
from .models import Note
from rest_framework.request import HttpRequest

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request: HttpRequest, view, obj: Note):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        
        return obj.owner == request.user