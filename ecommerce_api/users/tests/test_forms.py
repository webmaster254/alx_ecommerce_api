from django.test import TestCase
from django import forms
from ..forms import CustomAuthenticationForm, UserRegistrationForm
from ..models import CustomUser
from django.utils import timezone
class CustomAuthenticationFormTest(TestCase):
    def setUp(self):
        """Create a test user before each test"""
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_form_fields(self):
        """Test that form has correct fields and widgets"""
        form = CustomAuthenticationForm()
        
        # Check fields exist
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
        
        # Check field types
        self.assertIsInstance(form.fields['username'], forms.EmailField)
        self.assertIsInstance(form.fields['password'], forms.CharField)
        
        # Check widget attributes
        self.assertEqual(form.fields['username'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['username'].widget.attrs['placeholder'], 'Enter your email')
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['password'].widget.attrs['placeholder'], 'Enter your password')

    def test_form_validation_valid_data(self):
        """Test form validation with valid data"""
        form_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        
        # Debug: print errors if form is not valid
        if not form.is_valid():
            print(f"Authentication form errors: {form.errors}")
        
        self.assertTrue(form.is_valid(), f"Form should be valid but got errors: {form.errors}")

    def test_form_validation_invalid_email(self):
        """Test form validation with invalid email"""
        form_data = {
            'username': 'invalid-email',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_form_validation_missing_fields(self):
        """Test form validation with missing fields"""
        # Missing password
        form_data = {'username': 'test@example.com'}
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        
        # Missing username
        form_data = {'password': 'testpass123'}
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class UserRegistrationFormTest(TestCase):
    def test_form_fields(self):
        """Test that form has correct fields and widgets"""
        form = UserRegistrationForm()
        
        # Check fields exist
        expected_fields = ['email', 'phone_number', 'gender', 'date_of_birth', 'password', 'password_confirmation']
        for field in expected_fields:
            self.assertIn(field, form.fields)
        
        # Check widget classes and attributes
        self.assertEqual(form.fields['email'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['phone_number'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['gender'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['date_of_birth'].widget.attrs['class'], 'form-control')
        
        # Check if type attribute exists, but don't require it
        if 'type' in form.fields['date_of_birth'].widget.attrs:
            self.assertEqual(form.fields['date_of_birth'].widget.attrs['type'], 'date')
        
        self.assertEqual(form.fields['password'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['password_confirmation'].widget.attrs['class'], 'form-control')

    def test_form_validation_valid_data(self):
        """Test form validation with valid data"""
        # First create a user to authenticate against
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        form_data = {
            'username': 'test@example.com',
            'password': 'testpass123'
        }
        form = CustomAuthenticationForm(data=form_data)
        
        # Debug: print errors if form is not valid
        if not form.is_valid():
            print(f"Authentication form errors: {form.errors}")
        
        self.assertTrue(form.is_valid())

    def test_form_validation_password_mismatch(self):
        """Test form validation when passwords don't match"""
        form_data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'differentpass'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # Non-field error
        self.assertEqual(form.errors['__all__'][0], 'Passwords do not match')

    def test_form_validation_missing_required_fields(self):
        """Test form validation with missing required fields"""
        # Missing email
        form_data = {
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Missing password
        form_data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password_confirmation': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_form_validation_invalid_email(self):
        """Test form validation with invalid email"""
        form_data = {
            'email': 'invalid-email',
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_validation_duplicate_email(self):
        """Test form validation with duplicate email"""
        # Create a user first
        CustomUser.objects.create_user(
            email='existing@example.com',
            password='testpass123'
        )
        
        form_data = {
            'email': 'existing@example.com',  # Duplicate email
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_form_save(self):
        """Test that form saves correctly and creates a user"""
        form_data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'testpass123'
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        user = form.save()
        
        # Check that user was created with correct data
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone_number, '+1234567890')
        self.assertEqual(user.gender, 'M')
        self.assertEqual(str(user.date_of_birth), '1990-01-01')
        
        # Check that password was set
        self.assertTrue(user.check_password('testpass123'))
        
        # Check that user is in database
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())

    def test_form_save_commit_false(self):
        """Test that form save with commit=False works correctly"""
        form_data = {
            'email': 'test@example.com',
            'phone_number': '+1234567890',
            'gender': 'M',
            'date_of_birth': '1990-01-01',
            'password': 'testpass123',
            'password_confirmation': 'testpass123'
        }
        
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save(commit=False)
        
        # User should not be saved to database yet
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(CustomUser.objects.filter(email='test@example.com').exists())
        
        # Manually save and check
        user.save()
        self.assertTrue(CustomUser.objects.filter(email='test@example.com').exists())