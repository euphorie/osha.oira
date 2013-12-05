from euphorie.content import surveygroup
from five import grok
from plone.directives.form import SchemaEditForm
from z3c import form

class Edit(SchemaEditForm):
    grok.context(surveygroup.ISurveyGroup)

    def updateWidgets(self):
        result = super(Edit, self).updateWidgets()
        widget = self.widgets.get('obsolete')
        widget.mode = form.interfaces.HIDDEN_MODE
        return result
