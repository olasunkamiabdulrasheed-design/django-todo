"""Regression tests for template rendering bugs."""

from django.contrib.messages import constants as message_constants
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Item
from .templatetags.task_extras import message_icon


class _StubMessage:
    """Minimal stand-in exposing the only attribute the filter reads."""

    def __init__(self, level):
        self.level = level


class MessageIconTests(TestCase):
    def test_each_level_maps_to_its_own_icon(self):
        self.assertEqual(message_icon(_StubMessage(message_constants.SUCCESS)), '✓')
        self.assertEqual(message_icon(_StubMessage(message_constants.ERROR)), '!')
        self.assertEqual(message_icon(_StubMessage(message_constants.WARNING)), '!')
        self.assertEqual(message_icon(_StubMessage(message_constants.INFO)), 'ℹ')

    def test_an_unknown_level_falls_back_to_the_info_glyph(self):
        self.assertEqual(message_icon(_StubMessage(9999)), 'ℹ')

    def test_a_success_message_renders_a_tick(self):
        # Regression: MESSAGE_TAGS replaces the level name with CSS classes, so
        # the old `'success' in message.tags` check never matched and every
        # message rendered the neutral 'ℹ'.
        response = self.client.post(reverse('item_create'), {
            'title': 'Trigger a success message',
            'description': '',
            'priority': 'low',
            'category': '',
            'due_date': '',
        }, follow=True)

        self.assertContains(response, 'aria-hidden="true">✓</span>')

    def test_an_info_message_renders_the_info_glyph(self):
        item = Item.objects.create(title='Reopen me', completed=True)

        response = self.client.post(
            reverse('item_toggle', args=[item.pk]), follow=True
        )

        self.assertContains(response, 'aria-hidden="true">ℹ</span>')


class FormLabelTests(TestCase):
    def test_the_create_form_shows_the_title_label(self):
        # Regression: {{ form.label }} rendered nothing — the required marker
        # floated next to an empty string.
        response = self.client.get(reverse('item_create'))

        self.assertContains(response, 'Task <span class="text-rose-500">*</span>')

    def test_the_edit_form_shows_the_title_label(self):
        item = Item.objects.create(title='Editable')

        response = self.client.get(reverse('item_update', args=[item.pk]))

        self.assertContains(response, 'Task <span class="text-rose-500">*</span>')


class CompletedTaskDueLabelTests(TestCase):
    def test_a_task_finished_today_is_not_shown_as_due_in_zero_days(self):
        # Regression: is_due_today is False for completed work, so the template
        # fell through to "Due in 0 day".
        Item.objects.create(
            title='Already finished',
            due_date=timezone.localdate(),
            completed=True,
        )

        response = self.client.get(reverse('item_list'))

        self.assertNotContains(response, 'Due in 0 day')
        self.assertContains(response, 'Already finished')

    def test_an_open_task_due_today_is_flagged(self):
        Item.objects.create(title='Do it now', due_date=timezone.localdate())

        response = self.client.get(reverse('item_list'))

        self.assertContains(response, 'Due today')


class EmptyStateLinkTests(TestCase):
    """The empty-state CTA used to hardcode '/tasks/add/', bypassing {% url %}.

    The assertions target the empty-state button's own markup: the navbar
    already links to the create page, so a looser check would pass even if the
    empty state pointed nowhere.
    """

    def test_the_empty_list_links_to_the_create_page(self):
        response = self.client.get(reverse('item_list'))

        self.assertContains(
            response,
            f'href="{reverse("item_create")}" class="btn-primary mt-2"',
        )

    def test_the_filtered_empty_list_links_to_the_plain_list(self):
        response = self.client.get(reverse('item_list'), {'q': 'nothing-matches-this'})

        self.assertContains(
            response,
            f'href="{reverse("item_list")}" class="btn-primary mt-2"',
        )

    def test_the_empty_dashboard_links_to_the_create_page(self):
        response = self.client.get(reverse('home'))

        self.assertContains(
            response,
            f'href="{reverse("item_create")}" class="btn-primary mt-2"',
        )
