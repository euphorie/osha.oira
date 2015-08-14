#!/bin/sh

EUPHORIE_LOCALES="../../../../../Euphorie/src/euphorie/deployment/locales"
OUTPUT_DIR="untrans5"
TMP_DIR="/tmp"

# Firstly, msgmerge

msgmerge -U -N --backup=off bg/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off ca/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off cs/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off el/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off es/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off fi/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off it/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off is/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off lt/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off mt/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off pt/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off lv/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off fr/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off nl_BE/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off sk/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off sl/LC_MESSAGES/euphorie.po euphorie.pot
#msgmerge -U -N --backup=off de/LC_MESSAGES/euphorie.po euphorie.pot
#msgmerge -U -N --backup=off sv/LC_MESSAGES/euphorie.po euphorie.pot


msgmerge -U -N --backup=off $EUPHORIE_LOCALES/bg/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/ca/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/cs/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/el/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/es/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/fi/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/it/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/is/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/lt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/mt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/pt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/lv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/fr/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/nl_BE/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sk/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sl/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
#msgmerge -U -N --backup=off $EUPHORIE_LOCALES/de/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
#msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot


# Copy the OIRA files to the output dir

cp bg/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.bg.po
cp ca/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.ca.po
cp cs/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.cs.po
cp el/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.el.po
cp es/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.es.po
cp fi/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.fi.po
cp it/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.it.po
cp is/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.is.po
cp lt/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.lt.po
cp mt/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.mt.po
cp pt/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.pt.po
cp lv/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.lv.po
cp fr/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.fr.po
cp nl_BE/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.nl_BE.po
cp sk/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.sk.po
cp sl/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.sl.po
#cp de/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.de.po
#cp sv/LC_MESSAGES/euphorie.po $OUTPUT_DIR/osha.oira.sv.po


# Copy over existing translations from Euphorie to OIRA

./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.bg.po euphorie.pot $EUPHORIE_LOCALES/bg/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.ca.po euphorie.pot $EUPHORIE_LOCALES/ca/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.cs.po euphorie.pot $EUPHORIE_LOCALES/cs/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.el.po euphorie.pot $EUPHORIE_LOCALES/el/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.es.po euphorie.pot $EUPHORIE_LOCALES/es/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.fi.po euphorie.pot $EUPHORIE_LOCALES/fi/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.it.po euphorie.pot $EUPHORIE_LOCALES/it/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.is.po euphorie.pot $EUPHORIE_LOCALES/is/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.lt.po euphorie.pot $EUPHORIE_LOCALES/lt/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.mt.po euphorie.pot $EUPHORIE_LOCALES/mt/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.pt.po euphorie.pot $EUPHORIE_LOCALES/pt/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.lv.po euphorie.pot $EUPHORIE_LOCALES/lv/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.fr.po euphorie.pot $EUPHORIE_LOCALES/fr/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.nl_BE.po euphorie.pot $EUPHORIE_LOCALES/nl_BE/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.sk.po euphorie.pot $EUPHORIE_LOCALES/sk/LC_MESSAGES/euphorie.po
./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.sl.po euphorie.pot $EUPHORIE_LOCALES/sl/LC_MESSAGES/euphorie.po
#./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.de.po euphorie.pot $EUPHORIE_LOCALES/de/LC_MESSAGES/euphorie.po
#./copyExistingTranslations.py $OUTPUT_DIR/osha.oira.sv.po euphorie.pot $EUPHORIE_LOCALES/sv/LC_MESSAGES/euphorie.po


# find dirty translations in OiRA

./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.ca.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.ca.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.bg.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.bg.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.cs.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.cs.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.el.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.el.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.es.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.es.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.fi.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.fi.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.it.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.it.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.is.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.is.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.lt.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.lt.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.mt.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.mt.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.pt.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.pt.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.lv.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.lv.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.fr.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.fr.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.nl_BE.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.nl_BE.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.sk.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sk.po
./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.sl.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sl.po
#./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.de.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.de.po
#./findDirtyTranslations.py $OUTPUT_DIR/osha.oira.sv.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sv.po

# euphorie

./findDirtyTranslations.py $EUPHORIE_LOCALES/bg/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.bg.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/ca/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.ca.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/cs/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.cs.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/el/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.el.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/es/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.es.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/fi/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.fi.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/it/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.it.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/is/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.is.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/lt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.lt.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/mt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.mt.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/pt/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.pt.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/lv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.lv.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/fr/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.fr.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/nl_BE/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.nl_BE.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/sk/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.sk.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/sl/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.sl.XX.po --noprefill

# no wanted at the moment
# ./findDirtyTranslations.py $EUPHORIE_LOCALES/de/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.de.XX.po --noprefill
# ./findDirtyTranslations.py $EUPHORIE_LOCALES/sv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.sv.XX.po --noprefill


./getNewEntries.py bg/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.bg.XX.po $OUTPUT_DIR/euphorie.bg.po --ignore-translated
./getNewEntries.py ca/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.ca.XX.po $OUTPUT_DIR/euphorie.ca.po --ignore-translated
./getNewEntries.py cs/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.cs.XX.po $OUTPUT_DIR/euphorie.cs.po --ignore-translated
./getNewEntries.py el/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.el.XX.po $OUTPUT_DIR/euphorie.el.po --ignore-translated
./getNewEntries.py es/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.es.XX.po $OUTPUT_DIR/euphorie.es.po --ignore-translated
./getNewEntries.py fi/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.fi.XX.po $OUTPUT_DIR/euphorie.fi.po --ignore-translated
./getNewEntries.py it/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.it.XX.po $OUTPUT_DIR/euphorie.it.po --ignore-translated
./getNewEntries.py is/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.is.XX.po $OUTPUT_DIR/euphorie.is.po --ignore-translated
./getNewEntries.py lt/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.lt.XX.po $OUTPUT_DIR/euphorie.lt.po --ignore-translated
./getNewEntries.py mt/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.mt.XX.po $OUTPUT_DIR/euphorie.mt.po --ignore-translated
./getNewEntries.py pt/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.pt.XX.po $OUTPUT_DIR/euphorie.pt.po --ignore-translated
./getNewEntries.py lv/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.lv.XX.po $OUTPUT_DIR/euphorie.lv.po --ignore-translated
./getNewEntries.py fr/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.fr.XX.po $OUTPUT_DIR/euphorie.fr.po --ignore-translated
./getNewEntries.py nl_BE/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.nl_BE.XX.po $OUTPUT_DIR/euphorie.nl_BE.po --ignore-translated
./getNewEntries.py sk/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sk.XX.po $OUTPUT_DIR/euphorie.sk.po --ignore-translated
./getNewEntries.py sl/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sl.XX.po $OUTPUT_DIR/euphorie.sl.po --ignore-translated

# not wanted at the moment
#./getNewEntries.py de/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.de.XX.po $OUTPUT_DIR/euphorie.de.po --ignore-translated
#./getNewEntries.py sv/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sv.XX.po $OUTPUT_DIR/euphorie.sv.po --ignore-translated

