# coding=utf-8
from euphorie.content import surveygroup
from five import grok
from plone.directives.form import SchemaEditForm
from z3c import form


class Edit(SchemaEditForm):
    grok.context(surveygroup.ISurveyGroup)

    def updateWidgets(self):
        result = super(Edit, self).updateWidgets()
        # Hide the "Obsolete Survey" option, as OiRA doesn't use that feature, and it's
        # definitely not called a "survey". See https://projects.syslab.com/issues/9133
        widget = self.widgets.get('obsolete')
        widget.mode = form.interfaces.HIDDEN_MODE
        return result

    def update(self):
        if self.request.method == "POST":
            if 'form.widgets.obsolete' in self.request.form:
                del self.request.form['form.widgets.obsolete']
            self.request.form['form.widgets.obsolete-empty-marker'] = '1'
        super(Edit, self).update()
