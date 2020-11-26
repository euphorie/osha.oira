# coding=utf-8
from euphorie.content.browser import export
from euphorie.content.browser import upload
from euphorie.content.profilequestion import IProfileQuestion
from lxml import etree


PQ_FIELDS = [
    "label_multiple_present",
    "label_single_occurance",
    "label_multiple_occurances",
]


class OSHAExportSurvey(export.ExportSurvey):
    def exportProfileQuestion(self, parent, profile):
        node = super(OSHAExportSurvey, self).exportProfileQuestion(parent, profile)
        for field in PQ_FIELDS:
            value = getattr(profile, field, None)
            if value:
                etree.SubElement(node, field.replace("_", "-")).text = value
        return node


class ImporterMixin(object):
    def ImportProfileQuestion(self, node, survey):
        profile = upload.SurveyImporter.ImportProfileQuestion(self, node, survey)
        if IProfileQuestion.providedBy(profile):
            for field in PQ_FIELDS:
                setattr(
                    profile, field, upload.el_unicode(node, field.replace("_", "-"))
                )
        return profile


class SurveyImporter(ImporterMixin, upload.SurveyImporter):
    pass


class OSHAImportSurvey(upload.ImportSurvey):

    importer_factory = SurveyImporter
