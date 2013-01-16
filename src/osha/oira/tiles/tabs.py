from euphorie.deployment.tiles.tabs import SiteRootTabsTile


class OiRASiteRootTabsTile(SiteRootTabsTile):

    def update(self):
        super(OiRASiteRootTabsTile, self).update()
        for r in self.tabs:
            if r.get('id') == 'help':
                self.tabs.remove(r)
