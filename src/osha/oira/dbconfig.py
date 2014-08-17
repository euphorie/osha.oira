import Zope2
import logging
import transaction
from App.config import getConfiguration
from zope.app.publication.zopepublication import ZopePublication

configuration = getConfiguration()
if not hasattr(configuration, 'product_config'):
    conf = None
else:
    conf = configuration.product_config.get('osha.oira')
log = logging.getLogger('osha.oira')


def get_plone(instancename):
    db = Zope2.DB
    connection = db.open()
    root_folder = connection.root().get(ZopePublication.root_name, None)
    plone = root_folder.get(instancename, None)
    return plone


def dbconfig(event):
    if conf is None:
        log.error('No product config found! Configuration will not be set')
        return

    instancename = conf.get('ploneinstance_name', 'Plone2')
    plone = get_plone(instancename)
    if plone is None:
        log.error('No Plone instance found! Create it manually '
                  'with id %s and profile osha.policy' % instancename)
        # adding a Plone site without proper REQUEST is not supported
        return

    props = plone.portal_properties.site_properties

    birt_url = conf.get('birt.report_url', None)
    if (birt_url is not None and
            props.getProperty('birt_report_url') != birt_url):
        if not props.hasProperty('birt_report_url'):
            props.manage_addProperty('birt_report_url', birt_url, 'string')
        else:
            props.manage_changeProperties(birt_report_url=birt_url)
        log.info('birt_report_url set')

    transaction.commit()
