from collective.ftw.upgrade import UpgradeStep


class UpdateMatomoScript(UpgradeStep):
    """Update Matomo script."""

    def __call__(self):
        self.install_upgrade_profile()
