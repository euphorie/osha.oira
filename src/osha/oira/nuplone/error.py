from five import grok
from plonetheme.nuplone.skin import error
from ..interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class Unauthorized(error.Unauthorized):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("error_unauthorized")
