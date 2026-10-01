# TaskFlow

A small, tidy to-do app built with **Django 5.2** and **Tailwind CSS 4**.

Create tasks, give them a priority and a due date, group them by category, then
search, filter and sort your way through the day. Ships with a dark mode.

---

## Features

- **Full CRUD** — create, view, edit and delete tasks.
- **One-tap complete** — toggle a task from the list without opening it.
- **Priorities** — Low / Medium / High, colour-coded throughout.
- **Due dates** — with automatic *overdue* and *due today* highlighting.
- **Categories** — free-text grouping (Work, Errands, …).
- **Search & filter** — by text, status (open / done / overdue) and priority.
- **Sorting** — smart, newest, oldest, due date, priority or A→Z.
- **Pagination** — 8 tasks per page, filters preserved across pages.
- **Dashboard** — headline counts and a completion progress bar on the home page.
- **Dark mode** — remembered in `localStorage`, no flash on load.
- **Admin** — rich `ModelAdmin` with inline editing and bulk actions.
- **Tests** — model and view coverage in `list/tests.py`.

---

## Requirements

- Python 3.10+
- Node.js 18+ (only to build the Tailwind stylesheet)

## Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv (myenv)
source "(myenv)/Scripts/activate"      # Windows Git Bash
# .\(myenv)\Scripts\activate           # PowerShell

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install the Tailwind CLI
npm install

# 4. Build the stylesheet
npm run build        # one-off, minified
npm run dev          # or: rebuild on change while you work

# 5. Apply migrations
python manage.py migrate

# 6. Run the dev server
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

> The stylesheet is written to `static/src/output.css`. If the page looks
> unstyled, step 4 hasn't been run yet.

---

## Project layout

```
TO-DO/
├── list/                     # the tasks app
│   ├── models.py             # Item — the task model
│   ├── forms.py              # ItemForm, ItemFilterForm
│   ├── filters.py            # sort options and ordering table
│   ├── stats.py              # dashboard statistics
│   ├── views.py              # dashboard, CRUD, toggle
│   ├── urls.py               # app routes
│   ├── admin.py              # admin configuration
│   ├── tests.py              # model + view tests
│   ├── templatetags/
│   │   └── task_extras.py    # sort_url, pluralize_count, …
│   └── migrations/
├── templates/
│   ├── base.html             # shell: navbar, messages, theme toggle
│   ├── home.html             # dashboard
│   ├── item_*.html           # list / detail / form / delete
│   └── partials/             # navbar, task_card, pagination, …
├── static/src/
│   ├── input.css             # Tailwind source + design tokens
│   └── output.css            # generated — do not edit
└── to_do/                    # project settings and root urls
```

## Routes

| URL | Name | Purpose |
| --- | --- | --- |
| `/` | `home` | Dashboard |
| `/tasks/` | `item_list` | List, search, filter, sort |
| `/tasks/add/` | `item_create` | Create a task |
| `/tasks/<id>/` | `item_detail` | Task detail |
| `/tasks/<id>/edit/` | `item_update` | Edit a task |
| `/tasks/<id>/delete/` | `item_delete` | Confirm deletion |
| `/tasks/<id>/toggle/` | `item_toggle` | Mark done / reopen (POST) |
| `/admin/` | — | Django admin |

## Running the tests

```bash
python manage.py test
```

## Notes

- The app is deliberately unauthenticated; tasks are global. Adding
  `django.contrib.auth` scoping is the natural next step.
- `input.css` uses Tailwind v4's CSS-first configuration — there is no
  `tailwind.config.js`.
