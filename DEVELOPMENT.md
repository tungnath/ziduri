# Developing Ziduri.in

This site is phase 1 of the plan in [`ziduri-handbook/17-migration-and-scalability.md`](ziduri-handbook/17-migration-and-scalability.md): plain HTML/CSS/JS today, Astro if/when reusable templating earns its complexity. Read the handbook before making structural changes — it's the source of truth this site is implementing.

## Local development

No build step, no dependencies. From the repo root:

```bash
python3 -m http.server 4173
```

Open `http://localhost:4173`. Every page is a real `.html` file, so editing and refreshing is the whole workflow.

## Adding a new product

There is no metadata-driven page generator yet (see "Why pages are hand-written" below), so a new product is a new set of hand-written pages that follow the existing pattern:

1. Pick a slug, e.g. `my-new-product`.
2. Create `/products/my-new-product/index.html` — copy `/products/browser-native-notes/index.html` as a starting point and replace every section with real, verified facts about the new product. Keep the same section order (breadcrumb, hero, screenshot/illustration, problem/solution, features, use cases, how it works, installation, permissions if relevant, FAQ, related resources) — see [`ziduri-handbook/08-product-template.md`](ziduri-handbook/08-product-template.md).
3. Create `/privacy/my-new-product/index.html` from `/privacy/browser-native-notes/index.html`, describing that product's actual data handling — never copy another product's privacy claims. See [`ziduri-handbook/09-privacy-policy.md`](ziduri-handbook/09-privacy-policy.md).
4. Add the product to `/privacy/index.html` and `/products/index.html`.
5. Add a card for it to the homepage product grid in `/index.html`.
6. Add its icon/screenshots under `/assets/products/my-new-product/`.
7. Add its URLs to `/sitemap.xml`.
8. Update the footer "Products" list across pages (or leave it pointing at `/products/` only, if the list is getting long).
9. Run `python3 scripts/validate-seo.py` before committing.

Never invent features, permissions, screenshots, store links, or claims — every fact on a product page should be traceable to the product's actual source code or store listing.

## Adding a blog article

The blog has no posts yet by design (see [`ziduri-handbook/10-blog-strategy.md`](ziduri-handbook/10-blog-strategy.md) — quality over volume). To add one:

1. Create `/blog/<article-slug>/index.html`.
2. Use the same `<head>` metadata pattern as other pages: unique title, description, canonical, Open Graph/Twitter tags, and an `Article` + `BreadcrumbList` JSON-LD block (see schema.org's `Article` type for the shape).
3. Wrap the body copy in `<article class="prose">…</article>` inside `<main>` — `.prose` in `css/site.css` styles headings, lists and links for long-form content.
4. Add a card to `/blog/index.html`'s article grid (`.article-grid` / `.article-card`), replacing the empty state once the first post exists.
5. Link to relevant product pages naturally from the body.
6. Add the article URL to `/sitemap.xml`.

## Changing global SEO defaults

- **Site name, default OG image, theme color**: update the repeated `<meta property="og:*">` block and `assets/images/og-default.png` (regenerate with ImageMagick if the brand mark changes).
- **Per-page title/description/canonical**: these live in each page's own `<head>` — there's no central config, so update them page by page.
- **Structured data**: each page has its own JSON-LD `<script>` blocks. Keep them truthful — no fabricated ratings, reviews, prices or claims (see [`ziduri-handbook/06-seo.md`](ziduri-handbook/06-seo.md)).
- **Sitemap**: `/sitemap.xml` is hand-maintained. Add a `<url>` entry for every new indexable page and remove entries for pages you delete.
- Run `python3 scripts/validate-seo.py` after any SEO-related change — it checks every page has one `<title>`, a description, a canonical that's actually listed in the sitemap, exactly one `<h1>`, and no broken internal links.

## Deployment

1. **GitHub Pages**: In the repository's Settings → Pages, set the source to "GitHub Actions." `.github/workflows/deploy.yml` builds nothing (there's no build step) and publishes the repo root via `actions/upload-pages-artifact` + `actions/deploy-pages` on every push to `main`, after `.github/workflows/validate.yml` passes.
2. **Custom domain (`ziduri.in`)**: The `CNAME` file at the repo root already declares `ziduri.in`. You still need to, outside this repo:
   - Add the DNS records GitHub currently documents for apex + `www` custom domains (A/AAAA records for the apex, or a CNAME for a `www` subdomain — check GitHub's current docs, since these IPs can change).
   - Enable "Enforce HTTPS" in the repository's Pages settings once DNS has propagated and GitHub has issued a certificate.
3. **Search Console / Bing Webmaster Tools**: verify `ziduri.in`, submit `https://ziduri.in/sitemap.xml`, and request indexing for new pages after they go live. This is a manual, one-time setup step per property.

## Analytics integration

`js/analytics.js` is a documented no-op until configured — no tracking ID is hard-coded anywhere in the repo. To enable Google Analytics 4:

1. Create a GA4 property and get its Measurement ID (`G-XXXXXXXXXX`).
2. Add an inline script before `js/analytics.js` loads, e.g. in each page's `<head>` or right before the `<script type="module" src="/js/app.js">` tag:
   ```html
   <script>window.ZIDURI_CONFIG = { gaMeasurementId: "G-XXXXXXXXXX" };</script>
   ```
3. `analytics.js` will then load `gtag.js` and start sending page views. Use the exported `trackEvent(name, params)` helper for product interactions — `[data-track]` attributes on any element (see the product page's CTA and doc links) automatically fire an event with that name via `js/app.js`.

Known event names in use: `product_cta_click`, `store_click`, `documentation_open`, `privacy_open`. See [`ziduri-handbook/16-analytics-and-measurement.md`](ziduri-handbook/16-analytics-and-measurement.md) for the measurement strategy this supports.

## Theme system

- `css/tokens.css` defines the full color/typography/spacing/motion token set on `:root`, with a dark palette applied two ways: automatically via `prefers-color-scheme`, and explicitly via `[data-theme="dark"]`/`[data-theme="light"]` on `<html>`.
- Every page has a tiny inline script in `<head>` (before the stylesheets finish loading) that reads `localStorage["ziduri-theme"]` and sets `data-theme` immediately, to avoid a flash of the wrong theme.
- `js/theme.js` wires the header's theme toggle button, persisting the user's explicit choice to `localStorage`.
- To restyle a component for dark mode specifically, prefer adjusting the token values in `tokens.css` over writing component-level dark-mode overrides.

## Why pages are hand-written (for now)

Per [`ziduri-handbook/05-frontend-architecture.md`](ziduri-handbook/05-frontend-architecture.md), phase 1 deliberately avoids a framework or build step, and SEO-critical content must exist in crawlable HTML in the deployed output — so header/nav/footer are duplicated across pages rather than injected client-side. This is a known, accepted tradeoff: when adding products and articles becomes repetitive enough to justify the complexity, migrate to Astro (content collections, layouts) while preserving every public URL — see [`ziduri-handbook/17-migration-and-scalability.md`](ziduri-handbook/17-migration-and-scalability.md).

## Validation checklist before shipping a change

- `python3 scripts/validate-seo.py` passes.
- New/changed pages keep the same header/footer markup pattern as existing pages.
- No fabricated product claims, reviews, ratings, prices, team/company facts, or privacy claims.
- Images have descriptive `alt` text (or `alt=""` for purely decorative images).
- Tab through the page with a keyboard — focus should be visible and in a logical order.
- Check both themes (`prefers-color-scheme` and the manual toggle).
- Resize to a narrow viewport and confirm the mobile nav and layout hold up.
