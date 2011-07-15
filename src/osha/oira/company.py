from five import grok
from euphorie.client.company import Company as GenericCompany
from osha.oira.interfaces import IOSHAReportPhaseSkinLayer

grok.templatedir("templates")

class Company(GenericCompany):
    """ Override the class from euphorie.client to add our own layer.
    """
    grok.layer(IOSHAReportPhaseSkinLayer)
    grok.template("report_company")

