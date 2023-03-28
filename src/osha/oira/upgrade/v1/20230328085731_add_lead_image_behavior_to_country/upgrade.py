from ftw.upgrade import UpgradeStep


class AddLeadImageBehaviorToCountry(UpgradeStep):
    """Add lead image behavior to country."""

    def __call__(self):
        self.install_upgrade_profile()
