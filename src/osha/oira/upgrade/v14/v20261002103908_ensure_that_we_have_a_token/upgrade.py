from collective.ftw.upgrade import UpgradeStep
from osha.oira.setuphandlers.install import _setup_default_token


class EnsureThatWeHaveAToken(UpgradeStep):
    """Ensure that we have a token."""

    def __call__(self):
        _setup_default_token()
