from euphorie.client.browser.country import SessionsView


class OSHASessionsView(SessionsView):

    _portlet_names = [
        "portlet-my-ras",
        "portlet-available-tools",
        "portlet-my-trainings",
    ]
