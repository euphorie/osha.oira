from zope.component import adapter
from zope.interface import implementer
from zope.schema.interfaces import IChoice
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from plonetheme.nuplone.z3cform.widget import SingleRadioWidget
from interfaces import IOiRAFormLayer

@adapter(IChoice, IOiRAFormLayer)
@implementer(IFieldWidget)
def ChoiceWidgetFactory(field, request):
    """ #1537: OSHA wants Choice fields to all look alike and all be radio
        butotns.

        NuPlone on the other hand has radio buttons for items<5 and dropdown
        otherwise.
    """
    return FieldWidget(field, SingleRadioWidget(request))
