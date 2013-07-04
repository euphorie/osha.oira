#!/bin/bash

# A script that gathers all missing translations for Euphorie and osha.oira.
# Requires potools, translation-toolkit and pkzip.

if ! hash pounique 2>/dev/null; then
    echo "Could not find 'pounique', have you installed potools 0.3 or later?"
    exit 1
fi

if ! hash pofilter 2>/dev/null; then
    echo "Could not find 'pofilter', have you installed translate-toolkit?"
    exit 1
fi

if ! hash zip 2>/dev/null; then
    echo "Could not find 'zip', is it installed?"
    exit 1
fi

CURDIR=`pwd`
SRCDIR=$CURDIR

while ! [ -e "$SRCDIR/Euphorie" ]; do
    SRCDIR=`dirname $SRCDIR`
    if [ $SRCDIR == '/' ]; then
        echo "Could not find the source directory for Euphorie and osha.oira"
        exit 1
    fi
done;

if ! [ -e "$SRCDIR/osha.oira" ]; then
    echo "$SRCDIR seems to contain the Euphorie source code, but not the osha.oira source code."
    echo "I can't merge and find untranslated texts unless they are both checked out."
    exit 1
fi


# First merge Euphorie and osha.oira translations together, with osha.oira overriding Euphorie:

UNIQUEDIR=`mktemp -d`
echo "Uniqe dir: $UNIQUEDIR"

pounique "$SRCDIR/Euphorie/src/euphorie/deployment/locales" "$SRCDIR/osha.oira/src/osha/oira/locales" -o $UNIQUEDIR


# Now filter out only those who needs review or translation:

FILTEREDDIR=`mktemp -d`
echo "Filtered dir: $FILTEREDDIR"

pofilter -t untranslated -t isreview -t isfuzzy --nonotes $UNIQUEDIR -o $FILTEREDDIR

# To make the translators life easier, populate empty translations with defaults:

popopulate -u -f $FILTEREDDIR

# And zip those together into a zip-file:

OUTFILE=$CURDIR/untranslated_`date +%F`.zip

cd $FILTEREDDIR
zip -q -r $OUTFILE .
echo "Missing translations gathered into $OUTFILE"

