from ftw.upgrade import UpgradeStep
from plone import api


body_french = (
    "<p>Tous les entreprises doivent être affiliées à un service externe pour la "
    "prévention et la protection au travail (SEPPT). Ce service est composé de deux "
    "départements: le département de surveillance de santé des travailleurs et le "
    "département de gestion des risques. Il a donc pour mission d’assister "
    "l’entreprise dans le développement et la mise en œuvre d’un système de gestion "
    "dynamique des risques. Le tout, en collaboration avec le conseiller en prévention "
    "interne de l’entreprise.</p>"
    "<p>Vous trouverez ici la liste des services externes pour la prévention et la "
    "protection au travail agréés:<br />"
    '<a href="https://emploi.belgique.be/fr/agrements/agrement-services-externes-pour-'
    'la-prevention-et-la-protection-au-travail-seppt">Agrément : Services Externes '
    "pour la Prévention et la Protection au travail (SEPPT) | Service public fédéral "
    "Emploi, Travail et Concertation sociale (belgique.be)</a></p>"
)
body_dutch = (
    "<p>Alle ondernemingen moeten bij een Externe Dienst voor Preventie en Bescherming "
    "op het Werk (EDPBW) aangesloten zijn. Deze dienst bestaat uit twee afdelingen: de "
    "afdeling belast met het medisch toezicht en de afdeling belast met risicobeheer. "
    "Ze hebben dus als doel het bijstaan van de onderneming in de ontwikkeling en de "
    "uitvoering van een dynamisch risicobeheersingssysteem. Dit alles gebeurt in "
    "samenwerking met de interne preventieadviseur van de onderneming.</p>"
    "<p>Hier vindt u de lijst met erkende Externe Diensten voor Preventie en "
    "Bescherming op het Werk:<br />"
    '<a href="https://werk.belgie.be/nl/erkenningen/erkenning-externe-diensten-voor-'
    'preventie-en-bescherming-op-het-werk-edpbw">Erkenning: Externe Diensten voor '
    "Preventie en Bescherming op het werk (EDPBW) | Federale Overheidsdienst "
    "Werkgelegenheid, Arbeid en Sociaal Overleg (belgie.be)</a></p>"
)


class AddBelgianConsultantsInformation(UpgradeStep):
    """Add Belgian consultants information."""

    def __call__(self):
        be = api.portal.get().sectors.be
        help_folder = be.help

        if "fr" not in help_folder:
            api.content.create(
                container=help_folder, type="euphorie.page", id="fr", title="French"
            )
        fr = help_folder["fr"]
        if "consultants" not in fr:
            api.content.create(
                container=fr,
                type="euphorie.page",
                id="consultants",
                title="Consultants",
                body=body_french,
            )

        if "nl" not in help_folder:
            api.content.create(
                container=help_folder, type="euphorie.page", id="nl", title="Dutch"
            )
        nl = help_folder["nl"]
        if "consultants" not in nl:
            api.content.create(
                container=nl,
                type="euphorie.page",
                id="consultants",
                title="Consultants",
                body=body_dutch,
            )
