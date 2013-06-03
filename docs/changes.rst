Changelog
=========

2.2.3 (unreleased)
------------------

- Nothing changed yet.


2.2.2 (2013-06-03)
------------------

Upgrade notes
~~~~~~~~~~~~~

This release updates the profile version to *7*. Please use the upgrade feature
in ``portal_setup`` to upgrade the ``osha.oira:default`` profile to this
version.

Bugfixes
~~~~~~~~

- Bugfix. Adding a second measure causes server error. 

Feature changes
~~~~~~~~~~~~~~~

- Make XLS headings bold and space columns so that headings don't wrap.
- Add another column in the action plan XLS file for the top-level profile
  question or module #7322 [jcbrand]
- Dropped support for IE8 and enable browser detection to warn users. #7368 [jcbrand]
- New translations for EL, LV #7511 [jcbrand]
- Improvement in dropdown in the survey page #7050 [jcbrand]
- Added IOSHASurvey behavior with externl site link fields, refs #5880 [reinhardt]

*For older changes, please refer to ./docs/older_changes.rst*
