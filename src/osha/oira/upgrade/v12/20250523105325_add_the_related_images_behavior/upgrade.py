from ftw.upgrade import UpgradeStep


class AddTheRelatedImagesBehavior(UpgradeStep):
    """Add the related images behavior."""

    def __call__(self):
        self.install_upgrade_profile()
