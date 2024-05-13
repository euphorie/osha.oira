from ftw.upgrade import UpgradeStep
from plone import api


try:
    from plone.base.utils import get_installer
except ImportError:
    from Products.CMFPlone.utils import get_installer


class EnsurePloneRestapiIsInstalled(UpgradeStep):
    """Ensure plone.restapi is installed."""

    def __call__(self):
        installer = get_installer(api.portal.get())
        if installer.is_product_installed("plone.restapi"):
            return
        installer.install_product("plone.restapi")
