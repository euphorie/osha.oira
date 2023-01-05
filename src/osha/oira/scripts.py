from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from euphorie.client.utils import CreateEmailTo
from plone import api
from plone.dexterity.utils import safe_unicode
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from slc.zopescript.script import ConsoleScript
from zope.component import getMultiAdapter

import logging


log = logging.getLogger(__name__)


class OutdatedTools(ConsoleScript):
    def run(self):
        self.portal = self.app.Plone2
        outdated_tools_view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="outdated-tools-view"
        )
        outdated_tools_view()


outdated_tools = OutdatedTools()


class WriteStatistics(ConsoleScript):
    def run(self):
        self.portal = self.app.Plone2
        write_statistics_view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="write-statistics"
        )
        write_statistics_view()


write_statistics = WriteStatistics()


class OutdatedToolsView(BrowserView):
    def __init__(self, context=None, request=None):
        sprops = context.portal_properties.site_properties
        self.interval = sprops.getProperty("outdated_notications_interval_days", 365)
        super().__init__(context, request)

    def __call__(self):
        self.render(self.context)

    @property
    def email_from_name(self):
        return api.portal.get_registry_record("plone.email_from_name")

    @property
    def email_from_address(self):
        return api.portal.get_registry_record("plone.email_from_address")

    def render(self, portal):
        log.info("Called outdated-tools-view")
        self.portal = portal
        outdated_tool_paths = self.get_outdated_tool_paths()
        years = self.interval / 365
        if years:
            months = int((self.interval % 365) / 30.4)
            period = f"over {years} year(s) and {months} month(s)"
        else:
            period = f"over {int(self.interval / 30.4)} month(s)"
        log.info(
            "{} outdated tools have not been updated {}.".format(
                len(outdated_tool_paths), period
            )
        )
        # As requested by EU-OSHA, sector managers do not get emails, only
        # country managers.
        # self.send_sector_manager_notifications(outdated_tool_paths)
        self.send_country_manager_notifications(outdated_tool_paths)
        self.send_oira_team_notifications(outdated_tool_paths)

    def get_outdated_tool_paths(self):
        pc = self.context.portal_catalog
        client_path = "/".join(self.context.getPhysicalPath() + ("client",))
        now = datetime.now()
        one_year_ago = now - timedelta(days=self.interval)
        outdated_tools = pc.searchResults(
            portal_type="euphorie.survey",
            modified={"query": one_year_ago, "range": "max"},
            path={"query": client_path},
            sort_on="path",
        )

        sector_tool_paths = []
        for tool in outdated_tools:
            sector_tool_path = tool.getPath().replace("/client/", "/sectors/")
            if sector_tool_path.split("/")[-1] == "preview":
                continue
            sector_tool_paths.append(sector_tool_path)
        return sector_tool_paths

    def send_sector_manager_notifications(self, outdated_tool_paths):
        sector_paths = set()
        for path in outdated_tool_paths:
            sector_path = "/".join(path.split("/")[:5])
            sector_paths.add(sector_path)
        for sector_path in sector_paths:
            sector = self.context.unrestrictedTraverse(sector_path, False)
            if not sector or sector.portal_type != "euphorie.sector":
                log.error(f"Missing sector: {sector_path}")
                continue
            contact_name = sector.contact_name or ""
            contact_email = sector.contact_email
            if not contact_email:
                log.error(f"No contact email address: {sector_path}")
                continue
            sector_tools = filter(
                lambda x: x.startswith(sector_path), outdated_tool_paths
            )
            intro = """
You are receiving this notification since you are the sector manager for
"{}". """.format(
                safe_unicode(sector.Title())
            )
            self.send_notification(
                to_name=contact_name,
                to_address=contact_email,
                tool_paths=sector_tools,
                intro=intro,
            )

    def send_country_manager_notifications(self, outdated_tool_paths):
        country_paths = set()
        for path in outdated_tool_paths:
            country_path = "/".join(path.split("/")[:4])
            country_paths.add(country_path)
        for country_path in country_paths:
            country_tools = filter(
                lambda x: x.startswith(country_path), outdated_tool_paths
            )
            country = self.context.unrestrictedTraverse(country_path)
            view = country.restrictedTraverse("manage-ldap-users", None)
            managers = (
                [
                    userid
                    for userid in view.local_roles_userids()
                    if view.get_user(userid)
                ]
                if view
                else []
            )
            for manager in managers:
                intro = """
You are receiving this notification since you are the country manager for
"{}". """.format(
                    safe_unicode(country.Title())
                )

                self.send_notification(
                    to_name="",
                    to_address=manager,
                    tool_paths=country_tools,
                    intro=intro,
                )

    def send_oira_team_notifications(self, outdated_tool_paths):
        sprops = self.context.portal_properties.site_properties
        to_name = sprops.getProperty("outdated_notications_oira_team_name", "OiRA Team")
        to_email = sprops.getProperty(
            "outdated_notications_oira_team_email", "test@example.com"
        )
        intro = "This is the summary email of all outdated tools."
        empty_message = "No outdated tools were found for the requested period."
        self.send_notification(
            to_name=to_name,
            to_address=to_email,
            tool_paths=outdated_tool_paths,
            intro=intro,
            empty_message=empty_message,
        )

    def send_notification(
        self,
        to_name=None,
        to_address=None,
        tool_paths=None,
        intro="",
        empty_message=None,
    ):
        if not tool_paths and not empty_message:
            return
        to_name = safe_unicode(to_name)
        mailhost = getToolByName(self.context, "MailHost")
        if to_name:
            recipient = f"{to_name} <{to_address}>"
        else:
            recipient = to_address
        subject = "OiRA: Notification on outdated tools"
        portal_id = self.context.getId()
        portal_url = self.context.absolute_url()
        if tool_paths:
            paths_by_country = OrderedDict()
            for path in tool_paths:
                country = path.split("/")[3]
                if country in paths_by_country:
                    paths_by_country[country].append(path)
                else:
                    paths_by_country[country] = [path]
            tool_details = ""
            for country in paths_by_country.keys():
                if len(paths_by_country.keys()) > 1:
                    tool_details += "\n" + country + ":\n"
                else:
                    tool_details += "\n"
                tool_urls = [
                    i.replace("/" + portal_id, portal_url)
                    for i in paths_by_country[country]
                ]
                tool_details += "\n".join(tool_urls)
                tool_details += "\n"
        else:
            tool_details = empty_message
        years = self.interval / 365
        if years:
            months = int((self.interval % 365) / 30.4)
            period = f"over {years} year(s) and {months} month(s)"
        else:
            period = f"over {int(self.interval / 30.4)} month(s)"

        body = """
Dear {name},

{intro}

The following tool(s) have not been updated in {period}:
{tools}

Please check if they are still up to date and republish them.

Best regards,
OiRA
""".format(
            name=to_name or to_address, tools=tool_details, period=period, intro=intro
        )
        mail = CreateEmailTo(
            self.email_from_name, self.email_from_address, recipient, subject, body
        )
        try:
            mailhost.send(mail)
        except Exception as err:
            log.error(f"Failed to send notification {err}")
