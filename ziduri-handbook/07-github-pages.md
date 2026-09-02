# 07 — Hosting and Deployment
Default static hosting: GitHub Pages.
Primary domain: ziduri.in.

Choose one canonical host (root or www), redirect the alternate host and enforce HTTPS.

Configure DNS using the GitHub Pages records documented by GitHub at implementation time; do not hard-code potentially outdated infrastructure values into project documentation.

Repository should contain CNAME with the canonical hostname.

Use GitHub Actions for validation and deployment where practical. Pull requests should validate HTML, links and basic accessibility; main should deploy automatically.
