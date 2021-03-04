# coding=utf-8
from Products.Five import BrowserView


class Certificate(BrowserView):
    """This helper view instructs the @@certificate view on additional fields
    our certificate form should have.

    In addition it provides a macros to provide additional markup that
    for the certificate view
    """

    extra_known_field_names = ("dept_or_region", "contact")
