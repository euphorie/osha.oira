from plone import api
from plone.restapi.services import Service


class CountryToolsService(Service):
    """A JSON service version of @@country-tools"""

    def reply(self):
        tree = []
        ctv = api.content.get_view("country-tools", self.context, self.request)
        country = self.context.getId()
        for sector in ctv.sectors:
            surveygroups = []
            sector_path = f"{country}/{sector['id']}"
            for surveygroup in ctv.get_tools(sector["id"]):
                surveygroup_path = f"{sector_path}/{surveygroup['id']}"
                surveys = []
                for survey in surveygroup["surveys"]:
                    survey_path = f"{surveygroup_path}/{survey['id']}"
                    surveys.append(
                        {
                            "id": survey["id"],
                            "path": survey_path,
                            "title": survey["title"],
                            "url": survey["url"],
                            "is_published": survey["published"],
                        }
                    )
                surveygroups.append(
                    {
                        "id": surveygroup["id"],
                        "path": surveygroup_path,
                        "title": surveygroup["title"],
                        "is_obsolete": surveygroup["obsolete"],
                        "surveys": surveys,
                    }
                )
            tree.append(
                {
                    "id": sector["id"],
                    "path": sector_path,
                    "title": sector["title"],
                    "surveygroups": surveygroups,
                }
            )
        return {
            "@id": self.request.getURL(),
            "items": tree,
        }
