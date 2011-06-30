#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Extract all text to be translated, either from the msgstr or the msgid. Can be used for word-counting.

usage:      %(program)s input.po output.txt
input.po    A po file that contains text to be translated
output.txt  File name where the extracted text will be dumped
"""

import sys
import os
import re
import polib
from StringIO import StringIO

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

out = StringIO()


if not os.path.isfile(input):
    usage(sys.stderr, "\nERROR: path to input file is not valid")

po = polib.pofile(input)


# Copy all untranslated messages
for entry in po:
    match = patt.match(entry.comment)
    txt = entry.msgid
    if match:
        txt = match.group(1).replace('\n', ' ')
        if "Default:" in txt:
            print "ERROR! There seems to be a duplicate Default entry for msgid '%s'" % entry.msgid
    out.write(u"%s\n" % txt)


fh = open(output, 'w')
val = out.getvalue().encode('utf-8')
fh.write(val)
fh.close()

sys.exit('Ok')
