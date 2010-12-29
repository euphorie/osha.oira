#!/opt/python/python-2.6/bin/python2.6

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Extract all untranslated messages from a given po file and
write them to a new po file.

usage:    %(program)s input.po output.po
input.po  A po file that already contains some translations and some
          untranslated messages.
output.po The name of a po file that will be created by this script.
"""

import sys
import os
import re
import polib

patt = re.compile('Default: "(.*)"', re.S)


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

if not os.path.isfile(input):
    usage(sys.stderr, "\nERROR: path to input file is not valid")

po = polib.pofile(input)
newpo = polib.POFile()
# Copy header and metadata
newpo.header = po.header
[newpo.metadata.update({key: val}) for (key, val) in po.metadata.items()]

# Copy all untranslated messages
for entry in po.untranslated_entries():
    match = patt.match(entry.comment)
    # Write the "Default: " text into the msgstr. Reason: Many translators will
    # not see comments in their translation program.
    default = u""
    if match:
        default = match.group(1).replace('\n', ' ')
    newpo.append(polib.POEntry(msgid=entry.msgid, msgstr=default,
        comment=entry.comment))

newpo.save(output)

sys.exit('Ok')
