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

help_default_probability = _(
    u"help_default_probability",
    default=u"Indicate how likely occurence of this risk is in a normal situation.")
help_default_frequency = _(
    u"help_default_frequency",
    default=u"Indicate how often this risk occurs in a normal situation.")
help_default_severity =_(
    u"help_default_severity",
    default=u"Indicate the severity if this risk occurs.")


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

    enable_custom_evaluation_descriptions = schema.Bool(
        title=_("label_enable_custom_evaluation_descriptions",
                default=u"The criteria applied to evaluate risks are specific "
                u"of this tool? (If not, the common criteria descriptions "
                u"will apply)."),
        description=_("help_enable_custom_evaluation_descriptions",
                      default=u"Tick this option if you would like to define "
                      u"your own descriptions for the criteria of the "
                      u"evaluation algorithm. The user will see them as hints "
                      u"when answering the questions to calculate the "
                      u"priority of a risk."),
        required=False,
        default=False)

    depends("IOSHASurvey.description_probability",
            "IOSHASurvey.enable_custom_evaluation_descriptions",
            "on")
    description_probability = schema.Text(
        title=_(u"Probability"),
        description=_(
            u"description_criteria_explanation",
            default=u'Provide your custom explanation here, to override this '
                    u'default explanation: "${default_explanation}"',
            mapping={
                u'default_explanation': help_default_probability}
        ),
        required=False,
    )

    depends("IOSHASurvey.description_frequency",
            "IOSHASurvey.enable_custom_evaluation_descriptions",
            "on")
    description_frequency = schema.Text(
        title=_(u"Frequency"),
        description=_(
            u"description_criteria_explanation",
            default=u'Provide your custom explanation here, to override this '
                    u'default explanation: "${default_explanation}"',
            mapping={
                u'default_explanation': help_default_frequency}
        ),
        required=False,
    )

    depends("IOSHASurvey.description_severity",
            "IOSHASurvey.enable_custom_evaluation_descriptions",
            "on")
    description_severity = schema.Text(
        title=_(u"Severity"),
        description=_(
            u"description_criteria_explanation",
            default=u'Provide your custom explanation here, to override this '
                    u'default explanation: "${default_explanation}"',
            mapping={
                u'default_explanation': help_default_severity}
        ),
        required=False,
    )

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
    enable_custom_evaluation_descriptions = DCFieldProperty(IOSHASurvey['enable_custom_evaluation_descriptions'])
    description_probability = DCFieldProperty(IOSHASurvey['description_probability'])
    description_frequency = DCFieldProperty(IOSHASurvey['description_frequency'])
    description_severity = DCFieldProperty(IOSHASurvey['description_severity'])


class OSHASurveyEditForm(dexterity.EditForm):
    grok.context(survey.ISurvey)
    grok.layer(IOSHAContentSkinLayer)

    def updateWidgets(self):
        result = super(OSHASurveyEditForm, self).updateWidgets()
        evaluation_optional = self.widgets.get('evaluation_optional')
        evaluation_optional.mode = z3c.form.interfaces.HIDDEN_MODE
        if self.context.aq_parent.evaluation_algorithm == 'french':
            description_probability = self.widgets.get('IOSHASurvey.description_probability')
            description_probability.mode = z3c.form.interfaces.HIDDEN_MODE
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
