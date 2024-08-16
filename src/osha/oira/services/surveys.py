from Acquisition import aq_base
from Acquisition import aq_inner
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


class ToolVersionsGet(Service):
    """Get info from the oira tool (survey group) and its versions (surveys)."""

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
        }

        # Now add info for each tool version.
        items = []
        for survey in surveygroup.contentValues():
            items.append(self.get_survey_info(survey))
        result["versions"] = items
        return result
