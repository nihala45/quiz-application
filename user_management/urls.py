from django.urls import path, include
from .views import UserRegisterView, VerifyOTPView, LoginView,UserLogoutView, AdminLoginView, AdminLogoutView
from rest_framework.routers import DefaultRouter
router = DefaultRouter()


urlpatterns = [
    path('user/register/',UserRegisterView.as_view(), name='user_register'),
    path('user/verify_otp/<int:pk>/',VerifyOTPView.as_view(), name='verify_otp'),
    path('user/login/',LoginView.as_view(), name='user-login'),
    path('user/logout/',UserLogoutView.as_view(), name='user-logout'),
    
    path('admin/login/',AdminLoginView.as_view(), name='admin-login'),
    path('admin/logout/',AdminLogoutView.as_view(), name='admin-logout'),
    
    
    path('', include(router.urls)),
]