#!/bin/sh

EUPHORIE_LOCALES="../../../../../Euphorie/src/euphorie/deployment/locales"
OUTPUT_DIR="untranslated"

./findDirtyTranslations.py $EUPHORIE_LOCALES/bg/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.bg.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/ca/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.ca.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/cs/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.cs.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/el/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.el.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/es/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.es.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/lv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.lv.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/fr/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.fr.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/nl_BE/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.nl_BE.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/sk/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.sk.XX.po --noprefill
./findDirtyTranslations.py $EUPHORIE_LOCALES/sl/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.sl.XX.po --noprefill

# no wanted at the moment
# ./findDirtyTranslations.py $EUPHORIE_LOCALES/de/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.de.XX.po --noprefill
# ./findDirtyTranslations.py $EUPHORIE_LOCALES/sv/LC_MESSAGES/euphorie.po $EUPHORIE_LOCALES/euphorie.pot  --untranslated --debug --fuzzy --output=$OUTPUT_DIR/euphorie.sv.XX.po --noprefill


./getNewEntries.py bg/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.bg.XX.po $OUTPUT_DIR/euphorie.bg.po --ignore-translated
./getNewEntries.py ca/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.ca.XX.po $OUTPUT_DIR/euphorie.ca.po --ignore-translated
./getNewEntries.py cs/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.cs.XX.po $OUTPUT_DIR/euphorie.cs.po --ignore-translated
./getNewEntries.py el/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.el.XX.po $OUTPUT_DIR/euphorie.el.po --ignore-translated
./getNewEntries.py es/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.es.XX.po $OUTPUT_DIR/euphorie.es.po --ignore-translated
./getNewEntries.py lv/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.lv.XX.po $OUTPUT_DIR/euphorie.lv.po --ignore-translated
./getNewEntries.py fr/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.fr.XX.po $OUTPUT_DIR/euphorie.fr.po --ignore-translated
./getNewEntries.py nl_BE/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.nl_BE.XX.po $OUTPUT_DIR/euphorie.nl_BE.po --ignore-translated
./getNewEntries.py sk/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.sk.XX.po $OUTPUT_DIR/euphorie.sk.po --ignore-translated
./getNewEntries.py sl/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.sl.XX.po $OUTPUT_DIR/euphorie.sl.po --ignore-translated

# not wanted at the moment
#./getNewEntries.py de/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.de.XX.po $OUTPUT_DIR/euphorie.de.po --ignore-translated
#./getNewEntries.py sv/LC_MESSAGES/euphorie.po $OUTPUT_DIR/euphorie.sv.XX.po $OUTPUT_DIR/euphorie.sv.po --ignore-translated

