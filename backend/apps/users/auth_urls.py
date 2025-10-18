from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views

app_name = 'auth'

urlpatterns = [
    path('register/', auth_views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('token/refresh/', auth_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
]
