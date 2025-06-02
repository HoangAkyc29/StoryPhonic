from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    UserMeView,
    ProfileView,
    AdminUserViewSet,
    RoleViewSet,
    LoginView,
    ChangePasswordView,
    UpdateAvatarView
)
from .views.google_auth import GoogleLoginView, GoogleCallbackView

router = DefaultRouter()
router.register(r'admin/users', AdminUserViewSet, basename='admin-user')
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserMeView.as_view(), name='user-info'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/', LoginView.as_view(), name='token_obtain_pair'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('avatar/', UpdateAvatarView.as_view(), name='avatar'),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
    path('', include(router.urls)),
] 