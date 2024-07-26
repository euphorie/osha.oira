from Acquisition import aq_chain
from Acquisition import aq_inner
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service


class ToolVersionsGet(Service):
    """Get info from the containing tool and its versions.

    From the Quaive side we request this.
    Then we know if we are on a path that is within a survey group,
    and we can show info about the versions, if we want.

    This is meant to show information about versions like on the left
    in the prototype:
    https://proto.quaivecloud.com/tools/audio-visual-productions/edit

    We need this information in the sidebar.
    And we don't yet have a way of knowing what the "remote" portal_type
    is of the path we are viewing in Quaive, so we don't know if we are
    currently viewing a country or survey group or survey or risk.
    So from the Quaive side we have no idea if we should show this version
    information.  An extra REST API service then seems a good way to me.
    """

    def get_survey_info(self, survey):
        # Is this survey the tool version that is published on the client?
        published_on_client = self.published_tool_version_id == survey.id
        # Note that if 'published_on_client' is true, the review_state
        # should be 'published', otherwise 'draft', but this is not always
        # in sync.  So instead of 'api.content.get_state(obj=survey)',
        # let's report what the state is meant to be.
        review_state = "published" if published_on_client else "draft"
        return {
            "@id": survey.absolute_url(),
            "id": survey.id,
            "title": survey.Title(),
            "created": json_compatible(survey.created()),
            "modified": json_compatible(survey.modified()),
            "published": json_compatible(survey.published),
            "review_state": review_state,
        }

    def reply(self):
        obj = aq_inner(self.context)
        # First gather basic info about the context and request.
        result = {
            "@id": f"{obj.absolute_url()}/@tool-versions",
            # "id": obj.id,
            "@type": obj.portal_type,
        }
        survey = None
        surveygroup = None
        # Find nearest survey and survey group.
        # One of these might be the current object as well.
        for parent in aq_chain(obj):
            portal_type = getattr(parent, "portal_type", "")
            if not portal_type:
                break
            if portal_type == "euphorie.survey":
                survey = parent
            elif portal_type == "euphorie.surveygroup":
                surveygroup = parent

        if not surveygroup:
            # We are outside of a survey group, nothing to see here.
            return result

        # The 'published' attribute of the surveygroup has the id of the tool
        # version that is currently published on the OiRA client side.
        self.published_tool_version_id = getattr(surveygroup, "published", None)

        result["surveygroup"] = {
            "@id": surveygroup.absolute_url(),
            "title": surveygroup.Title(),
            "published_tool_version_id": self.published_tool_version_id,
        }
        if survey:
            current_survey_id = survey.id
            result["survey"] = self.get_survey_info(survey)
        else:
            current_survey_id = None
        items = []
        for survey in surveygroup.contentValues():
            if survey.id == current_survey_id:
                # This is the survey on which path we are.
                continue
            items.append(self.get_survey_info(survey))
        result["items"] = items
        return result
