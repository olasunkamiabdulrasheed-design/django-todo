"""Sorting options for the task list.

Kept separate from the views so the ordering table is easy to extend and to
unit-test on its own.
"""

from django.db.models import Case, F, IntegerField, Value, When

from .models import Item

DEFAULT_SORT = 'smart'

SORT_CHOICES = [
    ('smart', 'Smart'),
    ('newest', 'Newest'),
    ('oldest', 'Oldest'),
    ('due', 'Due date'),
    ('priority', 'Priority'),
    ('title', 'A → Z'),
]

# Tasks with no due date belong at the *end* of a date-ordered list, but an
# ascending sort puts NULLs first on both SQLite and Postgres.
DUE_DATE_ASC = F('due_date').asc(nulls_last=True)

# Ordering by the stored priority string is alphabetical — 'medium' > 'low' >
# 'high' — which is the opposite of what the "Priority" sort should show. Rank
# the choices explicitly instead.
PRIORITY_RANK = Case(
    When(priority=Item.PRIORITY_HIGH, then=Value(3)),
    When(priority=Item.PRIORITY_MEDIUM, then=Value(2)),
    When(priority=Item.PRIORITY_LOW, then=Value(1)),
    default=Value(0),
    output_field=IntegerField(),
)

# Maps the ?sort= value onto a model ordering plus any annotations it needs.
SORT_SPECS = {
    'smart': {'ordering': ['completed', DUE_DATE_ASC, '-created_at'], 'annotations': {}},
    'newest': {'ordering': ['-created_at'], 'annotations': {}},
    'oldest': {'ordering': ['created_at'], 'annotations': {}},
    'due': {'ordering': [DUE_DATE_ASC, 'completed'], 'annotations': {}},
    'priority': {
        'ordering': ['-priority_sort_rank', 'completed', DUE_DATE_ASC],
        'annotations': {'priority_sort_rank': PRIORITY_RANK},
    },
    'title': {'ordering': ['title', 'completed'], 'annotations': {}},
}


def resolve_sort(value):
    """Return ``(sort_key, ordering, annotations)`` for a raw ``?sort=`` value.

    Falls back to the default sorting for unknown or missing input.
    """
    if value in SORT_SPECS:
        spec = SORT_SPECS[value]
        return value, spec['ordering'], spec['annotations']
    spec = SORT_SPECS[DEFAULT_SORT]
    return DEFAULT_SORT, spec['ordering'], spec['annotations']
