"""Sorting options for the task list.

Kept separate from the views so the ordering table is easy to extend and to
unit-test on its own.
"""

DEFAULT_SORT = 'smart'

SORT_CHOICES = [
    ('smart', 'Smart'),
    ('newest', 'Newest'),
    ('oldest', 'Oldest'),
    ('due', 'Due date'),
    ('priority', 'Priority'),
    ('title', 'A → Z'),
]

# Maps the ?sort= value onto a model ordering tuple.
SORT_ORDERINGS = {
    'smart': ['completed', 'due_date', '-created_at'],
    'newest': ['-created_at'],
    'oldest': ['created_at'],
    'due': ['due_date', 'completed'],
    'priority': ['-priority', 'completed'],
    'title': ['title'],
}


def resolve_sort(value):
    """Return ``(sort_key, ordering)`` for a raw ``?sort=`` value.

    Falls back to the default ordering for unknown or missing input.
    """
    if value in SORT_ORDERINGS:
        return value, SORT_ORDERINGS[value]
    return DEFAULT_SORT, SORT_ORDERINGS[DEFAULT_SORT]
