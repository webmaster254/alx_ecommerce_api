from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Count
from .models import CustomUser, UserProfile, UserActivity


class UserProfileDataSerializer(serializers.ModelSerializer):  # Renamed to avoid conflict
    """Serializer for UserProfile model"""
    class Meta:
        model = UserProfile
        fields = [
            'shipping_address', 
            'billing_address', 
            'preferred_payment_method',
            'newsletter_subscription',
            'loyalty_points',
            'cart'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializes the user registration process. Handles creating a new user."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = (
            'id', 'email', 'password', 'password_confirmation', 'phone_number', 
            'date_of_birth', 'accepts_marketing', 'gender', 'first_name', 'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirmation': {'write_only': True},
        }

    def validate(self, data):
        """Validate that passwords match and date_of_birth is not in future"""
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError({"password_confirmation": "Passwords do not match."})
        
        if data.get('date_of_birth') and data['date_of_birth'] > timezone.now().date():
            raise serializers.ValidationError({"date_of_birth": "Date of birth cannot be in the future."})
        
        return data

    def create(self, validated_data):
        """Create a new user instance with the provided validated data."""
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password) 
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializes the user login process."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), username=email, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                msg = 'This account is inactive.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data


class UserProfileBaseSerializer(serializers.ModelSerializer):
    """Base serializer for user profile data"""
    age = serializers.ReadOnlyField()
    order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'role',
            'date_of_birth', 'gender', 'phone_number', 'profile_picture',
            'accepts_marketing', 'loyalty_tier', 'age', 'order_count',
            'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined', 'last_login']
    
    def get_order_count(self, obj):
        return obj.orders.count() if hasattr(obj, 'orders') else 0


class UserProfileSerializer(UserProfileBaseSerializer):
    """Serializer for regular user profile operations"""
    user_profile = UserProfileDataSerializer(read_only=True)  # Use the renamed serializer
    
    class Meta(UserProfileBaseSerializer.Meta):
        fields = UserProfileBaseSerializer.Meta.fields + ['user_profile']  # Fixed field name


class UserProfileDetailSerializer(UserProfileBaseSerializer):
    """Detailed serializer for user profile including profile data"""
    user_profile = UserProfileDataSerializer()  # Use the renamed serializer
    
    class Meta(UserProfileBaseSerializer.Meta):
        fields = UserProfileBaseSerializer.Meta.fields + ['user_profile']  # Fixed field name
    
    def update(self, instance, validated_data):
        """Handle nested profile update"""
        profile_data = validated_data.pop('user_profile', {})
        
        # Update user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create user profile
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        return instance


class UserAdminSerializer(UserProfileBaseSerializer):
    """Serializer for admin operations - includes all fields"""
    user_profile = UserProfileDataSerializer(read_only=True)  # Use the renamed serializer and consistent field name
    internal_note = serializers.CharField(read_only=True)
    registration_ip = serializers.IPAddressField(read_only=True)
    last_login_ip = serializers.IPAddressField(read_only=True)
    
    class Meta(UserProfileBaseSerializer.Meta):
        fields = UserProfileBaseSerializer.Meta.fields + [
            'email_verified', 'phone_verified', 'registration_ip', 
            'last_login_ip', 'internal_note', 'user_profile'  # Fixed field name
        ]
        read_only_fields = UserProfileBaseSerializer.Meta.read_only_fields + [
            'email_verified', 'phone_verified', 'registration_ip', 
            'last_login_ip'
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for user activity logs"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'action', 'ip_address', 
            'user_agent', 'timestamp', 'details'
        ]
        read_only_fields = fields


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer for user statistics"""
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    users_by_role = serializers.ListField(child=serializers.DictField())


# Additional serializers for specific operations
class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change operations"""
    current_password = serializers.CharField(write_only=True, min_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirmation = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError({
                "new_password_confirmation": "New passwords do not match."
            })
        return data


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification"""
    email = serializers.EmailField()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user updates (excluding sensitive fields)"""
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'date_of_birth',
            'gender', 'profile_picture', 'accepts_marketing'
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for profile updates"""
    class Meta:
        model = UserProfile
        fields = [
            'shipping_address', 'billing_address', 
            'preferred_payment_method', 'newsletter_subscription'
        ]