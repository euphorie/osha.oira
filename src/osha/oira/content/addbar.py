from euphorie.deployment.tiles.addbar import AddBarTile
from euphorie.content.interfaces import IQuestionContainer


class OshaAddBarTile(AddBarTile):
    def update(self):
        super(OshaAddBarTile, self).update()
        self.library_available = IQuestionContainer.providedBy(self.context)
