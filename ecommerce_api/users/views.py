from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from .models import CustomUser, UserProfile, UserActivity
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from .forms import CustomAuthenticationForm, UserRegistrationForm
from .utils import get_client_ip, is_staff_user, track_user_activity
from rest_framework.pagination import PageNumberPagination
from .serializers import UserActivitySerializer
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserProfileSerializer, UserAdminSerializer, UserProfileDetailSerializer
)

CustomUser = get_user_model()

# ===== UTILITY FUNCTIONS =====
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def is_staff_user(user):
    return user.is_staff

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ===== TEMPLATE VIEWS =====
def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


def login_template_view(request):
    """Template-based login view"""
    if request.method == 'GET':
        # Handle GET request - show the login form
        return render(request, 'users/login.html')
    
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            
            # Use the helper function for tracking
            track_user_activity(
                user=user,
                action='login',
                request=request,
                details={'method': 'template_login'}
            )
            
            return redirect('home')
        else:
            # Track failed login attempt
            try:
                user = CustomUser.objects.get(email=email)
                track_user_activity(
                    user=user,
                    action='login_failed',
                    request=request,
                    details={'reason': 'invalid_credentials'}
                )
            except CustomUser.DoesNotExist:
                pass
            
            messages.error(request, 'Invalid credentials')
            return render(request, 'users/login.html')  
    
    # Fallback for other methods
    return render(request, 'users/login.html')

def register_template_view(request):
    """Template-based registration view with form validation"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Create user with form data
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                
                # Create user profile
                UserProfile.objects.create(user=user)
                
                login(request, user)
                messages.success(request, 'Registration successful!')
                
                # Track registration activity
                UserActivity.objects.create(
                    user=user,
                    action='registration',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    details={'method': 'template_registration'}
                )
                
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        # Track logout activity
        UserActivity.objects.create(
            user=request.user,
            action='logout',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={}
        )
    
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def profile_template_view(request):
    """Template-based profile view"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Track which fields are being updated
        updated_fields = []
        original_data = {
            'phone_number': user.phone_number,
            'gender': user.gender,
            'date_of_birth': user.date_of_birth,
            'profile_picture': user.profile_picture,
            'accepts_marketing': user.accepts_marketing,
            'shipping_address': profile.shipping_address,
            'billing_address': profile.billing_address,
            'preferred_payment_method': profile.preferred_payment_method,
            'newsletter_subscription': profile.newsletter_subscription
        }
        
        # Handle profile update
        user.phone_number = request.POST.get('phone_number')
        user.gender = request.POST.get('gender')
        user.date_of_birth = request.POST.get('date_of_birth')
        user.profile_picture = request.POST.get('profile_picture')
        user.accepts_marketing = bool(request.POST.get('accepts_marketing'))
        
        # Check which fields changed
        if user.phone_number != original_data['phone_number']:
            updated_fields.append('phone_number')
        if user.gender != original_data['gender']:
            updated_fields.append('gender')
        if user.date_of_birth != original_data['date_of_birth']:
            updated_fields.append('date_of_birth')
        if user.profile_picture != original_data['profile_picture']:
            updated_fields.append('profile_picture')
        if user.accepts_marketing != original_data['accepts_marketing']:
            updated_fields.append('accepts_marketing')
        
        user.save()
        
        # Update profile fields
        profile.shipping_address = request.POST.get('shipping_address', '')
        profile.billing_address = request.POST.get('billing_address', '')
        profile.preferred_payment_method = request.POST.get('preferred_payment_method', '')
        profile.newsletter_subscription = bool(request.POST.get('newsletter_subscription'))
        
        # Check profile fields changes
        if profile.shipping_address != original_data['shipping_address']:
            updated_fields.append('shipping_address')
        if profile.billing_address != original_data['billing_address']:
            updated_fields.append('billing_address')
        if profile.preferred_payment_method != original_data['preferred_payment_method']:
            updated_fields.append('preferred_payment_method')
        if profile.newsletter_subscription != original_data['newsletter_subscription']:
            updated_fields.append('newsletter_subscription')
        
        profile.save()
        
        # Track profile update activity only if fields were actually changed
        if updated_fields:
            UserActivity.objects.create(
                user=user,
                action='profile_update',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'updated_fields': updated_fields}
            )
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile-template')
    
    return render(request, 'users/profile.html', {'user': user, 'profile': profile})

