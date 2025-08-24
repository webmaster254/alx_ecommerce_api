from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for all existing users who don\'t have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Display detailed output for each user',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        users_without_profile = User.objects.filter(user_profile__isnull=True)
        verbose = options['verbose']
        
        total_count = users_without_profile.count()
        
        self.stdout.write(f'Found {total_count} users without profiles')
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have profiles!'))
            return
        
        created_count = 0
        for user in users_without_profile:
            try:
                UserProfile.objects.create(user=user)
                created_count += 1
                if verbose:
                    self.stdout.write(f'✓ Created profile for user: {user.email}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Failed to create profile for {user.email}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created profiles for {created_count} out of {total_count} users'
            )
        )