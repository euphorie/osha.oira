import datetime

def run(self):
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

