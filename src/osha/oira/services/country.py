from plone import api
from plone.restapi.services import Service


class Tools(Service):
    """A JSON service version of @@country-tools"""

    def reply(self):
        tree = []
        ctv = api.content.get_view("country-tools", self.context, self.request)
        country = self.context.getId()
        for sector in ctv.sectors:
            groups = []
            sector_path = f"{country}/{sector['id']}"
            for group in ctv.get_tools(sector["id"]):
                group_path = "/".join([sector_path, group["id"]])
                surveys = []
                for survey in group["surveys"]:
                    survey_path = "/".join([group_path, survey["id"]])
                    surveys.append(
                        {
                            "id": survey["id"],
                            "path": survey_path,
                            "title": survey["title"],
                            "url": survey["url"],
                            "is_published": True if survey["published"] else False,
                        }
                    )
                groups.append(
                    {
                        "id": group["id"],
                        "path": group_path,
                        "title": group["title"],
                        "is_obsolete": True if group["obsolete"] else False,
                        "surveys": surveys,
                    }
                )
            tree.append(
                {
                    "id": sector["id"],
                    "path": sector_path,
                    "title": sector["title"],
                    "groups": groups,
                }
            )
        return {
            "@id": self.request.getURL(),
            "items": tree,
        }
