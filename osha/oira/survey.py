from five import grok
import htmllaundry
from osha.oira import model
from sqlalchemy import sql
from z3c.saconfig import Session
from euphorie.client import survey, report
import interfaces
from zope.i18n import translate

from cStringIO import StringIO
from rtfng.document.paragraph import Paragraph
from rtfng.Renderer import Renderer
from osha.oira import _

grok.templatedir("templates")

class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    phases = {
            "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
            "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
            "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
            "report": interfaces.IOSHAReportPhaseSkinLayer, }

class OSHAActionPlanReportView(report.ActionPlanReportView):
    """
    Overrides the original ActionPlanReportView in euphorie.client.survey.py

    Provides the following extra attributes (as per #1517, #1518):
        unanswered_risk_nodes
        not_present_risk_nodes

    Please refer to original for more details.
    """
    grok.template("report_actionplan")
    grok.layer(interfaces.IOSHAReportPhaseSkinLayer)
    grok.name("view")
    download = False

    def update(self):
        """ """
        super(OSHAActionPlanReportView, self).update()
        self._extra_updates()

    def _extra_updates(self):
        """ Provides the following extra attributes (as per #1517, #1518):
            - unanswered_risk_nodes
            - not_present_risk_nodes

            Place in a separate method so that OSHAActionPlanReportDownload
            can call it.
        """
        if survey.redirectOnSurveyUpdate(self.request):
            return

        session=Session()
        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                                model.UNANSWERED_RISKS_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.unanswered_nodes=query.all()

        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                                model.RISK_NOT_PRESENT_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.risk_not_present_nodes=query.all()


class OSHAIdentificationReport(report.IdentificationReport):
    """
    Overrides the original IdentificationReport in euphorie.client.survey.py
    in order to provide a new template.

    Please refer to original for more details.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("report_identification")


class OSHAActionPlanReportDownload(report.ActionPlanReportDownload):
    """ Generate and download action report.
    """
    grok.layer(interfaces.IOSHAReportPhaseSkinLayer)
    grok.name("download")
    download =  True

    def update(self):
        """ Perform the super class' update and then get all the unanswered and
            non-present risks.
        """
        super(OSHAActionPlanReportDownload, self).update()

        session=Session()
        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                                model.UNANSWERED_RISKS_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.unanswered_nodes=query.all()

        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                                model.RISK_NOT_PRESENT_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.risk_not_present_nodes=query.all()


    def addOtherNodes(self, document, nodes, heading):
        """ """
        survey=self.request.survey
        t=lambda txt: translate(txt, context=self.request)
        section = report.createSection(document, self.context, self.request)
        section.append(
                    Paragraph( document.StyleSheet.ParagraphStyles.Heading1, 
                               heading))

        normal_style=document.StyleSheet.ParagraphStyles.Normal
        comment_style=document.StyleSheet.ParagraphStyles.Comment
        warning_style=document.StyleSheet.ParagraphStyles.Warning
        measure_heading_style=document.StyleSheet.ParagraphStyles.MeasureHeading
        header_styles={
                0: document.StyleSheet.ParagraphStyles.Heading2,
                1:  document.StyleSheet.ParagraphStyles.Heading3,
                2:  document.StyleSheet.ParagraphStyles.Heading4,
                3:  document.StyleSheet.ParagraphStyles.Heading5,
                }

        for node in nodes:
            section.append(Paragraph(
                        header_styles[node.depth], 
                        u"%s %s" % (node.number, node.title))
                        )

            if node.type!="risk":
                continue

            zodb_node=survey.restrictedTraverse(node.zodb_path.split("/"))
            if node.postponed or not node.identification:
                section.append(Paragraph(warning_style,
                    t(_("risk_unanswered", 
                        default=u"This risk still needs to be inventorised."))))
            elif node.identification in [u"n/a", u"yes"]:
                section.append(Paragraph(warning_style,
                    t(_("risk_not_present", 
                        default=u"This risk hasbeen identified as not being " \
                                u"present in your organisation"))))

            if node.priority:
                if node.priority=="low":
                    level=_("report_priority_low", default=u"low priority risk")
                elif node.priority=="medium":
                    level=_("report_priority_medium", default=u"medium priority risk")
                elif node.priority=="high":
                    level=_("report_priority_high", default=u"high priority risk")
                section.append(Paragraph(normal_style, 
                    t(_("report_priority", default=u"This is a ")), t(level)))

            section.append(Paragraph(normal_style, htmllaundry.StripMarkup(zodb_node.description)))
            if node.comment and node.comment.strip():
                section.append(Paragraph(comment_style, node.comment))

            for (idx, measure) in enumerate(node.action_plans):
                if len(node.action_plans)==1:
                    section.append(Paragraph(measure_heading_style,
                        t(_("header_measure_single", default=u"Measure"))))
                else:
                    section.append(Paragraph(measure_heading_style,
                        t(_("header_measure", default=u"Measure ${index}", mapping={"index": idx+1}))))
                self.addMeasure(document, section, measure)
 


    def render(self):
        """ Mostly a copy of the render method in euphorie.client, but with
            some changes to also show unanswered risks and non-present risks.
            #1517 and #1518
        """
        document=report.createDocument()
        self.addIntroduction(document)
        self.addCompanyInformation(document)
        self.addActionPlan(document)

        # XXX: This part is added
        heading = translate(
                _(  "plan_report_unanswered_risks", 
                    default=u"Unanswered Risks"), 
                self.request)
        self.addOtherNodes(document, self.unanswered_nodes, heading)

        heading = translate(
                _(  "plan_report_unanswered_risks",
                    default=u"Positively Answered Risks"), 
                self.request)
        self.addOtherNodes(document, self.risk_not_present_nodes, heading)
        # Until here...

        renderer=Renderer()
        output=StringIO()
        renderer.Write(document, output)

        filename=_("filename_report_actionplan",
                   default=u"Action plan ${title}",
                   mapping=dict(title=self.session.title))
        filename=translate(filename, context=self.request)
        self.request.response.setHeader("Content-Disposition",
                            "attachment; filename=\"%s.rtf\"" % filename.encode("utf-8"))
        self.request.response.setHeader("Content-Type", "application/rtf")
        return output.getvalue()

