# Snapshot Matomo page context before fetching dimensions

Status: Accepted (2026-11-17)

## Context

The Matomo integration script fetches request-specific
dimensions from `@@piwikvars.json`. Navigation can occur while that request is
pending. Reading the page URL, title or fallback metadata after the fetch can
combine one page's dimensions with another page's context.

Registering the Patternslib navigation listener only after the initial fetch
also misses navigation events during that fetch.

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

Accept the remaining overlapping-request ordering edge case rather than adding
a tracking queue in this change.

## Consequences

- Each page view retains its captured page context when dimensions requests
  succeed or fall back after navigation.
- Navigation during initial dimensions loading can trigger tracking.
- Responses can still complete out of order, recording B before A after an
  A-to-B navigation. A late response can leave an earlier page's tracker fields
  active for subsequent link tracking. This is an accepted limitation; a future
  queue must capture page context at event time, not when queued work starts.
- The fallback snapshot cannot correct metadata already stale in the DOM.
- A Node harness verified URL/tool pairing for successful and failed fetches
  resolved in reverse order, and reproduced the accepted ordering limitation.
  This does not validate delivery to live Matomo servers.
