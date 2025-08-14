from osha.oira.content.browser.surveygroup import SurveyGroupImage
from plone import api
from plone.restapi.services.search.get import SearchGet


class SearchWithVersionDescriptionGet(SearchGet):
    """Modified search endpoint that returns the version description of the survey
    instead of the survey group description.
    """

    def reply(self):
        """Override the reply method to include version description."""
        result = super().reply()

        survey_group_items = [
            item for item in result["items"] if item["@type"] == "euphorie.surveygroup"
        ]
        if not survey_group_items:
            return result

        portal = api.portal.get()
        portal_url = portal.absolute_url()

        for item in survey_group_items:
            path = item["@id"].partition(portal_url)[2].lstrip("/")
            survey_group = portal.restrictedTraverse(path)
            survey_group_image_view: SurveyGroupImage = api.content.get_view(
                "survey-group-image", survey_group, self.request
            )
            item["image_url"] = survey_group_image_view.image_url
            survey_version = next(survey_group_image_view.surveys, None)
            if survey_version is not None:
                item["description"] = survey_version.description

        return result
