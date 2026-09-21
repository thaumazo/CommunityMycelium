from .view_simulation import compute_session_simulation, activate, deactivate


class ViewSimulationMiddleware:
    """
    Attaches the current user's active view-simulation (if any) to the
    request and makes it available to apps.acl.utils permission checks for
    the duration of the request only. See view_simulation.py for the
    security model.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        simulation = compute_session_simulation(request)
        token = activate(request, simulation)
        try:
            response = self.get_response(request)
        finally:
            deactivate(token)
        return response
