from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import implementsOnly
from ZPublisher.HTTPRequest import FileUpload
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IText
from z3c.form.browser.select import SelectWidget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from z3c.form.interfaces import IDataManager
from z3c.form.interfaces import NOVALUE
from z3c.form.browser.file import FileWidget
from plonetheme.nuplone.z3cform.widget import SingleRadioWidget
from plonetheme.nuplone.z3cform.utils import getVocabulary
from plone.namedfile.interfaces import INamedFileField
from plone.formwidget.namedfile.widget import NamedFileWidget
from ..interfaces import IOSHAContentSkinLayer
from .interfaces import ILargeTextAreaWidget
from .interfaces import IOiRAFormLayer


@adapter(IChoice, IOiRAFormLayer)
@implementer(IFieldWidget)
def ChoiceWidgetFactory(field, request):
    """ #1537: OSHA wants Choice fields to all look alike and all be radio
        buttons.

        NuPlone on the other hand has radio buttons for items<5 and dropdown
        otherwise.

        We increase min here
    """
    vocabulary=getVocabulary(field)
    if vocabulary is None or len(vocabulary)>6:
        widget=SelectWidget
    else:
        widget=SingleRadioWidget
    return FieldWidget(field, widget(request))


class LargeTextAreaWidget(TextAreaWidget,  Widget):
    """Textarea widget implementation."""
    implementsOnly(ILargeTextAreaWidget)

    klass = u'textarea-widget'
    value = u''


@adapter(IText, IOSHAContentSkinLayer)
@implementer(IFieldWidget)
def LargeTextAreaFieldWidget(field, request):
    return FieldWidget(field, LargeTextAreaWidget(request))


class NicerNamedFileWidget(NamedFileWidget):
    def extract(self, default=NOVALUE):
        action = self.request.get("%s.action" % self.name, None)
        if action == 'remove':
            return None

        value = FileWidget.extract(self, default)

        if value is NOVALUE or \
                (isinstance(value, FileUpload) and not value.filename):
            if self.ignoreContext:
                return default

            dm = getMultiAdapter((self.context, self.field,), IDataManager)
            return dm.get()

        # Note that we allow the user to upload an empty file.
        return value


@adapter(INamedFileField, IOiRAFormLayer)
@implementer(IFieldWidget)
def NamedFileWidgetFactory(field, request):
    return FieldWidget(field, NicerNamedFileWidget(request))
