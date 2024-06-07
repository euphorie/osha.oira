from euphorie.client.browser.publish import PublishSurvey


# from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin


class PublishSurveyQuaiveForm(PublishSurvey):
    """Custom edit form designed to be embedded in Quaive

    Actually, there is nothing custom yet.
    We probably want to use QuaiveEditFormMixin, but then we need our own template,
    or use quaive-edit.pt and get this to show the PublishSurvey form,
    but then we need to make make some changes in
    euphorie.client.browser.templates/publish.pt so that the various texts there
    are available in the PublishSurvey class, as a label or something.  I mean
    texts like "Are you sure you want to publish this OiRA Tool?", or "republish".
    That should be doable in a way that is fine for standard Euphorie as well,
    but takes a bit of time.
    """
