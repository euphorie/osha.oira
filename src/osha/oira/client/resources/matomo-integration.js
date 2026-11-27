// Matomo integration script
//
// This script is used for oira and dsetool (eguides) for staging and
// production.
// Reports to a Matomo 3 + 5 server until the old one is retired.
//
// Version 2.0
var _paq = (window._paq = window._paq || []);

(async function () {
  const tracking_url_map = {
    // hostname : site id
    // production
    "oira.osha.europa.eu": "9",
    // DSE production
    "eguides.osha.europa.eu": "25",
    // staging
    "test-oira.osha.europa.eu": "11",
    // dse staging
    "test-eguides.osha.europa.eu": "11",
    // development
    localhost: "11",
  };

  const tracking_url_map_matomo5 = {
    // hostname : site id
    // production
    "oira.osha.europa.eu": "9",
    // DSE production
    "eguides.osha.europa.eu": "25",
    // staging
    "test-oira.osha.europa.eu": "11",
    // dse staging
    "test-eguides.osha.europa.eu": "11",
    // development
    localhost: "11",
  };

  const site_id = tracking_url_map[window.location.hostname];
  const site_id_matomo5 = tracking_url_map_matomo5[window.location.hostname];

  if (!site_id) {
    // unconfigured URL. ignore and return.
    console.warn("Matomo: no site_id found - exiting.");
    return;
  }
  console.debug("Matomo: site_id", site_id);

  const is_development = window.location.hostname === "localhost";

  const tracking_script_url = "https://piwik.osha.europa.eu/piwik/matomo.js";

  const tracking_endpoint_url = "https://piwik.osha.europa.eu/piwik/matomo.php";
  const tracking_endpoint_url_matomo5 =
    "https://webstats.osha.europa.eu/matomo.php";
  const tracking_endpoint_url_development =
    "http://localhost:8080/Plone/piwikmock.php";

  const download_path_pattern =
    /(?:@@pdf|@@timeline|\.(?:docx|xlsx|pptx|pdf|gif|jpe?g|png|zip))$/i;

  /**
   * Clean a URL by removing the session id.
   */
  function clean_url(url) {
    // Remove the session id from the URL
    const tracked_url = url.replace(/\+\+session\+\+.*\//, "");
    return tracked_url;
  }

  function is_download_link(link) {
    if (link.matches("a.pat-button.download")) {
      return true;
    }
    try {
      return download_path_pattern.test(
        new URL(link.href, window.location.href).pathname,
      );
    } catch (error) {
      return false;
    }
  }

  function is_outbound_link(link) {
    try {
      const url = new URL(link.href, window.location.href);
      return (
        ["http:", "https:"].includes(url.protocol) &&
        url.origin !== window.location.origin
      );
    } catch (error) {
      return false;
    }
  }

  /**
   * Initialize download buttons tracking without the session id.
   * This uses delegated event handlers which also allows to track links
   * injected dynamically by JavaScript after this script was invoked.
   */
  function initialize_link_tracking() {
    // We do our own link tracking.
    //_paq.push(["enableLinkTracking"]);

    // Delegated event handler - this also tracks content which is injected
    // after the initial page load.
    document.addEventListener(
      "click",
      function (event) {
        const el = event.target.closest("a");
        if (!el) {
          // No link was clicked
          return;
        }

        let link_type;
        if (is_download_link(el)) {
          // Download URL
          link_type = "download";
        } else if (is_outbound_link(el)) {
          // Outbound URL
          link_type = "link";
        } else {
          // Not a tracked link
          return;
        }

        // Trigger tracking.
        _paq.push(["trackLink", clean_url(el.href), link_type]);
      },
      { capture: true },
    );
  }

  async function load_tracking_dimensions() {
    try {
      const url_elems = window.location.href.split("?");
      const urlParts = url_elems[0].split("/");
      if (urlParts[urlParts.length - 1] === "") {
        urlParts.pop(); // Remove trailing slash if present
      }
      urlParts[urlParts.length - 1] = "@@piwikvars.json";
      let vars_url = urlParts.join("/");
      if (url_elems.length > 1) {
        vars_url = vars_url + "?" + url_elems[1];
      }

      const response = await fetch(vars_url, {
        headers: { Accept: "application/json" },
      });
      if (!response.ok) {
        throw new Error("HTTP " + response.status);
      }

      // Get the response and parse as JSON, but first check, if the response is
      // empty.
      const body = await response.text();
      if (!body.trim()) {
        return null;
      }
      const data = JSON.parse(body);

      console.debug("Matomo: 📌 Loaded Piwik Variables:", data);
      return data;
    } catch (error) {
      console.debug("Matomo: ❌ Error loading Piwik variables:", error);
      return null;
    }
  }

  // Serializes the tracker updates, so that page views are recorded in
  // navigation order even if the dimensions requests complete out of order.
  let tracking_chain = Promise.resolve();

  // The URL of the last tracked page view. It is used as referrer for
  // in-page navigations, where `document.referrer` does not change.
  let last_tracked_url = null;

  function track_page_view() {
    console.debug("Matomo: Tracking triggered.");

    // Capture the page context synchronously, before anything is awaited.
    // Navigation can happen while the dimensions are loading.
    const url = clean_url(window.location.href);
    const context = {
      document_title: `${document.domain}/${document.title}`,
      url: url,
      referrer_url: last_tracked_url ?? clean_url(document.referrer),
      // Fall back to tracking dimensions from the template.
      // NOTE: The #metadata element is outside of the injected #content, so
      // after in-page navigations these values are those of the initially
      // loaded page.
      // TODO: this code can probably be removed when scrum-3351 is rolled-out.
      fallback_dimensions: {
        country_name: get_template_value("country_name"),
        sector_name: get_template_value("sector_name"),
        tool_name: get_template_value("tool_name"),
        language_code: get_template_value("language_code"),
      },
    };
    last_tracked_url = url;

    // Start the request now, so that it refers to the captured page.
    const dimensions_request = load_tracking_dimensions();

    // Wait for previous page views to be tracked before tracking this one.
    tracking_chain = tracking_chain
      .then(() => dimensions_request)
      .then((tracking_dimensions) =>
        push_page_view(context, tracking_dimensions),
      )
      .catch((error) => {
        console.error("Matomo: ❌ Error tracking page view:", error);
      });
    return tracking_chain;
  }

  function get_template_value(id) {
    return document.getElementById(id)?.textContent?.trim() || "";
  }

  function push_page_view(context, tracking_dimensions) {
    if (!tracking_dimensions) {
      console.debug(
        "Matomo: No Piwik data loaded, using template values for tracking.",
      );
      tracking_dimensions = context.fallback_dimensions;
    }

    const activity = "-3.1. Online interactive Risk Assessment (OiRA) tool";
    const activity_var = "3.1. Online interactive Risk Assessment (OiRA) tool";
    const country = tracking_dimensions.country_name;
    const sector = tracking_dimensions.sector_name;
    const tool = tracking_dimensions.tool_name;
    const language = tracking_dimensions.language_code;

    // Set all tracker fields and track the page view without awaiting in
    // between, so that no other page view can interfere.
    _paq.push(["setDocumentTitle", context.document_title]);
    _paq.push(["setCustomUrl", context.url]);
    _paq.push(["setReferrerUrl", context.referrer_url]);
    _paq.push(["setCustomDimension", 1, activity]);
    _paq.push(["setCustomDimension", 2, country]);
    _paq.push(["setCustomDimension", 3, sector]);
    _paq.push(["setCustomDimension", 4, tool]);
    _paq.push(["setCustomDimension", 5, language]);

    // Custom variables
    // These are kept for compatibility with existing Matomo reports.
    _paq.push(["setCustomVariable", 1, "Activity", activity_var, "visit"]);
    _paq.push(["setCustomVariable", 2, "Country", country, "visit"]);
    _paq.push(["setCustomVariable", 3, "Sector", sector, "visit"]);
    _paq.push(["setCustomVariable", 4, "Tool", tool, "visit"]);

    // Queue or invoke (if tracking script is already loaded) the tracking request
    _paq.push(["trackPageView"]);
    console.debug("Matomo: ✅ Page view tracked:", context.url);
  }

  function base_tracking_initialization() {
    // Main Matomo variables

    if (is_development) {
      // Development
      _paq.push(["setTrackerUrl", tracking_endpoint_url_development]);
      _paq.push(["setSiteId", site_id]);
    } else {
      // Production

      // Default Matomo (Currently 3)
      _paq.push(["setTrackerUrl", tracking_endpoint_url]);
      _paq.push(["setSiteId", site_id]);

      // Matomo 5 testing tracker
      _paq.push(["addTracker", tracking_endpoint_url_matomo5, site_id_matomo5]);
    }

    // Link tracking is handled below so that dynamically injected links
    // and the custom URL cleanup follow the same code path.

    // Create tracking script element
    const tracking_script = document.createElement("script");
    tracking_script.type = "text/javascript";
    tracking_script.async = true;
    tracking_script.src = tracking_script_url;

    // Add the tracking script to the page
    const sibling = document.getElementsByTagName("script")[0];
    sibling.parentNode.insertBefore(tracking_script, sibling);
  }

  // Initialize download buttons tracking
  initialize_link_tracking();
  // Load the tracker in parallel with the dimensions request.
  // The page view still waits for dimensions or the template fallback.
  base_tracking_initialization();

  // Register the navigation handler before tracking the initial page view, so
  // that navigation during the initial dimensions request is tracked too.
  let previous_url = location.href;
  document.addEventListener("patterns-injected-delayed", function () {
    // Track page injections with history changes.
    if (previous_url !== location.href) {
      console.debug("Matomo: pat-inject triggered tracking.");
      // Only track if the URL has changed
      previous_url = location.href;
      track_page_view();
    }
  });

  // Track the initial page view.
  await track_page_view();
})();
