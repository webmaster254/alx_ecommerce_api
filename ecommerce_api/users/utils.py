# users/utils.py
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required

CustomUser = get_user_model()

def get_client_ip(request):
    """
    Get the client's IP address from the request.
    Handles proxies and various header configurations.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Extract the first IP from the X-Forwarded-For header
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def is_staff_user(user):
    """
    Check if the user is staff or superuser.
    Can be used with @user_passes_test decorator.
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_admin_user(user):
    """
    Check if the user is an admin (superuser).
    """
    return user.is_authenticated and user.is_superuser

def get_user_agent(request):
    """
    Extract user agent from request.
    """
    return request.META.get('HTTP_USER_AGENT', 'Unknown')

def track_user_activity(user, action, request, details=None):
    """
    Helper function to track user activity.
    """
    from .models import UserActivity
    
    if details is None:
        details = {}
    
    return UserActivity.objects.create(
        user=user,
        action=action,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        details=details
    )

def validate_email_domain(email):
    """
    Basic email domain validation.
    Returns True if email domain is valid, False otherwise.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_phone_number(phone_number):
    """
    Basic phone number formatting.
    You can enhance this based on your requirements.
    """
    if not phone_number:
        return None
    
    # Remove any non-digit characters
    cleaned = ''.join(filter(str.isdigit, str(phone_number)))
    
    # Simple formatting - adjust based on your needs
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    elif len(cleaned) == 11 and cleaned[0] == '1':
        return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
    
    return phone_number  # Return original if format doesn't match

def calculate_age(date_of_birth):
    """
    Calculate age from date of birth.
    """
    from datetime import date
    
    if not date_of_birth:
        return None
    
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )

def generate_username(email):
    """
    Generate a username from email address.
    """
    if not email:
        return None
    return email.split('@')[0]

def check_password_strength(password):
    """
    Basic password strength checker.
    Returns a strength score (0-4) and suggestions.
    """
    import re
    
    score = 0
    suggestions = []
    
    # Check length
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Password should be at least 8 characters long")
    
    # Check for uppercase
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        suggestions.append("Include uppercase letters")
    
    # Check for lowercase
    if re.search(r'[a-z]', password):
        score += 1
    else:
        suggestions.append("Include lowercase letters")
    
    # Check for numbers
    if re.search(r'[0-9]', password):
        score += 1
    else:
        suggestions.append("Include numbers")
    
    # Check for special characters
    if re.search(r'[^A-Za-z0-9]', password):
        score += 1
    else:
        suggestions.append("Include special characters")
    
    return {
        'score': score,
        'max_score': 5,
        'suggestions': suggestions,
        'is_strong': score >= 3
    }