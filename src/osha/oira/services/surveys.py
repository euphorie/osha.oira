from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.base.utils import base_hasattr
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


class ToolVersionsGet(Service):
    """Get info from the oira tool (survey group) and its versions (surveys).

    And we can use a bit of info from the country as well.
    """

    def get_survey_info(self, survey):
        # Is this survey the tool version that is published on the client?
        published_on_client = self.published_tool_version_id == survey.id
        # Note that if 'published_on_client' is true, the review_state
        # should be 'published', otherwise 'draft', but this is not always
        # in sync.  So instead of 'api.content.get_state(obj=survey)',
        # let's report what the state is meant to be.
        review_state = "published" if published_on_client else "draft"
        # The 'published' attribute should be the date of publication of this
        # survey, but we could inherit this attribute from the surveygroup,
        # where it would contain the id of the client-published tool version.
        # So do not inherit this.
        published_date = getattr(aq_base(survey), "published", None)
        return {
            "@id": survey.absolute_url(),
            "id": survey.id,
            "title": survey.Title(),
            "created": json_compatible(survey.created()),
            "modified": json_compatible(survey.modified()),
            "published": json_compatible(published_date),
            "review_state": review_state,
        }

    def reply(self):
        surveygroup = aq_inner(self.context)
        # The 'published' attribute of the surveygroup has the id of the tool
        # version that is currently published on the OiRA client side.
        self.published_tool_version_id = getattr(surveygroup, "published", None)

        # First gather info about the survey group.
        result = {
            "@id": f"{surveygroup.absolute_url()}/@tool-versions",
            "id": surveygroup.id,
            "title": surveygroup.Title(),
            "published_tool_version_id": self.published_tool_version_id,
            "@type": surveygroup.portal_type,
            # We will try to get the next ones from one of the surveys.
            "image_url": "",
            "summary": "",
            "introduction": "",
        }

        # Add info about the country.
        country = aq_parent(aq_parent(surveygroup))
        result["country"] = {
            "enable_web_training": country.enable_web_training,
            "enable_consultancy": country.enable_consultancy,
        }

        # Now add info for each tool version.
        items = []
        surveys = surveygroup.contentValues()
        for survey in surveys:
            items.append(self.get_survey_info(survey))
        result["versions"] = items

        # Get some more info from the published survey, or from the first one.
        survey = (
            surveygroup.get(self.published_tool_version_id)
            if self.published_tool_version_id
            else None
        )
        if survey is None and surveys:
            survey = surveys[0]
        if survey is not None:
            if base_hasattr(survey, "image") and survey.image:
                # The survey has a not inherited image attribute and it is not empty.
                result["image_url"] = f"{survey.absolute_url()}/@@images/image"
            if base_hasattr(survey, "introduction"):
                result["introduction"] = survey.introduction
            # The description field always exists.
            result["summary"] = survey.Description()

        return result
