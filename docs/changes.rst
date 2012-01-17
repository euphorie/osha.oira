Changelog
=========

1.2 (Unreleased)
----------------

1.1 (2012-12-17)
----------------
- #3813: Also show children of optional modules in the downloadable report. [jcbrand]
- #3536: Updated the en translations file. [jcbrand]
- AttributeError bugfix on the report.pt view. [jcbrand]

1.0 (2012-12-13)
----------------

- #3813 Adjust the Content of tools feature to display ALL risks [jcbrand]    
- #3811 "Measure" text on accordion not translated. [jcbrand] 
- #3792 Provide route back to Identification phase from the identification report. [jcbrand]
- #3779 Privacy not working on client and community sites [jcbrand]
- #3892 Exchange the OiRA logo in the admin part [jcbrand] 
- #4071 Integrate Wichert's changes in to osha.oira [jcbrand]

0.24 (2011-10-07)
-----------------
- 3805: Added Slovenian translations. [thomas_w]

0.23 (2011-09-27)
-----------------

- 3520: Add upgrade step to renew the 'published' date of all client surveys. [jcbrand]
- 3797: Renamed travailleurs to salaríes and statut to avancement. [jcbrand]
- Removed the bugfix for 2583, since a more proper bugfix is now in Euphorie [jcbrand]
- Language changes for 3414 and 3515 [jcbrand]
- Czech translations [thomas_w]

0.22 (2011-09-05)
-----------------

- 3414: Bugfix on _actionplan_ landing page. Add i18n var. [jcbrand]
- Add DE, EL, SK translations [thomas_w]
- Add title attrs on clicktips for IE6/7 [jcbrand]
- Changed headers for mobile compatibility [jcbrand]
- Lots of browser fixes [jcbrand]

0.21 (2011-08-26)
-----------------

- NB: Depends on Euphorie 3.0syslab19 or higher

- Refactored @@delete on sector view back to Euphorie. [jcbrand]
- Depend on zrtresource screen-ie6. [jcbrand]
- More tests and bugfixes [jcbrand]
- Move the surveypopup code to survey_popup.js (disabled for now) [jcbrand]

0.20 (2011-08-23)
-----------------

- Updated Spanish translations [thomas_w]
- IE 6 fix. Remove the tooltips in AJAX add measure form. [jcbrand] 
- Stop using minified css for IE6. [jcbrand]

0.19 (2011-08-16)
-----------------

- Updated French translations [jcbrand]

0.18 (2011-08-15)
-----------------

- #3044 Last wave of English changes [jcbrand]
- #3049 Design fixes [jcbrand]
- #3343 Customize InfoBubble description according to calculation method [jcbrand]
- #3361 Correct position of an info bubble [jcbrand]
- #3365 Add favicon [jcbrand]  
- #3386: Rename "Next" and "Continue" buttons to "Save and continue" when on forms. [jcbrand]

0.17 (2011-07-02)
-----------------

- Bugfix, when populating Prevention Plan with standard solution [jcbrand]

0.16 (2011-07-01)
-----------------

- #1537 Merged changes from Euphorie. 
        Use radio buttons instead of dropdown
        Add a new InfoBubble on the OiRA tool add page.
        Make fields required to remove "No Value" option. [jcbrand]
- #2510 Merged changes from Euphorie into osha.oira [jcbrand]
- #3002 Found and fixed some more instances where survey is being used [jcbrand]
- #3048 Updated the translations [jcbrand]
- #3323 Add custom start page with new text and merge old patch into this template [jcbrand]
- #2510 Add js to animate the measures button/link


0.15 (2011-05-31)
-----------------

- #2223 Add the FancyBox to the module evaluation page [jcbrand]


0.14 (2011-05-30)
-----------------

- #3044 New English copy [jcbrand]
- #3281 Fix is_region AttributeError when copying countries to the client [jcbrand]
- #3048 More translation updates

0.13 (2011-05-26)
-----------------

- #2223 Add FancyBox image zoom to module images [jcbrand]
- #3260 Make European Flag visible on the client homepage. [jcbrand]
- #3277 Stale quote [pilz]
- #3221 Priority gone for FR [jcbrand]
- #3048 Add more translations [jcbrand]
- #3265 Hide empty modules on final report [jcbrand]
- #2560 Info bubbles for statistics fields [jcbrand]


0.12 (2011-05-05)
-----------------

- Restructure package to faciliate automated tested. 
- #2556 Backported the frontpage fixes from Cornelis. [jcbrand]
- #2754 Modules should be movable before profile questions. [jcbrand]
- #2611 Changed headings in the final report [jcbrand]
- #2885 Risks that are not evaluated but do have action plans must be shown as
  finalised. [jcbrand]


0.11 (2011-04-12)
-----------------

- #2611 The identification report should also have page numbers in the bottom
        right and the download date in the top right of each page. [jcbrand]
- #2885 Parked risks must also be shown affirmatively [jcbrand]


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

