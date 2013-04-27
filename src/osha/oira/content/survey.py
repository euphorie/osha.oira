import z3c.form
from five import grok
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope import schema
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import dexterity, form
from plone.namedfile import field as filefield

from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content.survey import View as SurveyView
from euphorie.content.survey import ISurvey
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class IOSHASurvey(form.Schema):
    """ Adds a logo, URL and name of an external reference site to a survey """

    external_site_url = schema.URI(
        title=_("label_external_site_url", default=u"External site URL"),
        description=_("help__external_site_url",
                      default=u"This is the URL of an external site that is"
                      "linked to. Clicking the logo or the name will take the"
                      " user to this URL."),
        required=False)

    external_site_name = schema.TextLine(
        title=_("label_external_site_name", default=u"External site name"),
        description=_("help_external_site_name",
                      default=u"This is the name of an external site that is "
                      "linked to. It will appear next to the logo."),
        required=False)

    external_site_logo = filefield.NamedBlobImage(
        title=_("label_external_site_logo", default=u"External site logo"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
                    u"png, jpg or gif and does not contain any special "
                    u"characters."),
        required=False)


alsoProvides(IOSHASurvey, IFormFieldProvider)


class OSHASurvey(MetadataBase):

    external_site_url = DCFieldProperty(IOSHASurvey['external_site_url'])
    external_site_name = DCFieldProperty(IOSHASurvey['external_site_name'])
    external_site_logo = DCFieldProperty(IOSHASurvey['external_site_logo'])


class OSHASurveyEditForm(dexterity.EditForm):
    grok.context(ISurvey)

    def updateWidgets(self):
        result = super(OSHASurveyEditForm, self).updateWidgets()
        widget = self.widgets.get('evaluation_optional')
        widget.mode = z3c.form.interfaces.HIDDEN_MODE
        return result


class OSHASurveyView(SurveyView):
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
