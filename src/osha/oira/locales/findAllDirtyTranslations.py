#!/usr/bin/env python

import sys
import os
import time
from subprocess import *


langs = ['en', 'bg', 'cs', 'da', 'de', 'el', 'es', 'et', 'fi', 'fr', 'hu',
    'is', 'it', 'lt', 'lv', 'mt', 'nl', 'nl_BE', 'no', 'pl', 'pt', 'ro', 'sk', 'sl',
    'sv', 'ca']

for lang in langs:
    if os.path.exists(lang):
        cmdline="./findDirtyTranslations.py %(lang)s/LC_MESSAGES/euphorie.po " \
        "euphorie.pot --fuzzy --untranslated --output=dirty/osha.oira_%(lang)s.po" % dict(lang=lang)
        print "executing for language ", lang
        p = Popen(cmdline, shell=True)
        sts = os.waitpid(p.pid, 0)[1]
        time.sleep(0.5)
sys.exit('ok')

