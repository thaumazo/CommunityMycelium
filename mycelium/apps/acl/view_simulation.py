"""
Support for letting a signed-in user preview the site as if they had a
lower/different visibility level (Public, Member, or a specific Commons they
belong to), without affecting any other user or granting any access beyond
what the real user already has.

Security model:
- The simulated mode is stored in the user's own session only.
- It is re-validated against the database on every request (a stale or
  tampered session value is discarded rather than trusted).
- It only ever narrows "view" permission checks; every other action
  ("add", "change", "delete", "delegate", ...) always uses the user's real,
  full permissions regardless of simulation state.
- The active simulation is scoped to the current request's authenticated
  user id, so it can never be (mis)applied to a permission check performed
  for a different user.
"""

import contextvars

SESSION_KEY = "view_simulation"
VALID_MODES = {"public", "member", "commons"}

# Holds (mode, commons_id, label, viewer_user_id) for the current request/thread.
_current_simulation = contextvars.ContextVar("acl_view_simulation", default=None)


def compute_session_simulation(request):
    """
    Validate the requested simulation (from session) against real, current
    data and return (mode, commons_id, label) or None. Never trusts the
    session value blindly - invalid/stale state is cleared.
    """
    if not request.user.is_authenticated:
        return None

    raw = request.session.get(SESSION_KEY)
    if not raw or not isinstance(raw, dict):
        return None

    mode = raw.get("mode")
    if mode not in VALID_MODES:
        request.session.pop(SESSION_KEY, None)
        return None

    if mode == "commons":
        from django.db.models import Q
        from apps.commons.models import Commons

        commons_id = raw.get("commons_id")
        commons = Commons.objects.filter(
            Q(pk=commons_id)
            & (Q(owners=request.user) | Q(admins=request.user) | Q(members=request.user))
        ).first()
        if not commons:
            # No longer (or never) a member of this commons; drop stale state.
            request.session.pop(SESSION_KEY, None)
            return None
        return ("commons", commons.pk, commons.title)

    label = "Public" if mode == "public" else "Member"
    return (mode, None, label)


def activate(request, simulation):
    """Push the validated simulation into the request and context var. Returns a reset token."""
    request.view_simulation = simulation
    value = None
    if simulation:
        mode, commons_id, label = simulation
        value = (mode, commons_id, label, request.user.pk)
    return _current_simulation.set(value)


def deactivate(token):
    _current_simulation.reset(token)


def get_simulation_for(user):
    """Return (mode, commons_id, label) if a simulation is active for exactly this user, else None."""
    data = _current_simulation.get()
    if not data:
        return None
    mode, commons_id, label, viewer_id = data
    if user is None or getattr(user, "pk", None) != viewer_id:
        return None
    return (mode, commons_id, label)
