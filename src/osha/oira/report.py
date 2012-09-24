from five import grok
from euphorie.client import report
from euphorie.client.session import SessionManager
from osha.oira.interfaces import IOSHAReportPhaseSkinLayer

grok.templatedir("templates")

class ReportView(report.ReportView):
    """ Override so that skipped or filled in company forms are not shown
    again. For #4436.
    """
    grok.layer(IOSHAReportPhaseSkinLayer)
    grok.template("report")

    def update(self):
        self.session = SessionManager.session

        if self.request.environ["REQUEST_METHOD"] == "POST":
            reply = self.request.form
            self.session.report_comment = reply.get("comment")

            url = "%s/report/company" % self.request.survey.absolute_url()
            if getattr(self.session, 'company', None) is not None:
                if getattr(self.session.company, 'country') != None:
                    url = "%s/report/view" % self.request.survey.absolute_url()

            self.request.response.redirect(url)
            return
