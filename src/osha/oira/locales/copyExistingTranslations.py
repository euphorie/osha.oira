#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: We have a po file LOCAL, based on the pot file REFERENCE. It
might be that new entries have been added to REFERENCE which need to be
propagated to LOCAL and translated. Some of the new msgids might already be
translated in po file EXISTING.
All new msgids which also exist in EXISTING and have the same default
translation will be copied to LOCAL.

usage:    %(program)s orig.po update.po
local.po      A po file that contains some translations and needs to be updated
reference.po  A pot file that is the basis for the update to local.po
existing.po   A po file that contains already existing translations
"""

import sys
import os
import re
import polib

patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)

if len(sys.argv) < 4:
    usage(sys.stderr, "\nERROR: Not enough arguments")
localfile = sys.argv[1]
referencefile = sys.argv[2]
existingfile = sys.argv[3]

if not os.path.isfile(localfile):
    usage(sys.stderr, "\nERROR: path to LOCAL file is not valid")

if not os.path.isfile(referencefile):
    usage(sys.stderr, "\nERROR: path to REFERENCE file is not valid")

if not os.path.isfile(existingfile):
    usage(sys.stderr, "\nERROR: path to EXISTING file is not valid")

local = polib.pofile(localfile)
reference = polib.pofile(referencefile)
existing = polib.pofile(existingfile)

cnt = 0
for entry in reference:
    default_reference = default_existing = u''
    # fist, extract the default translation of the reference (POT) file
    match_reference = patt.match(entry.comment)
    if match_reference:
        default_reference = match_reference.group(1).replace('\n', ' ')
    else:
        # print "WARNING! msgid '%s' in REFERENCE file does not have a " \
        #     "default translation." % entry.msgid
        default_reference = entry.msgid
    # is this msgid present in LOCAL?
    target_local = local.find(entry.msgid)
    if target_local:
        target_existing = existing.find(entry.msgid)
        if target_existing:
            match_existing = patt.match(target_existing.comment)
            if match_existing:
                default_existing = match_existing.group(1).replace('\n', ' ')
            else:
                print "WARNING! msgid '%s' in EXISTING file does not have a " \
                     "default translation." % entry.msgid
                default_existing = target_existing.msgid
            if (default_existing == default_reference and
                    target_existing.msgstr != '' and target_local.msgstr == ''):
                target_local.msgstr = target_existing.msgstr
                print u"UPDATED '%s' with translation '%s'" % (
                    entry.msgid, target_existing.msgstr)
                cnt += 1

print "Found and updated %d matching translations" % cnt

local.save()
sys.exit('Ok')
