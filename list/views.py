from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Item
from .forms import ItemForm
from django.http import HttpResponse

def item_list(request):
    return HttpResponse("This is the task list page.")

# ─── HOME ─────────────────────────────────────────────────────────────────────
def home(request):
    return render(request, 'home.html')


# ─── LIST (Read all) ──────────────────────────────────────────────────────────
def item_list(request):
    items = Item.objects.all().order_by('-created_at')  # Newest first
    return render(request, 'nameofapp/item_list.html', {'items': items})
    # The dict {'items': items} passes data to the template


# ─── DETAIL (Read one) ────────────────────────────────────────────────────────
def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)  # Gets item or shows 404 if not found
    return render(request, 'nameofapp/item_detail.html', {'item': item})


# ─── CREATE ───────────────────────────────────────────────────────────────────
def item_create(request):
    if request.method == 'POST':
        # Form was submitted — process it
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Item created successfully!')
            return redirect('item_list')
    else:
        # Page was just opened — show an empty form
        form = ItemForm()
    return render(request, 'nameofapp/item_form.html', {'form': form, 'action': 'Create'})


# ─── UPDATE ───────────────────────────────────────────────────────────────────
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)  # instance= ties form to existing record
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Item updated successfully!')
            return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)  # Pre-fills form with existing data
    return render(request, 'nameofapp/item_form.html', {'form': form, 'action': 'Update', 'item': item})


# ─── DELETE ───────────────────────────────────────────────────────────────────
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == 'POST':
        item.delete()
        messages.error(request, '🗑️ Item deleted.')
        return redirect('item_list')
    return render(request, 'nameofapp/item_confirm_delete.html', {'item': item})


