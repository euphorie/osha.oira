#!/usr/bin/env python
# Authors: Wolfgang Thomas <thomas@syslab.com>
#          JC Brand <brand@syslab.com>

"""%(program)s: Compare two .po or .pot files to find entries that need to be
updated. This is done by comparing the "Default" translations.
All entries found in this way are written to a new po file that can be sent
to translators.

usage:           %(program)s old.po new.pot 
old.po           A po file that contains existing, potentially outdated translations
new.pot          A po/pot file with updated default translations (e.g. via extraction)
--untranslated   Optional. Specifies that untranslated entries from old.po must also be
                 included in the out.po file.
--fuzzy          Optional. Specifies that fuzzy entries in old.po must
                 also be included in the out.po file.
--debug          Print debug statistics.
--output         Specify file to which contents must be written (using =), otherwise stdout is used.
--noprefill      With this option you can prevent the "msgstr" field being filled
                 with the default translation.
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
                    msgstr=default.strip(),
                    occurrences=entry.occurrences,
                    comment=entry.comment)
                )
    return pofile

def main():

    include_untranslated = False
    include_fuzzy = False
    debug = False
    extra_entries = []
    files = []
    outfile = None
    noprefill = False

    for i in range(1, len(sys.argv)):
        arg = sys.argv.pop()
        if arg == "--untranslated":
            include_untranslated = True
        elif arg == "--fuzzy":
            include_fuzzy = True
        elif arg == "--debug":
            debug = True
        elif "--output=" in arg:
            outfile = arg.split('=')[1]
        elif arg == "--noprefill":
            noprefill = True
        elif os.path.isfile(arg):
            files.append(arg)
        else:
            usage(sys.stderr, "\nERROR: path to file is not valid: %s" % arg)

    if len(files) != 2:
        usage(sys.stderr, "\nERROR: Too many or too few files specified")

    newfile, oldfile = files
    oldpo = polib.pofile(oldfile)
    newpo = polib.pofile(newfile)
    outpo = polib.POFile()
            
    # Copy header and metadata
    outpo.header = newpo.header
    [outpo.metadata.update({key: val}) for (key, val) in newpo.metadata.items()]

    new_entries = 0
    changed_entries = 0

    for entry in newpo:
        if entry.obsolete:
            # Ignore commented out entries
            continue

        default_old = default_new = u''
        # fist, extract the default translation of the new (POT) file
        default_new = get_default(entry)
        # string to put as translation:
        default_msgstr = noprefill and " " or default_new
        # try to find the same message in the existing po file
        target = oldpo.find(entry.msgid)
        if not target:
            # not found == new translation
            new_entries += 1
            outpo = append_entry(outpo, entry, default_msgstr)
            continue 

        default_old = get_default(target)
        if default_old != default_new:
            # Default value is different between the two files
            changed_entries += 1
            outpo = append_entry(outpo, entry, default_msgstr)

    if include_untranslated:
        extra_entries += oldpo.untranslated_entries()
    if include_fuzzy:
        extra_entries += oldpo.fuzzy_entries()

    for entry in extra_entries:
        if entry.obsolete: 
            # Remove commented entries
            continue
        default_msgstr = noprefill and " " or get_default(entry)
        outpo = append_entry(outpo, entry, default_msgstr)

    if outfile:
        outpo.save(outfile)
    else:
        print outpo 

    if debug:
        print "--------------------------------------------------------"
        print "SOME STATS TO HELP WITH DOUBLE-CHECKING:"
        print "In %s: %d untranslated entries and %d fuzzy entries" \
                            % ( oldfile, 
                                len(oldpo.untranslated_entries()), 
                                len(oldpo.fuzzy_entries())
                            )
        print "In %s: %d new entries and %d changed entries" % (newfile, new_entries, changed_entries)
        print "%d entries were updated" % len(outpo)
        print "--------------------------------------------------------"

    sys.exit('Finished sucessfully')

if __name__ == "__main__":
    main()

