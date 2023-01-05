from .. import _
from euphorie.content import survey
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile import field as filefield
from plone.supermodel import model
from plonetheme.nuplone.z3cform.directives import depends
from zope import interface
from zope import schema


help_default_probability = _(
    "help_default_probability",
    default="Indicate how likely occurence of this risk is in a normal situation.",
)
help_default_frequency = _(
    "help_default_frequency",
    default="Indicate how often this risk occurs in a normal situation.",
)
help_default_severity = _(
    "help_default_severity", default="Indicate the severity if this risk occurs."
)


class IOSHASurvey(model.Schema):
    """Adds a logo, URL and name of an external reference site to a survey."""

    enable_external_site_link = schema.Bool(
        title=_(
            "label_external_site_enabled",
            default="Include a logo which links to an external " "website.",
        ),
        description=_(
            "help_external_site_enabled",
            default="Tick this option if you would like to create "
            "a hyperlink on the OiRA tool which points to an "
            "external website. The hyperlink will be in the form "
            "of a logo image.",
        ),
        required=False,
        default=False,
    )

    depends(
        "IOSHASurvey.external_site_url", "IOSHASurvey.enable_external_site_link", "on"
    )
    external_site_url = schema.URI(
        title=_("label_external_site_url", default="External site URL"),
        description=_(
            "help__external_site_url",
            default="This is the URL of an external site that is "
            "linked to. Clicking the logo or the name will take "
            "the user to this URL.",
        ),
        required=False,
    )

    depends(
        "IOSHASurvey.external_site_name", "IOSHASurvey.enable_external_site_link", "on"
    )
    external_site_name = schema.TextLine(
        title=_("label_external_site_name", default="External site name"),
        description=_(
            "help_external_site_name",
            default="This is the name of the external site that is "
            "linked to. It will appear next to the logo.",
        ),
        required=False,
    )

    depends(
        "IOSHASurvey.external_site_logo", "IOSHASurvey.enable_external_site_link", "on"
    )
    external_site_logo = filefield.NamedBlobImage(
        title=_("label_external_site_logo", default="External site logo"),
        description=_(
            "help_image_upload",
            default="Upload an image. Make sure your image is of format "
            "png, jpg or gif and does not contain any special "
            "characters.",
        ),
        required=False,
    )

    enable_custom_evaluation_descriptions = schema.Bool(
        title=_(
            "label_enable_custom_evaluation_descriptions",
            default="The criteria applied to evaluate risks are specific "
            "of this tool? (If not, the common criteria descriptions "
            "will apply).",
        ),
        description=_(
            "help_enable_custom_evaluation_descriptions",
            default="Tick this option if you would like to define "
            "your own descriptions for the criteria of the "
            "evaluation algorithm. The user will see them as hints "
            "when answering the questions to calculate the "
            "priority of a risk.",
        ),
        required=False,
        default=False,
    )

    depends(
        "IOSHASurvey.description_probability",
        "IOSHASurvey.enable_custom_evaluation_descriptions",
        "on",
    )
    description_probability = schema.Text(
        title=_("Probability"),
        description=_(
            "description_criteria_explanation",
            default="Provide your custom explanation here, to override this "
            'default explanation: "${default_explanation}"',
            mapping={"default_explanation": help_default_probability},
        ),
        required=False,
    )

    depends(
        "IOSHASurvey.description_frequency",
        "IOSHASurvey.enable_custom_evaluation_descriptions",
        "on",
    )
    description_frequency = schema.Text(
        title=_("Frequency"),
        description=_(
            "description_criteria_explanation",
            default="Provide your custom explanation here, to override this "
            'default explanation: "${default_explanation}"',
            mapping={"default_explanation": help_default_frequency},
        ),
        required=False,
    )

    depends(
        "IOSHASurvey.description_severity",
        "IOSHASurvey.enable_custom_evaluation_descriptions",
        "on",
    )
    description_severity = schema.Text(
        title=_("Severity"),
        description=_(
            "description_criteria_explanation",
            default="Provide your custom explanation here, to override this "
            'default explanation: "${default_explanation}"',
            mapping={"default_explanation": help_default_severity},
        ),
        required=False,
    )


interface.alsoProvides(IOSHASurvey, IFormFieldProvider)


class IOSHASurveyMarker(survey.ISurvey):
    """Marker interface so that we can register more specific adapters for
    OSHA's survey object."""


interface.classImplements(survey.Survey, IOSHASurveyMarker)


class OSHASurvey(MetadataBase):
    enable_external_site_link = DCFieldProperty(
        IOSHASurvey["enable_external_site_link"]
    )
    external_site_url = DCFieldProperty(IOSHASurvey["external_site_url"])
    external_site_name = DCFieldProperty(IOSHASurvey["external_site_name"])
    external_site_logo = DCFieldProperty(IOSHASurvey["external_site_logo"])
    enable_custom_evaluation_descriptions = DCFieldProperty(
        IOSHASurvey["enable_custom_evaluation_descriptions"]
    )
    description_probability = DCFieldProperty(IOSHASurvey["description_probability"])
    description_frequency = DCFieldProperty(IOSHASurvey["description_frequency"])
    description_severity = DCFieldProperty(IOSHASurvey["description_severity"])
