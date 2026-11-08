# objekt launch status

Launch Fri 20 Nov 2026. Content freeze Thu 12 Nov. Founder approval Thu 19 Nov.

Three daily sessions work on this repo, one section each. Each session updates **only its own section** (date it, newest first, keep the last 3 entries) and the shared decision list. Sabry answers decisions in one line.

## Decisions needed from Sabry
<!-- one line each: [workstream] question · options · recommendation. Remove when answered. -->
- [content] Day-1 list: approve the 41 in `plan/day1-product-list.md` (plan 46 minus sofa OBJ-012, with OBJ-015, 049, 148, 159 on hold)? · yes / edit · rec: yes.
- [content] Freeze is Thu 12 Nov and only ~10 products have a drawing or prototype · (a) all 41 go live, the rest as 'coming soon' drafts later (b) launch only products with real data by 12 Nov, add the rest weekly (c) move the date · rec: (b).
- [content] OBJ-148 and OBJ-159 references are named third-party products (Mosha Home tray; jeremylechatelier Hublot shelf) · redesign as our own / drop · rec: drop for day 1.
- [content] 15 store drafts not on the plan (OBJ-035, 039, 052, 074, 086, 090, 093, 107, 112, 141, 146, 150, 168, 170, 174) · archive / keep as drafts · rec: keep as drafts, never activate; website session archives only on your yes.
- [content] May AI renders go on the public site as product images until photos exist?
- [website] Reconnect the Shopify connector in this account (store hs1a1c-ut, OBJEKT).
- [website] Sign in to Paymob so test mode can be set up.
- [website] Fill sections 5, 6 and 8 of CONTENT_TO_SUPPLY.md (delivery, returns, payment, policies) before the 12 Nov freeze, or say which may stay out at launch.
- [all] Licences: PP Mori (web), Galak Round, logo lettering (Raftwork). No public launch without them.

## Content and product list

### Sun 8 Nov 2026
- First run. Read the plan (46), the production book (45), the product sheet (stale, 5 Oct flags = the 49 store drafts), the import template (18) and the workspace export. Store not re-read (no Shopify access in this run).
- Wrote `plan/day1-product-list.md`: one table of all 61 OBJ ids across the sources with category, type, process, drawing, images and in/out. Recommendation: 41 in, 4 on hold, 16 out.
- Added section 3d to `website/docs/CONTENT_TO_SUPPLY.md`: recorded category, process (marked guess), colours, proposed finish, drawing and image status for the 45 in/hold products, plus who must answer (Sabry / Polycraft). Titles, prices, sizes, lead times, materials and copy left blank.
- No product copy drafted: Sabry has not approved copy in this file.
- Next: once the list is approved, a per-product gap list for the products that can make the 12 Nov freeze; check OBJ-166 heights (850 vs 700 mm conflict).

## Drawings and files

## Website (Shopify)
### 8 Nov 2026 (Sun)
- Ran: repo pulled (up to date at b5ef657); `npm ci` in website/tools; `theme check` 48 files, no offenses.
- Store not reachable: no Shopify connector in this account, so steps 1 to 3 (OBJ-099 swap, Paymob, menus and pages) not run. No store writes. Shopify CLI login not checked, nothing pushed to theme 189754769632.
- CONTENT_TO_SUPPLY.md: delivery, returns, payment, policies and collection-intro answers are still empty, so step 3 has no text to use even once the store is back.
- OBJ-099: the two v2 Oxblood JPEGs are in plan/images/OBJ-099/, ready to upload.

**Pre-launch cleanup checklist (HANDOVER section 8; state as last read on 7 Nov, not re-read today):**
- [ ] OBJ-099: upload the 2 v2 Oxblood JPEGs, link the Oxblood variant, remove v1 Oxblood media
- [ ] Delete the 3 `[TEST]` products and 2 `[TEST]` articles
- [ ] 13 `preview-active` products back to draft, or real data in; drop `placeholder-data` tags only when real
- [ ] Remove the 4 reference photos of unknown rights and the 8 placeholder images
- [ ] Expand `objekt-main` and footer menus; connect the delivery page; add policies (needs Sabry's text)
- [ ] Paymob: Sabry signs in; then test mode, activate, capture Automatic, test order and refund
- [ ] QA launch check "no active product with `placeholder-data`, 9999.00 or [PLACEHOLDER]" (fails by design today)
- [ ] Sabry only: publish theme, remove storefront password, Paymob live. Horizon stays as rollback.
