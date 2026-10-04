"""Views for the task list app: dashboard, CRUD, complete toggle and focus."""

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .filters import resolve_sort
from .focus import focus_queue, focus_reasons
from .forms import ItemFilterForm, ItemForm
from .models import Item
from .stats import task_stats


def _safe_next(request, fallback):
    """Return a safe ``next`` URL from the request, or ``fallback``.

    Only same-host URLs are honoured, so a crafted ``?next=`` can't turn the
    toggle endpoint into an open redirect.
    """
    candidate = request.POST.get('next') or request.GET.get('next')
    if candidate and url_has_allowed_host_and_scheme(
        candidate,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return candidate
    return fallback


# ─── HOME / DASHBOARD ─────────────────────────────────────────────────────────

def home(request):
    """Landing page with headline stats and the most recent tasks."""
    stats = task_stats()
    recent = (
        Item.objects.filter(completed=False)
        .order_by(F('due_date').asc(nulls_last=True), '-created_at')[:5]
    )
    return render(request, 'home.html', {'stats': stats, 'recent': recent})


# ─── LIST (Read all) ──────────────────────────────────────────────────────────

def item_list(request):
    """Paginated, searchable and sortable list of every task."""
    form = ItemFilterForm(request.GET or None)
    tasks = form.filter_queryset(Item.objects.all())

    sort_key, ordering, annotations = resolve_sort(request.GET.get('sort'))
    if annotations:
        tasks = tasks.annotate(**annotations)
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


# ─── FOCUS (What should I do right now?) ──────────────────────────────────────

def focus(request):
    """Show a single recommended task, best-first.

    Skipping is stateless: ``?skip=1,4`` drops those ids from the queue for
    this request only, so no session or database writes are needed.
    """
    skipped = [s for s in request.GET.get('skip', '').split(',') if s.isdigit()]

    queue = [task for task in focus_queue() if str(task.pk) not in skipped]
    task = queue[0] if queue else None

    # The next skip link has to carry every id skipped so far, otherwise
    # skipping twice would bounce straight back to the first task.
    skip_param = ','.join(skipped + [str(task.pk)]) if task else ''

    context = {
        'task': task,
        'reasons': focus_reasons(task) if task else [],
        'skip_param': skip_param,
        'remaining': len(queue),
        'open_count': Item.objects.filter(completed=False).count(),
    }
    return render(request, 'focus.html', context)


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
    """Flip a task's completed flag from the list, detail or focus page."""
    item = get_object_or_404(Item, pk=pk)
    item.completed = not item.completed
    item.save()

    if item.completed:
        messages.success(request, f'Nice — "{item.title}" is done.')
    else:
        messages.info(request, f'"{item.title}" was reopened.')

    # Send the user back where they acted from, so finishing a task in focus
    # mode doesn't dump them into the full list.
    return redirect(_safe_next(request, 'item_list'))
