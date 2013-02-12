from five import grok
from lxml import etree
from euphorie.content import export
from euphorie.content import upload
from euphorie.content.profilequestion import IProfileQuestion
from ..interfaces import IOSHAContentSkinLayer


PQ_FIELDS = ['label_multiple_present',
             'label_single_occurance',
             'label_multiple_occurances']


class ExportSurvey(export.ExportSurvey):
    grok.layer(IOSHAContentSkinLayer)

    def exportProfileQuestion(self, parent, profile):
        node = super(ExportSurvey, self).exportProfileQuestion(parent, profile)
        for field in PQ_FIELDS:
            value = getattr(profile, field, None)
            if value:
                etree.SubElement(node, field.replace('_', '-')).text = value
        return node


class ImporterMixin(object):
    def ImportProfileQuestion(self, node, survey):
        profile = upload.SurveyImporter.ImportProfileQuestion(self, node, survey)
        if IProfileQuestion.providedBy(profile):
            for field in PQ_FIELDS:
                setattr(profile, field,
                        upload.el_unicode(node, field.replace('_', '-')))
        return profile


class SurveyImporter(ImporterMixin, upload.SurveyImporter):
    pass


class SectorImporter(ImporterMixin, upload.SectorImporter):
    pass


class ImportSurvey(upload.ImportSurvey):
    grok.layer(IOSHAContentSkinLayer)
    importer_factory = SurveyImporter


class ImportSector(upload.ImportSector):
    grok.layer(IOSHAContentSkinLayer)
    importer_factory = SectorImporter
