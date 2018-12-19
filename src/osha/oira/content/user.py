# coding=utf-8
from euphorie.content import user
from euphorie.content.user import IUser
from five import grok
from os import urandom
from osha.oira.content.statistics import IOSHAContentSkinLayer
from p01.widget.password.interfaces import IPasswordConfirmationWidget
from plone.directives import form
from Products.Archetypes.utils import IStatusMessage
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IValidator
from zope import schema
from zope.interface import Interface

import logging
import string


log = logging.getLogger(__name__)


def NotifyError(user, e):
    log.error(
        "%r sending account activation link to: %s",
        e,
        user.contact_email,
    )
    flash = IStatusMessage(user.REQUEST).addStatusMessage
    flash(
        (
            u'Could not send an account activation email to "{}".'
            u'Please contact the site administrator.'
        ).format("error")
    )
    return


class PasswordValidator(user.PasswordValidator):
    grok.implements(IValidator)
    grok.adapts(
        Interface,
        IOSHAContentSkinLayer,
        IForm,
        schema.Password,
        IPasswordConfirmationWidget,
    )

    def validate(self, value):
        """ Don't validate when adding a country manager or sector.
            They'll get a default password (see default_password below) and
            then an email with link to set their password themselves.
            Refs: #10284
        """
        if (
            IAddForm.providedBy(self.view) and self.view.portal_type in [
                'euphorie.countrymanager',
                'euphorie.sector',
            ]
        ):
            return
        return super(PasswordValidator, self).validate(value)


@form.default_value(field=IUser['password'])
def default_password(data):
    """ Set a default value for passwords, otherwise new country managers and
        sectors will get empty passwords set.
        Refs: #10284
    """
    chars = string.letters + string.digits
    return u"".join([chars[ord(c) % len(chars)] for c in urandom(20)])
