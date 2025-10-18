from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import auth_views
from . import otp_views

app_name = 'auth'

urlpatterns = [
    path('register/', auth_views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('token/refresh/', auth_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('profile/', auth_views.profile_view, name='profile'),
    
    # OTP endpoints
    path('send-otp/', otp_views.SendOTPView.as_view(), name='send_otp'),
    path('verify-otp/', otp_views.VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', otp_views.ResendOTPView.as_view(), name='resend_otp'),
    path('otp-status/', otp_views.otp_status_view, name='otp_status'),
]
