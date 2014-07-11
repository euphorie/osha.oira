# -*- coding: UTF-8 -*-
from plone.i18n.locales import languages

# See: https://projects.syslab.com/issues/5978
_combinedlanguagelist = {
u'nl-be' : {u'name' : 'Dutch (Belgium)', u'native': 'Nederlands (BE)', u'flag' : u'/++resource++country-flags/be.gif'},
}
# convert the utf-8 encoded values to unicode
for code in _combinedlanguagelist:
    value = _combinedlanguagelist[code]
    if u'name' in value:
        value[u'name'] = unicode(value[u'name'], 'utf-8')
    if u'native' in value:
        value[u'native'] = unicode(value[u'native'], 'utf-8')

languages._combinedlanguagelist.update(_combinedlanguagelist)
