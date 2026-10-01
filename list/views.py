"""Views for the task list app: dashboard, CRUD and the complete toggle."""

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .filters import resolve_sort
from .forms import ItemFilterForm, ItemForm
from .models import Item
from .stats import task_stats

from django.conf import settings


# ─── HOME / DASHBOARD ─────────────────────────────────────────────────────────

def home(request):
    """Landing page with headline stats and the most recent tasks."""
    stats = task_stats()
    recent = Item.objects.filter(completed=False).order_by('due_date', '-created_at')[:5]
    return render(request, 'home.html', {'stats': stats, 'recent': recent})


# ─── LIST (Read all) ──────────────────────────────────────────────────────────

def item_list(request):
    """Paginated, searchable and sortable list of every task."""
    form = ItemFilterForm(request.GET or None)
    tasks = form.filter_queryset(Item.objects.all())

    sort_key, ordering = resolve_sort(request.GET.get('sort'))
    tasks = tasks.order_by(*ordering)

    paginator = Paginator(tasks, settings.TASKS_PER_PAGE)
    page = paginator.get_page(request.GET.get('page'))

    # Querystring without ?page=, so pagination links keep the active filters.
    params = request.GET.copy()
    params.pop('page', None)

    return render(request, 'item_list.html', {
        'form': form,
        'page_obj': page,
        'tasks': page.object_list,
        'total_count': paginator.count,
        'sort': sort_key,
        'filters_qs': params.urlencode(),
    })


# ─── DETAIL (Read one) ────────────────────────────────────────────────────────

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item_detail.html', {'item': item})


# ─── CREATE ───────────────────────────────────────────────────────────────────

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'Task "{item.title}" was created.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'item_form.html', {'form': form, 'action': 'Create'})


# ─── UPDATE ───────────────────────────────────────────────────────────────────

def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{item.title}" was updated.')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item_form.html', {'form': form, 'action': 'Update', 'item': item})


# ─── DELETE ───────────────────────────────────────────────────────────────────

def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.info(request, f'Task "{title}" was deleted.')
        return redirect('item_list')
    return render(request, 'item_confirm_delete.html', {'item': item})


# ─── TOGGLE COMPLETE ──────────────────────────────────────────────────────────

@require_POST
def item_toggle(request, pk):
    """Flip a task's completed flag from the list or detail page."""
    item = get_object_or_404(Item, pk=pk)
    item.completed = not item.completed
    item.save()

    if item.completed:
        messages.success(request, f'Nice — "{item.title}" is done.')
    else:
        messages.info(request, f'"{item.title}" was reopened.')

    return redirect('item_list')
