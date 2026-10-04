"""Admin configuration for tasks."""

from django.contrib import admin
from django.utils import timezone

from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'category', 'due_date', 'completed', 'created_at')
    list_filter = ('completed', 'priority', 'category', 'created_at')
    search_fields = ('title', 'description', 'category')
    list_editable = ('priority', 'completed')
    date_hierarchy = 'created_at'
    ordering = ('completed', 'due_date')
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    actions = ('mark_completed', 'mark_incomplete')

    fieldsets = (
        (None, {
            'fields': ('title', 'description'),
        }),
        ('Organisation', {
            'fields': ('priority', 'category', 'due_date'),
        }),
        ('Status', {
            'fields': ('completed', 'completed_at'),
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )

    @admin.action(description='Mark selected tasks as completed')
    def mark_completed(self, request, queryset):
        # A bulk update bypasses Item.save(), so set the timestamp here too —
        # otherwise the admin leaves completed_at NULL, breaking the invariant
        # the model and detail view both rely on.
        updated = queryset.filter(completed=False).update(
            completed=True,
            completed_at=timezone.now(),
        )
        self.message_user(request, f'{updated} task(s) marked as completed.')

    @admin.action(description='Mark selected tasks as not completed')
    def mark_incomplete(self, request, queryset):
        updated = queryset.update(completed=False, completed_at=None)
        self.message_user(request, f'{updated} task(s) reopened.')
