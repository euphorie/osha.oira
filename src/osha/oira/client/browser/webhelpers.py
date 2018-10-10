# coding=utf-8
from euphorie.client.browser.webhelpers import Appendix
from euphorie.client.browser.webhelpers import WebHelpers
from logging import getLogger
from euphorie.decorators import reify

log = getLogger(__name__)


class OSHAWebHelpers(WebHelpers):

    @reify
    def styles_override(self):

        css = super(OSHAWebHelpers, self).styles_override
        css += """
#osc .miller-columns .browser .item .object-name {
    color: inherit;
}
"""
        return css


class OSHAAppendix(Appendix):
    """ OSHA custom appendix
    """
