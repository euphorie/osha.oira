from ftw.upgrade import UpgradeStep


class RemoveObsoleteBehavior(UpgradeStep):
    """Remove obsolete behavior."""

    def __call__(self):
        self.install_upgrade_profile()
