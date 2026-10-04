"""Tests for task-list sorting and filtering."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Item


class SortOrderingTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def _titles(self, **params):
        response = self.client.get(reverse('item_list'), params)
        return [task.title for task in response.context['tasks']]

    def test_priority_sort_ranks_high_first(self):
        # Regression: ordering by the priority string is alphabetical, which
        # produced Medium → Low → High.
        Item.objects.create(title='Low', priority=Item.PRIORITY_LOW)
        Item.objects.create(title='High', priority=Item.PRIORITY_HIGH)
        Item.objects.create(title='Medium', priority=Item.PRIORITY_MEDIUM)

        self.assertEqual(self._titles(sort='priority'), ['High', 'Medium', 'Low'])

    def test_undated_tasks_sort_after_dated_ones(self):
        # Regression: NULLs sort first on an ascending date sort.
        Item.objects.create(title='Undated')
        Item.objects.create(title='Later', due_date=self.today + timedelta(days=3))
        Item.objects.create(title='Sooner', due_date=self.today + timedelta(days=1))

        self.assertEqual(self._titles(sort='due'), ['Sooner', 'Later', 'Undated'])

    def test_smart_sort_puts_dated_tasks_first(self):
        Item.objects.create(title='Undated')
        Item.objects.create(title='Dated', due_date=self.today)

        self.assertEqual(self._titles(), ['Dated', 'Undated'])

    def test_completed_tasks_still_sort_last(self):
        Item.objects.create(title='Finished', completed=True, due_date=self.today - timedelta(days=5))
        Item.objects.create(title='Open', due_date=self.today + timedelta(days=5))

        self.assertEqual(self._titles(), ['Open', 'Finished'])

    def test_unknown_sort_falls_back_to_the_default(self):
        Item.objects.create(title='Anything')

        response = self.client.get(reverse('item_list'), {'sort': 'nonsense'})
        self.assertEqual(response.context['sort'], 'smart')


class FilterRobustnessTests(TestCase):
    def setUp(self):
        Item.objects.create(title='Keep me', priority=Item.PRIORITY_HIGH)

    def test_an_unknown_priority_does_not_discard_the_search(self):
        # Regression: one invalid parameter made the whole form invalid, which
        # silently widened the results to everything.
        response = self.client.get(reverse('item_list'), {'q': 'Keep', 'priority': 'bogus'})

        self.assertContains(response, 'Keep me')

    def test_an_unknown_priority_is_ignored_rather_than_fatal(self):
        Item.objects.create(title='Other', priority=Item.PRIORITY_LOW)

        response = self.client.get(reverse('item_list'), {'priority': 'bogus'})

        self.assertEqual(response.context['total_count'], 2)

    def test_blank_parameters_are_ignored(self):
        response = self.client.get(reverse('item_list'), {'q': '', 'status': '', 'priority': ''})

        self.assertEqual(response.context['total_count'], 1)

    def test_an_unknown_status_is_ignored(self):
        Item.objects.create(title='Second task')

        response = self.client.get(reverse('item_list'), {'status': 'bogus'})

        self.assertEqual(response.context['total_count'], 2)

    def test_category_filter_shows_only_matching_tasks(self):
        Item.objects.create(title='Work task', category='Work')
        Item.objects.create(title='Personal task', category='Personal')

        response = self.client.get(reverse('item_list'), {'category': 'Work'})

        self.assertContains(response, 'Work task')
        self.assertNotContains(response, 'Personal task')
