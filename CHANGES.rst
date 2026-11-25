15.1.1 (2026-11-25)
-------------------

Bug fixes:


- Matomo: Emit debug messages instead of errors when Piwik variables loadings fails. @thet (#5293)


15.1.0 (2026-11-25)
-------------------

New features:


- Matomo: Move integration script to own resource.
  This will reduce the payload per page view, as the script can be cached by the
  browser. Also, browsers won't report "unsafe-inline" CSP error. (#5293)


Bug fixes:


- Matomo: Preserve page context while loading tracking dimensions.
  Register navigation tracking before the initial dimensions request and snapshot
  page metadata before fetching.
  Track page views in navigation order, even if the dimensions requests complete
  out of order, and use the previous page as referrer for in-page navigations.
  Retain legacy reporting values. (#5293)
- Respect the `euphorie.personal_details__enabled` registry record.
  @ale-rt (#5429)


15.0.0 (2026-11-09)
-------------------

Breaking changes:


- Support Plone 6.2 and SQLAlchemy 2.1.
  @ale-rt (#5421)


Internal:


- Apply plone.meta.
  @ale-rt
