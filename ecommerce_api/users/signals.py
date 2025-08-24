from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile, UserActivity
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

def get_client_ip(request):
    """Get the client's IP address from the request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a new CustomUser is created.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save the UserProfile when the CustomUser is saved.
    """
    if hasattr(instance, 'user_profile'):
        instance.user_profile.save()

# Track user registrations - improved version
@receiver(post_save, sender=CustomUser)
def track_user_registration(sender, instance, created, **kwargs):
    if created:
        # Try to get request from kwargs (if passed during user creation)
        request = kwargs.get('request', None)
        ip_address = get_client_ip(request) if request else '127.0.0.1'
        user_agent = request.META.get('HTTP_USER_AGENT', 'System') if request else 'System'
        
        UserActivity.objects.create(
            user=instance,
            action='registration',
            ip_address=ip_address,
            user_agent=user_agent,
            details={'method': 'system_created'}
        )

# Track successful logins
@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    UserActivity.objects.create(
        user=user,
        action='login',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={'method': 'web_login'}
    )

# Track logouts
@receiver(user_logged_out)
def track_user_logout(sender, request, user, **kwargs):
    UserActivity.objects.create(
        user=user,
        action='logout',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={}
    )

# Track failed login attempts
@receiver(user_login_failed)
def track_login_failed(sender, credentials, request, **kwargs):
    email = credentials.get('username') or credentials.get('email')
    if email:
        try:
            user = CustomUser.objects.get(email=email)
            UserActivity.objects.create(
                user=user,
                action='login_failed',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'invalid_credentials'}
            )
        except CustomUser.DoesNotExist:
            UserActivity.objects.create(
                user=None,  
                action='login_failed',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'reason': 'user_not_found', 'attempted_email': email}
            )