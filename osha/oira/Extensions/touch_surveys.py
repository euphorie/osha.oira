import datetime

def run(self):
    """ """
    ls = []
    # We don't use the catalog here, because it seems some surveys are not
    # catalogged.
    for country in self.client.objectValues():
        for sector in country.objectValues():
            for survey in sector.objectValues():
                published=getattr(survey, "published", None)

                if published is not None:
                    survey.published=datetime.datetime.now()
                    ls.append('/'.join(survey.getPhysicalPath()))
            
    return ls

