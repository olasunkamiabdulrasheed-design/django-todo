"""Focus mode: pick the one task that most deserves your attention right now.

A long list is a decision problem, not a storage problem. Everything here is
about *ranking* open work so the app can suggest a single next action instead
of showing the user twenty equally-valid options.

The score is deliberately simple and explainable — urgency first, then stated
priority, then how long the task has been quietly rotting on the list.
"""

from django.utils import timezone

from .models import Item

# Stated priority is worth less than real-world urgency: a low-priority task
# that is a week overdue should outrank a high-priority task due next month.
PRIORITY_WEIGHT = {
    Item.PRIORITY_HIGH: 40,
    Item.PRIORITY_MEDIUM: 20,
    Item.PRIORITY_LOW: 10,
}

OVERDUE_BONUS = 50
# Each day late adds pressure, but the curve flattens so one ancient task
# can't pin itself to the top forever.
OVERDUE_PER_DAY = 3
OVERDUE_MAX_DAYS = 14

DUE_TODAY_BONUS = 30
DUE_TOMORROW_BONUS = 15
DUE_THIS_WEEK_BONUS = 5
# An undated task is a real task too; give it a small nudge so it can't be
# starved out by dated ones, without letting it win outright.
UNDATED_BONUS = 8

AGE_PER_DAY = 1
AGE_MAX_DAYS = 30

# Only the first N open tasks are scored. Focus mode is a personal tool, not a
# batch job; this keeps the work bounded even if the table grows large.
MAX_CANDIDATES = 500


def focus_score(task, today=None):
    """Return a numeric urgency score for ``task`` (higher = do it sooner)."""
    today = today or timezone.localdate()

    score = PRIORITY_WEIGHT.get(task.priority, PRIORITY_WEIGHT[Item.PRIORITY_MEDIUM])

    if task.due_date:
        days_until = (task.due_date - today).days
        if days_until < 0:
            overdue_days = min(-days_until, OVERDUE_MAX_DAYS)
            score += OVERDUE_BONUS + overdue_days * OVERDUE_PER_DAY
        elif days_until == 0:
            score += DUE_TODAY_BONUS
        elif days_until == 1:
            score += DUE_TOMORROW_BONUS
        elif days_until <= 7:
            score += DUE_THIS_WEEK_BONUS
    else:
        score += UNDATED_BONUS

    age_days = 0
    if task.created_at:
        age_days = (today - task.created_at.date()).days
    score += min(max(age_days, 0), AGE_MAX_DAYS) * AGE_PER_DAY

    return score


def focus_queue(queryset=None, limit=MAX_CANDIDATES):
    """Return open tasks ranked best-first by :func:`focus_score`.

    Scoring happens in Python because it needs per-task date arithmetic and a
    capped, non-linear overdue curve — both awkward to express portably in SQL
    for a list this size.
    """
    tasks = Item.objects.all() if queryset is None else queryset
    candidates = list(tasks.filter(completed=False)[:limit])

    # sorted() is stable, so tasks on equal scores keep their queryset order
    # (which is itself ordered by due date, then newest first).
    return sorted(candidates, key=focus_score, reverse=True)


def focus_reasons(task, today=None):
    """Return short human-readable reasons why ``task`` was recommended.

    A recommendation the user can't understand is one they won't trust, so the
    UI shows its working rather than a bare score.
    """
    today = today or timezone.localdate()
    reasons = []

    if task.is_overdue:
        days_late = abs(task.days_left)
        reasons.append(f'{days_late} day{"s" if days_late != 1 else ""} overdue')

    if task.due_date and not task.completed:
        days_until = (task.due_date - today).days
        if days_until == 0:
            reasons.append('Due today')
        elif days_until == 1:
            reasons.append('Due tomorrow')

    if task.priority == Item.PRIORITY_HIGH:
        reasons.append('High priority')

    if not task.due_date and task.created_at:
        age_days = (today - task.created_at.date()).days
        if age_days >= 7:
            reasons.append(f'Open for {age_days} days')

    return reasons

