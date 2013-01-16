#!/bin/sh

EUPHORIE_LOCALES="../../../../../Euphorie/src/euphorie/deployment/locales"
OUTPUT_DIR="untranslated"
TMP_DIR="/tmp"

# Firstly, msgmerge

msgmerge -U -N --backup=off bg/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off ca/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off cs/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off el/LC_MESSAGES/euphorie.po euphorie.pot
msgmerge -U -N --backup=off es/LC_MESSAGES/euphorie.po euphorie.pot
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
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/lv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/fr/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/nl_BE/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sk/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sl/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
#msgmerge -U -N --backup=off $EUPHORIE_LOCALES/de/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot
#msgmerge -U -N --backup=off $EUPHORIE_LOCALES/sv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot

# osha.oira

./findDirtyTranslations.py ca/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.ca.po
./findDirtyTranslations.py bg/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.bg.po
./findDirtyTranslations.py cs/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.cs.po
./findDirtyTranslations.py el/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.el.po
./findDirtyTranslations.py es/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.es.po
./findDirtyTranslations.py lv/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.lv.po
./findDirtyTranslations.py fr/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.fr.po
./findDirtyTranslations.py nl_BE/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.nl_BE.po
./findDirtyTranslations.py sk/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sk.po
./findDirtyTranslations.py sl/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sl.po
#./findDirtyTranslations.py de/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.de.po
#./findDirtyTranslations.py sv/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=$OUTPUT_DIR/osha.oira.sv.po

# euphorie

./findDirtyTranslations.py $EUPHORIE_LOCALES/bg/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.bg.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/ca/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.ca.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/cs/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.cs.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/el/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.el.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/es/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$TMP_DIR/euphorie.es.XX.po --noprefill
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
./getNewEntries.py lv/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.lv.XX.po $OUTPUT_DIR/euphorie.lv.po --ignore-translated
./getNewEntries.py fr/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.fr.XX.po $OUTPUT_DIR/euphorie.fr.po --ignore-translated
./getNewEntries.py nl_BE/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.nl_BE.XX.po $OUTPUT_DIR/euphorie.nl_BE.po --ignore-translated
./getNewEntries.py sk/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sk.XX.po $OUTPUT_DIR/euphorie.sk.po --ignore-translated
./getNewEntries.py sl/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sl.XX.po $OUTPUT_DIR/euphorie.sl.po --ignore-translated

# not wanted at the moment
#./getNewEntries.py de/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.de.XX.po $OUTPUT_DIR/euphorie.de.po --ignore-translated
#./getNewEntries.py sv/LC_MESSAGES/euphorie.po $TMP_DIR/euphorie.sv.XX.po $OUTPUT_DIR/euphorie.sv.po --ignore-translated

