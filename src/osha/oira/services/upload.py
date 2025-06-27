from lxml.etree import XMLSyntaxError
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest

import base64


class Upload(Service):
    """A JSON service version of @upload"""

    def reply(self):
        data = json_body(self.request)
        upload = data.get("upload", None)
        if upload is None:
            raise BadRequest("Missing XML file")
        surveygroup_title = data.get("surveygroup_title", "")
        survey_title = data.get("survey_title", "OiRA Tool import")
        is_etranslate_compatible = data.get("is_etranslate_compatible", False)
        upload_view = api.content.get_view("upload", self.context, self.request)
        importer = upload_view.importer_factory(self.context)
        try:
            importer(
                base64.b64decode(upload),
                surveygroup_title,
                survey_title,
                is_etranslate_compatible,
            )
        except XMLSyntaxError:
            self.request.response.setStatus(400)
            return {"error": {"type": "Invalid XML"}}
