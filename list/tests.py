"""Tests for the task list app: models, views and routing."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Item


class ItemModelTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def test_str_returns_title(self):
        item = Item.objects.create(title='Write tests')
        self.assertEqual(str(item), 'Write tests')

    def test_defaults(self):
        item = Item.objects.create(title='Defaults')
        self.assertFalse(item.completed)
        self.assertIsNone(item.completed_at)
        self.assertEqual(item.priority, Item.PRIORITY_MEDIUM)
        self.assertEqual(item.category, '')

    def test_get_absolute_url_points_at_detail(self):
        item = Item.objects.create(title='Linked')
        self.assertEqual(item.get_absolute_url(), reverse('item_detail', args=[item.pk]))

    def test_completing_sets_completed_at(self):
        item = Item.objects.create(title='Finish me')
        self.assertIsNone(item.completed_at)

        item.completed = True
        item.save()
        self.assertIsNotNone(item.completed_at)

    def test_reopening_clears_completed_at(self):
        item = Item.objects.create(title='Reopen me', completed=True)
        item.completed = False
        item.save()
        self.assertIsNone(item.completed_at)

    def test_is_overdue_only_for_open_past_due_tasks(self):
        overdue = Item.objects.create(title='Late', due_date=self.today - timedelta(days=1))
        self.assertTrue(overdue.is_overdue)

        done = Item.objects.create(
            title='Late but done',
            due_date=self.today - timedelta(days=1),
            completed=True,
        )
        self.assertFalse(done.is_overdue)

        future = Item.objects.create(title='Later', due_date=self.today + timedelta(days=3))
        self.assertFalse(future.is_overdue)

    def test_days_left(self):
        item = Item.objects.create(title='Dated', due_date=self.today + timedelta(days=5))
        self.assertEqual(item.days_left, 5)

        undated = Item.objects.create(title='Undated')
        self.assertIsNone(undated.days_left)

    def test_is_due_today(self):
        item = Item.objects.create(title='Today', due_date=self.today)
        self.assertTrue(item.is_due_today)

    def test_priority_badge_class_is_never_empty(self):
        for priority in ('low', 'medium', 'high', 'nonsense'):
            item = Item(priority=priority)
            self.assertTrue(item.priority_badge_class())

    def test_ordering_puts_open_tasks_first(self):
        Item.objects.create(title='Done', completed=True)
        Item.objects.create(title='Open')
        self.assertEqual(Item.objects.first().title, 'Open')


class ItemViewTests(TestCase):
    def setUp(self):
        self.item = Item.objects.create(title='Existing task', description='hello world')

    def test_home_page_renders_stats(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['stats']['total'], 1)
        self.assertContains(response, 'TaskFlow')

    def test_task_list_page_renders(self):
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing task')

    def test_search_filters_results(self):
        Item.objects.create(title='Unrelated')
        response = self.client.get(reverse('item_list'), {'q': 'hello'})
        self.assertContains(response, 'Existing task')
        self.assertNotContains(response, 'Unrelated')

    def test_status_filter_hides_completed(self):
        Item.objects.create(title='Finished task', completed=True)
        response = self.client.get(reverse('item_list'), {'status': 'active'})
        self.assertContains(response, 'Existing task')
        self.assertNotContains(response, 'Finished task')

    def test_priority_filter(self):
        Item.objects.create(title='Urgent thing', priority=Item.PRIORITY_HIGH)
        response = self.client.get(reverse('item_list'), {'priority': 'high'})
        self.assertContains(response, 'Urgent thing')
        self.assertNotContains(response, 'Existing task')

    def test_detail_page(self):
        response = self.client.get(reverse('item_detail', args=[self.item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Existing task')

    def test_detail_404_for_missing_task(self):
        response = self.client.get(reverse('item_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_create_task(self):
        response = self.client.post(reverse('item_create'), {
            'title': 'Brand new',
            'description': 'from the test',
            'priority': 'high',
            'category': 'Work',
            'due_date': '',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Item.objects.filter(title='Brand new', priority='high').exists())

    def test_create_rejects_blank_title(self):
        response = self.client.post(reverse('item_create'), {'title': '', 'description': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Item.objects.count(), 1)

    def test_update_task(self):
        response = self.client.post(reverse('item_update', args=[self.item.pk]), {
            'title': 'Renamed',
            'description': 'updated',
            'priority': 'low',
            'category': '',
            'due_date': '',
        })
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertEqual(self.item.title, 'Renamed')

    def test_delete_task(self):
        response = self.client.post(reverse('item_delete', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=self.item.pk).exists())

    def test_toggle_completes_task(self):
        response = self.client.post(reverse('item_toggle', args=[self.item.pk]))
        self.assertEqual(response.status_code, 302)
        self.item.refresh_from_db()
        self.assertTrue(self.item.completed)

    def test_toggle_requires_post(self):
        response = self.client.get(reverse('item_toggle', args=[self.item.pk]))
        self.assertEqual(response.status_code, 405)

    def test_pagination_limits_page_size(self):
        for i in range(12):
            Item.objects.create(title=f'Task {i}')
        response = self.client.get(reverse('item_list'))
        self.assertEqual(len(response.context['tasks']), 8)
