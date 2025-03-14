from plone import api
from plone.restapi.services import Service


class TrainingService(Service):
    """Get training info for this survey."""

    def reply(self):
        questions = []
        for brain in api.content.find(
            context=self.context,
            portal_type="euphorie.training_question",
        ):
            obj = brain.getObject()
            questions.append(
                {
                    "id": obj.getId(),
                    "title": obj.Title(),
                    "right_answer": obj.right_answer,
                    "wrong_answer_1": obj.wrong_answer_1,
                    "wrong_answer_2": obj.wrong_answer_2,
                }
            )
        result = {
            "@id": self.request.getURL(),
            "enable_web_training": self.context.enable_web_training,
            "questions": questions,
        }
        return result
