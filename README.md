# TaskFlow

A small, tidy to-do app built with **Django 5.2** and **Tailwind CSS 4**.

Create tasks, give them a priority and a due date, group them by category, then
search, filter and sort your way through the day. When the list gets long, hand
the decision back to the app: **Focus mode** picks the single task that most
deserves your attention and shows you that one, with a 25-minute timer.

---

## Features

- **Focus mode** — ranks every open task by urgency and shows you the one to do
  next, with the reasons behind the recommendation and a built-in timer.
- **Full CRUD** — create, view, edit and delete tasks.
- **One-tap complete** — toggle a task from the list without opening it, and
  stay on the page you were on.
- **Priorities** — Low / Medium / High, colour-coded throughout.
- **Due dates** — with automatic *overdue* and *due today* highlighting.
- **Categories** — free-text grouping (Work, Errands, …).
- **Search & filter** — by text, status (open / done / overdue) and priority.
- **Sorting** — smart, newest, oldest, due date, priority or A→Z.
- **Pagination** — 8 tasks per page, filters preserved across pages.
- **Dashboard** — headline counts and a completion progress bar on the home page.
- **Dark mode** — remembered in `localStorage`, no flash on load.
- **Admin** — rich `ModelAdmin` with inline editing and bulk actions.
- **Tests** — model, view, template and ranking coverage in `list/test_*.py`.

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
│   ├── focus.py              # focus ranking and reasons
│   ├── stats.py              # dashboard statistics
│   ├── views.py              # dashboard, CRUD, toggle, focus
│   ├── urls.py               # app routes
│   ├── admin.py              # admin configuration
│   ├── tests.py              # model + view tests
│   ├── test_filters.py       # sorting and filter tests
│   ├── test_focus.py         # ranking and focus-page tests
│   ├── test_templates.py     # template regression tests
│   ├── templatetags/
│   │   └── task_extras.py    # sort_url, message_icon, …
│   └── migrations/
├── templates/
│   ├── base.html             # shell: navbar, messages, theme toggle
│   ├── home.html             # dashboard
│   ├── focus.html            # focus mode
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
| `/focus/` | `focus` | The single next task, ranked |
| `/tasks/` | `item_list` | List, search, filter, sort |
| `/tasks/add/` | `item_create` | Create a task |
| `/tasks/<id>/` | `item_detail` | Task detail |
| `/tasks/<id>/edit/` | `item_update` | Edit a task |
| `/tasks/<id>/delete/` | `item_delete` | Confirm deletion |
| `/tasks/<id>/toggle/` | `item_toggle` | Mark done / reopen (POST) |
| `/admin/` | — | Django admin |

## Focus mode

`/focus/` answers "what should I do right now?" with a single task instead of a
list of twenty. Each open task is scored in `list/focus.py`:

| Signal | Weight |
| --- | --- |
| High / Medium / Low priority | 40 / 20 / 10 |
| Overdue | +50, plus 3 per day late (capped at 14 days) |
| Due today / tomorrow / this week | +30 / +15 / +5 |
| No due date | +8 |
| Age | +1 per day on the list (capped at 30) |

Urgency deliberately outweighs stated priority, so a low-priority task that is
a week overdue outranks a high-priority task due next month. The page explains
its reasoning with chips ("3 days overdue", "High priority") — a suggestion you
can't understand is one you won't act on.

Skipping is stateless: `?skip=1,4` drops those ids for that request only, so
nothing is written to the database or the session. The 25-minute timer is
entirely client-side.

**Running the tests**

```bash
python manage.py test
```

## Configuration

Everything works out of the box in development. For deployment, set these
environment variables instead of editing `settings.py`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | insecure dev key | **Set this in production.** |
| `DJANGO_DEBUG` | `True` | Set to `False` when deployed. |
| `DJANGO_ALLOWED_HOSTS` | *(empty)* | Comma-separated hostnames, e.g. `example.com,www.example.com`. |

`STATIC_ROOT` (`staticfiles/`) is where `manage.py collectstatic` gathers
assets for the web server.

## Notes

- The app is deliberately unauthenticated; tasks are global. Adding
  `django.contrib.auth` scoping is the natural next step.
- `input.css` uses Tailwind v4's CSS-first configuration — there is no
  `tailwind.config.js`.
- Focus mode's `?skip=` parameter is per-request by design: nothing is stored,
  so the queue resets when you leave the page.
