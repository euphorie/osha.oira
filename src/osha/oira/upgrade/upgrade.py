#  -* coding: utf8 *-
from euphorie.client import model
from euphorie.client.country import IClientCountry
from euphorie.client.publish import EnableCustomRisks
from euphorie.client.sector import IClientSector
from euphorie.content.survey import ISurvey
from euphorie.deployment.upgrade.utils import TableExists
from osha.oira import _
from plone import api
from plone.dexterity import utils
from z3c.appconfig.interfaces import IAppConfig
from z3c.appconfig.utils import asBool
from z3c.saconfig import Session
from zope.component.hooks import getSite
from zope.sqlalchemy import datamanager
import datetime
import logging
import transaction
import zope.component

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
        container,
        'oira.homepage',
        checkConstraints=False,
        id="homepage",
        title='OiRA Homepage'
    )
    content.description = """\
<!-- The header and footer of the homepage is fixed and cannot be changed.
Add here any HTML code that you'd like to be rendered in the body of
 the homepage.-->"""


def reset_evaluation_flag(context):
    """ """
    site = getSite()
    ps = site.portal_catalog(portal_type='euphorie.survey')
    for p in ps:
        try:
            survey = p.getObject()
        except:
            continue
        else:
            if survey.evaluation_optional:
                survey.evaluation_optional = False
                survey.reindexObject()


def sql_create_all(context):
    """Add all missing SQL tables and indices.
    """
    session = Session()
    transaction.get().commit()
    model.metadata.create_all(session.bind, checkfirst=True)
    datamanager.mark_changed(session)


def alter_time_column(context):
    session = Session()
    if TableExists(session, "statistics_login"):
        session.execute(
            "ALTER TABLE statistics_login ALTER COLUMN time SET DEFAULT CURRENT_TIMESTAMP")
        model.metadata.create_all(session.bind, checkfirst=True)
        datamanager.mark_changed(session)
        transaction.get().commit()
    log.info("Changed default for column 'time' to current timestamp")


def remove_birt_file_format(context):
    site = getSite()
    sprops = site.portal_properties.site_properties
    url = sprops.getProperty('birt_report_url')
    base, query = url.split('?')
    if not query:
        return
    params = query.split('&')
    if '__format=pdf' in params:
        params.remove('__format=pdf')
        newurl = '?'.join([base, '&'.join(params)])
        sprops.manage_changeProperties({'birt_report_url': newurl})


def update_types_information(context):
    """ Reimport types to activate new behavior """
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile('profile-osha.oira:default', 'typeinfo')


def increase_statistics_surveys_path_column(context):
    session = Session()
    if TableExists(session, "statistics_surveys"):
        session.execute(
            "ALTER TABLE statistics_surveys ALTER COLUMN zodb_path TYPE varchar(512)")
        model.metadata.create_all(session.bind, checkfirst=True)
        datamanager.mark_changed(session)
        transaction.get().commit()
    log.info("Increased the size of column zodb_path in table statistics_surveys.")


def increase_sessions_path_column(context):
    session = Session()
    if TableExists(session, "session"):
        session.execute(
            "ALTER TABLE session ALTER COLUMN zodb_path TYPE varchar(512)")
        model.metadata.create_all(session.bind, checkfirst=True)
        datamanager.mark_changed(session)
        transaction.get().commit()
    log.info("Increased the size of column zodb_path in table session.")


def reset_surveygroup_obsolete(context):
    """ """
    log.info('Reset "obsolete" flag from surveygroups.')
    site = getSite()
    brains = site.portal_catalog(portal_type='euphorie.surveygroup')
    for brain in brains:
        try:
            surveygroup = brain.getObject()
        except:
            log.warning("Stale catalog entry for brain {0}".format(
                brain.getPath()))
            continue
        else:
            if getattr(surveygroup, 'obsolete', False):
                log.info("Survey {0} was obsolete".format(
                    surveygroup.absolute_url()))
                surveygroup.obsolete = False
                surveygroup.reindexObject()


def enable_custom_risks_on_all_modules(context):
    """ """
    appconfig = zope.component.getUtility(IAppConfig)
    if not asBool(appconfig["euphorie"].get("allow_user_defined_risks")):
        log.warning(
            "Custom risks are not enabled. Set 'allow_user_defined_risks' to "
            "true in euphorie.ini for enabling them.")
        return
    portal = api.portal.get()
    client = portal.client
    count = 0
    for country in client.objectValues():
        if IClientCountry.providedBy(country):
            for sector in country.objectValues():
                if IClientSector.providedBy(sector):
                    for survey in sector.objectValues():
                        try:
                            is_new = EnableCustomRisks(survey)
                            count += 1
                            custom = getattr(survey, 'custom-risks', None)
                            if custom:
                                custom.title = _(u'title_other_risks', default=u"Added risks (by you)")
                                custom.description = _(
                                    u"description_other_risks",
                                    default=u"In case you have identified risks not included in "
                                    u"the tool, you are able to add them now:")
                                custom.question = _(
                                    u"question_other_risks",
                                    default=u"<p>Would you now like to add your own defined risks "
                                    u"to this tool?</p><p><strong>Important:</strong> In "
                                    u"order to avoid duplicating risks, we strongly recommend you "
                                    u"to go first through all the previous modules, if you have not "
                                    u"done it yet.</p><p>If you don't need to add risks, please select 'No.'</p>")
                            if is_new:
                                survey.published = (
                                    survey.id, survey.title, datetime.datetime.now())
                        except Exception, e:
                            log.error("Could not enable custom risks for module. %s" % e)
    log.info('All %d published surveys can now have custom risks.' % count)
    session = Session()
    if TableExists(session, "tree"):
        session.execute(
            "UPDATE tree SET title = 'title_other_risks' WHERE zodb_path ='custom-risks'")
        model.metadata.create_all(session.bind, checkfirst=True)
        datamanager.mark_changed(session)
        transaction.get().commit()
        log.info('Set correct title on all exisiting sessions for custom risks module.')


def install_private_resources(context):
    """ Install the oira.private egg, which contains non-free JS and CSS
        resources.
    """
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile('profile-oira.private:default')


def drop_constraint_no_duplicates_in_tree(context):
    session = Session()
    if TableExists(session, "tree"):
        session.execute(
            "ALTER TABLE tree DROP CONSTRAINT no_duplicates")
        model.metadata.create_all(session.bind, checkfirst=True)
        datamanager.mark_changed(session)
        transaction.get().commit()
    log.info("Removed the constraint `no_duplicates` from table tree.")


def configure_outdated_tool_notification(context):
    setup = api.portal.get_tool('portal_setup')
    setup.runImportStepFromProfile(
        'profile-osha.oira:default', 'propertiestool')
