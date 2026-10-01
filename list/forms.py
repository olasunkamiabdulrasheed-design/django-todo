"""Forms for creating, editing and filtering tasks."""

from django import forms

from .models import Item

# Shared Tailwind classes so every widget in the app looks the same.
INPUT_CLASSES = (
    'w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-slate-900 '
    'shadow-sm transition placeholder:text-slate-400 '
    'focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 '
    'dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500'
)

SELECT_CLASSES = INPUT_CLASSES + ' pr-10'


class ItemForm(forms.ModelForm):
    """Create / update form for a task."""

    class Meta:
        model = Item
        fields = ['title', 'description', 'priority', 'category', 'due_date', 'completed']
        labels = {
            'title': 'Task',
            'description': 'Notes',
            'due_date': 'Due date',
            'completed': 'Already done',
        }
        help_texts = {
            'description': 'Anything you need to remember about this task.',
            'category': 'Group related tasks together.',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'e.g. Finish the Django project',
                'autofocus': True,
            }),
            'description': forms.Textarea(attrs={
                'class': INPUT_CLASSES + ' min-h-32 resize-y',
                'placeholder': 'Add any details, links or sub-steps…',
                'rows': 5,
            }),
            'priority': forms.Select(attrs={'class': SELECT_CLASSES}),
            'category': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Work, Personal, Errands…',
            }),
            'due_date': forms.DateInput(
                attrs={'class': INPUT_CLASSES, 'type': 'date'},
                format='%Y-%m-%d',
            ),
            'completed': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 rounded border-slate-300 text-indigo-600 '
                         'focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # DateInput needs an explicit input format or an existing value renders
        # as "Oct. 1, 2026" and the browser date picker ignores it.
        self.fields['due_date'].input_formats = ['%Y-%m-%d']


class ItemFilterForm(forms.Form):
    """Search / filter toolbar on the task list page. Every field is optional."""

    STATUS_CHOICES = [
        ('', 'All tasks'),
        ('active', 'Open'),
        ('done', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': INPUT_CLASSES,
            'placeholder': 'Search tasks…',
            'type': 'search',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASSES}),
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'Any priority')] + Item.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': SELECT_CLASSES}),
    )

    def filter_queryset(self, queryset):
        """Apply the cleaned filters to ``queryset``."""
        if not self.is_valid():
            return queryset

        from django.db.models import Q
        from django.utils import timezone

        data = self.cleaned_data

        if data.get('q'):
            term = data['q']
            queryset = queryset.filter(
                Q(title__icontains=term)
                | Q(description__icontains=term)
                | Q(category__icontains=term)
            )

        status = data.get('status')
        if status == 'active':
            queryset = queryset.filter(completed=False)
        elif status == 'done':
            queryset = queryset.filter(completed=True)
        elif status == 'overdue':
            queryset = queryset.filter(
                completed=False,
                due_date__lt=timezone.localdate(),
            )

        if data.get('priority'):
            queryset = queryset.filter(priority=data['priority'])

        return queryset
