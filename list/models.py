from django.db import models

class Item(models.Model):
    title = models.CharField(max_length=200)          # Short text field
    description = models.TextField()                   # Long text field (no limit)
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)      # Auto-updated on every save

    def __str__(self):
        return self.title 