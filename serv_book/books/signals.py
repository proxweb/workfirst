from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import BookAndUser, StoryBook

@receiver(post_delete, sender=BookAndUser)
def create_storybooks_entry(sender, instance, **kwargs):
    StoryBook.objects.create(
        user=instance.user,
        book=instance.book,
        begin_date=instance.received_date,
        end_date=timezone.now()  
    )
