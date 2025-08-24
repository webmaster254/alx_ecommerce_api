from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import CustomUser, UserProfile, UserActivity

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    list_display = ['user_email', 'loyalty_points', 'newsletter_subscription', 'preferred_payment_method']
    list_filter = ['newsletter_subscription', 'loyalty_points']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'shipping_address', 'billing_address']
    readonly_fields = ['user_link']
    fieldsets = (
        ('User Information', {
            'fields': ('user_link',)
        }),
        ('Address Information', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Preferences', {
            'fields': ('preferred_payment_method', 'newsletter_subscription', 'loyalty_points')
        }),
        ('Cart Data', {
            'fields': ('cart',),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
    def user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    
    def has_add_permission(self, request):
        return False

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin interface for UserActivity model"""
    list_display = ['user_email', 'action', 'ip_address', 'timestamp', 'truncated_user_agent']
    list_filter = ['action', 'timestamp', 'user__role']
    search_fields = ['user__email', 'ip_address', 'action', 'user_agent']
    readonly_fields = ['user_link', 'timestamp', 'ip_address', 'user_agent', 'details_display']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('user_link', 'action', 'timestamp')
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent', 'details_display'),
            'classes': ('collapse',)
        })
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.email)
    user_link.short_description = 'User'
    
    def truncated_user_agent(self, obj):
        if obj.user_agent and len(obj.user_agent) > 50:
            return obj.user_agent[:50] + '...'
        return obj.user_agent
    truncated_user_agent.short_description = 'User Agent'
    
    def details_display(self, obj):
        if obj.details:
            return format_html('<pre>{}</pre>', str(obj.details))
        return '-'
    details_display.short_description = 'Details'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'
    readonly_fields = ['loyalty_points']
    fields = [
        'shipping_address', 'billing_address', 'preferred_payment_method',
        'newsletter_subscription', 'loyalty_points', 'cart'
    ]
    
    def has_add_permission(self, request, obj):
        return False

class UserActivityInline(admin.TabularInline):
    """Inline admin for UserActivity"""
    model = UserActivity
    extra = 0
    max_num = 10
    can_delete = False
    readonly_fields = ['action', 'ip_address', 'timestamp', 'truncated_user_agent']
    fields = ['action', 'ip_address', 'timestamp', 'truncated_user_agent']
    
    def truncated_user_agent(self, obj):
        if obj.user_agent and len(obj.user_agent) > 30:
            return obj.user_agent[:30] + '...'
        return obj.user_agent
    truncated_user_agent.short_description = 'User Agent'
    
    def has_add_permission(self, request, obj):
        return False

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser model"""
    inlines = [UserProfileInline, UserActivityInline]
    
    list_display = [
        'email', 'first_name', 'last_name', 'role', 'is_active',
        'email_verified', 'date_joined', 'last_login', 'age'
    ]
    
    list_filter = [
        'role', 'is_active', 'email_verified', 'phone_verified',
        'accepts_marketing', 'gender', 'date_joined'
    ]
    
    search_fields = ['email', 'first_name', 'last_name', 'phone_number']
    
    ordering = ['-date_joined']
    
    readonly_fields = [
        'date_joined', 'last_login', 'registration_ip', 'last_login_ip',
        'age_display', 'user_activities_link'
    ]
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'profile_picture')
        }),
        ('Contact Info', {
            'fields': ('phone_number', 'phone_verified')
        }),
        ('Permissions', {
            'fields': (
                'role', 'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        ('Preferences', {
            'fields': ('accepts_marketing', 'loyalty_tier')
        }),
        ('Verification', {
            'fields': ('email_verified',)
        }),
        ('Internal Information', {
            'fields': ('internal_note',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'date_joined', 'last_login', 'registration_ip',
                'last_login_ip', 'age_display', 'user_activities_link'
            ),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name')
        }),
        ('Additional Info', {
            'fields': ('date_of_birth', 'gender', 'phone_number', 'accepts_marketing')
        })
    )
    
    filter_horizontal = ('groups', 'user_permissions',)
    
    def age_display(self, obj):
        return obj.age or 'N/A'
    age_display.short_description = 'Age'
    
    def user_activities_link(self, obj):
        count = obj.user_activities.count()
        url = reverse('admin:users_useractivity_changelist') + f'?user__id__exact={obj.id}'
        return format_html('<a href="{}">{} Activities</a>', url, count)
    user_activities_link.short_description = 'Activities'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('user_activities')
    
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))  
        if obj:  
            readonly_fields.append('email')  
        return readonly_fields  #
    
    def get_inlines(self, request, obj):
        if obj:
            return [UserProfileInline, UserActivityInline]
        return []
    
    def save_model(self, request, obj, form, change):
        if not change:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                obj.registration_ip = x_forwarded_for.split(',')[0]
            else:
                obj.registration_ip = request.META.get('REMOTE_ADDR')
        super().save_model(request, obj, form, change)

# Custom admin site configuration
admin.site.site_header = 'E-Commerce Administration'
admin.site.site_title = 'E-Commerce Admin Portal'
admin.site.index_title = 'Welcome to E-Commerce Administration'

# Custom actions
def make_users_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)
make_users_inactive.short_description = "Mark selected users as inactive"

def verify_users_email(modeladmin, request, queryset):
    queryset.update(email_verified=True)
verify_users_email.short_description = "Verify email for selected users"

def promote_to_staff(modeladmin, request, queryset):
    queryset.update(role=CustomUser.Role.STAFF)
promote_to_staff.short_description = "Promote to Staff role"

CustomUserAdmin.actions = [make_users_inactive, verify_users_email, promote_to_staff]