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

Adding new translations
=======================

We cannot use infrae.i18nextract to extract messages for osha.oira's
euphorie.pot because it will look in all the packages containing the *euphorie*
domain, and we only want the strings from osha.oira.

Additionally, apparently it cannot properly parse Chameleon templates.

We can however use osha.oira's setup.py. It's however important to have
*lingua* installed, it's a package (hosted on GitHub by Wichert) containing helpers for parsing *Chameleon*
templates.

There is no *lingua* egg on pypi, but I released one to syslabcom.

So, to update the euphorie.pot file in osha.oira, do this:

* python setup.py extract_messages

If lingua is installed via buildout (which development.cfg does), then use this:

* ~/${buildout:dir}/bin/zopepy setup.py extract_messages


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


Updating existing translations
==============================

Finding dirty translations
--------------------------

Whenever a default (English) string changes, all translations of it become dirty and need to be re-translated.
We use the script findDirtyTranslations.py to generate a po file of all dirty entries per language.
It is compares the "Default" entries to achieve this
The script takes 2 arguments:
1) The existing translation po file
2) A file with updated "Default" translations; usually this will be a newly generated .pot file
3) --output (optional) specifies file to which contents must be written, otherwise stdout is used.
4) --untranslated which specifies whether untranslated entries which
are already in old.po must also be included in the output file
5) --fuzzy which specifies whether fuzzy entries should also be
included.

E.g:
./findDirtyTranslations.py sv/LC_MESSAGES/euphorie.po euphorie.pot  --untranslated --fuzzy --output=dirtySV.po

The output file will contain all "dirty" msgids, as well as all new ones (and
existing untranslated or fuzzy ones if specified).


Finding translations added to the Euphorie mother-package
---------------------------------------------------------

OSHA is very finnicky about certain terms (i.e OiRA Tool vs Survey). So
whenever Wichert or someone else upstream adds new entries to the euphorie.po
in euphorie/deployment, we have to check that these verboten strings/terms are
not there.

getNewEntries.py is a script that can help. It provides all the entries in a
po/pot file that is not in another po/pot file.

We can then run this script on osha/oira/locales/euphorie.pot and
euphorie/deployment/locales/euphorie.pot and get a list of all the entries in
the second file that are not in the first. Then we can grep for those terms
that need to be replaced.

E.g:
./getNewEntries.py euphorie.pot ../../../euphorie/deployment/locales/euphorie.pot newWichert.po

Creating po files for the translators
-------------------------------------

For both osha.oira and euphorie.deployment, make sure euphorie.pot is updated.

* For *osha.oira*: Now use findDirtyTranslations (with --untranslated and --fuzzy)
to generate the *.po files for translators.

E.g: 
./findDirtyTranslations.py sv/LC_MESSAGES/euphorie.po euphorie.pot --untranslated --fuzzy --output=dirtySV.po

* For *euphorie.deployment*: Use getNewEntries (with --ignore-translated) to
generate *.po files for translators

E.g: 
./getNewEntries.py el/LC_MESSAGES/euphorie.po ../../../euphorie/deployment/locales/el/LC_MESSAGES/euphorie.po euphorieEL.po --ignore-translated

Now we have oiraSV.po and euphorieSV.po which can be sent to the translators.


Propagating translations to existing po-files
---------------------------------------------

Every so often, we need to send a sub-set of an existing po-file to the translators, either because
1) new msgids were added and no translation exists yet or
2) the default translation has changed and a re-translation is necessary.

From the translators, we get back an UPDATE.po which is a subset of the existing ORIG.po. You can use the script
updatePoWithTranslations.py to propagate the newly translated entries.
If UPDATE.po contains msgids that are not present in ORIG.po, they will be ignored! The proper way to introduce new
msgids is by adding them to the .pot file first and propagating them via msgmerge (see above).

A note on formatting
--------------------

The script updatePoWithTranslations.py uses polib to manipulate ORIG.po. It will format the file in such a way that lines
don't exceed 80 characters but are filled up as much as possible (optimisation). This is contrary to what babel (used in
Euphorie) does. Therefore a `svn diff` will be useless after applying the script. But if you run the update_catalog step
from Euphorie's i18nupdate again, the formatting will be reverted to Euphorie style, and a `svn diff` will only show
the actual changes.


