from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from euphorie.client.utils import CreateEmailTo
from euphorie.content.countrymanager import ICountryManager
from five import grok
from plone.dexterity.utils import safe_unicode
from slc.zopescript.script import ConsoleScript
from zope.component import getMultiAdapter

import logging

log = logging.getLogger(__name__)


class OutdatedTools(ConsoleScript):
    def run(self):
        self.portal = self.app.Plone2
        outdated_tools_view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name='outdated-tools-view')
        outdated_tools_view()

outdated_tools = OutdatedTools()


class OutdatedToolsView(grok.View):
    grok.context(ISiteRoot)
    grok.require("cmf.ManagePortal")
    grok.name("outdated-tools-view")

    def __call__(self):
        sprops = self.context.portal_properties.site_properties
        self.interval = sprops.getProperty(
            'outdated_notications_interval_days', 365)
        self.render(self.context)

    def render(self, portal):
        self.portal = portal
        outdated_tool_paths = self.get_outdated_tool_paths()
        self.send_sector_manager_notifications(outdated_tool_paths)
        self.send_country_manager_notifications(outdated_tool_paths)
        self.send_oira_team_notifications(outdated_tool_paths)

    def get_outdated_tool_paths(self):
        pc = self.context.portal_catalog
        client_path = '/'.join(self.context.getPhysicalPath() + ('client',))
        now = datetime.now()
        one_year_ago = now - timedelta(days=self.interval)
        outdated_tools = pc.searchResults(
            portal_type='euphorie.survey',
            modified={'query': one_year_ago, 'range': 'max'},
            path={'query': client_path},
            sort_on='path',
        )

        sector_tool_paths = []
        for tool in outdated_tools:
            sector_tool_path = tool.getPath().replace('/client/', '/sectors/')
            if sector_tool_path.split('/')[-1] == 'preview':
                continue
            sector_tool_paths.append(sector_tool_path)
        return sector_tool_paths

    def send_sector_manager_notifications(self, outdated_tool_paths):
        sector_paths = set()
        for path in outdated_tool_paths:
            sector_path = '/'.join(path.split('/')[:5])
            sector_paths.add(sector_path)
        for sector_path in sector_paths:
            sector = self.context.unrestrictedTraverse(sector_path, False)
            if not sector or sector.portal_type != 'euphorie.sector':
                log.error('Missing sector: {}'.format(sector_path))
                continue
            contact_name = sector.contact_name or ''
            contact_email = sector.contact_email
            if not contact_email:
                log.error('No contact email address: {}'.format(sector_path))
                continue
            sector_tools = filter(
                lambda x: x.startswith(sector_path), outdated_tool_paths)
            self.send_notification(
                to_name=contact_name,
                to_address=contact_email,
                tool_paths=sector_tools,
            )

    def send_country_manager_notifications(self, outdated_tool_paths):
        country_paths = set()
        for path in outdated_tool_paths:
            country_path = '/'.join(path.split('/')[:4])
            country_paths.add(country_path)
        for country_path in country_paths:
            country_tools = filter(
                lambda x: x.startswith(country_path), outdated_tool_paths)
            country = self.context.unrestrictedTraverse(country_path)
            managers = [
                i for i in country.values() if ICountryManager.providedBy(i)]
            for manager in managers:
                contact_name = manager.Title() or ''
                contact_email = manager.contact_email
                if not contact_email:
                    continue
                self.send_notification(
                    to_name=contact_name,
                    to_address=contact_email,
                    tool_paths=country_tools,
                )

    def send_oira_team_notifications(self, outdated_tool_paths):
        sprops = self.context.portal_properties.site_properties
        to_name = sprops.getProperty(
            'outdated_notications_oira_team_name', 'OiRA Team')
        to_email = sprops.getProperty(
            'outdated_notications_oira_team_email', 'test@example.com')
        self.send_notification(
            to_name=to_name,
            to_address=to_email,
            tool_paths=outdated_tool_paths,
        )

    def send_notification(self, to_name=None, to_address=None, tool_paths=None):
        if not tool_paths:
            return
        to_name = safe_unicode(to_name)
        mailhost = getToolByName(self.context, "MailHost")
        recipient = u'{} <{}>'.format(to_name, to_address)
        subject = u'Outdated tools'
        portal_id = self.context.getId()
        portal_url = self.context.absolute_url()
        paths_by_country = OrderedDict()
        for path in tool_paths:
            country = path.split('/')[3]
            if country in paths_by_country:
                paths_by_country[country].append(path)
            else:
                paths_by_country[country] = [path]
        tool_details = ''
        for country in paths_by_country.keys():
            if len(paths_by_country.keys()) > 1:
                tool_details += '\n' + country + ':\n'
            else:
                tool_details += '\n'
            tool_urls = [
                i.replace('/' + portal_id, portal_url)
                for i in paths_by_country[country]
            ]
            tool_details += '\n'.join(tool_urls)
            tool_details += '\n'
        years = self.interval / 365
        if years:
            period = "over {0} year(s)".format(years)
        else:
            period = "over {0} month(s)".format(self.interval / 30)

        body = u'''
Dear {name},

The following tool(s) have not been updated in {period}:
{tools}
Best regards,
OiRA
'''.format(name=to_name, tools=tool_details, period=period)
        mail = CreateEmailTo(
            self.context.email_from_name,
            self.context.email_from_address,
            recipient,
            subject,
            body,
        )
        try:
            mailhost.send(mail)
        except Exception, err:
            log.error('Failed to send notification {}'.format(err))
