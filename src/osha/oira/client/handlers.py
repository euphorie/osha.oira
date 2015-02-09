from Products.statusmessages.interfaces import IStatusMessage
from ZPublisher.pubevents import IPubAfterTraversal
from euphorie.client import MessageFactory as _
from euphorie.client import config
from euphorie.client.interfaces import IClientSkinLayer
from five import grok
from plone import api
from z3c.appconfig.interfaces import IAppConfig
from zope import component


@grok.subscribe(IPubAfterTraversal)
def showGuestUserWarning(event):
    """ Show a warning to inform guest users that they need to register or log
        in.
    """
    if not IClientSkinLayer.providedBy(event.request):
        return
    appconfig = component.getUtility(IAppConfig)
    if not appconfig.get('euphorie').get('allow_guest_accounts', False):
        return
    user = api.user.get_current()
    if (getattr(user, 'account_type', None) == config.GUEST_ACCOUNT):
        IStatusMessage(event.request).add(
            _(u"You are currently evaluating OiRA as a guest user."
              u"You will not be able to save your progress or download any "
              u"reports. To save your work, please sign in or register by "
              u"clicking the \"sign in\" link at the top right of the page."
            ), type=u"warn")

