# -*- coding: <utf-8> -*-
import datetime
import logging
from zope.app.component.hooks import getSite
from plone.dexterity import utils
from euphorie.client.sector import IClientSector
from euphorie.content.survey import ISurvey

log = logging.getLogger(__name__)

def renew_survey_published_date(context):
    """ Update the published attr of surveys to set the date to now.
        This will force all surveys to redirect to the @@update page from where
        users' session trees can be updated.
    """
    site = getSite()
    client = getattr(site, 'client')
    # Loop through all client surveys
    for country in client.objectValues():
        for sector in country.objectValues():
            if not IClientSector.providedBy(sector):
                continue

            for survey in sector.objectValues():
                if not ISurvey.providedBy(survey):
                    continue

                published = getattr(survey, "published", None)
                if isinstance(published, tuple):
                    survey.published = (
                        published[0], published[1], datetime.datetime.now())
                else:
                    # BBB: Euphorie 1.x did not use a tuple to store extra 
                    # information.
                    published = datetime.datetime.now()


def add_custom_homepage(context):
    """ """
    site = getSite()
    try:
        container = site.unrestrictedTraverse('documents/en') 
    except [AttributeError, KeyError]:
        log.error('Could not navigate to documents/en folder. '
                   'Abort creation of custom homepage.')

    content = utils.createContentInContainer(
                                container, 'oira.homepage', 
                                checkConstraints=False, 
                                id="homepage",
                                title='OiRA Homepage')
    content.description = """\
<!-- The header and footer of the homepage is fixed and cannot be changed.
     Add here any HTML code that you'd like to be rendered in the body of the homepage.-->"""

