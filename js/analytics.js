/*
  Analytics integration point.
  No tracking ID is configured yet, so this module is a documented no-op.

  To enable Google Analytics 4:
    1. Set window.ZIDURI_CONFIG.gaMeasurementId in a small inline script
       before this module loads (e.g. "G-XXXXXXXXXX").
    2. This module will load gtag.js and start sending page_view + the
       events tracked via trackEvent() below.

  See ziduri-handbook/16-analytics-and-measurement.md and DEVELOPMENT.md
  ("Analytics integration") for the full rationale and event list.
*/

const config = window.ZIDURI_CONFIG || {};
const measurementId = config.gaMeasurementId || "";

let ready = false;

if (measurementId) {
  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
  document.head.appendChild(script);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag() {
    window.dataLayer.push(arguments);
  };
  window.gtag("js", new Date());
  window.gtag("config", measurementId);
  ready = true;
}

/**
 * Track a product-relevant interaction. No-ops until a measurement ID is
 * configured. Known event names: product_cta_click, store_click,
 * documentation_open, privacy_open.
 */
export function trackEvent(name, params = {}) {
  if (!ready || typeof window.gtag !== "function") return;
  window.gtag("event", name, params);
}
