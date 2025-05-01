from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content.utils import StripMarkup
from plone.indexer import indexer


@indexer(IProfileQuestion)
def SearchableTextIndexer(obj):
    return " ".join(
        [
            obj.title,
            StripMarkup(obj.question),
            StripMarkup(obj.label_multiple_present),
            StripMarkup(obj.label_single_occurance),
            StripMarkup(obj.label_multiple_occurances),
            StripMarkup(obj.description),
        ]
    )
