from plone import api
from plone.memoize.view import memoize
from Products.CMFPlone.utils import get_installer
from Products.Five import BrowserView

import pkg_resources


class About(BrowserView):
    """"""

    @property
    def packages(self):
        return ["Euphorie", "osha.oira", "NuPlone"]

    def get_version(self, package):
        try:
            version = pkg_resources.get_distribution(package).version
        except pkg_resources.DistributionNotFound:
            version = "N/A"
        return version

    @property
    @memoize
    def installer(self):
        return get_installer(self.context, self.request)

    def is_installed(self, package):
        return self.installer.is_product_installed(package)

    def versions(self):
        version_items = [
            (package, self.get_version(package)) for package in self.packages
        ]
        versions = [
            "{} {} {}".format(
                name, version, "(installed)" if self.is_installed(name) else ""
            )
            for name, version in version_items
        ]
        controlpanel = api.content.get_view(
            context=self.context, request=self.request, name="overview-controlpanel"
        )
        versions.extend(controlpanel.version_overview())
        return versions
