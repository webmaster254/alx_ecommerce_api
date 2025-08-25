from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models import Count  

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.Role.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        CUSTOMER = 'CUSTOMER', 'Customer'
        VENDOR = 'VENDOR', 'Vendor'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    date_of_birth = models.DateField(blank=True, null=True, help_text="Format: YYYY-MM-DD")
    GENDER_CHOICES = (
        ('M', 'Male'), 
        ('F', 'Female'), 
        ('O', 'Other'), 
        ('N', 'Prefer not to say')
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    accepts_marketing = models.BooleanField(default=False, help_text="User agrees to receive marketing emails.")
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    registration_ip = models.GenericIPAddressField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)

    profile_picture = models.ImageField(blank=True, null=True, help_text="Optional. You can add a profile picture later.")
    loyalty_tier = models.CharField(max_length=50, blank=True, default='Standard')
    internal_note = models.TextField(blank=True, null=True, help_text="Private notes for staff about this user.")

     # Engagement features 
    favorites = models.ManyToManyField("products.Product", related_name="favorited_by", blank=True)


    class Meta:
        permissions = [
            ("can_view_customer_list", "Can view the list of all customers"),
            ("can_deactivate_user", "Can deactivate a user account"),
            ("can_promote_to_staff", "Can assign a user to the Staff role"),
            ("can_manage_vendors", "Can manage vendor accounts"),
        ]

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    def is_staff_user(self): 
        return self.role == self.Role.STAFF
    
    def is_customer_user(self): 
        return self.role == self.Role.CUSTOMER
    
    def is_vendor_user(self):
        return self.role == self.Role.VENDOR
    
    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    @property
    def order_count(self):
        """Get the number of orders for this user"""
        if hasattr(self, 'orders'):
            return self.orders.count()
        return 0


class UserProfile(models.Model):
    user = models.OneToOneField(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='user_profile'  
    )
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    preferred_payment_method = models.CharField(max_length=100, blank=True)
    cart = models.JSONField(default=dict)
    newsletter_subscription = models.BooleanField(default=False)
    loyalty_points = models.IntegerField(default=0) 
    def __str__(self):
        return f"{self.user.email}'s Profile"
    
    def get_order_history(self):
        """Get user's order history - this will work once orders are defined"""
        if hasattr(self.user, 'orders'):
            return self.user.orders.all()
        return []


class UserActivity(models.Model):
    class ActivityType(models.TextChoices):
        LOGIN = 'LOGIN', 'User Login'
        LOGOUT = 'LOGOUT', 'User Logout'
        PURCHASE = 'PURCHASE', 'Made a Purchase'
        WISHLIST_ADD = 'WISHLIST_ADD', 'Added to Wishlist'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_activities')
    action = models.CharField(max_length=100, choices=ActivityType.choices)  # <-- enforce choices
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User activities'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
    ]

    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
