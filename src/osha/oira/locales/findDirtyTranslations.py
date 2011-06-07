#!/usr/bin/env python
# Authors: Wolfgang Thomas <thomas@syslab.com>
#          JC Brand <brand@syslab.com>

"""%(program)s: Compare two .po or .pot files to find entries that need to be
updated. This is done by comparing the "Default" translations.
All entries found in this way are written to a new po file that can be sent
to translators.

usage:                  %(program)s old.po new.pot out.po
old.po                  A po file that contains existing, potentially outdated translations
new.pot                 A po/pot file with updated default translations (e.g. via extraction)
out.po                  A name for the output po file
--include-untranslated  Optional. Specifies that untranslated entries from old.po must also be
                        included in the out.po file.
--include-fuzzy         Optional. Specifies that fuzzy entries in old.po must
                        also be included in the out.po file.
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

def get_default(entry):
    """ Extract the default translation from the entry (without "Default:")
    """
    match = patt.match(entry.comment)
    # Write the "Default: " text into the msgstr. Reason: Many translators will
    # not see comments in their translation program.
    default = entry.msgid
    if match:
        default = match.group(1).replace('\n', ' ')
        if "Default:" in default:
            print "ERROR! There seems to be a duplicate Default entry for " \
                "msgid '%s'" % entry.msgid
    else:
        print "WARNING! msgid '%s' in 'new' file does not have a default " \
            "translation." % entry.msgid
        default = entry.msgid
    return default

def append_entry(pofile, entry, default):
    pofile.append(
        polib.POEntry(
                    msgid=entry.msgid, 
                    msgstr=default, 
                    occurrences=entry.occurrences,
                    comment=entry.comment)
                )
    return pofile

def main():
    if len(sys.argv) < 4:
        usage(sys.stderr, "\nERROR: Not enough arguments")

    oldfile = sys.argv[1]
    if not os.path.isfile(oldfile):
        usage(sys.stderr, "\nERROR: path to 'old' file is not valid")

    newfile = sys.argv[2]
    if not os.path.isfile(newfile):
        usage(sys.stderr, "\nERROR: path to 'new' file is not valid")

    outfile = sys.argv[3]

    oldpo = polib.pofile(oldfile)
    newpo = polib.pofile(newfile)
    outpo = polib.POFile()

    # Copy header and metadata
    outpo.header = newpo.header
    [outpo.metadata.update({key: val}) for (key, val) in newpo.metadata.items()]

    for entry in newpo:
        default_old = default_new = u''
        # fist, extract the default translation of the new (POT) file
        default_new = get_default(entry)

        # try to find the same message in the existing po file
        target = oldpo.find(entry.msgid)
        if not target:
            # not found == new translation
            outpo = append_entry(outpo, entry, default_new)
            continue 

        default_old = get_default(target)
        if default_old != default_new:
            outpo = append_entry(outpo, entry, default_new)

    if len(sys.argv) > 4:
        extra_entries = []
        if "--include-untranslated" in sys.argv[4:]:
            extra_entries += oldpo.untranslated_entries()

        if "--include-fuzzy" in sys.argv[4:]:
            extra_entries += oldpo.fuzzy_entries()
            
        for entry in extra_entries:
            if entry.obsolete: 
                # Remove commented entries
                continue
            default = get_default(entry)
            outpo = append_entry(outpo, entry, default)

    outpo.save(outfile)
    sys.exit('Found %d entries that need to be updated' % len(outpo))

if __name__ == "__main__":
    main()

