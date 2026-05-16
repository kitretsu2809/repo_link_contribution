from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RepositoryViewSet

router = DefaultRouter()
router.register(r'repos', RepositoryViewSet, basename='repository')

urlpatterns = [
    path('', include(router.urls)),
]
