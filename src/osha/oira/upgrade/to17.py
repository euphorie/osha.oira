from euphorie.client.sector import IClientSector
from euphorie.content.survey import ISurvey
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from transaction import commit

import logging


log = logging.getLogger(__name__)

countries_with_simple_measures = ["it", "lt", "lv", "mt", "fr"]


def walk(node):
    for idx, sub_node in node.ZopeFind(node, search_sub=0):
        if ISurvey.providedBy(sub_node):
            yield sub_node
        if IDexterityContainer.providedBy(sub_node):
            yield from walk(sub_node)


def _set_skip_evaluation(walker):
    count = 0
    for survey in walker:
        parent = survey.aq_parent
        if IClientSector.providedBy(parent):
            # client
            country = parent.aq_parent
        else:
            # CMS
            country = parent.aq_parent.aq_parent
        count += 1
        if country.getId() in countries_with_simple_measures:
            survey.measures_text_handling = "simple"
        else:
            survey.measures_text_handling = "full"
        if count % 10 == 0:
            log.info("Handled %d items" % count)
        if count % 1000 == 0:
            log.info("Intermediate commit")
            commit()
    log.info("Finished. Updated %d OiRA tools" % count)


def set_handle_measures_text_in_cms(context):
    site = api.portal.get()
    section = "sectors"
    walker = walk(getattr(site, section))
    log.info(f'Iterating over section "{section}"')
    _set_skip_evaluation(walker)


def set_handle_measures_text_in_client(context):
    site = api.portal.get()
    section = "client"
    walker = walk(getattr(site, section))
    log.info(f'Iterating over section "{section}"')
    _set_skip_evaluation(walker)
