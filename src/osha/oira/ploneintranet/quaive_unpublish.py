from euphorie.content.browser.surveygroup import Unpublish
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin


class UnpublishSurveyGroup(QuaiveEditFormMixin, Unpublish):
    """Wrapper around Unpublish page designed to be embedded in Quaive

    This lets euphorie.content.browser.surveygroup.Unpublish do its work on a
    POST request.  But it has a template with only the bare minimum that we
    need from 'euphorie.client.browser.templates.surveygroup_unpublish.pt'.
    """
