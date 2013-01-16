from plone.tiles import Tile


class FooterTile(Tile):
    def __call__(self):
        return self.index()
