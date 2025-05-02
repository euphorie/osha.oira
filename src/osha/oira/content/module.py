from euphorie.content.module import IModule
from euphorie.content.utils import StripMarkup
from plone.indexer import indexer


@indexer(IModule)
def SearchableTextIndexer(obj):
    return " ".join(
        [
            obj.title,
            StripMarkup(obj.description),
            StripMarkup(obj.solution_direction),
            obj.caption or "",
            obj.file1_caption or "",
            obj.file2_caption or "",
            obj.file3_caption or "",
            obj.file4_caption or "",
        ]
    )
