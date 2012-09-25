from five import grok
from euphorie.content.country import View as ContentView
from euphorie.client.country import View as EuphorieView
from euphorie.content.sector import ISector
from osha.oira.interfaces import IOSHAClientSkinLayer
from osha.oira.interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")

class View(EuphorieView):
    grok.layer(IOSHAClientSkinLayer)
    grok.template("sessions")

class View(ContentView):
    grok.layer(IOSHAContentSkinLayer)

    def update(self):
        super(View, self).update()
        names=self.request.locale.displayNames.territories
        self.title=names.get(self.context.id.upper(), self.context.title)
        self.sectors=[dict(id=sector.id,
                           title=sector.title,
                           url=sector.absolute_url())
                      for sector in self.context.values()
                      if ISector.providedBy(sector)]
        try:
            self.sectors.sort(key=lambda s: s["title"].lower())
        except UnicodeDecodeError:
            self.sectors.sort(key=lambda s: s["title"].lower().decode('utf-8'))
