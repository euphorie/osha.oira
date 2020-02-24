# coding=utf-8
from euphorie.client.browser.webhelpers import Appendix
from euphorie.client.browser.webhelpers import WebHelpers
from logging import getLogger
from plone.namedfile.interfaces import INamedBlobImage
from plone.memoize.instance import memoize

log = getLogger(__name__)


class OSHAWebHelpers(WebHelpers):

    @memoize
    def styles_override(self):

        css = super(OSHAWebHelpers, self).styles_override
        css += """
#osc .miller-columns .browser .item .object-name {
    color: inherit;
}
"""
        return css

    def is_image_small(self, context, fname="image", usecase="module"):
        # import pdb; pdb.set_trace()
        image = getattr(context, fname, None)
        if image and INamedBlobImage.providedBy(image):
            x, y = image.getImageSize()
            if x < 1000 or y < 430:
                return True

    @property
    @memoize
    def show_completion_percentage(self):
        return True


class OSHAAppendix(Appendix):
    """ OSHA custom appendix
    """