@login_required
@user_passes_test(is_staff_user)
def user_list_template_view(request):
    """Template-based user list view (admin only)"""
    users = CustomUser.objects.all().select_related('user_profile')
    
    # Track admin viewing user list
    UserActivity.objects.create(
        user=request.user,
        action='admin_view_user_list',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={}
    )
    
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_staff_user)
def admin_dashboard(request):
    """Admin dashboard with user statistics"""
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    new_users_today = CustomUser.objects.filter(
        date_joined__date=timezone.now().date()
    ).count()
    
    # User activity statistics
    recent_activities = UserActivity.objects.select_related('user').order_by('-timestamp')[:10]
    
    # Track admin viewing dashboard
    UserActivity.objects.create(
        user=request.user,
        action='admin_view_dashboard',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        details={}
    )
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'user_roles': CustomUser.objects.values('role').annotate(count=Count('id')),
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin/dashboard.html', context)

# ===== API VIEWS =====
class UserRegistrationView(APIView):
    """API View for user registration."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            
            tokens = get_tokens_for_user(user)
            
            # Track registration activity
            UserActivity.objects.create(
                user=user,
                action='registration',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'method': 'api_registration'}
            )
            
            return Response(
                {
                    'message': 'Registration Successful',
                    'tokens': tokens,
                    'user': UserProfileSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    """API View for user login."""
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            
            # Track login activity
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                details={'method': 'api_login'}
            )
            
            return Response(
                {
                    'message': 'Login Success',
                    'tokens': tokens,
                    'user': UserProfileSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        else:
            # Track failed login attempt
            email = request.data.get('email')
            if email:
                try:
                    user = CustomUser.objects.get(email=email)
                    UserActivity.objects.create(
                        user=user,
                        action='login_failed',
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        details={'reason': 'invalid_credentials_api'}
                    )
                except CustomUser.DoesNotExist:
                    pass
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveUpdateAPIView):
    """API View for users to see and update their own profile."""
    serializer_class = UserProfileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Track profile update via API
        UserActivity.objects.create(
            user=request.user,
            action='profile_update',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api_update', 'updated_fields': list(request.data.keys())}
        )
        
        return response

class UserViewSet(ModelViewSet):
    """API ViewSet for user operations with filtering, searching and ordering"""
    queryset = CustomUser.objects.all().select_related('user_profile')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = [
        'role', 'gender', 'is_active', 'email_verified', 
        'accepts_marketing', 'loyalty_tier'
    ]
    
    search_fields = [
        'email', 'phone_number', 'first_name', 'last_name',
        'user_profile__shipping_address', 'user_profile__billing_address'
    ]
    
    ordering_fields = [
        'date_joined', 'email', 'date_of_birth', 'last_login',
        'user_profile__loyalty_points'
    ]
    
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.request.user.is_staff:
            return UserAdminSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return CustomUser.objects.all().select_related('user_profile')
        return CustomUser.objects.filter(id=self.request.user.id).select_related('user_profile')
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        # Track profile view via API
        UserActivity.objects.create(
            user=request.user,
            action='profile_view',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api_view'}
        )
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Track profile update via API
        UserActivity.objects.create(
            user=request.user,
            action='profile_update',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api_update_me', 'updated_fields': list(request.data.keys())}
        )
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """Deactivate user (admin only)"""
        user = self.get_object()
        user.is_active = False
        user.save()
        
        # Track deactivation activity
        UserActivity.objects.create(
            user=user,
            action='deactivation',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'performed_by': request.user.email, 'method': 'api'}
        )
        
        return Response({'status': 'user deactivated'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def promote_to_staff(self, request, pk=None):
        """Promote user to staff (admin only)"""
        user = self.get_object()
        user.role = CustomUser.Role.STAFF
        user.is_staff = True
        user.save()
        
        # Track promotion activity
        UserActivity.objects.create(
            user=user,
            action='promotion_to_staff',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'performed_by': request.user.email, 'method': 'api'}
        )
        
        return Response({'status': 'user promoted to staff'})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def statistics(self, request):
        """Get user statistics (admin only)"""
        # Track admin viewing statistics
        UserActivity.objects.create(
            user=request.user,
            action='admin_view_statistics',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api'}
        )
        
        stats = {
            'total_users': CustomUser.objects.count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'new_users_today': CustomUser.objects.filter(
                date_joined__date=timezone.now().date()
            ).count(),
            'users_by_role': CustomUser.objects.values('role').annotate(count=Count('id')),
        }
        return Response(stats)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_login_view(request):
    """API login endpoint"""
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        
        # Track login activity
        UserActivity.objects.create(
            user=user,
            action='login',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            details={'method': 'api_session_login'}
        )
        
        user_serializer = UserProfileSerializer(user)
        return Response({
            'user': user_serializer.data,
            'message': 'Login successful'
        })
    return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

class EmailVerificationView(APIView):
    """Send and verify email confirmation"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Send verification email logic
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            
            # Use the send_verification_email function
            send_verification_email(user, request)
            
            return Response({'message': 'Verification email sent'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def get(self, request, token=None):
        if token:
            # Only create activity if user is authenticated
            if request.user.is_authenticated:
                UserActivity.objects.create(
                    user=request.user,  # Don't allow None
                    action='email_verified',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                    details={'method': 'api', 'token': token}
                )
            
            # TODO: Implement actual token verification logic here
            # For now, just return success
            return Response({'message': 'Email verified successfully'})
        else:
            # Handle case where no token is provided
            return Response({'error': 'Token required'}, status=status.HTTP_400_BAD_REQUEST)

def send_verification_email(user, request):
    """
    Send verification email to user
    Implement your actual email sending logic here
    """
    # TODO: Implement actual email sending logic
    # This would typically:
    # 1. Generate a verification token
    # 2. Create a verification link
    # 3. Send email with the link
    
    # Track email sending activity
    UserActivity.objects.create(
        user=user,
        action='verification_email_sent',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        details={'method': 'api'}
    )
    
    return True  # Return True to indicate success

def verify_email_template(request, token):
    """Template view for email verification"""
    # Only create activity if user is authenticated
    if request.user.is_authenticated:
        UserActivity.objects.create(
            user=request.user,  # Don't allow None
            action='email_verification_attempt',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
            details={'method': 'template', 'token': token}
        )
    
    # DEFINE the context variable here (this was missing)
    context = {'token': token, 'verified': False}
    
    # Simulate verification for now (replace with actual verification logic)
    if token:  # Replace with actual verification logic
        context['verified'] = True
        # Use Django's messages framework if needed
        from django.contrib import messages
        messages.success(request, 'Email verified successfully!')
    
    return render(request, 'users/verify_email.html', context)

# Utility function 
def log_user_activity(user, action, request, details=None):
    """Helper to create a user activity log entry."""
    if user and user.is_authenticated:
        UserActivity.objects.create(
            user=user,
            action=action,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],  
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_activity_view(request):
    """
    Retrieve the authenticated user's activity history.

    Features:
    - Tracks when a user views their own activity.
    - Returns paginated activity list.
    - Uses serializer for consistent formatting.
    """
    # Log this action
    log_user_activity(
        user=request.user,
        action="view_own_activities",
        request=request,
        details={"method": "api"},
    )

    # Get user activities ordered by latest
    queryset = UserActivity.objects.filter(user=request.user).order_by("-timestamp")

    # Paginate results
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_qs = paginator.paginate_queryset(queryset, request)

    serializer = UserActivitySerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serializer.data)
