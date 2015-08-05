from five import grok
from euphorie.content import risk
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.dexterity.behaviors.metadata import MetadataBase
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.namedfile import field as filefield
from zope import interface
from zope import schema
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class IOSHARisk(form.Schema):
    form.fieldset(
        "additional_content",
        label=_("header_additional_content", default=u"Additional content"),
        description=_(
            "intro_additional_content",
            default=u"Attach any additional content you consider helpful "
            "for the user"),
        fields=[
            "file1", "file1_caption", "file2", "file2_caption",
            "file3", "file3_caption", "file4", "file4_caption"])

    file1 = filefield.NamedBlobFile(
        title=_("label_file", default=u"Content file"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
            u"png, jpg or gif and does not contain any special "
            u"characters."),
        required=False)
    file1_caption = schema.TextLine(
        title=_("label_file_caption", default=u"Content caption"),
        required=False)

    file2 = filefield.NamedBlobFile(
        title=_("label_file", default=u"Content file"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
            u"png, jpg or gif and does not contain any special "
            u"characters."),
        required=False)
    file2_caption = schema.TextLine(
        title=_("label_file_caption", default=u"Content caption"),
        required=False)

    file3 = filefield.NamedBlobFile(
        title=_("label_file", default=u"Content file"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
            u"png, jpg or gif and does not contain any special "
            u"characters."),
        required=False)
    file3_caption = schema.TextLine(
        title=_("label_file_caption", default=u"Content caption"),
        required=False)

    file4 = filefield.NamedBlobFile(
        title=_("label_file", default=u"Content file"),
        description=_(
            "help_image_upload",
            default=u"Upload an image. Make sure your image is of format "
            u"png, jpg or gif and does not contain any special "
            u"characters."),
        required=False)
    file4_caption = schema.TextLine(
        title=_("label_file_caption", default=u"Content caption"),
        required=False)

interface.alsoProvides(IOSHARisk, IFormFieldProvider)


class IOSHARiskMarker(risk.IRisk):
    """ Marker interface so that we can register more specific adapters for
        OSHA's survey object.
    """

interface.classImplements(risk.Risk, IOSHARiskMarker)


class OSHARisk(MetadataBase):
    file1 = DCFieldProperty(IOSHARisk['file1'])
    file1_caption = DCFieldProperty(IOSHARisk['file1_caption'])
    file2 = DCFieldProperty(IOSHARisk['file2'])
    file2_caption = DCFieldProperty(IOSHARisk['file2_caption'])
    file3 = DCFieldProperty(IOSHARisk['file3'])
    file3_caption = DCFieldProperty(IOSHARisk['file3_caption'])
    file4 = DCFieldProperty(IOSHARisk['file4'])
    file4_caption = DCFieldProperty(IOSHARisk['file4_caption'])


class IOSHAFrenchRisk(risk.IFrenchRisk, IOSHARisk):
    pass


class IOSHAKinneyRisk(risk.IKinneyRisk, IOSHARisk):
    pass


class OSHAFormMixin:
    """ """
    def setDynamicDescriptions(self):
        """ Set the evaluation_method description depending on the evaluation
            algorithm (Kinney or French)
        """
        evalgroup = self.groups[self.order.index('header_evaluation')]
        evalfield = evalgroup.fields.get('evaluation_method')
        if self.evaluation_algorithm == 'kinney':
            evalfield.field.description = \
                _("help_evaluation_method_kinney",
                default="Choose between ESTIMATED (rough estimation) or "
                        "CALCULATED (combination of probability, frequency "
                        "and severity) method.")

        elif self.evaluation_algorithm == 'french':
            evalfield.field.description = \
                _("help_evaluation_method_french",
                default="Choose between ESTIMATED (rough estimation) or "
                        "CALCULATED (combination of frequency "
                        "and severity) method.")


class Add(risk.Add, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.context(risk.IRisk)
    grok.layer(IOSHAContentSkinLayer)

    def __init__(self, context, request):
        risk.Add.__init__(self, context, request)
        self.order.append('header_additional_content')

    def updateFields(self):
        super(Add, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Risk")


class Edit(risk.Edit, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.context(risk.IRisk)
    grok.layer(IOSHAContentSkinLayer)

    def __init__(self, context, request):
        risk.Edit.__init__(self, context, request)
        self.order.append('header_additional_content')
        self.evaluation_algorithm = context.evaluation_algorithm()
        if self.evaluation_algorithm == u"french":
            self.schema = IOSHAFrenchRisk
        else:
            self.schema = IOSHAKinneyRisk

    def updateFields(self):
        super(Edit, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")
