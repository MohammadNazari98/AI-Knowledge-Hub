from rest_framework.routers import DefaultRouter
from .views import DocumentAPIViewSet

router = DefaultRouter()
router.register("documents", DocumentAPIViewSet, basename="documents")

urlpatterns = router.urls