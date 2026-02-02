from Acquisition import aq_base
from html import unescape
from Products.Five import BrowserView

import json
import re


class SurveyLinks(BrowserView):
    attributes_checked = [
        "action",
        "action_plan",
        "description",
        "introduction",
        "legal_reference",
        "prevention_plan",
        "recommendation",
        "requirements",
        "solution_direction",
        "text",
    ]
    url_regex = re.compile(r"https?://[^\s<>\"'\[\](){}]+", re.UNICODE)

    def clean_url(self, url):
        """Clean the URL."""
        # HTML entity encoded to unescaped, e.g. `&amp;` to `&`
        url = unescape(url)
        # Strip trailing punctuation that's likely not part of the URL.
        url = url.rstrip(".,;:!?")
        return url

    def extract_links(self, obj):
        """For the survey and each subobject in its content tree, list external
        hyperlinks if it has them. Take care to return a datastructure with a
        deterministic sort order.
        """
        _obj = aq_base(obj)
        links = set()
        for attrib in self.attributes_checked:
            value = getattr(_obj, attrib, "")
            if value:
                urls = [self.clean_url(url) for url in self.url_regex.findall(value)]
                links.update(urls)
        if links:
            yield {
                "title": obj.Title(),
                "url": obj.absolute_url(),
                "path": "/".join(
                    obj.getPhysicalPath()[len(self.context.getPhysicalPath()) :]
                ),
                # Store the url in a nested dictionary, because we will later
                # want to augment that dictionary with status information.
                # Enforce deterministic sort order of links to make that access
                # stable.
                "links": [{"url": url} for url in sorted(links)],
            }
        if hasattr(obj, "objectIds"):
            # reimplement objectValues() with deterministic sort order of sections
            for child_id in sorted(obj.objectIds()):
                yield from self.extract_links(obj[child_id])

    # Explicitly not cached. Let the consumer take care of that.
    # Return always the current up-to-date contents.
    @property
    def sections(self):
        return {"sections": list(self.extract_links(self.context))}

    def __call__(self):
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(self.sections)
