from zope.component import adapter
from zope.interface import implementer
from zope.interface import implementsOnly
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import IText
from z3c.form.browser.select import SelectWidget
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from z3c.form.widget import Widget
from plonetheme.nuplone.z3cform.widget import SingleRadioWidget
from plonetheme.nuplone.z3cform.utils import getVocabulary
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
    vocabulary = getVocabulary(field)
    if vocabulary is None or len(vocabulary) > 6:
        widget = SelectWidget
    else:
        widget = SingleRadioWidget
    return FieldWidget(field, widget(request))


class LargeTextAreaWidget(TextAreaWidget, Widget):
    """Textarea widget implementation."""
    implementsOnly(ILargeTextAreaWidget)

    klass = u'textarea-widget'
    value = u''


@adapter(IText, IOSHAContentSkinLayer)
@implementer(IFieldWidget)
def LargeTextAreaFieldWidget(field, request):
    return FieldWidget(field, LargeTextAreaWidget(request))
