from django.test import TestCase
from rest_framework.exceptions import ValidationError
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializerTest(TestCase):
    def test_create_user(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'ValidPass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('ValidPass123!'))

    def test_short_password(self):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'short'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_invalid_email(self):
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'newpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_missing_required_fields(self):
        # Test missing username
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

        # Test missing email
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

        # Test missing password
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)

    def test_duplicate_username(self):
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'newpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_duplicate_email(self):
        User.objects.create_user(
            username='user1',
            email='existing@example.com',
            password='testpass123'
        )
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'newpass123'
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)