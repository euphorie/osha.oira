#!/usr/bin/env python
# Author: JC Brand <brand@syslab.com>

"""%(program)s: Compare two .po or .pot files and find all the entries in the
second file that are not in the first one. These entries are then written to a
new po file.

usage:                  %(program)s first.po second.pot out.po
first.po                A po/pot file with
second.pot              A po/pot file with updated default translations (e.g. via extraction)
out.po                  A name for the output po file
--ignore-translated     Ignore translated entries. Only untranslated and fuzzy
                        entries will be returned.
"""

import sys
import os
import re
import polib

patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)

from findDirtyTranslations import get_default
from findDirtyTranslations import append_entry

def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)

def main():
    if len(sys.argv) < 4:
        usage(sys.stderr, "\nERROR: Not enough arguments")
    elif len(sys.argv) > 5:
        usage(sys.stderr, "\nERROR: Too many arguments")

    oldfile = sys.argv[1]
    if not os.path.isfile(oldfile):
        usage(sys.stderr, "\nERROR: path to 'old' file is not valid")

    newfile = sys.argv[2]
    if not os.path.isfile(newfile):
        usage(sys.stderr, "\nERROR: path to 'new' file is not valid")

    outfile = sys.argv[3]

    firstpo = polib.pofile(oldfile)
    secondpo = polib.pofile(newfile)
    outpo = polib.POFile()

    # Copy header and metadata
    outpo.header = secondpo.header
    [outpo.metadata.update({key: val}) for (key, val) in secondpo.metadata.items()]

    if len(sys.argv) == 5 and "--ignore-translated" in sys.argv[4]:
        entries = secondpo.untranslated_entries() + secondpo.fuzzy_entries()
    else:
        entries = secondpo

    for entry in entries:
        if entry.obsolete:
            # Ignore outcommented entries
            continue

        default= get_default(entry)
        if not firstpo.find(entry.msgid):
            outpo = append_entry(outpo, entry, default)

    outpo.save(outfile)
    sys.exit('Found %d entries in %s that are not in %s' % (len(outpo), newfile, oldfile))

if __name__ == "__main__":
    main()
    
