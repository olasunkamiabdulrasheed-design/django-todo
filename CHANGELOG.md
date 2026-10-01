# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
