from ftw.upgrade import UpgradeStep


class InstallTheRecaptchaAddOn(UpgradeStep):
    """Install the recaptcha add on."""

    def __call__(self):
        self.ensure_profile_installed("plone.formwidget.recaptcha:default")
