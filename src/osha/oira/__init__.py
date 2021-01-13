from logging import getLogger
from zope.i18nmessageid import MessageFactory

import patch_passwordreset  # noqa: F401


_ = MessageFactory("euphorie")
log = getLogger(__name__)
