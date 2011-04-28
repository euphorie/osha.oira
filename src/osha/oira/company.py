from five import grok
from euphorie.client.company import Company as GenericCompany
from interfaces import IOSHAReportPhaseSkinLayer

class Company(GenericCompany):
    """ Override the class from euphorie.client to add our own layer.
    """
    grok.layer(IOSHAReportPhaseSkinLayer)

