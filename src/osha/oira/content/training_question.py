from euphorie.content.training_question import ITrainingQuestion
from plone.indexer import indexer


@indexer(ITrainingQuestion)
def SearchableTextIndexer(obj):
    return " ".join(
        [
            obj.title,
            obj.right_answer,
            obj.wrong_answer_1,
            obj.wrong_answer_2,
        ]
    )
