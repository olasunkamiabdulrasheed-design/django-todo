"""Small template helpers used across the task templates."""

from django import template
from django.contrib.messages import constants as message_constants

from list.filters import SORT_CHOICES

register = template.Library()

# Icon per Django message level.
_MESSAGE_ICONS = {
    message_constants.SUCCESS: '✓',
    message_constants.ERROR: '!',
    message_constants.WARNING: '!',
    message_constants.INFO: 'ℹ',
    message_constants.DEBUG: 'ℹ',
}


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
def message_icon(message):
    """Return the glyph for a message, keyed on its level.

    ``message.tags`` can't be used for this: ``settings.MESSAGE_TAGS`` replaces
    the level name ("success", "error", …) with CSS classes, so a check like
    ``'success' in message.tags`` never matches. The numeric level is stable.
    """
    return _MESSAGE_ICONS.get(getattr(message, 'level', None), 'ℹ')


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
