from euphorie.client.browser.publish import PreviewSurvey
from euphorie.client.browser.publish import PublishSurvey
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin


class PublishSurveyQuaiveForm(QuaiveEditFormMixin, PublishSurvey):
    """Page for publishing a survey, designed to be embedded in Quaive.

    Note: this only displays some text, it does not actually do anything.
    This text snippets are copied from 'euphorie.client.browser.templates.publish.pt'.
    TODO It could be nice to have these texts shared.

    The logic for which text snippets to show, is defined in the PublishSurvey
    view that we inherit from.

    Now some background on what happens when publishing a survey, to make it a
    bit easier to follow.

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
    When you publish a survey, its review_state is set to 'published'
    and its contents are copied to client/country/sector/survey
    where it overrides whatever is there.
    So when you publish a new version of a tool, the old version is gone
    from the client.  So only one tool version can really be seen as
    being published.

    But: the review_state of the old version as it was within the sector's
    folder, is not changed: it is still 'published'.

    An event handler in src/euphorie/content/surveygroup.py sets the id of
    the survey as 'published' on the survey group:

        >>> app.Plone.sectors.eu['covid-19']['covid-19'].published
        'second-version-based-on-import'

    I think this should change the review state of the previous survey to
    'draft' though.  Or really of all sibling surveys (tool versions).
    But that may be too drastic.
    """


class PreviewSurveyQuaiveForm(QuaiveEditFormMixin, PreviewSurvey):
    """Page for previewing a survey, designed to be embedded in Quaive.

    The messages in the template are copied from
    'euphorie.client.browser.templates.preview.pt'.
    """
