from django.db import models
from django.utils import timezone

class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True, db_index=True)  # Added db_index
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Added db_index
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)  # Added updated_at
    
    class Meta:
        verbose_name_plural = "Waitlist Entries"
        ordering = ['-created_at']  # Latest entries first
    
    def __str__(self):
        return self.email