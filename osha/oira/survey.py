import htmllaundry
from cStringIO import StringIO
from Acquisition import aq_inner

from five import grok
from sqlalchemy import sql
from z3c.saconfig import Session
from zope.i18n import translate
from zope.component import getMultiAdapter
from zExceptions import NotFound
from plonetheme.nuplone.utils import formatDate

from rtfng.PropertySets import ParagraphPropertySet, TabPropertySet
from rtfng.document.section import Section
from rtfng.document.paragraph import Paragraph
from rtfng.document.base import TAB
from rtfng.Renderer import Renderer

from euphorie.client import survey, report
from euphorie.client.session import SessionManager

from osha.oira import utils
from osha.oira import model
from osha.oira import _
import interfaces

grok.templatedir("templates")

class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    phases = {
            "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
            "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
            "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
            "report": interfaces.IOSHAReportPhaseSkinLayer, }


class OSHAReportView(report.ReportView):
    """ Override the default view, to add a popup overlay
        asking the user if they want to participate in a survey. #2558

        See euphorie/client/survey.py for more info
    """
    grok.template("report")
    
    def get_language(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
                                (context, self.request), 
                                name=u'plone_portal_state'
                                )
        return portal_state.language()

    def get_survey_url(self):
        context = aq_inner(self.context)
        site_properties = context.portal_properties.site_properties
        sdict = {}
        if hasattr(site_properties, 'survey_urls'):
            survey_urls = site_properties.survey_urls
            for l in survey_urls:
                t = l.split(" ")
                if len(t) != 2:
                    continue
                lang, url = t
                sdict[lang] = url

        lang = self.get_language()
        if sdict.has_key(lang):
            return sdict[lang]
        elif sdict.has_key('en'):
            return sdict['en']
        else:
            return 'http://www.surveymonkey.com/s/OiRATool'


class OSHAActionPlan(survey.ActionPlan):
    """
    Overrides the original ActionPlanReport in euphorie.client.survey.py
    to provide our own template.

    Please refer to original for more details.
    """
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("actionplan")


class OSHAActionPlanMixin():

    def _extra_updates(self):
        """ Provides the following extra attributes (as per #1517, #1518):
            - unanswered_risk_nodes
            - not_present_risk_nodes
            - unevaluated_nodes
            - evaluated_nodes

            Place in a separate method so that OSHAActionPlanReportDownload can call it.
        """
        if survey.redirectOnSurveyUpdate(self.request):
            return

        # I would have prefered to get the evaluated and unevaluated nodes via 
        # SQLAlchemy, but querying for action_plans (via any()) didn't seem 
        # to work, and in any case, a node might have an action plan that 
        # isn't fully populated yet!
        self.evaluated_nodes = utils.get_evaluated_nodes(self.nodes) 
        self.unevaluated_nodes = utils.get_unevaluated_nodes(self.nodes) 
        
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


class OSHAActionPlanReportView(report.ActionPlanReportView, OSHAActionPlanMixin):
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

    def risk_status(self, node, zodbnode):
        """ """
        if node.postponed or not node.identification:
            return "unanswered"
        elif node.identification in [u"n/a", u"yes"]:
            return "not-present"
        elif node.identification == "no":
            if node.probability == 0:
                return "no-actionplans"
            elif node.action_plans == []:
                return "unevaluated"
            return "present"


