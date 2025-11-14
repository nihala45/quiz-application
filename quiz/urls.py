# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'quizzes', views.QuizViewSet, basename='quiz')
router.register(r'questions', views.QuestionViewSet, basename='question')
router.register(r'user-quiz', views.QuizUserViewSet, basename='user-quiz')

urlpatterns = [
    path('', include(router.urls)),
]