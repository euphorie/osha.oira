from euphorie.content.risk import IRisk
from euphorie.content.utils import StripMarkup
from plone.indexer import indexer


@indexer(IRisk)
def SearchableTextIndexer(obj):
    return " ".join(
        [
            obj.title,
            StripMarkup(obj.problem_description),
            StripMarkup(obj.description),
            StripMarkup(obj.legal_reference),
            obj.caption or "",
            obj.caption2 or "",
            obj.caption3 or "",
            obj.caption4 or "",
            obj.file1_caption or "",
            obj.file2_caption or "",
            obj.file3_caption or "",
            obj.file4_caption or "",
        ]
    )
