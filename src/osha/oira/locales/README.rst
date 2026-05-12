OiRA translations
*****************

Overview
========

The basic translations for OiRA are located inside the Euphorie package. Additional translations are placed into the osha.oira for the following reasons:

* Some terms / messages need to differ from Euphorie (e.g. survey -> OiRA Tool)
* Some terms / messages do not exist in Euphorie but are required for OiRA

The domain used for the osha.oira .po files is still euphorie!

As usual, there is one .pot file (euphorie.pot), plus one directory for every required language.

We also have a directory (and .po file) for English, because the default values
in euphorie.pot aren't used by default. Instead the default values in
euphorie/deployment/locales/euphorie.pot gets used!
