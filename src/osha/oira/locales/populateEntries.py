#!/usr/bin/env python
# Authors: Wolfgang Thomas <thomas@syslab.com>
#          JC Brand <brand@syslab.com>

"""%(program)s: For every untranslated or fuzzy entry, 
copy its "Default" string for its value. If no default value exists, copy its
msgid.

usage:                  %(program)s file.po
file.po                 The po file
outfile.po              The po file to be written to
"""

import sys
import os
import re
import polib

from findDirtyTranslations import get_default
from findDirtyTranslations import append_entry

patt = re.compile("""Default:.?["\' ](.*?)(["\']$|$)""", re.S)


def usage(stream, msg=None):
    if msg:
        print >> stream, msg
        print >> stream
    program = os.path.basename(sys.argv[0])
    print >> stream, __doc__ % {"program": program}
    sys.exit(0)


def main():
    if len(sys.argv) < 3:
        usage(sys.stderr, "\nERROR: Not enough arguments")
    elif len(sys.argv) > 3:
        usage(sys.stderr, "\nERROR: Too many arguments")

    file = sys.argv[1]
    if not os.path.isfile(file):
        usage(sys.stderr, "\nERROR: path to 'old' file is not valid")

    outfile = sys.argv[2]

    pofile = polib.pofile(file)
    outpo = polib.POFile()

    # Copy header and metadata
    outpo.header = pofile.header
    [outpo.metadata.update({key: val}) for (key, val) in pofile.metadata.items()]

    entries = pofile.untranslated_entries() + pofile.fuzzy_entries()

    for entry in entries:
        default = get_default(entry)
        outpo = append_entry(outpo, entry, default)

    outpo.save(outfile)
    print "--------------------------------------------------------"
    print "SOME STATS TO HELP WITH DOUBLE-CHECKING:"
    print "Untranslated entries in old.po: %d" % len(pofile.untranslated_entries())
    print "Fuzzy entries in old.po: %d" % len(pofile.fuzzy_entries())
    print "Found %d entries that need to be updated" % len(outpo)
    print "--------------------------------------------------------"

    sys.exit('Finished sucessfully')

if __name__ == "__main__":
    main()

