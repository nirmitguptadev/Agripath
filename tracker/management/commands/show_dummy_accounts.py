from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Show login credentials for dummy farmers'

    def handle(self, *args, **kwargs):
        dummy_users = ['rajesh_kanpur', 'priya_farmer', 'amit_agri', 'sunita_crops', 'vikram_farm']
        
        self.stdout.write(self.style.SUCCESS('\n=== DUMMY FARMER ACCOUNTS ===\n'))
        
        for username in dummy_users:
            try:
                user = User.objects.get(username=username)
                profile = user.profile
                self.stdout.write(f"Username: {username}")
                self.stdout.write(f"Name: {profile.name}")
                self.stdout.write(f"Phone: {profile.phone_number}")
                self.stdout.write(f"Location: {profile.location}")
                self.stdout.write(f"Password: farmer123")
                self.stdout.write("-" * 50)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"User {username} not found"))
        
        self.stdout.write(self.style.WARNING('\nNote: Use Django admin to login with username/password'))
        self.stdout.write(self.style.WARNING('Or use the phone numbers with OTP (if Twilio is configured for test numbers)'))
