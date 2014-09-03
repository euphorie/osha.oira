# -*- coding: UTF-8 -*-
from plone.i18n.locales import languages
from plone.app.upgrade.v43 import alphas

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


def reindex_sortable_title(context):
    pass


def upgradeToI18NCaseNormalizer(context):
    pass


def upgradeSyndication(context):
    pass


alphas.reindex_sortable_title = reindex_sortable_title
alphas.upgradeToI18NCaseNormalizer = upgradeToI18NCaseNormalizer
alphas.upgradeSyndication = upgradeSyndication
