# Matomo integration script as a cache-busted Zope resource

Status: Accepted (2026-11-14)

## Context

OiRA (`oira.osha.europa.eu`) and the DSE tool (`eguides.osha.europa.eu`),
plus their staging sites, report page views to EU-OSHA's Matomo servers:
the old Matomo 3 instance and, in parallel, the new Matomo 5 instance until
the old one is retired.

The tracking code was a ~260 line inline `<script>` pasted by hand into the
`plone.webstats_js` registry record. The reference copy lived in
`matomo/matomo-tracking.html` in this repository and had to be copied into
each site's control panel after every change. Euphorie renders the record
in the client shell (`shell.pt`, `shell_bare.pt`) through the `webstats_js`
macro, which calls `webhelpers/get_webstats_js`.

Problems with this setup:

- **CSP:** an inline script requires `'unsafe-inline'` in the
  Content-Security-Policy, and browsers report violations for it.
- **Payload:** the full script is sent with every HTML page and cannot be
  cached separately.
- **Drift:** the code that runs is whatever someone last pasted into each
  site. It is not versioned with the package and not covered by tests.

## Decision

### 1. Ship the script as a file in osha.oira

The script lives in `src/osha/oira/client/resources/matomo-integration.js`
and is served by the existing `osha.oira.client` resource directory
(`browser:resourceDirectory` in `client/configure.zcml`), as
`++resource++osha.oira.client/matomo-integration.js`. Its logic is
unchanged from the inline version; it was only reformatted and given a
header comment.

### 2. Inject it from `OSHAWebHelpers.get_webstats_js`

`osha.oira.client.browser.webhelpers.OSHAWebHelpers` overrides
`get_webstats_js`. It returns the `plone.webstats_js` registry value (empty
string if `None`), followed by:

```html
<script async src="{portal_url}/++webresource++{key}/++resource++osha.oira.client/matomo-integration.js"></script>
```

The registry record stays usable for other, site-specific snippets.
`async` doesn't change behaviour: the script never relied on running at a
fixed point in the page.

### 3. Cache busting with Plone's `++webresource++` URL convention

`{key}` is `++webresource++` plus the first 16 hex digits of the SHA-256 of
the file content. It is computed once per process (`functools.cache` on
`_matomo_unique_key`).

This reuses the mechanism Plone 6 uses for its resource registry bundles
(verified against Products.CMFPlone 6.2.3, plone.resource 4.0.0,
webresource 2.0.1):

- CMFPlone registers `plone.resource.traversal.UniqueResourceTraverser` as
  the `++webresource++` namespace traverser for any object
  (`Products/CMFPlone/resources/browser/configure.zcml`). It ignores the
  hash segment, returns the object it was called on and marks the request
  with `IUniqueResourceRequest`.
- plone.resource's `UniqueResourceLookup` assigns marked requests the
  `plone.stableResource` caching ruleset (strong caching, 1 year max-age in
  plone.app.caching's caching profiles), instead of the 24h
  `plone.resource` ruleset that plain `++resource++` URLs get.

So the browser may cache the script for a year, and a changed file gets a
new URL with the next release.

Alternatives considered:

- **A `plone.resource` (`++plone++`) directory instead of
  `browser:resourceDirectory`.** It gets the same caching ruleset and
  doesn't add cache busting either. Its extra feature, overriding files in
  the ZODB via `portal_resources`, would bring back the editing on live
  sites that this decision removes.
- **A resource registry bundle.** Plone adds the hashed URL automatically
  for bundles, but the Euphorie client shell doesn't render Plone's
  resource viewlets, so a bundle would never be included.
- **Rendering a `PloneScriptResource(unique=True)`.** It produces the same
  URL shape, but re-traverses and re-hashes the file on every request.
- **A manual `?v=` query parameter.** It works, but only if someone
  remembers to bump it.
- **A Subresource Integrity (`integrity`) attribute.** Rejected: little gain
  for a same-origin script, and any proxy that rewrites the response
  would block it.

### 4. Empty the registry record with an upgrade step

The upgrade step `v14/v20261113130244_update_matomo_script` imports a
`registry.xml` that sets `plone.webstats_js` to an empty value, removing
the pasted inline copy. The obsolete `matomo/matomo-tracking.html` and its
`prune matomo` line in `MANIFEST.in` are removed.

## Consequences

- No inline Matomo script on client pages, so it needs no `'unsafe-inline'`
  exception in the CSP. The script is downloaded once and cached.
- The tracking code is versioned and released with osha.oira. Changes to
  site IDs, tracker endpoints or tracking logic now need a release instead
  of a control panel edit.
- **Deploy and upgrade together.** New code with the old registry value
  loads the script twice, so every page view is counted twice in both
  Matomo instances. Running the upgrade with old code removes tracking
  entirely. The upgrade overwrites the whole record, so anything else in
  it is lost. Check the record on the production and staging sites before
  upgrading.
- The URL depends on CMFPlone's `++webresource++` traverser. Every Plone 6
  bundle URL uses it, so it is unlikely to go away without notice.
- The 1-year caching only applies where a plone.app.caching profile is
  active. Without it, browsers fall back to heuristic caching based on
  Last-Modified; the changing URL still busts that cache.
- In development, the hash only changes after a Zope restart.
- `src/osha/oira/client/tests/test_webhelpers.py` checks that the file
  exists, that the rendered tag has the expected URL, that the registry
  value is kept, and that the rendered URL serves the file content.

## Open issues

- The two site ID maps (`tracking_url_map`, `tracking_url_map_matomo5`) are
  identical, and custom dimension 1 has a leading `-` that custom variable 1
  doesn't. Both were carried over unchanged. Revisit when the Matomo 3
  tracker is retired, which also removes the second tracker setup.

## Changes

- osha.oira, branch `thet/5495/matomo-static`: 33b46fa3.
