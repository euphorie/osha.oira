import htmllaundry
from datetime import datetime
from cStringIO import StringIO
from Acquisition import aq_inner

from five import grok
from sqlalchemy import sql
from z3c.saconfig import Session
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.i18n import translate
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from plonetheme.nuplone.utils import formatDate

from rtfng.Elements import PAGE_NUMBER
from rtfng.PropertySets import BorderPropertySet
from rtfng.PropertySets import FramePropertySet
from rtfng.PropertySets import ParagraphPropertySet
from rtfng.PropertySets import TabPropertySet
from rtfng.PropertySets import TextPropertySet 
from rtfng.Renderer import Renderer
from rtfng.Styles import ParagraphStyle
from rtfng.Styles import TextStyle
from rtfng.document import character
from rtfng.document.base import TAB, LINE
from rtfng.document.paragraph import Paragraph, Table, Cell
from rtfng.document.section import Section

from euphorie.client import survey, report
from euphorie.client.session import SessionManager
from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content.survey import View as SurveyView

from osha.oira import utils
from osha.oira import model
from osha.oira import _
from osha.oira import interfaces

grok.templatedir("templates")

class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    phases = {
            "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
            "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
            "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
            "report": interfaces.IOSHAReportPhaseSkinLayer, }


class OSHAStart(survey.Start):
    """ Override the 'start' page to provide our own template.
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("start")
    grok.name("start")


class OSHAIdentification(survey.Identification):
    """ Override the 'identification' page to provide our own template.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("identification")
    grok.name("index_html")


