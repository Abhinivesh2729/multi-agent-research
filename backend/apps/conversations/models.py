import uuid
from django.db import models


class Conversation(models.Model):
    """Model to store research conversations."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.TextField()
    plan = models.TextField(blank=True)
    search_results = models.TextField(blank=True)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.question[:50]}... ({self.created_at})"
