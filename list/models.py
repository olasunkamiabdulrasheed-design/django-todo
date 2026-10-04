"""Domain models for the task list app."""

from django.db import models
from django.urls import reverse
from django.utils import timezone


class Item(models.Model):
    """A single task."""

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    # Tailwind classes rendered on the priority pill in the templates.
    PRIORITY_BADGE = {
        PRIORITY_LOW: 'bg-sky-100 text-sky-700 ring-sky-200 dark:bg-sky-500/15 dark:text-sky-300 dark:ring-sky-500/30',
        PRIORITY_MEDIUM: 'bg-amber-100 text-amber-700 ring-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:ring-amber-500/30',
        PRIORITY_HIGH: 'bg-rose-100 text-rose-700 ring-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:ring-rose-500/30',
    }

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    category = models.CharField(
        max_length=60,
        blank=True,
        help_text='Optional grouping, e.g. "Work" or "Groceries".',
    )
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['completed', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['completed']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('item_detail', args=[self.pk])

    # ── Presentation helpers ──────────────────────────────────────────────

    def priority_badge_class(self):
        """Tailwind classes for this task's priority pill."""
        return self.PRIORITY_BADGE.get(self.priority, self.PRIORITY_BADGE[self.PRIORITY_MEDIUM])

    @property
    def priority_rank(self):
        """Sort key where High > Medium > Low."""
        return {self.PRIORITY_HIGH: 3, self.PRIORITY_MEDIUM: 2, self.PRIORITY_LOW: 1}.get(
            self.priority, 0
        )

    # ── Date helpers ──────────────────────────────────────────────────────

    @property
    def is_overdue(self):
        """True when the task has a due date in the past and is still open."""
        return bool(
            self.due_date
            and not self.completed
            and self.due_date < timezone.localdate()
        )

    @property
    def is_due_today(self):
        return bool(self.due_date and not self.completed and self.due_date == timezone.localdate())

    @property
    def days_left(self):
        """Days until the due date; negative when overdue, None when undated."""
        if not self.due_date:
            return None
        return (self.due_date - timezone.localdate()).days

    # ── Persistence ───────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        # Keep completed_at in sync with the completed flag so callers never
        # have to remember to set both.
        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None

        # When a caller passes an explicit update_fields list, any field we
        # just changed is silently dropped unless we add it back. An empty
        # list is left alone so Django still rejects it.
        update_fields = kwargs.get('update_fields')
        if update_fields:
            kwargs['update_fields'] = set(update_fields) | {'completed_at'}

        super().save(*args, **kwargs)
