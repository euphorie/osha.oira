from five import grok
from euphorie.content import upload
from euphorie.content.profilequestion import IProfileQuestion
from ..interfaces import IOSHAContentSkinLayer


PQ_FIELDS = ['label_multiple_present',
             'label_single_occurance',
             'label_multiple_occurances']


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
