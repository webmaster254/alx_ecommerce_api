from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import serializers
from django.utils import timezone
from datetime import date
from unittest.mock import patch
from users.models import CustomUser, UserProfile, UserActivity
from users.serializers import (
    UserProfileDataSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileBaseSerializer,
    UserProfileSerializer,
    UserProfileDetailSerializer,
    UserAdminSerializer,
    UserActivitySerializer,
    UserStatisticsSerializer,
    PasswordChangeSerializer,
    EmailVerificationSerializer,
    UserUpdateSerializer,
    ProfileUpdateSerializer
)

User = get_user_model()


class UserProfileDataSerializerTest(TestCase):
    """Test UserProfileDataSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.profile_data = {
            'shipping_address': '123 Test St',
            'billing_address': '456 Test Ave',
            'preferred_payment_method': 'credit_card',
            'newsletter_subscription': True,
            'loyalty_points': 100,
            'cart': {}
        }
    
    def test_serializer_valid_data(self):
        serializer = UserProfileDataSerializer(data=self.profile_data)
        self.assertTrue(serializer.is_valid())
    
    def test_serializer_missing_optional_fields(self):
        data = {
            'shipping_address': '123 Test St',
            'billing_address': '456 Test Ave'
        }
        serializer = UserProfileDataSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class UserRegistrationSerializerTest(TestCase):
    """Test UserRegistrationSerializer"""
    
    def setUp(self):
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirmation': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+1234567890',
            'date_of_birth': date(1990, 1, 1),
            'gender': 'M',
            'accepts_marketing': True
        }
    
    def test_valid_registration_data(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_mismatch(self):
        data = self.valid_data.copy()
        data['password_confirmation'] = 'differentpassword'
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirmation', serializer.errors)
    
    def test_future_date_of_birth(self):
        data = self.valid_data.copy()
        data['date_of_birth'] = date(2050, 1, 1)
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('date_of_birth', serializer.errors)
    
    def test_create_user(self):
        serializer = UserRegistrationSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')


class UserLoginSerializerTest(TestCase):
    """Test UserLoginSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    
    @patch('django.contrib.auth.signals.user_login_failed.send')
    def test_valid_login_data(self, mock_signal):
        serializer = UserLoginSerializer(data=self.valid_data, context={'request': None})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)
    
    @patch('django.contrib.auth.signals.user_login_failed.send')
    def test_invalid_credentials(self, mock_signal):
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
    
    def test_missing_email(self):
        data = {'password': 'testpass123'}
        serializer = UserLoginSerializer(data=data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)
    
    @patch('django.contrib.auth.signals.user_login_failed.send')
    def test_inactive_user(self, mock_signal):
        self.user.is_active = False
        self.user.save()
        
        serializer = UserLoginSerializer(data=self.valid_data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)


class UserProfileSerializerTest(TestCase):
    """Test UserProfile serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(1990, 1, 1),
            gender='M'
        )
        # Use the automatically created profile
        self.profile = self.user.user_profile
        self.profile.shipping_address = '123 Test St'
        self.profile.billing_address = '456 Test Ave'
        self.profile.save()
    
    def test_user_profile_base_serializer(self):
        serializer = UserProfileBaseSerializer(instance=self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], 'test@example.com')
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertEqual(data['order_count'], 0)
    
    def test_user_profile_serializer(self):
        serializer = UserProfileSerializer(instance=self.user)
        data = serializer.data
        
        self.assertIn('user_profile', data)
        self.assertEqual(data['user_profile']['shipping_address'], '123 Test St')
    
    def test_user_profile_detail_serializer_update(self):
        update_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'user_profile': {
                'shipping_address': '789 Updated St',
                'billing_address': '101 Updated Ave'
            }
        }
        
        serializer = UserProfileDetailSerializer(instance=self.user, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        
        updated_user = serializer.save()
        
        # Refresh from database to get the latest data
        updated_user.refresh_from_db()
        updated_user.user_profile.refresh_from_db()
        
        self.assertEqual(updated_user.first_name, 'Jane')
        self.assertEqual(updated_user.user_profile.shipping_address, '789 Updated St')


class UserAdminSerializerTest(TestCase):
    """Test UserAdminSerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
    
    def test_admin_serializer_fields(self):
        serializer = UserAdminSerializer(instance=self.user)
        data = serializer.data
        
        self.assertIn('email_verified', data)
        self.assertIn('phone_verified', data)
        self.assertIn('registration_ip', data)
        self.assertIn('user_profile', data)


class UserActivitySerializerTest(TestCase):
    """Test UserActivitySerializer"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.activity = UserActivity.objects.create(
            user=self.user,
            action='login',
            ip_address='127.0.0.1',
            user_agent='Test Browser'
        )
    
    def test_activity_serializer(self):
        serializer = UserActivitySerializer(instance=self.activity)
        data = serializer.data
        
        self.assertEqual(data['action'], 'login')
        self.assertEqual(data['user_email'], 'test@example.com')
        self.assertEqual(data['ip_address'], '127.0.0.1')


class MiscellaneousSerializersTest(TestCase):
    """Test other serializers"""
    
    def test_password_change_serializer(self):
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirmation': 'newpass123'
        }
        serializer = PasswordChangeSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_change_mismatch(self):
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password_confirmation': 'differentpass'
        }
        serializer = PasswordChangeSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirmation', serializer.errors)
    
    def test_email_verification_serializer(self):
        data = {'email': 'test@example.com'}
        serializer = EmailVerificationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_update_serializer(self):
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+1234567890'
        }
        serializer = UserUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_profile_update_serializer(self):
        data = {
            'shipping_address': 'New Address',
            'billing_address': 'New Billing Address'
        }
        serializer = ProfileUpdateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_user_statistics_serializer(self):
        data = {
            'total_users': 100,
            'active_users': 75,
            'new_users_today': 5,
            'users_by_role': [{'role': 'CUSTOMER', 'count': 80}]
        }
        serializer = UserStatisticsSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class SerializerIntegrationTest(APITestCase):
    """Integration tests for serializers with actual API calls"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirmation': 'testpass123',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    
    def test_registration_serializer_integration(self):
        # Test that serializer works with actual registration
        serializer = UserRegistrationSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        
        # Verify user was created properly
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.email, 'test@example.com')
        
        # Verify profile was created
        self.assertTrue(hasattr(user, 'user_profile'))