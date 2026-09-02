# Ziduri.in

The source for [ziduri.in](https://ziduri.in) — a static site built with plain HTML5, CSS3 and vanilla JavaScript, deployed on GitHub Pages.

Ziduri is a product studio building lightweight, dependable productivity software. See [`ziduri-handbook/`](ziduri-handbook/) for the architecture, design, SEO and privacy handbook this site is built from.

## Quick start

No build step. Serve the repo root with any static file server:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

## Structure

```
/                              homepage
/products/                     product catalog
/products/<slug>/              product landing page
/products/<slug>/docs/         product documentation
/products/<slug>/changelog/    product release notes
/privacy/                      privacy policy index
/privacy/<slug>/               per-product privacy policy
/blog/                         blog index
/about/                        about page
/contact/                      contact page
/css/tokens.css                design tokens (colors, type, spacing, motion)
/css/site.css                  components and layout
/js/                           theme toggle, mobile nav, analytics stub
/assets/                       images, icons, per-product assets
/scripts/validate-seo.py       CI validation (SEO metadata + internal links)
```

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for how to add a product, add a blog article, and change site-wide defaults.

## Deployment

Pushes to `main` run [`.github/workflows/validate.yml`](.github/workflows/validate.yml) (SEO metadata, JSON-LD, HTML validity, broken links) and then [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) publishes to GitHub Pages. See `DEVELOPMENT.md` for the manual GitHub/DNS setup this still requires.
