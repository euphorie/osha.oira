from plone import api
from plone.restapi.services import Service


class SurveyPublicationCountService(Service):
    """A JSON service version of @@survey-publication-count"""

    def reply(self):
        view = api.content.get_view(
            "survey-publication-count", self.context, self.request
        )
        return {
            "@id": self.request.getURL(),
            "items": view.survey_details,
        }
