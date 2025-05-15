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
        links = []
        for attrib in self.attributes_checked:
            value = getattr(aq_base(obj), attrib, "")
            if value:
                links.extend(self.url_regex.findall(value))
        # enforce deterministic sort order of links
        links.sort()
        if links:
            yield {
                "title": obj.Title(),
                "url": obj.absolute_url(),
                "path": "/".join(
                    obj.getPhysicalPath()[len(self.context.getPhysicalPath()) :]
                ),
                # store the url in a nested dicationary, because we will later
                # want to augment that dictionary with status information
                "links": [{"url": url} for url in links],
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
        return json.dumps(self.sections)
