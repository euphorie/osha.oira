from five import grok
from lxml import etree
from euphorie.content.export import ExportSurvey as BaseExportSurvey
from euphorie.content.upload import ImportSector as BaseImportSector
from euphorie.content.upload import SectorImporter as BaseSectorImporter
from euphorie.content.upload import el_unicode
from euphorie.content.profilequestion import IProfileQuestion
from .interfaces import IOSHAContentSkinLayer


PQ_FIELDS = ['label_multiple_present',
             'label_single_occurance',
             'label_multiple_occurances']


class ExportSurvey(BaseExportSurvey):
    grok.layer(IOSHAContentSkinLayer)

    def exportProfileQuestion(self, parent, profile):
        node = super(ExportSurvey, self).exportProfileQuestion(parent, profile)
        for field in PQ_FIELDS:
            value = getattr(profile, field, None)
            if value:
                etree.SubElement(node, field.replace('_', '-'), value)
        return node


class SectorImporter(BaseSectorImporter):
    def ImportProfileQuestion(self, node, survey):
        profile = super(SectorImporter)
        if IProfileQuestion.providedBy(profile):
            for field in PQ_FIELDS:
                setattr(profile, field,
                        el_unicode(node, field.replace('_', '-')))
        return profile


class ImportSector(BaseImportSector):
    importer_factory = None
