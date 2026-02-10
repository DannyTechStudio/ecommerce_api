from django.core.management.base import BaseCommand
from inventory.services import release_expired_reservations

class Command(BaseCommand):
    help = "Release expired inventory reservations and restore stock"
    
    def handle(self, *args, **options):
        self.stdout.write((self.style.WARNING("Checking for expired reservations...")))
        
        result = release_expired_reservations()
        
        self.stdout.write(self.style.SUCCESS("Expiration cleanup complete"))
        self.stdout.write(f"Expired found: {result['expired_found']}")
        self.stdout.write(f"Released: {result['release']}")
        self.stdout.write(f"Failed: {result['failed']}")