import { initThemeToggle } from "./theme.js";
import { initMobileNav } from "./nav.js";
import { trackEvent } from "./analytics.js";

initThemeToggle(document.querySelector("[data-theme-toggle]"));
initMobileNav(document.querySelector("[data-nav-toggle]"), document.querySelector("[data-nav-primary]"));

document.querySelectorAll("[data-track]").forEach((el) => {
  el.addEventListener("click", () => {
    trackEvent(el.getAttribute("data-track"), {
      label: el.getAttribute("data-track-label") || el.textContent.trim(),
    });
  });
});
