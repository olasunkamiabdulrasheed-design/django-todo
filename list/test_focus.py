"""Tests for focus mode: the ranking engine and its page."""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .focus import focus_queue, focus_reasons, focus_score
from .models import Item


class FocusScoreTests(TestCase):
    """The ranking is the feature — if it ranks badly, the feature is noise."""

    def setUp(self):
        self.today = timezone.localdate()

    def test_overdue_beats_due_today(self):
        overdue = Item(title='Late', due_date=self.today - timedelta(days=2))
        due_today = Item(title='Today', due_date=self.today)

        self.assertGreater(focus_score(overdue, self.today), focus_score(due_today, self.today))

    def test_due_today_beats_next_week(self):
        due_today = Item(title='Today', due_date=self.today)
        next_week = Item(title='Later', due_date=self.today + timedelta(days=5))

        self.assertGreater(focus_score(due_today, self.today), focus_score(next_week, self.today))

    def test_high_priority_beats_low_priority_all_else_equal(self):
        high = Item(title='Important', priority=Item.PRIORITY_HIGH)
        low = Item(title='Whatever', priority=Item.PRIORITY_LOW)

        self.assertGreater(focus_score(high, self.today), focus_score(low, self.today))

    def test_urgency_outranks_stated_priority(self):
        # The whole point: a late chore matters more than a big task that
        # isn't due for a month.
        late_low = Item(
            title='Late errand',
            priority=Item.PRIORITY_LOW,
            due_date=self.today - timedelta(days=7),
        )
        distant_high = Item(
            title='Someday big',
            priority=Item.PRIORITY_HIGH,
            due_date=self.today + timedelta(days=30),
        )

        self.assertGreater(focus_score(late_low, self.today), focus_score(distant_high, self.today))

    def test_the_overdue_penalty_is_capped(self):
        # A task from last year must not grow an unbounded score.
        ancient = Item(title='Ancient', due_date=self.today - timedelta(days=500))
        merely_late = Item(title='Merely late', due_date=self.today - timedelta(days=20))

        self.assertEqual(focus_score(ancient, self.today), focus_score(merely_late, self.today))

    def test_undated_tasks_are_not_starved(self):
        undated = Item(title='No date')
        far_off = Item(title='Far off', due_date=self.today + timedelta(days=90))

        self.assertGreater(focus_score(undated, self.today), focus_score(far_off, self.today))


class FocusReasonsTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def test_overdue_reason_reads_naturally(self):
        item = Item(title='Late', due_date=self.today - timedelta(days=2))

        self.assertIn('2 days overdue', focus_reasons(item, self.today))

    def test_one_day_overdue_is_singular(self):
        item = Item(title='Late', due_date=self.today - timedelta(days=1))

        self.assertIn('1 day overdue', focus_reasons(item, self.today))

    def test_due_today_and_high_priority_are_both_reported(self):
        item = Item(title='Now', priority=Item.PRIORITY_HIGH, due_date=self.today)

        reasons = focus_reasons(item, self.today)
        self.assertIn('Due today', reasons)
        self.assertIn('High priority', reasons)

    def test_a_plain_task_has_no_reasons(self):
        item = Item(title='Plain', due_date=self.today + timedelta(days=30))

        self.assertEqual(focus_reasons(item, self.today), [])


class FocusQueueTests(TestCase):
    def test_queue_excludes_completed_tasks(self):
        Item.objects.create(title='Finished', completed=True)
        Item.objects.create(title='Open')

        self.assertEqual([task.title for task in focus_queue()], ['Open'])

    def test_queue_ranks_the_most_urgent_first(self):
        Item.objects.create(title='Someday', priority=Item.PRIORITY_HIGH,
                            due_date=timezone.localdate() + timedelta(days=30))
        Item.objects.create(title='Very late', priority=Item.PRIORITY_LOW,
                            due_date=timezone.localdate() - timedelta(days=10))

        self.assertEqual(focus_queue()[0].title, 'Very late')

    def test_queue_honours_the_limit(self):
        for index in range(10):
            Item.objects.create(title=f'Task {index}')

        self.assertEqual(len(focus_queue(limit=4)), 4)


class FocusViewTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()

    def test_page_renders_the_recommended_task(self):
        Item.objects.create(title='Only task')

        response = self.client.get(reverse('focus'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Only task')

    def test_recommends_the_overdue_task_over_a_distant_important_one(self):
        Item.objects.create(title='Someday', priority=Item.PRIORITY_HIGH,
                            due_date=self.today + timedelta(days=30))
        Item.objects.create(title='Very late', priority=Item.PRIORITY_LOW,
                            due_date=self.today - timedelta(days=10))

        response = self.client.get(reverse('focus'))

        self.assertEqual(response.context['task'].title, 'Very late')

    def test_skip_advances_to_the_next_task(self):
        first = Item.objects.create(title='First', priority=Item.PRIORITY_HIGH)
        Item.objects.create(title='Second', priority=Item.PRIORITY_LOW)

        response = self.client.get(reverse('focus'), {'skip': str(first.pk)})

        self.assertEqual(response.context['task'].title, 'Second')

    def test_skip_accumulates_across_requests(self):
        first = Item.objects.create(title='First', priority=Item.PRIORITY_HIGH)
        second = Item.objects.create(title='Second', priority=Item.PRIORITY_MEDIUM)
        Item.objects.create(title='Third', priority=Item.PRIORITY_LOW)

        response = self.client.get(reverse('focus'), {'skip': f'{first.pk},{second.pk}'})

        self.assertEqual(response.context['task'].title, 'Third')

    def test_skipping_everything_shows_the_empty_state(self):
        item = Item.objects.create(title='Alone')

        response = self.client.get(reverse('focus'), {'skip': str(item.pk)})

        self.assertIsNone(response.context['task'])
        self.assertEqual(response.context['open_count'], 1)

    def test_empty_state_when_nothing_is_open(self):
        response = self.client.get(reverse('focus'))

        self.assertIsNone(response.context['task'])
        self.assertEqual(response.context['open_count'], 0)
        self.assertContains(response, 'all clear')

    def test_an_ignored_skip_value_does_not_break_the_page(self):
        Item.objects.create(title='Fine')

        response = self.client.get(reverse('focus'), {'skip': 'not-a-number'})

        self.assertEqual(response.context['task'].title, 'Fine')

    def test_done_sends_the_user_back_to_focus(self):
        # Without this, finishing a task in focus mode dumped you in the list.
        item = Item.objects.create(title='Finish me')

        response = self.client.post(
            reverse('item_toggle', args=[item.pk]),
            {'next': reverse('focus')},
        )

        self.assertRedirects(response, reverse('focus'))

    def test_reasons_are_rendered_on_the_page(self):
        Item.objects.create(title='Urgent', priority=Item.PRIORITY_HIGH,
                            due_date=self.today - timedelta(days=2))

        response = self.client.get(reverse('focus'))

        self.assertContains(response, '2 days overdue')
        self.assertContains(response, 'High priority')
