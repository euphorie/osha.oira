#!/usr/bin/env python

# Author: Wolfgang Thomas <thomas@syslab.com>

"""%(program)s: For an existing po file ORIG and a second po file UPDATE that
contains new translations for a subset of ORIG, the new translations are
merged to ORIG.
Msgids present in UPDATE that are not present in ORIG will be a ignored
(warning) given

usage:    %(program)s orig.po update.po
orig.po   A po file that should be updated with new translations
update.po The po file that contains new translations to go into orig.po
"""


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


if len(sys.argv) < 3:
    usage(sys.stderr, "\nERROR: Not enough arguments")
origfile = sys.argv[1]
updatefile = sys.argv[2]

if not os.path.isfile(origfile):
    usage(sys.stderr, "\nERROR: path to ORIG file is not valid")

if not os.path.isfile(updatefile):
    usage(sys.stderr, "\nERROR: path to UPDATE file is not valid")

orig = polib.pofile(origfile)
update = polib.pofile(updatefile)

cnt = 0
for entry in update:
    msgid = entry.msgid
    if msgid.strip() == "":
        continue
    target = orig.find(msgid)
    if not target:
        print(f"WARNING! msgid '{msgid}' not present in {origfile}.")
        continue
    if entry.msgstr == "" and target.msgstr != "":
        continue
    target.msgstr = entry.msgstr
    cnt += 1

orig.save()

sys.exit(f"Ok, updated {cnt} translations")