class OSHAIdentificationReport(report.IdentificationReport):
    """
    Overrides the original IdentificationReport in euphorie.client.survey.py
    in order to provide a new template.

    Please refer to original for more details.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("report_identification")
    download = False

    def title(self, node, zodbnode):
        return node.title

    def publishTraverse(self, request, name):
        """Check if the user wants to download this report by checking for a
        ``download`` URL entry. This uses a little trick: browser views
        implement `IPublishTraverse`, which allows us to catch traversal steps.
        """
        if name=="download":
            return OSHAIdentificationReportDownload(aq_inner(self.context), request)
        else:
            raise NotFound(self, name, request)


class OSHAActionPlanReportDownload(report.ActionPlanReportDownload, OSHAActionPlanMixin):
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
        if self.session.company is None:
            self.session.company=model.Company()
        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.not_(model.SKIPPED_PARENTS))\
                .filter(sql.or_(model.MODULE_WITH_RISK_OR_TOP5_FILTER,
                                model.RISK_PRESENT_OR_TOP5_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.nodes=query.all()

        self._extra_updates()


    def addReportNodes(self, document, nodes, section):
        """ """
        survey=self.request.survey
        t=lambda txt: translate(txt, context=self.request)
        styles = document.StyleSheet.ParagraphStyles
        normal_style = styles.Normal
        comment_style = styles.Comment
        warning_style = styles.Warning
        measure_heading_style = styles.MeasureHeading
        header_styles={
                0: styles.Heading2,
                1: styles.Heading3,
                2: styles.Heading4,
                3: styles.Heading5,
                4: styles.Heading6,
                }

        for node in nodes:
            zodb_node = survey.restrictedTraverse(node.zodb_path.split("/"))

            if node.type!="risk" or node.identification in [u"n/a", u"yes"]:
                title =  node.title
            elif zodb_node.problem_description and zodb_node.problem_description.strip():
                title =  zodb_node.problem_description
            else:
                title = node.title

            section.append(
                    Paragraph(
                        header_styles.get(node.depth, styles.Heading6),
                        u"%s %s" % (node.number, title)
                        )
                    )
            if node.type!="risk":
                continue

            if node.priority:
                if node.priority=="low":
                    level=_("report_priority_low", default=u"low priority risk")
                elif node.priority=="medium":
                    level=_("report_priority_medium", default=u"medium priority risk")
                elif node.priority=="high":
                    level=_("report_priority_high", default=u"high priority risk")
                section.append(Paragraph(normal_style, 
                    t(_("report_priority", default=u"This is a ")), t(level)))

            if node.comment and node.comment.strip():
                section.append(Paragraph(comment_style, node.comment))

            for (idx, measure) in enumerate(node.action_plans):
                if not measure.action_plan:
                    continue
                    
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
        # XXX: This part is removed
        # self.addActionPlan(document)
        # XXX: and replaced with this part:
        t = lambda txt: translate(txt, context=self.request)
        section = report.createSection(document, self.context, self.request)
        heading = t(_("header_oira_report_download", 
                    default=u"OiRA Report: \"${title}\"",
                    mapping=dict(title=self.session.title)))
        section.append(
                    Paragraph(
                        document.StyleSheet.ParagraphStyles.Heading1, 
                        ParagraphPropertySet(alignment=ParagraphPropertySet.CENTER),
                        heading 
                        )
                    )
        if len(self.evaluated_nodes):
            heading = t(_("header_present_risks", 
                        default=u"Risks that have been identified, evaluated and have an Action Plan:"))
            section.append(
                        Paragraph( document.StyleSheet.ParagraphStyles.Heading1, 
                                heading)
                        )
            self.addReportNodes(document, self.evaluated_nodes, section)

        if len(self.unevaluated_nodes):
            heading = t(_("header_unevaluated_risks", 
                        default=u"Risks that have been identified but NOT evaluated and do NOT have an Action Plan:"))
            section.append(
                        Paragraph( document.StyleSheet.ParagraphStyles.Heading1, 
                                heading)
                        )
            self.addReportNodes(document, self.unevaluated_nodes, section)

        if len(self.unanswered_nodes):
            heading = t(_("header_unanswered_risks",
                        default=u'Risks that have been "parked" and are still to be dealt with:'))
            section.append(
                        Paragraph( document.StyleSheet.ParagraphStyles.Heading1, 
                                heading)
                        )
            self.addReportNodes(document, self.unanswered_nodes, section)
        
        if len(self.risk_not_present_nodes):
            heading = t(_("header_risks_not_present",
                        default=u"Risks that are not present in your organisation:"))
            section.append(
                        Paragraph( document.StyleSheet.ParagraphStyles.Heading1, 
                                heading)
                        )
            self.addReportNodes(document, self.risk_not_present_nodes, section)
        # Until here...

        renderer=Renderer()
        output=StringIO()
        renderer.Write(document, output)

        filename = t(_("filename_report_actionplan",
                   default=u"Action plan ${title}",
                   mapping=dict(title=self.session.title)))
        self.request.response.setHeader("Content-Disposition",
                            "attachment; filename=\"%s.rtf\"" % filename.encode("utf-8"))
        self.request.response.setHeader("Content-Type", "application/rtf")
        return output.getvalue()


class OSHAIdentificationReportDownload(report.IdentificationReportDownload):
    """Generate identification report in RTF form.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)

    def addIdentificationResults(self, document):
        survey=self.request.survey
        section = createIdentificationReportSection(document, self.context, self.request)

        styles = document.StyleSheet.ParagraphStyles

        normal_style=document.StyleSheet.ParagraphStyles.Normal
        warning_style=document.StyleSheet.ParagraphStyles.Warning
        comment_style=document.StyleSheet.ParagraphStyles.Comment
        header_styles={
                0: styles.Heading2,
                1: styles.Heading3,
                2: styles.Heading4,
                3: styles.Heading5,
                4: styles.Heading6,
                }

        for node in self.getNodes():
            section.append(
                    Paragraph(
                        header_styles.get(node.depth, styles.Heading6), 
                        u"%s %s" % (node.number, node.title))
                        )

            if node.type!="risk":
                continue

            zodb_node=survey.restrictedTraverse(node.zodb_path.split("/"))
            section.append(Paragraph(normal_style, htmllaundry.StripMarkup(zodb_node.description)))

            for i in range(0,8):
                p =  Paragraph(styles.Normal, " ")
                section.append(p)

            tabs = TabPropertySet(
                section.TwipsToRightMargin(),
                alignment=TabPropertySet.RIGHT,
                leader=getattr(TabPropertySet, 'UNDERLINE')
                )
            p = Paragraph(styles.Normal, ParagraphPropertySet(tabs=[tabs]))
            p.append(TAB)
            section.append(p)

            if node.comment and node.comment.strip():
                section.append(Paragraph(comment_style, node.comment))


def createIdentificationReportSection(document, survey, request):
    t=lambda txt: translate(txt, context=request)
    footer=t(_("report_identification_revision",
        default=u"This document was based on the OiRA Tool '${title}' of "
                u"revision date ${date}.",
        mapping={"title": survey.published[1],
                 "date": formatDate(request, survey.published[2])}))
    # rtfng does not like unicode footers
    footer=Paragraph(document.StyleSheet.ParagraphStyles.Footer,
            "".join(["\u%s?" % str(ord(e)) for e in footer]))
    section = Section()
    section.Header.append(Paragraph(
        document.StyleSheet.ParagraphStyles.Footer, SessionManager.session.title))
    section.Footer.append(footer)
    section.SetBreakType(section.PAGE)
    document.Sections.append(section)
    return section


