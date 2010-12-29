OiRA translations
*****************

Overview
========

The basic translations for OiRA are located inside the Euphorie package. Additional translations are placed into the osha.oira for the following reasons:

* Some terms / messages need to differ from Euphorie (e.g. survey -> OiRA Tool)
* Some terms / messages do not exist in Euphorie but are required for OiRA

The domain used for the osha.oira .po files is still euphorie!


As usual, there is one .pot file (euphorie.pot), plus one directory for every required language.

Adding new translations
=======================

Since these .po files are used to override existing translations in the same domain, we cannot use any automatic extraction mechanism to find new msgids. The automatic extraction is done solely in the Euphorie package (see there). That means all msgids will be added manually as the need arises.

General rules
-------------

* _NEVER_, under penalty of (insert horrible punishment here) add a msgid directly into a .po file. Always add a msgid to the .pot file. Otherwise it will be impossible to keep track of changes.

* In the .pot file, add the default translation as a comment and leave the msgstr blank. Example:

  #. Default: "OiRA - Online interactive Risk Assessment"
  msgid "title_tool"
  msgstr ""

* If you detect a missing translation, e.g. due to a missing i18n:translate statement in one of the Euphorie templates, please check if the new msgid might not be of general interest and add it to the Euphorie package, before you add it here.

`gettext' is your friend
------------------------

Good documentation: http://www.gnu.org/software/hello/manual/gettext/

To propagate a new message from the .pot file, use the msgmerge command. Example:

  msgmerge -U -N --backup=off en/LC_MESSAGES/euphorie.po euphorie.pot

This will add new msgids (plus comments) to the .po file but leave existing translations untouched.

To extract all untranslated messages from a .po file, you can use the script getUntranslated.py. Example

  python getUntranslated.py fr/LC_MESSAGES/euphorie.po send_to_translation.po



