from rest_framework.routers import DefaultRouter

from .views import workspaceViewSet


router = DefaultRouter()
router.register("workspaces", workspaceViewSet, basename="workspace")


urlpatterns = router.urls