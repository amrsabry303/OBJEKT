# objekt launch status

Launch Fri 20 Nov 2026. Content freeze Thu 12 Nov. Founder approval Thu 19 Nov.

Three daily sessions work on this repo, one section each. Each session updates **only its own section** (date it, newest first, keep the last 3 entries) and the shared decision list. Sabry answers decisions in one line.

## Decisions needed from Sabry
<!-- one line each: [workstream] question · options · recommendation. Remove when answered. -->
- [content] Final day-1 product list: plan says 46, store has 49 drafts plus OBJ-099. Which products launch?
- [content] May AI renders go on the public site as product images until photos exist?
- [website] Reconnect the Shopify connector in this account (store hs1a1c-ut, OBJEKT).
- [website] Sign in to Paymob so test mode can be set up.
- [website] Fill sections 5, 6 and 8 of CONTENT_TO_SUPPLY.md (delivery, returns, payment, policies) before the 12 Nov freeze, or say which may stay out at launch.
- [all] Licences: PP Mori (web), Galak Round, logo lettering (Raftwork). No public launch without them.

## Content and product list

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
