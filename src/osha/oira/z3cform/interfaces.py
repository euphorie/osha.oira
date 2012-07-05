from plone.app.z3cform.interfaces import IPloneFormLayer
from z3c.form.interfaces import ITextAreaWidget

class IOiRAFormLayer(IPloneFormLayer):
    """ Browser layer to indicate we want OiRA form components.
    """

class ILargeTextAreaWidget(ITextAreaWidget):
    """ Interface for a custom widget for the Homepage's description,
         which is used for manual (non-wysiwyg) editing of HTML.
    """

