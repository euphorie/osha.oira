# Snapshot Matomo page context before fetching dimensions

Status: Accepted (2026-11-17)

## Context

The Matomo integration script fetches request-specific
dimensions from `@@piwikvars.json`. Navigation can occur while that request is
pending. Reading the page URL, title or fallback metadata after the fetch can
combine one page's dimensions with another page's context.

Registering the Patternslib navigation listener only after the initial fetch
also misses navigation events during that fetch.

Overlapping dimensions requests can complete out of order. Without ordering,
page B can be recorded before page A after an A-to-B navigation, and a late
response leaves the earlier page's tracker fields active for subsequent link
tracking.

`document.referrer` does not change on in-page (pat-inject) navigation, so
every in-app page view reported the external referrer of the initial load.

## Decision

Register the `patterns-injected-delayed` listener before starting initial page
tracking, retaining the URL-change check to avoid counting unrelated injections.
Capture the page title, cleaned URL, referrer and template fallback dimensions
synchronously before fetching dimensions. The dimensions request also starts
before yielding, so its URL refers to the same page.

After the fetch completes, use its dimensions or the captured fallback. Set all
tracker fields and call `trackPageView` together, without awaiting between those
operations. Keep both Custom Dimensions and legacy Custom Variables for existing
reports, including their distinct historical Activity values.

Keep the Patternslib event rather than switching to `navigatesuccess`. Browser
navigation completion does not inherently wait for Patternslib's content updates;
changing the event would not serialize dimensions requests either.

Serialize the tracker updates with a promise chain. Each page view captures
its context and starts its dimensions request at event time, then appends to
the chain. Requests still run in parallel; only setting the tracker fields and
calling `trackPageView` happens in navigation order. An error in one page view
is caught so it does not block later ones.

Use the cleaned URL of the previously tracked page view as referrer for
in-page navigations. The initial page view keeps `document.referrer`.

## Consequences

- Each page view retains its captured page context when dimensions requests
  succeed or fall back after navigation.
- Navigation during initial dimensions loading can trigger tracking.
- Page views are recorded in navigation order, even if responses complete out
  of order. After the last response, the tracker fields belong to the most
  recently navigated page, so link tracking uses the current page context.
- A slow dimensions request delays the tracking of later page views until it
  completes or fails.
- In-app page views report the previous page as referrer, so Matomo can show
  navigation paths within the tool.
- The fallback snapshot cannot correct metadata already stale in the DOM. The
  `#metadata` element is outside the injected `#content`, so after in-page
  navigations the fallback holds the initially loaded page's values.
- The script is loaded `async`. If a pat-inject navigation happens before it
  runs, the initial page view records the new URL and the first page is not
  tracked. This is accepted as unlikely.
- A Node harness verified, for an A-to-B navigation with B's successful
  response arriving before A's failed one, that A is tracked first with the
  fallback dimensions, B second with its own dimensions and A's URL as
  referrer. This does not validate delivery to live Matomo servers.
