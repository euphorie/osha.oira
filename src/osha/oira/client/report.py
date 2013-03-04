from five import grok
from euphorie.ghost import PathGhost
from euphorie.client import report
from euphorie.client.session import SessionManager
from .interfaces import IOSHAReportPhaseSkinLayer
from .. import _

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
                if getattr(self.session.company, 'country') is not None:
                    url = "%s/report/view" % self.request.survey.absolute_url()

            self.request.response.redirect(url)
            return


COLUMN_ORDER = ['title', 'priority', 'action_plan', 'prevention_plan',
                'requirements', 'planning_end',
                'responsible', 'budget', 'number', 'comment']


class ReportLanding(grok.View):
    """Custom report landing page.

    This replaces the standard online view of the report with a page
    offering the RTF and XLSX download options.
    """
    grok.context(PathGhost)
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(IOSHAReportPhaseSkinLayer)
    grok.template("report_landing")
    grok.name("view")


class ActionPlanTimeline(report.ActionPlanTimeline):
    grok.layer(IOSHAReportPhaseSkinLayer)

    columns = sorted(
            (col for col in report.ActionPlanTimeline.columns
                if col[1] in COLUMN_ORDER),
            key=lambda d, co=COLUMN_ORDER: co.index(d[1]))
    columns.insert(-1, (None, None, _('report_timeline_progress',
        default=u'Status (planned, in process, implemented)')))
