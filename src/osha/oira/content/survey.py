from five import grok
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import dexterity, form
from plone.namedfile import field as filefield
from plonetheme.nuplone.z3cform.directives import depends
from zope import schema
from zope import interface
from zope.component import getMultiAdapter
import z3c.form

from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content import survey
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class IOSHASurvey(form.Schema):
    """ Adds a logo, URL and name of an external reference site to a survey """
    enable_external_site_link = schema.Bool(
        title=_("label_external_site_enabled",
                default=u"Include a logo which links to an external "
                        u"website."),
        description=_("help_external_site_enabled",
                      default=u"Tick this option if you would like to create "
                      u"a hyperlink on the OiRA tool which points to an "
                      u"external website. The hyperlink will be in the form "
                      u"of a logo image."),
        required=False,
        default=False)

    depends("IOSHASurvey.external_site_url",
            "IOSHASurvey.enable_external_site_link",
            "on")
    external_site_url = schema.URI(
        title=_("label_external_site_url", default=u"External site URL"),
        description=_("help__external_site_url",
                      default=u"This is the URL of an external site that is "
                      u"linked to. Clicking the logo or the name will take "
                      u"the user to this URL."),
        required=False)

    depends("IOSHASurvey.external_site_name",
            "IOSHASurvey.enable_external_site_link",
            "on")
    external_site_name = schema.TextLine(
        title=_("label_external_site_name", default=u"External site name"),
        description=_("help_external_site_name",
                      default=u"This is the name of the external site that is "
                      u"linked to. It will appear next to the logo."),
        required=False)

    depends("IOSHASurvey.external_site_logo",
            "IOSHASurvey.enable_external_site_link",
            "on")
    external_site_logo = filefield.NamedBlobImage(
        title=_("label_external_site_logo", default=u"External site logo"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
                    u"png, jpg or gif and does not contain any special "
                    u"characters."),
        required=False)

interface.alsoProvides(IOSHASurvey, IFormFieldProvider)


class IOSHASurveyMarker(survey.ISurvey):
    """ Marker interface so that we can register more specific adapters for
        OSHA's survey object.
    """

interface.classImplements(survey.Survey, IOSHASurveyMarker)


class OSHASurvey(MetadataBase):
    enable_external_site_link = \
        DCFieldProperty(IOSHASurvey['enable_external_site_link'])
    external_site_url = DCFieldProperty(IOSHASurvey['external_site_url'])
    external_site_name = DCFieldProperty(IOSHASurvey['external_site_name'])
    external_site_logo = DCFieldProperty(IOSHASurvey['external_site_logo'])


class OSHASurveyEditForm(dexterity.EditForm):
    grok.context(survey.ISurvey)
    grok.layer(IOSHAContentSkinLayer)

    def updateWidgets(self):
        result = super(OSHASurveyEditForm, self).updateWidgets()
        widget = self.widgets.get('evaluation_optional')
        widget.mode = z3c.form.interfaces.HIDDEN_MODE
        return result


class OSHASurveyView(survey.View):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("survey_view")

    def modules_and_profile_questions(self):
        return [self._morph(child) for child in self.context.values()]

    def _morph(self, child):
        state = getMultiAdapter(
                    (child, self.request),
                    name="plone_context_state")

        return dict(id=child.id,
                    title=child.title,
                    url=state.view_url(),
                    is_profile_question=IProfileQuestion.providedBy(child))
