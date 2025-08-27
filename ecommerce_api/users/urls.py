from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views as user_views
from .views import ( 
    UserViewSet, UserRegistrationView, UserLoginView, 
    UserProfileView, api_login_view, home_view,
    login_template_view, register_template_view,
    profile_template_view, user_list_template_view, logout_view,
    admin_dashboard , user_activity_view, EmailVerificationView, 
    verify_email_template  
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

api_urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('auth/login/', api_login_view, name='auth-login'),
    path('user/activity/', user_activity_view, name="user-activity"),
    path('verify-email/', EmailVerificationView.as_view(), name='email-verification'),
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='email-verification-token'),
]

# Template URLs (for browser access - under /users/)
template_urlpatterns = [ 
    path('web/login/', login_template_view, name='login-template'),  
    path('web/register/', register_template_view, name='user-register'),  
    path('web/profile/', profile_template_view, name='user-profile'),     
    path('web/users/', user_list_template_view, name='user-list-template'),
    path('web/logout/', logout_view, name='user-logout'),
    path('web/admin/dashboard/', admin_dashboard, name='admin-dashboard'),
    path('verify-email-template/<str:token>/', verify_email_template, name='verify-email-template'),
]

# Combine them
urlpatterns = api_urlpatterns + template_urlpatterns