from io import StringIO
from plone import api
from Products.Five import BrowserView

import csv


class SurveyPublicationCount(BrowserView):
    """Report the number of times each Survey has been published"""

    fieldnames = ["country", "path", "count"]

    @property
    def survey_details(self):
        details = []
        pc = api.portal.get_tool("portal_catalog")
        wft = api.portal.get_tool("portal_workflow")
        surveys = pc.searchResults(portal_type="euphorie.survey")
        for brain in surveys:
            survey = brain.getObject()
            review_history = wft.getInfoFor(survey, "review_history")
            count = 0
            for entry in review_history:
                if entry["action"] in ["publish", "update"]:
                    count += 1
            if count:
                split_path = brain.getPath().split("/")
                country = split_path[3]
                details.append(
                    {
                        "country": country,
                        "path": "/".join(split_path[2:]),
                        "count": count,
                    }
                )
        sorted_details = sorted(details, key=lambda r: r["country"])
        return sorted_details


class SurveyPublicationCountCSV(SurveyPublicationCount):
    """CSV download version of SurveyPublicationCount"""

    def __call__(self):
        csvfile = StringIO()
        writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
        writer.writeheader()
        for row in self.survey_details:
            writer.writerow(row)
        csvfile.seek(0)
        self.request.response.setHeader("Content-type", "text/csv")
        self.request.response.setHeader(
            "Content-disposition", 'attachment;filename="survey-publication-count.csv"'
        )
        return csvfile.read()
