import datetime
import logging
from zope.component import getUtility
from z3c.appconfig.interfaces import IAppConfig
from euphorie.client import utils

log = logging.getLogger(__name__)

def touch_surveys(self):
    """ Update the client survey's timestamps. This will force every user's
        session to be updated automatically, as soon as it is loaded.
    """
    ls = []
    # We don't use the catalog here, because it seems some surveys are not
    # catalogged.
    for country in self.client.objectValues():
        for sector in country.objectValues():
            for survey in sector.objectValues():
                published=getattr(survey, "published", None)

                if published is not None:
                    survey.published=(survey.id, survey.title, datetime.datetime.now())
                    ls.append('/'.join(survey.getPhysicalPath()))
            
    return ls


def set_sector_colour_values(self):
    """ """
    appconfig = getUtility(IAppConfig)
    settings = appconfig.get('euphorie')
    main_colour  = settings.get('main_colour', "#003399")
    support_colour  = settings.get('support_colour', "#996699")

    brains = self.portal_catalog(portal_type='euphorie.sector')
    ls = []
    for brain in brains:
        sector = brain.getObject()
        if not sector.main_colour or not sector.support_colour:
            ls.append(brain.getPath())

        if not sector.main_colour:
            sector.main_colour =  main_colour
            sector.main_background_colour = main_colour 
            sector.main_foreground_colour = utils.MatchColour(sector.main_background_colour, 0.0, 0.6, 0.3)
            sector.main_background_bright = utils.IsBright(sector.main_background_colour)

        if sector.support_colour is None:
            sector.support_colour =  support_colour
            sector.support_background_colour = support_colour
            sector.support_foreground_colour = utils.MatchColour(sector.support_background_colour)
            sector.support_background_bright = utils.IsBright(sector.support_background_colour)

    return ls



def fix_non_catalogged_solutions(self):
    """ Set the description for solutions that are not in the catalog.
    """
    from htmllaundry import StripMarkup
    def update_risks(obj):
        for o in obj.objectValues():
            if o.objectValues():
                update_risks(o)
            if o.portal_type == "euphorie.solution":
                description = StripMarkup(o.description)
                if description != o.description:
                    log.info("Setting description: %s" % o.absolute_url())
                    o.description = description
            
    for obj in self.client.objectValues():
	update_risks(obj)

    return "Successfully updated the solutions."



