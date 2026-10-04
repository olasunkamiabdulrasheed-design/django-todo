# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **Focus mode** (`/focus/`) — ranks open tasks by urgency and recommends the
  single next one, with the reasoning shown as chips and a 25-minute timer.
- `list/focus.py`: `focus_score()`, `focus_queue()` and `focus_reasons()`.
- `message_icon` template filter, keyed on the numeric message level.
- Environment-driven settings: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`,
  `DJANGO_ALLOWED_HOSTS`.
- `STATIC_ROOT`, so `collectstatic` works in production.
- Test modules `list/test_filters.py`, `list/test_focus.py` and
  `list/test_templates.py`.
- `next` support on the complete/reopen toggle, so acting on a task returns you
  to the page you were on.

### Changed
- Opening a task, editing it or finishing it no longer navigates away from the
  list or focus queue.
- Empty-state CTAs build their links with `{% url %}` instead of hardcoded
  paths.
- Sort links and pagination keep the active filters.

### Fixed
- **Priority sort ordered tasks alphabetically** — `medium` > `low` > `high`,
  the opposite of intent. Now ranked with an explicit `CASE` expression.
- **Tasks with no due date sorted to the top** of every date-ordered list,
  because ascending sorts put NULLs first. Now sorted last.
- **One invalid filter parameter silently discarded every other filter** —
  `?priority=bogus` returned the whole table. Fields are now validated
  individually and unknown values ignored.
- **Bulk "mark completed" in the admin left `completed_at` NULL**, bypassing
  the model's own invariant.
- **`save(update_fields=[...])` dropped `completed_at`**, breaking the
  timestamp on any targeted save.
- The required-field marker on the task form sat next to an empty label
  (`{{ form.label }}` instead of `{{ form.title.label }}`).
- **Every flash message rendered the neutral ℹ icon.** `MESSAGE_TAGS` replaces
  the level name with CSS classes, so `'success' in message.tags` never
  matched.
- A task completed today displayed "📅 Due in 0 day".
- The toggle endpoint honoured an arbitrary `?next=`, allowing an open
  redirect. Only same-host destinations are accepted now.
- Unescaped `SECRET_KEY`, hardcoded `DEBUG = True` and empty `ALLOWED_HOSTS`
  shipped in `settings.py`.

## [1.0.0] — earlier

### Added
- Task **priority** levels (low / medium / high) with colour-coded badges.
- **Due dates** with automatic *overdue* and *due today* detection.
- **Categories** for grouping tasks.
- **Search** across title, notes and category.
- **Status and priority filters**, plus six **sort** orders.
- **Pagination** (8 per page) that preserves the active filters.
- **Dashboard** with headline counts and a completion progress bar.
- **Complete / reopen toggle** straight from the list and detail views.
- **Dark mode** with a navbar toggle persisted to `localStorage`.
- Custom `task_extras` template tag library (`sort_url`, `pluralize_count`, `initials`).
- Rich admin: inline editing, filters, date hierarchy and bulk actions.
- Model and view **test suite** in `list/tests.py`.
- `requirements.txt`, `.editorconfig`, `.gitattributes` and project documentation.

### Changed
- Reworked the UI onto Tailwind v4 with design tokens and a component layer.
- Split view logic into `filters.py` and `stats.py` for testability.
- Replaced the ad-hoc template paths with a consistent `templates/` layout.

### Fixed
- `INSTALLED_APPS` had a missing comma that silently concatenated two entries.
- Removed a broken `django-compressor` configuration that dropped every
  static-file finder, leaving the site unstyled.
- `item_list` was defined twice, so the first definition was dead code.
- Views rendered `nameofapp/...` template paths that did not exist.
- Templates linked to `task_update` / `task_delete` routes that were never
  registered, raising `NoReverseMatch`.
- A stray `\`html` line at the top of `item_detail.html`.
- Missing final newlines across several source files.
