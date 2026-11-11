# QA checklist

Mark an item only when actually executed; record date, tool/device and result in the right column. Blank = not run. `[x]` = run and passed as described; `[~]` = partly run (what was not run is written out). Full results: `docs/QA_REPORT_2026-10-30.md`.

## Visual
- [x] Brand colors exact (`#263A5A`, `#E2D9CF`) — **static scan 2026-10-30: only the 7 palette hex values exist**; "navy not dominant" not reviewed visually
- [x] No gradients, gold, heavy shadows, floating widgets — **static scan 2026-10-30: none; fixed elements are the sticky bars only**
- [x] Placeholder imagery labelled; no placeholder passes as product — **2026-10-30: every empty image is a sand panel labelled "Image to come"**
- [ ] Type scale, tracking, label style consistent across pages
- [ ] Creative Director audit of each template

## Responsive (320, 375, 768, 1024, 1440)
- [x] No horizontal scroll — **2026-10-30, in-app browser: 0 overflow on home, collection, product at 351/375/768/1024/1440; bag, About, The Edit at 375/1440; story, search, 404, collections list at 375. 320px not reachable in the pane (min about 351)**
- [~] Mobile menu, filters drawer, variant selector run 2026-10-30 (steps 1 to 4); gallery swipe with real images **not run**
- [x] Tap targets ≥ 44px — **2026-10-30 script check, 0 undersized on the pages and widths above**

## Functional
- [~] Variant matrix **run 2026-10-30 on test data** (ready, sold out, made to order, mixed; price, label, delivery, button, URL); per-variant image **not run**
- [~] Made-to-order shows no stock count; sold-out variant returned 422 from `/cart/add.js` (**2026-10-30**); overselling with real tracked stock **not run**
- [~] Cart **run 2026-10-30**: add, change qty, remove, mixed choice, `delivery_preference` saved on the cart, line properties present; "on the order" **not run** (no order placed)
- [ ] Deposit flow: manual payment order created, reference shown, proof upload reaches staff, order can be marked paid, lapse after hold time
- [~] Filters and sort **run 2026-10-30** (6 filters, combinations, live counts); smart collections Ready/Made to Order **not created or run**; open defect QA-04
- [~] Search and 404 **run 2026-10-30** (templates built after QA-01); account (Shopify-hosted, 302) and newsletter submit **not run**

## Commerce
- [ ] Checkout completes with the chosen gateway in test mode
- [ ] EGP formatting; taxes/shipping as configured
- [ ] Deposit flow (if adopted) works end to end
- [ ] Order shows made-to-order data to fulfilment staff

## Accessibility
- [ ] Keyboard-only pass, visible focus, skip link
- [ ] Screen-reader pass of nav, gallery, variant changes (live region)
- [x] Contrast — **Lighthouse accessibility 100 on 8 rendered templates, 2026-10-30** (local proxy, mobile mode)
- [~] `prefers-reduced-motion` — rule present in `base.css` (static); **not emulated**

## Performance & SEO
- [~] Lighthouse run 2026-10-30 on 8 templates (performance 98 to 100 in the last run, 71 to 98 in earlier runs; proxy and Shopify scripts make it unreliable); **CrUX/INP and live HTTPS not run**
- [ ] Image sizes and formats; font loading
- [~] Product and story JSON-LD parse and carry expected types; titles, canonical, noindex checked on every template type (**2026-10-30**); Rich Results test and sitemap **not run**; meta descriptions missing (QA-06)

## Theme editor
- [ ] Every section has sensible settings, presets, empty states; reorder works

## Launch
- [x] No active product carries `placeholder-data`, 9999.00 or "[PLACEHOLDER]": **passes 11 Nov 2026** (read via Admin API: 50 products, 0 active, 0 `[TEST]`). Re-run on launch day: it fails again if any product is activated with placeholders still in.
- [ ] PP Mori web licence held and receipt filed (blocks any public publish, D-013)
- [ ] Rollback plan documented (previous theme kept unpublished)
- [ ] Founder launch approval

## Defect report format
`ID · severity (blocker/major/minor) · page · steps · expected · actual · evidence · suggested fix`
