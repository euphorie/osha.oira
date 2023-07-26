from ftw.upgrade import UpgradeStep


class EnableTheLockingFeature(UpgradeStep):
    """Enable the locking feature."""

    def __call__(self):
        self.install_upgrade_profile()
