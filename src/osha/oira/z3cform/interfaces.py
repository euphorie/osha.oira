from plonetheme.nuplone.z3cform.interfaces import INuPloneFormLayer
from z3c.form.interfaces import ITextAreaWidget

class IOiRAFormLayer(INuPloneFormLayer):
    """ Browser layer to indicate we want OiRA form components.
    """

class ILargeTextAreaWidget(ITextAreaWidget):
    """ Interface for a custom widget for the Homepage's description,
         which is used for manual (non-wysiwyg) editing of HTML.
    """

