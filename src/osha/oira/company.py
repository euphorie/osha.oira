from five import grok
from z3c.form import button
from euphorie.client.company import Company as GenericCompany
from osha.oira.interfaces import IOSHAReportPhaseSkinLayer

grok.templatedir("templates")

class Company(GenericCompany):
    """ Override the class from euphorie.client to add our own layer.
    """
    grok.layer(IOSHAReportPhaseSkinLayer)
    grok.template("report_company")

    @button.buttonAndHandler(u"Skip")
    def handleSkip(self, action):
        url="%s/report" % self.request.survey.absolute_url()
        self.request.response.redirect(url)

