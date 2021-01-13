# coding=utf-8
from Acquisition import aq_inner
from euphorie.content import MessageFactory as _
from euphorie.content.country import ManageUsers
from euphorie.content.sector import ISector
from five import grok
from htmllaundry.z3cform import HtmlText
from osha.oira.interfaces import IOSHAContentSkinLayer
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives import form
from plone.supermodel import model
from plonetheme.nuplone.z3cform.directives import depends
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import invariant


grok.templatedir("templates")


class OSHAManageUsers(ManageUsers):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("user_mgmt")

    def update(self):
        from euphorie.content.countrymanager import ICountryManager

        super(OSHAManageUsers, self).update()
        country = aq_inner(self.context)
        self.sectors = []
        for sector in country.values():
            if not ISector.providedBy(sector):
                continue
            entry = {
                "id": sector.id,
                "login": sector.login,
                "password": sector.password,
                "title": sector.title,
                "url": sector.absolute_url(),
                "locked": sector.locked,
                "contact_email": sector.contact_email,
            }
            view = sector.restrictedTraverse("manage-ldap-users", None)
            if not view:
                entry["managers"] = []
            else:
                entry["managers"] = [
                    userid
                    for userid in view.local_roles_userids()
                    if view.get_user(userid)
                ]
            self.sectors.append(entry)

        self.sectors.sort(key=lambda s: s["title"].lower())
        self.managers = [
            {
                "id": manager.id,
                "login": manager.login,
                "title": manager.title,
                "url": manager.absolute_url(),
                "locked": manager.locked,
                "contact_email": manager.contact_email,
            }
            for manager in country.values()
            if ICountryManager.providedBy(manager)
        ]
        self.managers.sort(key=lambda s: s["title"].lower())


class IOSHACountry(model.Schema):
    """Additional fields for the OSHA countries"""

    certificates_enabled = schema.Bool(
        title=_("Enable certificates"),
        description=_(
            "If enabled, users will be able to obtain an official certificate of "
            "completion once they reach the threshold defined below."
        ),
        default=False,
    )
    depends(
        "IOSHACountry.certificate_initial_threshold",
        "IOSHACountry.certificates_enabled",
        "on",
    )
    certificate_initial_threshold = schema.Int(
        title=_("Certificate initial threshold (in percent)"),
        description=_(
            "After a session completion rate is greater than this limit, "
            "the user will be informed about the possibility to earn a certificate. "
        ),
        default=10,
        min=0,
        max=100,
    )

    depends(
        "IOSHACountry.certificate_completion_threshold",
        "IOSHACountry.certificates_enabled",
        "on",
    )
    certificate_completion_threshold = schema.Int(
        title=_("Certificate completion threshold (in percent)"),
        description=_(
            "After a session completion rate is greater than this limit "
            "the user will earn a certificate."
        ),
        default=85,
        min=0,
        max=100,
    )
    depends(
        "IOSHACountry.certificate_explanatory_sentence",
        "IOSHACountry.certificates_enabled",
        "on",
    )
    certificate_explanatory_sentence = HtmlText(
        title=_("Explanatory sentence"),
        description=_(
            "A short explanation that is shown to the user after reaching the initial "
            "threshold. You can use this to point to an external website that provides "
            "more information."
        ),
        required=False,
    )
    form.widget(
        certificate_explanatory_sentence="plone.app.z3cform.wysiwyg.WysiwygFieldWidget"
    )

    @invariant
    def threshold_invariant(data):
        if data.certificate_initial_threshold >= data.certificate_completion_threshold:
            raise Invalid(
                _(u"Completion threshold has to be greater than the initial threshold")
            )


alsoProvides(IOSHACountry, IFormFieldProvider)
