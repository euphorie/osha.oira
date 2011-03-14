from five import grok
from euphorie.content import surveygroup
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from euphorie.client.sector import IClientSector
from euphorie.content.survey import ISurvey

grok.templatedir("templates")

class View(surveygroup.View):
    grok.layer(NuPloneSkin)
    grok.name("nuplone-view")
    grok.template("surveygroup_view")
    
    def surveys(self):
        templates = [ dict(title=survey.title, url=survey.absolute_url())
                      for survey in self.context.values()
                      if ISurvey.providedBy(survey)
                    ]
        return templates

View.render = None

