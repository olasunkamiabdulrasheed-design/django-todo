"""Small template helpers used across the task templates."""

from django import template

from list.filters import SORT_CHOICES

register = template.Library()


@register.simple_tag
def sort_url(request, value):
    """Build a ?sort=<value> link that preserves the active filters."""
    params = request.GET.copy()
    params['sort'] = value
    params.pop('page', None)
    return f'?{params.urlencode()}'


@register.simple_tag
def sort_options():
    return SORT_CHOICES


@register.filter
def pluralize_count(value, singular='task'):
    """'1 task' / '3 tasks' — used in the results summary."""
    value = int(value or 0)
    return f'{value} {singular}' if value == 1 else f'{value} {singular}s'


@register.filter
def initials(value):
    """First letters of the first two words, for the category chip."""
    parts = [p for p in str(value or '').split() if p]
    return ''.join(p[0].upper() for p in parts[:2]) or '—'
