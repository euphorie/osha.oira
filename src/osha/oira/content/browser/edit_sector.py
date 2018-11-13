# coding=utf-8
from euphorie.content.sector import Settings
from five import grok
from osha.oira.interfaces import IProductLayer


grok.templatedir("templates")


class OSHASettings(Settings):
    grok.layer(IProductLayer)
    grok.name('edit')
    grok.template('settings')

    def extractData(self):
        unwanted_fields = ('locked', 'password')
        self.fields = self.fields.omit(*unwanted_fields)
        for key in unwanted_fields:
            if key in self.widgets:
                del self.widgets[key]
        return super(OSHASettings, self).extractData()
