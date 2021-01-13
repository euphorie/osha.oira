from ..interfaces import IOSHAContentSkinLayer
from five import grok
from plonetheme.nuplone.skin import error


grok.templatedir("templates")


class Unauthorized(error.Unauthorized):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("error_unauthorized")
