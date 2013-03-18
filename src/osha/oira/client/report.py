from five import grok
from z3c.saconfig import Session
from sqlalchemy import sql
from euphorie.ghost import PathGhost
from euphorie.client import report
from euphorie.client.session import SessionManager
from euphorie.client import model
from .interfaces import IOSHAReportPhaseSkinLayer
from .. import _
from openpyxl.workbook import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from zope.i18n import translate


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

    combine_keys = ['prevention_plan', 'requirements']

    columns = sorted(
            (col for col in report.ActionPlanTimeline.columns
                if col[1] in COLUMN_ORDER),
            key=lambda d, co=COLUMN_ORDER: co.index(d[1]))
    extra_cols = [x for x in columns if x[1] in combine_keys]
    columns = [x for x in columns if x[1] not in combine_keys]
    columns[3] = ('measure', 'planning_end',
                    _('report_timeline_end_date', default=u'End date'))
    columns.insert(-1, (None, None, _('report_timeline_progress',
        default=u'Status (planned, in process, implemented)')))


    def create_workbook(self):
        """Create an Excel workbook containing the all risks and measures.
        """
        t = lambda txt: translate(txt, context=self.request)
        book = Workbook()
        sheet = book.worksheets[0]
        sheet.title = t(_('report_timeline_title', default=u'Timeline'))
        sheet.default_column_dimension.auto_size = True
        survey = self.request.survey


        for (column, (type, key, title)) in enumerate(self.columns):
            if key in self.combine_keys:
                continue
            sheet.cell(row=0, column=column).value = t(title)

        for (row, (risk, measure)) in enumerate(self.get_measures(), 1):
            column = 0
            zodb_node = survey.restrictedTraverse(risk.zodb_path.split('/'))
            
            for (type, key, title) in self.columns+self.extra_cols:
                value = None
                if type == 'measure':
                    value = getattr(measure, key, None)
                elif type == 'risk':
                    value = getattr(risk, key, None)
                    if key == 'priority':
                        value = self.priority_name(value)
                    elif key == 'title':
                        if zodb_node.problem_description and \
                                zodb_node.problem_description.strip():
                            value = zodb_node.problem_description
                
                # style
                sheet.cell(row=row, column=column).style.alignment.wrap_text = True
                
                if key in self.combine_keys and value is not None:
                    # osha wants to combine action_plan (col 3), prevention_plan and requirements in one cell
                    if not sheet.cell(row=row, column=2).value:
                        sheet.cell(row=row, column=2).value = u''
                    sheet.cell(row=row, column=2).value += '\r\n'+value  
                    continue
                    
                if value is not None:
                    sheet.cell(row=row, column=column).value = value
                column += 1
        

        return book

    def get_measures(self):
        """Find all data that should be included in the report.

        The data is returned as a list of tuples containing a
        :py:class:`Risk <euphorie.client.model.Risk>` and
        :py:class:`ActionPlan <euphorie.client.model.ActionPlan>`. Each
        entry in the list will correspond to a row in the generated Excel
        file.

        This implementation differs from Euphorie in its ordering:
        it sorts on risk priority instead of start date.
        """
        query = Session.query(model.SurveyTreeItem, model.ActionPlan)\
                .outerjoin(model.ActionPlan)\
                .filter(model.SurveyTreeItem.session == self.session)\
                .filter(sql.not_(model.SKIPPED_PARENTS))\
                .filter(sql.or_(model.MODULE_WITH_RISK_OR_TOP5_FILTER,
                                model.RISK_PRESENT_OR_TOP5_FILTER))\
                .join(model.Risk)\
                .order_by(
                        sql.case(
                            value=model.Risk.priority,
                            whens={'high': 0, 'medium': 1},
                            else_=2),
                        model.Risk.path)
        return query.all()
        



