from django.urls import path
from .views import NoteListAPIView, NoteDetailAPIView, NoteListGenericAPIView, NoteDetailGenericAPIView, NoteViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("notes-viewset", NoteViewSet, basename="note")


urlpatterns = [
    path("notes/", NoteListAPIView.as_view(), name="note-list"),
    path("notes/<int:pk>", NoteDetailAPIView.as_view(), name="note-detail"),
    path("notes-generic/", NoteListGenericAPIView.as_view(), name="note-list-generic"),
    path("notes-generic/<int:pk>", NoteDetailGenericAPIView.as_view(), name="note-detail-generic"),
]

urlpatterns += router.urls