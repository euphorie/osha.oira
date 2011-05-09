#!/usr/bin/python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Compare two .po or .pot files to find entries that need to be
updated. This is done by comparing the "Default" translations.
All entries found in this way are written to a new po file that can be sent
to translators.

usage:    %(program)s old.po new.pot out.po
old.po   A po file that contains existing, potentially outdated translations
new.pot  A po/pot file with updated default translations (e.g. via extraction)
out.po   A name for the output po file
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
oldfile = sys.argv[1]
newfile = sys.argv[2]
outfile = sys.argv[3]

if not os.path.isfile(oldfile):
    usage(sys.stderr, "\nERROR: path to 'old' file is not valid")

if not os.path.isfile(newfile):
    usage(sys.stderr, "\nERROR: path to 'new' file is not valid")

oldpo = polib.pofile(oldfile)
newpo = polib.pofile(newfile)
outpo = polib.POFile()

# Copy header and metadata
outpo.header = newpo.header
[outpo.metadata.update({key: val}) for (key, val) in newpo.metadata.items()]

counter = 0

# look at every entry in the new (POT) file
for entry in newpo:
    default_old = default_new = u''
    # fist, extract the default translation of the new (POT) file
    match_new = patt.match(entry.comment)
    if match_new:
        default_new = match_new.group(1).replace('\n', ' ')
    else:
        print "WARNING! msgid '%s' in 'new' file does not have a default " \
            "translation." % entry.msgid
        continue
    # try to find the same message in the existing po file
    target = oldpo.find(entry.msgid)
    if not target:
        # not found == new translation
        outpo.append(polib.POEntry(msgid=entry.msgid, msgstr=default_new,
            occurrences=entry.occurrences, comment=entry.comment))
        counter += 1
    else:
        match_old = patt.match(target.comment)
        if match_old:
            default_old = match_old.group(1).replace('\n', ' ')
            if "Default:" in default_old:
                print "ERROR! There seems to be a duplicate Default entry for msgid '%s'" % entry.msgid
        if default_old != default_new:
            outpo.append(polib.POEntry(msgid=entry.msgid, msgstr=default_new,
                occurrences=entry.occurrences, comment=entry.comment))
            counter += 1

outpo.save(outfile)

sys.exit('Found %d entries that need to be updated' % counter)
