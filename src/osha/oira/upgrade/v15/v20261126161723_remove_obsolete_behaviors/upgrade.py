from collective.ftw.upgrade import UpgradeStep


class RemoveObsoleteBehaviors(UpgradeStep):
    """Remove obsolete module and risk behaviors."""

    def __call__(self):
        self.install_upgrade_profile()
