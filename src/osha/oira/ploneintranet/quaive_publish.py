from euphorie.client.browser.publish import PublishSurvey
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin


class PublishSurveyQuaiveForm(QuaiveEditFormMixin, PublishSurvey):
    """Custom edit form designed to be embedded in Quaive.

    Let's write down here what I think happens when publishing a survey.
    You have this path:

      sectors/country/sector/surveygroup/survey

    Here 'surveygroup' is of type euphorie.surveygroup, which in portal_types
    has title 'OiRA Tool' and description 'A survey'.

    'survey' is of type euphorie.survey, which in portal_type has title
    'OiRA Tool version' and description 'A version of an OiRA Tool.'

    So if you get confused, you are not the only one...

    On the OiRA client side, you have this path:

      client/country/sector/survey

    So on the client side, survey groups do not exist.
    When you publish a survey, it's review_state is set to 'published'
    and its contents are copied to client/country/sector/survey
    where it overrides whatever is there.
    So when you publish a new version of a tool, the old version is gone
    from the client.  So only one tool version can really be seen as
    being published.

    But: the review_state of the old version as it was within the sectors
    folder, is not changed: it is still 'published'.

    An event handler in src/euphorie/content/surveygroup.py sets the id of
    the survey as 'published' on the survey group:

        >>> app.Plone.sectors.eu['covid-19']['covid-19'].published
        'second-version-based-on-import'

    I think this should change the review state of the previous survey to
    'draft' though.  Or really of all sibling surveys (tool versions).
    """
