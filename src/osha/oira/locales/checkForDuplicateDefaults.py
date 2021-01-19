#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: Parse a given .po file and shout a warning for every entry that
has more than one Default entry.

usage:    %(program)s file.po
file.po   A po to check
--debug   Print debug statistics.
"""

from __future__ import print_function

import os
import polib
import re
import sys


patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)


def usage(stream, msg=None):
    if msg:
        print(msg, file=stream)
        print("\n", file=stream)
    program = os.path.basename(sys.argv[0])
    print(__doc__ % {"program": program}, file=stream)
    sys.exit(0)


if len(sys.argv) < 2:
    usage(sys.stderr, "\nERROR: Not enough arguments")
filename = sys.argv[1]

debug = False
for i in range(1, len(sys.argv)):
    arg = sys.argv.pop()
    if arg == "--debug":
        debug = True


po = polib.pofile(filename)
counter = 0

for entry in po:
    counter += 1
    match = patt.match(entry.comment)
    if match:
        default = match.group(1).replace("\n", " ")
        if "Default:" in default:
            print(
                "ERROR! There seems to be a duplicate Default entry for msgid '%s'"
                % entry.msgid
            )  # noqa: E501
    else:
        if debug:
            print("WARNING! No Default translation for msgid '%s'." % entry.msgid)

sys.exit("Finished, checked all %d entries." % counter)
