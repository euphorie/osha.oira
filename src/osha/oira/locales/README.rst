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

There is also a bug when parsing tal-statements that are inside javascript.
Instead we are using pybabel, and this is done via osha.oira's makefile.

To update the .pot file, go to the root osha.oira directory and type:

    $ make pot
    
This installs a whole Plone the first time it's run, but that's just because
of dependencies, you will not actually run it.

You then need to update all the po files, which you do with 

    $ make all

General rules
-------------

* **NEVER**, under penalty of (insert horrible punishment here) add a msgid directly into a .po file. And neither should you manually edit the .pot file.
  All text to be translated must be found via automatic extraction. If you have text to translate that does not appear in any python code
  or in page templates (e.g. because it is dynamic), or text that requires a different default translation, you must place it into
  osha.oira.manual_translations.py. The next run of extract_messages will pick it up.
  Otherwise it will be impossible to keep track of changes.

* If you detect a missing translation, e.g. due to a missing i18n:translate statement in one of the Euphorie templates, please check if the
  new msgid might not be of general interest and add it to the Euphorie package, before you add it here.



To extract all untranslated messages from a .po file, you can use the script getUntranslated.py. Example::

  python getUntranslated.py fr/LC_MESSAGES/euphorie.po send_to_translation.po


Updating existing translations
==============================

Finding dirty translations
--------------------------

Whenever a default (English) string changes, all translations of it become dirty and need to be re-translated.
We use the script *findDirtyTranslations.py* to generate a po file of all dirty entries per language.
It is compares the "Default" entries to achieve this. The script takes several arguments:

1. The existing translation po file
2. A file with updated "Default" translations; usually this will be a newly generated .pot file
3. --output (optional) specifies file to which contents must be written, otherwise stdout is used.
4. --untranslated which specifies whether untranslated entries which are already in old.po must also be included in the output file
5. --fuzzy which specifies whether fuzzy entries should also be included.

Example::

  ./findDirtyTranslations.py sv/LC_MESSAGES/euphorie.po euphorie.pot  --untranslated --fuzzy --output=dirtySV.po

The output file will contain all "dirty" msgids, as well as all new ones (and
existing untranslated or fuzzy ones if specified).


Finding translations added to the Euphorie mother-package
---------------------------------------------------------

OSHA is very finnicky about certain terms (i.e OiRA Tool vs Survey). So
whenever Wichert or someone else upstream adds new entries to the euphorie.po
in euphorie/deployment, we have to check that these verboten strings/terms are
not there.

*getNewEntries.py* is a script that can help. It provides all the entries in a
po/pot file that is not in another po/pot file.

We can then run this script on osha/oira/locales/euphorie.pot and
euphorie/deployment/locales/euphorie.pot and get a list of all the entries in
the second file that are not in the first. Then we can grep for those terms
that need to be replaced. E.g::

  ./getNewEntries.py euphorie.pot ../../../euphorie/deployment/locales/euphorie.pot newWichert.po


Creating po files for the translators
-------------------------------------

To find untranslated messages, including fuzzy translations, run the script *gatherTranslations.sh*.
You will need version 1.3.1 or later of potools installed.

  $ cd src/osha/oira/locales
  $ ./gatherTranslations.sh
  
This will create a zip file of necessary translations.


Updating po files with new translations
---------------------------------------

When updating the translations you need to update both the Euphorie and the osha.oira translations.

If you have just one translation file, you can update the translations like this,
from the buildout root:

  $ poupdate -r src/osha.oira/src/osha/oira/locales/sv/LC_MESSAGES/euphorie.po new_sv_translation/euphorie.po
  $ poupdate -r src/Euphorie/src/euphorie/deployment/locales/sv/LC_MESSAGES/euphorie.po new_sv_translation.po
  
If you get the translations in a ZIP-file, unzip that file, and update both packages:

  $ poupdate -r src/osha.oira/src/osha/oira/locales/ /tmp/new_translations/
  $ poupdate -r src/Euphorie/src/euphorie/deployment/locales/ /tmp/new_translations/


Beware of fuzzy!
----------------

There's apparently a problem with "#fuzzy" entries in po files in combination with chameleon.
In the admin interface, changing to a language in which a fuzzy entry is present **can** lead to a UnicodeDecodeError.

Therefore, before releasing a new egg version for osha.oira, Euphorie or NuPlone, make sure

* that no single .po file contains any #fuzzy entry (grep is your friend)
* for those eggs in which mo files are included, make sure they are up to date


A note on formatting
--------------------

The script *updatePoWithTranslations.py* uses polib to manipulate ORIG.po. It will format the file in such a way that lines
don't exceed 80 characters but are filled up as much as possible (optimisation). This is contrary to what babel (used in
Euphorie) does. Therefore a `svn diff` will be useless after applying the script. But if you run the update_catalog step
from Euphorie's i18nupdate again, the formatting will be reverted to Euphorie style, and a ``svn diff`` will only show
the actual changes.


