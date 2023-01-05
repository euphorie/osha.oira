from datetime import datetime
from DateTime import DateTime
from plone.app.dexterity.behaviors.metadata import DCFieldProperty
from plone.app.upgrade.v43 import alphas
from plone.i18n.locales import languages
from Products.CMFPlone.utils import safe_unicode
from zope.schema.interfaces import ISequence
from zope.schema.interfaces import IText

import sys


if sys.version_info[0] >= 3:
    unicode = str


# See: https://projects.syslab.com/issues/5978
_combinedlanguagelist = {
    "nl-be": {
        "name": "Dutch (Belgium)",
        "native": "Nederlands (BE)",
        "flag": "/++resource++country-flags/be.gif",
    },
}
# convert the utf-8 encoded values to unicode
for code in _combinedlanguagelist:
    value = _combinedlanguagelist[code]
    if "name" in value:
        value["name"] = unicode(value["name"], "utf-8")
    if "native" in value:
        value["native"] = unicode(value["native"], "utf-8")

languages._combinedlanguagelist.update(_combinedlanguagelist)


def reindex_sortable_title(context):
    pass


def upgradeToI18NCaseNormalizer(context):
    pass


def upgradeSyndication(context):
    pass


alphas.reindex_sortable_title = reindex_sortable_title
alphas.upgradeToI18NCaseNormalizer = upgradeToI18NCaseNormalizer
alphas.upgradeSyndication = upgradeSyndication

_marker = object()


# See https://projects.syslab.com/issues/11361
def __get__(self, inst, klass):
    if inst is None:
        return self

    attribute = getattr(inst.context, self._get_name, _marker)
    if attribute is _marker:
        field = self._field.bind(inst)
        attribute = getattr(field, "default", _marker)
        if attribute is _marker:
            raise AttributeError(self._field.__name__)
    elif callable(attribute):
        attribute = attribute()

    if isinstance(attribute, DateTime):
        # Ensure datetime value is stripped of any timezone and seconds
        # so that it can be compared with the value returned by the widget
        return datetime(*map(int, attribute.parts()[:6]))

    if attribute is None:
        return

    if IText.providedBy(self._field):
        return safe_unicode(attribute)

    if ISequence.providedBy(self._field):
        if IText.providedBy(self._field.value_type):
            return type(attribute)(safe_unicode(item) for item in attribute)

    return attribute


DCFieldProperty.__get__ = __get__
