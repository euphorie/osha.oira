# coding=utf-8
from euphorie.client.browser.webhelpers import WebHelpers
from euphorie.content.utils import StripMarkup
from osha.oira.client.client import cached_tools_json
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
        if len(entries):
            entry = entries[0]
            description = (
                entry.get('body_alt', None) or entry.get('body') or
                self.tool_description)
            ploneview = getMultiAdapter(
                (self.context, self.request), name="plone")
            self.tool_description = ploneview.cropText(
                StripMarkup(description), 800)
