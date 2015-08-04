#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Extract all untranslated messages from a given po file and
write them to a new po file.
The "Default" translation will be written into the msgstr field, or the msgid
itself if not default is present. This can be optionally turned off.

usage:      %(program)s input.po output.po [--noprefill]
input.po    A po file that contains untranslated messages and potentially
            some tranlated ones.
output.po   The name of a po file that will be created by this script.
--noprefill With this option you can prevent the "msgstr" field being filled
            with the default translation.
"""

import sys
import os
import re
import polib

patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)
noprefill = False

def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)

if len(sys.argv) < 3:
    usage(sys.stderr, "\nERROR: Not enough arguments")
input = sys.argv[1]
output = sys.argv[2]
if len(sys.argv) > 3 and sys.argv[3] == "--noprefill":
    noprefill = True

if not os.path.isfile(input):
    usage(sys.stderr, "\nERROR: path to input file is not valid")

po = polib.pofile(input)
newpo = polib.POFile()
# Copy header and metadata
newpo.header = po.header
[newpo.metadata.update({key: val}) for (key, val) in po.metadata.items()]
cnt = 0

# Copy all untranslated messages
for entry in po.untranslated_entries():
    match = patt.match(entry.comment)
    # Write the "Default: " text into the msgstr. Reason: Many translators will
    # not see comments in their translation program.
    default = entry.msgid
    if match:
        default = match.group(1).replace('\n', ' ')
        if "Default:" in default:
            print "ERROR! There seems to be a duplicate Default entry for msgid '%s'" % entry.msgid
    if noprefill:
        default = u''
    newpo.append(polib.POEntry(msgid=entry.msgid, msgstr=default, occurrences=entry.occurrences,
        comment=entry.comment))
    cnt += 1

newpo.save(output)

sys.exit('Ok, found %d untranslated.' % cnt)
