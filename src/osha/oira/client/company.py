# coding=utf-8
from five import grok
from z3c.form import button
from euphorie.client.company import Company as GenericCompany
from .interfaces import IOSHAReportPhaseSkinLayer

grok.templatedir("templates")


class Company(GenericCompany):
    """ Override the class from euphorie.client to add our own layer.
    """
    grok.layer(IOSHAReportPhaseSkinLayer)
    grok.template("report_company")

    @button.buttonAndHandler(u"Previous")
    def handlePrevious(self, action):
        url = "%s/report" % self.request.survey.absolute_url()
        self.request.response.redirect(url)

    @button.buttonAndHandler(u"Next")
    def handleNext(self, action):
        (data, errors) = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        url = "%s/report/view" % self.request.survey.absolute_url()
        self.request.response.redirect(url)

    @button.buttonAndHandler(u"Skip")
    def handleSkip(self, action):
        # XXX: This a hack. We need to know if a company report has been
        # skipped but can't add new SQL columns. So we mark the country 'xx'.
        # (Country field is restricted to 3 chars). For #4436.
        data = {
            'conductor': None,
            'country': u'xx',
            'employees': None,
            'referer': None,
            'workers_participated': None,
            'needs_met': None,
            'recommend_tool': None,
        }
        self.applyChanges(data)
        url = "%s/report/view" % self.request.survey.absolute_url()
        self.request.response.redirect(url)
