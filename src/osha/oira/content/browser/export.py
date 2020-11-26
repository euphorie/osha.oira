# coding=utf-8
from euphorie.content.browser import export
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