class OSHASurveyView(SurveyView):
    grok.layer(NuPloneSkin)
    grok.template("survey_view")

    def modules_and_profile_questions(self):
        return [self._morph(child) for child in self.context.values()] 

    def _morph(self, child):
        state=getMultiAdapter(
                    (child, self.request), 
                    name="plone_context_state")

        return dict(id=child.id,
                    title=child.title,
                    url=state.view_url(),
                    is_profile_question=IProfileQuestion.providedBy(child))



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
            - unactioned_nodes
            - actioned_nodes

            Place in a separate method so that OSHAActionPlanReportDownload can call it.
        """
        if survey.redirectOnSurveyUpdate(self.request):
            return

        self.actioned_nodes = utils.get_actioned_nodes(self.nodes) 
        self.unactioned_nodes = utils.get_unactioned_nodes(self.nodes) 
        
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


def node_title(node, zodbnode):
    # 2885: Non-present risks and unanswered risks are shown affirmatively,
    # i.e 'title'
    if node.type!="risk" or node.identification in [u"n/a", u"yes", None]:
        return node.title
    # The other two groups of risks are shown negatively, i.e
    # 'problem_description'
    if zodbnode.problem_description and zodbnode.problem_description.strip():
        return zodbnode.problem_description
    return node.title


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

    def title(self, node, zodbnode):
        return node_title(node, zodbnode)

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

    def update(self):
        if survey.redirectOnSurveyUpdate(self.request):
            return

        # 3813: Include children from optional modules.
        # Removed this: .filter(sql.not_(model.SKIPPED_PARENTS))\
        session = Session()
        dbsession = SessionManager.session
        query = session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session == dbsession)\
                .order_by(model.SurveyTreeItem.path)
        self.nodes = query.all()


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


    def addReportNodes(self, document, nodes, heading, toc, body):
        """ """
        t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=self.request)])
        ss = document.StyleSheet
        toc_props = ParagraphPropertySet()
        toc_props.SetLeftIndent(TabPropertySet.DEFAULT_WIDTH*1)
        toc_props.SetRightIndent(TabPropertySet.DEFAULT_WIDTH*1)
        p = Paragraph(ss.ParagraphStyles.Heading6, toc_props)
        p.append(character.Text(heading, TextPropertySet(italic=True)))
        toc.append(p)
        
        body.append(Paragraph(ss.ParagraphStyles.Heading1, heading))

        survey=self.request.survey
        styles = ss.ParagraphStyles
        header_styles = {
                0: styles.Heading2,
                1: styles.Heading3,
                2: styles.Heading4,
                3: styles.Heading5,
                4: styles.Heading6,
                }
        for node in nodes:
            zodb_node = survey.restrictedTraverse(node.zodb_path.split("/"))
            title = node_title(node, zodb_node)
            thin_edge  = BorderPropertySet(width=20, style=BorderPropertySet.SINGLE)
            if node.depth == 1:
                p = Paragraph(
                        header_styles.get(node.depth, styles.Heading6),
                        FramePropertySet(thin_edge, thin_edge, thin_edge, thin_edge),
                        u"%s %s" % (node.number, title))
            else:
                p = Paragraph(
                        header_styles.get(node.depth, styles.Heading6),
                        u"%s %s" % (node.number, title))
            body.append(p)

            if node.type!="risk":
                continue

            if node.priority:
                if node.priority=="low":
                    level=_("risk_priority_low", default=u"low")
                elif node.priority=="medium":
                    level=_("risk_priority_medium", default=u"medium")
                elif node.priority=="high":
                    level=_("risk_priority_high", default=u"high")

                msg = _("risk_priority", 
                    default="This is a ${priority_value} priority risk.",
                    mapping={'priority_value': level})

                body.append(Paragraph(
                                styles.RiskPriority, 
                                t(msg)
                            ))
                body.append(
                        Paragraph(
                                styles.Normal, 
                                ParagraphPropertySet(left_indent=300, right_indent=300),
                                t(_(htmllaundry.StripMarkup(zodb_node.description)))
                                )
                            )
                body.append(Paragraph(""))

            if node.comment and node.comment.strip():
                body.append(Paragraph(styles.Comment, node.comment))

            for (idx, measure) in enumerate(node.action_plans):
                if not measure.action_plan:
                    continue
                    
                if len(node.action_plans)==1:
                    heading = t(_("header_measure_single", default=u"Measure"))
                else:
                    heading = t(_("header_measure", 
                                    default=u"Measure ${index}", 
                                    mapping={"index": idx+1}))

                self.addMeasure(document, heading, body, measure)


    def addMeasure(self, document, heading, section, measure):
        """ Requirements for how the measure section should be displayed are 
            in #2611 
        """
        t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=self.request)])
        ss = document.StyleSheet
        styles = ss.ParagraphStyles

        table = Table(9500)
        thin_edge  = BorderPropertySet(width=20, style=BorderPropertySet.SINGLE)
        no_edge = BorderPropertySet(width=0, colour=ss.Colours.White)
        p = Paragraph(
                styles.MeasureHeading,
                ParagraphPropertySet(left_indent=300, right_indent=300),
                t(_("header_measure_single", default=u"Measure")))
        c = Cell(p, FramePropertySet(thin_edge, thin_edge, no_edge, thin_edge))
        table.AddRow(c)


        ss = document.StyleSheet
        styles = document.StyleSheet.ParagraphStyles
        headings = [
            t(_("label_measure_action_plan", default=u"General approach (to "
                u"eliminate or reduce the risk)")),
            t(_("label_measure_prevention_plan", default=u"Specific action(s) "
                u"required to implement this approach")),
            t(_("label_measure_requirements", default=u"Level of expertise "
                u"and/or requirements needed")),
            t(_("label_action_plan_responsible", default=u"Who is "
                u"responsible?")),
            t(_("label_action_plan_budget", default=u"Budget (in Euro)")),
            t(_("label_action_plan_start", default=u"Planning start")),
            t(_("label_action_plan_end", default=u"Planning end")),
            ]
        m = measure
        values = [
            m.action_plan,
            m.prevention_plan,
            m.requirements,
            m.responsible,
            m.budget and str(m.budget) or '',
            m.planning_start and formatDate(self.request, m.planning_start) or '',
            m.planning_end and formatDate(self.request, m.planning_end) or '',
            ]
        for heading, value in zip(headings, values):
            p = Paragraph(
                        styles.MeasureField,
                        heading
                        )
            c = Cell(p, FramePropertySet(no_edge, thin_edge, no_edge, thin_edge))
            table.AddRow(c)

            if headings.index(heading) == len(headings)-1:
                frame = FramePropertySet(no_edge, thin_edge, thin_edge, thin_edge)
            else:
                frame = FramePropertySet(no_edge, thin_edge, no_edge, thin_edge)

            p = Paragraph(styles.Normal, 
                    ParagraphPropertySet(left_indent=600, right_indent=600),
                    value)
            c = Cell(p, frame)
            table.AddRow(c)

        section.append(table)


    def addConsultationBox(self, section, document):
        """ Add the consultation box that needs to be signed by the employer
            and workers.
        """
        ss = document.StyleSheet
        styles = document.StyleSheet.ParagraphStyles
        thin_edge  = BorderPropertySet(width=20, style=BorderPropertySet.SINGLE)
        t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=self.request)])

        table = Table(9500)
        thin_edge  = BorderPropertySet(width=20, style=BorderPropertySet.SINGLE)
        no_edge = BorderPropertySet(width=0, colour=ss.Colours.White)
        p = Paragraph(
                styles.Heading3,
                ParagraphPropertySet(alignment=ParagraphPropertySet.CENTER),
                t(_("header_oira_report_consultation", 
                    default="Consultation of workers"))
                )
        c = Cell(p, FramePropertySet(thin_edge, thin_edge, no_edge, thin_edge))
        table.AddRow(c)

        p = Paragraph(
                styles.Normal,
                ParagraphPropertySet(alignment=ParagraphPropertySet.LEFT),
                t(_("paragraph_oira_consultation_of_workers", 
                    default="The undersigned hereby declare that the workers " 
                            "have been consulted on the content of this "
                            "document.")),
                LINE
                )
        c = Cell(p, FramePropertySet(no_edge, thin_edge, no_edge, thin_edge))
        table.AddRow(c)

        p = Paragraph(
                styles.Normal,
                ParagraphPropertySet(alignment=ParagraphPropertySet.LEFT),
                )
        employer = t(_("oira_consultation_employer", 
                    default="On the behalf of the employer:"))
        workers = t(_("oira_consultation_workers", 
                    default="On the behalf of the workers:"))

        p.append(employer, TAB, TAB, TAB, TAB, workers, LINE, LINE)
        c = Cell(p, FramePropertySet(no_edge, thin_edge, no_edge, thin_edge))
        table.AddRow(c)

        p = Paragraph(
                ParagraphPropertySet(alignment=ParagraphPropertySet.LEFT),
                t(_("oira_survey_date", default="Date:")),
                LINE, LINE
                )
        c = Cell(p, FramePropertySet(no_edge, thin_edge, thin_edge, thin_edge))
        table.AddRow(c)
        section.append(table)


    def render(self):
        """ Mostly a copy of the render method in euphorie.client, but with
            some changes to also show unanswered risks and non-present risks.
            #1517 and #1518
        """
        document=report.createDocument()
        ss = document.StyleSheet

        # Define some more custom styles
        ss.ParagraphStyles.append(
            ParagraphStyle("RiskPriority",
                    TextStyle(TextPropertySet(
                                    font=ss.Fonts.Arial, 
                                    size=22, 
                                    italic=True,
                                    colour=ss.Colours.Blue)),
                    ParagraphPropertySet(left_indent=300, right_indent=300))
                    )
        ss.ParagraphStyles.append(
            ParagraphStyle("MeasureField",
                    TextStyle(TextPropertySet(
                                    font=ss.Fonts.Arial, 
                                    size=18, 
                                    underline=True)),
                    ParagraphPropertySet(left_indent=300, right_indent=300))
                    )

        # XXX: This part is removed
        # self.addActionPlan(document)

        # XXX: and replaced with this part:
        t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=self.request)])
        toc = createSection(document, self.context, self.request)
        body = Section()
        heading = t(_("header_oira_report_download", 
                    default=u"OiRA Report: \"${title}\"",
                    mapping=dict(title=self.session.title)))
        toc.append(
                    Paragraph(
                        ss.ParagraphStyles.Heading1, 
                        ParagraphPropertySet(alignment=ParagraphPropertySet.CENTER),
                        heading,
                        )
                    )
        toc_props = ParagraphPropertySet()
        toc_props.SetLeftIndent(TabPropertySet.DEFAULT_WIDTH*1)
        toc_props.SetRightIndent(TabPropertySet.DEFAULT_WIDTH*1)
        p = Paragraph(ss.ParagraphStyles.Heading6, toc_props)
        txt = t(_("toc_header", default=u"Contents"))
        p.append(character.Text(txt))
        toc.append(p)

        headings = [
            t(_("header_present_risks", 
                default=u"Risks that have been identified, evaluated and have an Action Plan")),
            t(_("header_unevaluated_risks", 
                default=u"Risks that have been identified but do NOT have an Action Plan")),
            t(_("header_unanswered_risks",
                default=u'Hazards/problems that have been "parked" and are still to be dealt with')),
            t(_("header_risks_not_present",
                default=u"Hazards/problems that are not present in your organisation"))
            ]
        nodes = [
            self.actioned_nodes,
            self.unactioned_nodes,
            self.unanswered_nodes,
            self.risk_not_present_nodes,
            ]

        for nodes, heading in zip(nodes, headings):
            if not nodes:
                continue
            self.addReportNodes(document, nodes, heading, toc, body)

        toc.append(Paragraph(LINE))
        body.append(Paragraph(LINE))
        self.addConsultationBox(body, document)
        document.Sections.append(body)
        # Until here...

        renderer=Renderer()
        output=StringIO()
        renderer.Write(document, output)

        filename = translate(_("filename_report_actionplan",
                        default=u"Action plan ${title}",
                        mapping=dict(title=self.session.title)),
                        context=self.request,)
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
        header_styles = {
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
            section.append(Paragraph(styles.Normal, htmllaundry.StripMarkup(zodb_node.description)))

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
                section.append(Paragraph(styles.Comment, node.comment))


def createIdentificationReportSection(document, survey, request):
    t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=request)])
    section = Section()

    footer_txt = t(_("report_identification_revision",
            default=u"This document was based on the OiRA Tool '${title}' of "
                    u"revision date ${date}.",
            mapping={"title": survey.published[1],
                    "date": formatDate(request, survey.published[2])}))
    header = Table(4750, 4750)
    c1 = Cell(Paragraph(
                document.StyleSheet.ParagraphStyles.Footer, 
                SessionManager.session.title))

    pp = ParagraphPropertySet
    header_props = pp(alignment=pp.RIGHT)
    c2 = Cell(Paragraph(
                document.StyleSheet.ParagraphStyles.Footer, 
                header_props,
                formatDate(request, datetime.today())))
    header.AddRow(c1, c2)
    section.Header.append(header)

    footer = Table(9000, 500)
    c1 = Cell(Paragraph(document.StyleSheet.ParagraphStyles.Footer,
                pp(alignment=pp.LEFT),
                footer_txt))
    c2 = Cell(Paragraph(pp(alignment=pp.RIGHT), PAGE_NUMBER))
    footer.AddRow(c1, c2)
    section.Footer.append(footer)
    section.SetBreakType(section.PAGE)
    document.Sections.append(section)
    return section


def createSection(document, survey, request):
    t = lambda txt: "".join(["\u%s?" % str(ord(e)) for e in translate(txt, context=request)])
    section = Section(break_type=Section.PAGE, first_page_number=1)
    footer_txt = t(_("report_survey_revision",
        default=u"This report was based on the OiRA Tool '${title}' of revision date ${date}.",
        mapping={"title": survey.published[1],
                 "date": formatDate(request, survey.published[2])}))

    header = Table(4750, 4750)
    c1 = Cell(Paragraph(
                document.StyleSheet.ParagraphStyles.Footer, 
                survey.published[1]))

    pp = ParagraphPropertySet
    header_props = pp(alignment=pp.RIGHT)
    c2 = Cell(Paragraph(
                document.StyleSheet.ParagraphStyles.Footer, 
                header_props,
                formatDate(request, datetime.today())))
    header.AddRow(c1, c2)
    section.Header.append(header)

    footer = Table(9000, 500)
    # rtfng does not like unicode footers
    c1 = Cell(Paragraph(document.StyleSheet.ParagraphStyles.Footer,
                pp(alignment=pp.LEFT),
                footer_txt))

    c2 = Cell(Paragraph(pp(alignment=pp.RIGHT), PAGE_NUMBER))
    footer.AddRow(c1, c2)
    section.Footer.append(footer)
    document.Sections.append(section)
    return section

