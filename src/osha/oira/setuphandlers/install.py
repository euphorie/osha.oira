from plone import api


def _setup_memcached():
    """Setup Memcached configuration for OIRA.

    Ensure that the request_vars setting contain:

    - AUTHENTICATED_USER
    - SERVER_URL
    """
    portal = api.portal.get()
    memcached = portal.get("Memcached")
    if not memcached:
        return

    settings = memcached.getSettings()
    request_vars = settings.get("request_vars") or tuple()

    changed = False
    for var in ("AUTHENTICATED_USER", "SERVER_URL"):
        if var not in request_vars:
            changed = True
            request_vars = request_vars + (var,)

    if not changed:
        return

    settings["request_vars"] = request_vars
    memcached.manage_editProps(memcached.title, settings)


def post_install(context):
    """Post-install script for the OIRA package.

    This function is called after the package is installed. It can be used
    to perform any necessary setup or configuration tasks.
    """
    _setup_memcached()
