"""Dashboard statistics shown on the home page."""

from django.utils import timezone

from .models import Item


def task_stats(queryset=None):
    """Return a dict of headline numbers for the given (or all) tasks."""
    tasks = Item.objects.all() if queryset is None else queryset

    today = timezone.localdate()
    total = tasks.count()
    completed = tasks.filter(completed=True).count()
    overdue = tasks.filter(completed=False, due_date__lt=today).count()
    due_today = tasks.filter(completed=False, due_date=today).count()
    high_priority = tasks.filter(completed=False, priority=Item.PRIORITY_HIGH).count()

    return {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'overdue': overdue,
        'due_today': due_today,
        'high_priority': high_priority,
        'progress': round(completed / total * 100) if total else 0,
    }
