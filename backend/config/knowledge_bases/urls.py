from rest_framework.routers import DefaultRouter
from .views import KnowledgeBaseAPIViewSet

router = DefaultRouter()
router.register("knowledge-bases", KnowledgeBaseAPIViewSet, basename="knowledge_bases")

urlpatterns = router.urls