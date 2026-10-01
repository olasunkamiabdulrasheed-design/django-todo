# Contributing

## Setup

```bash
python -m venv (myenv)
source "(myenv)/Scripts/activate"
pip install -r requirements.txt
npm install
npm run build
python manage.py migrate
```

## While you work

Rebuild the stylesheet on every change:

```bash
npm run dev
```

Tailwind v4 reads its configuration from `static/src/input.css`
(`@theme`, `@source`, `@custom-variant`). There is no `tailwind.config.js`.

## Before you commit

```bash
python manage.py check
python manage.py test
```

## Style

- Python: 4-space indent, single quotes, keep lines under ~100 characters.
- Templates: 4-space indent, and put reusable markup in `templates/partials/`.
- CSS: prefer utility classes in templates; only add to `@layer components`
  when a pattern repeats across three or more templates.

## Commit messages

Conventional-commit style prefixes, e.g.:

```
feat(models): add due dates to tasks
fix(views): correct the item detail template path
style(list): tighten the task card spacing
```
