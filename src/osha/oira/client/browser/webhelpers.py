# coding=utf-8
from euphorie.client.browser.webhelpers import Appendix
from euphorie.client.browser.webhelpers import WebHelpers
from euphorie.content.utils import StripMarkup
from osha.oira.client.client import cached_tools_json
from plone.memoize.instance import memoize
from zope.component import getMultiAdapter


class OSHAWebHelpers(WebHelpers):
    """
    Override the original WebHelpers so that we can provide our own template
    """

    def __init__(self, context, request):
        super(OSHAWebHelpers, self).__init__(context, request)
        survey = self._survey
        if not survey:
            return
        data = cached_tools_json(self.request.client, self.request)
        own_path = "/".join(self._survey.getPhysicalPath()[-3:])
        entries = [
            entry for entry in data
            if entry.get('tool_link', '').endswith(own_path)]
        self.tool_entry = None
        if len(entries):
            self.tool_entry = entries[0]

    @property
    @memoize
    def tool_description(self):
        ploneview = getMultiAdapter(
            (self.context, self.request), name="plone")

        if getattr(self, "tool_entry", None):
            description = (
                self.tool_entry.get('body_alt', None) or
                self.tool_entry.get('body'))
            return ploneview.cropText(StripMarkup(description), 800)
        elif self._tool:
            return ploneview.cropText(StripMarkup(
                self._tool.introduction), 800)
        return ""


class OSHAAppendix(Appendix):
    """ OSHA custom appendix
    """
