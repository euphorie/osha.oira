from Acquisition import aq_base
from Products.Five import BrowserView

import json
import re


class SurveyLinks(BrowserView):
    attributes_checked = [
        "description",
        "introduction",
        "solution_direction",
        "legal_reference",
        "action",
        "action_plan",
        "prevention_plan",
        "requirements",
    ]
    url_regex = re.compile(
        r"https?://[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b"
        r"(?:[-a-zA-Z0-9()@:%_+.~#?&/=]*)"
    )

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
                links.update(self.url_regex.findall(value))
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
