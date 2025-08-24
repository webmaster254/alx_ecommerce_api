from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserActivity

class Command(BaseCommand):
    help = 'Create registration activities for existing users'

    def handle(self, *args, **options):
        CustomUser = get_user_model()
        users_without_registration_activity = CustomUser.objects.filter(
            user_activities__action='registration'
        ).exclude(
            user_activities__action='registration'
        ).distinct()

        created_count = 0
        for user in users_without_registration_activity:
            UserActivity.objects.create(
                user=user,
                action='registration',
                ip_address='127.0.0.1',
                user_agent='Backfill System',
                details={'method': 'backfill'}
            )
            created_count += 1
            self.stdout.write(f'Created registration activity for {user.email}')

        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} registration activities')
        )