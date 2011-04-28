Changelog
=========

0.12 (unreleased)
-----------------

- Restructure package to faciliate automated tested.


0.11 (2011-04-12)
-----------------

- #2611 The identification report should also have page numbers in the bottom
        right and the download date in the top right of each page.
- #2885 Parked risks must also be shown affirmatively


0.10 (2011-04-11)
-----------------

- #2560 Added a new schema field on the Sector obj, statistics_level.
- #2699 Headers of the Legal boxes and also the risk headings in the evaluation
        and identification reports must be in lower case for Greek. 
- #2924 OiRA tools with policy risks that have been actioned, should not
        appear in the "Risks that have NOT been evaluated and do NOT have action
        plans", but instead in the top section.
- #2964 Make sure that the logo is visible on the last report page
- #2611 Lots of changes to the final download report 
- #3002 the word "survey" should not be used anymore
- #2989 Final HTML report headers were dodgy in IE7
- #2914 The Hairdressers in Cyprus tool must be shown when viewing the Swedish sector in English
- #2885 String at the bottom of the final report changed.
        Risks that have been identified as not present should be stated affirmatively. 
        Risks must have their priorities indicated (if set)
- #2560 Added admin-edit form and statistics level field on sectors
- #2752 Fixed default color for published surveys
- #2623 Empty legal boxes should not be displayed.

0.9 (2011-03-10)
----------------

- Two bugfixes (for which there aren't any ticket numbers).
  Both are related to the same problem of bullets sometimes being deeper than 4
  levels in the download forms.
  [jcbrand]


0.8 (2011-03-10)
----------------

- Just a version bump. [jcbrand]


0.7 (2011-03-10)
----------------

- #2367 and #2752: Fixed various color picker problems.
- #2750: OiRA client - Change text [jcbrand]
- #2591: Change text on the company form page [jcbrand]
- #2707: OiRA, client - change text above profile questions [jcbrand]


0.6 (2011-03-04)
----------------

- Merged new translation strings and default values to the .po files. [jcbrand]
- Bugfix in touch_surveys.py external-method. [jcbrand]
- #2649: Use portal_properties to store the survey urls. Fallback to English if
  none found. [jcbrand]


0.5 (2011-03-03)
----------------

- Just a version bump. [jcbrand]


0.4 (2011-03-03)
----------------

- #2649: We will now follow the convention that the different SurveyMonkey language
  URLs will be the base url (English version) plus _de, _nl, etc.
  [jcbrand]
- #2681: Remove header capitalization for Greek language. [jcbrand]
- #2555: The footer for the "contents of tool" .rtf document was changed. Also
  removed the "this risk must still be inventorised statement". [jcbrand]
- #2583: Problem in the sessions after updating and republishing [jcbrand]


0.3 (2011-02-23)
----------------

- during the xml import, langauge values might still include trailing and leading spaces. 
  For the frontpage langauge detection, we need to strip them.
  [pilz]
- Bugfix for identification download report generation. [jcbrand]


0.2 (2011-02-23)
----------------

- (Hopefully) Resolves: #1433 #2231 #2293 #2555 #2556 #2621 #2623 #2649
  [jcbrand]


0.1 (2011-01-26)
----------------

* Initial release

