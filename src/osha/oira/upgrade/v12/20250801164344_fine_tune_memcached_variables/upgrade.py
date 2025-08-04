from ftw.upgrade import UpgradeStep
from osha.oira.setuphandlers.install import _setup_memcached


class FineTuneMemcachedVariables(UpgradeStep):
    """Fine tune memcached variables.

    Ensure that the request_vars setting contains:

    - AUTHENTICATED_USER
    - SERVER_URL
    """

    def __call__(self):
        _setup_memcached()
