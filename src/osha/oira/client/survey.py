# coding=utf-8
from euphorie.client.browser import session
from five import grok

grok.templatedir("templates")


class OSHAStatusPrint(session.Status):
    """ Override the 'status' page to provide our own template.
    """

    grok.template("status_print")
    grok.name("status_print")
