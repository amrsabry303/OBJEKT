# objekt launch status

Launch Fri 20 Nov 2026. Content freeze Thu 12 Nov. Founder approval Thu 19 Nov.

Three daily sessions work on this repo, one section each. Each session updates **only its own section** (date it, newest first, keep the last 3 entries) and the shared decision list. Sabry answers decisions in one line.

## Decisions needed from Sabry
<!-- one line each: [workstream] question · options · recommendation. Remove when answered. -->
- [content] Freeze list (12 Nov, unchanged 14 Nov; candidates need answers by Tue 17 Nov, else launch with the 10 live): the 10 live products + 9 that may still join by 19 Nov if each gets name, price and approved image (OBJ-002, 038, 152, 194, 149, 173, 075, 115, 164); all other drafts go live weekly after launch. Table: `plan/day1-product-list.md` · yes / edit · rec: yes. Note: 0 planters live, only 2 pieces under 2,000 EGP.
- [content] ARRIS (172) is live with no drawing, size or lead time; PYRA (169) shows 3–5 days and "approximate" sizes with no recorded source · ask Polycraft today / put ARRIS back to draft until sized · rec: ask Polycraft today; draft ARRIS if no size by Tue 17 Nov.
- [content] OBJ-149 has two drawings: sheet says rev 0 approved 11 Nov (about 220 × 220 × 60, brushed); the drawings session made a different DRAFT 12 Nov (140 × 140 × 38, book size) · keep 11 Nov / keep 12 Nov · rec: keep your approved 11 Nov one, drop the draft.
- [content] Branch `claude/zen-newton-irxvlr` holds the 11–12 Nov records for 020, 166, 167, 194, 197, 198 (not on main) · merge / leave · rec: merge once the repo is private.
- [content] OBJ-148 and OBJ-159 references are named third-party products · redesign as our own / drop · rec: drop for day 1.
- [content] 15 store drafts not on the plan (OBJ-035, 039, 052, 074, 086, 090, 093, 107, 112, 141, 146, 150, 168, 170, 174) · archive / keep as drafts · rec: keep as drafts, never activate.
- [website] **The store is public** since 11 Nov ~23:15 UTC (still on 13 Nov): password off, 10 products buyable. The live theme changed again on 12 Nov to "OBJEKT UX audit (draft 12 Nov)"; neither change is in any repo log. Was this your go? · keep live / put the password back until 19 Nov · rec: if not intended, password back today (only you can).
- [website] Checkout offers **PayPal only** (checked 13 Nov); Paymob is not signed in, and checkout takes the full price (no 50% deposit). Sign in to Paymob so I can run test mode · rec: today, live orders can already come in.
- [website] All live variants weigh 0 kg, so **every order pays 118 EGP**, even a 28,000 EGP table · send packed weights per product (catalogue session enters them) · rec: weights from Polycraft by Tue 17 Nov.
- [website] Live theme is now in git (13 Nov, read through the API). Who edits the live theme from here: whoever made the 11–12 Nov drafts keeps going, or all theme edits go through the repo and an unpublished copy first · rec: repo first, so nothing is lost or overwritten before launch.
- [website] Fix 3 small typos in admin policies (Settings → Policies): Shipping "1,200 EGP.." ; Privacy contact ends "2240.</span>." ; Refund and Shipping headings run into the first sentence · connector cannot write policies.
- [website] Lawyer check on 48-hour returns, non-refundable deposit and governing law: the policies are now public · who checks, by when · rec: this week.
- [website] Branch `claude/handoff-section-7-shipping-umz7rf` still holds 10 Nov non-website work not on main (OBJ-167/003 renders, Arabic pack, Polycraft sheet). Website part now on main · merge rest / leave · rec: merge after the repo is private.
- [website] Arabic for the menu, About, collection intros and SEO text: send to the translator, or launch English only? · translator / EN only · rec: translator before 19 Nov.
- [catalogue] Fix the live listings from your own notes, on your yes: lead-time days SLAB 14–20 and TORSO 14–30 (both sizes, or give Small its own), `made_to_order` on BLOK's 4 variants · yes / no · rec: yes today, the buy box shows no days on SLAB and TORSO. (13 Nov: OCTA, CAIRN, SPAN, INGOT now show in Furniture, so no collection join is needed.)
- [catalogue] Lead time for BLOK and SPAN, and where PYRA 3–5, ARRIS 14–30 and OCTA 7–14 days came from (not in any note) · give days / confirm · rec: answer with the weights from Polycraft.
- [catalogue] SEO title and description are empty on all 10 live products · I draft them in Dough voice from the approved copy for your review / you write them · rec: I draft, nothing goes on the store until you say yes.
- [catalogue] Online Store channel: the 10 live products are on it; the 9 candidate drafts are not · I add it when each candidate is approved / you do it on activation · rec: I add it on approval.
- [images] **Magnific credits 0 of 20,000 (13 and 14 Nov; 195 on 12 Nov).** Image runs are stopped until topped up. At ~65 per render, the 4 hero follow-ups plus the 9 freeze candidates need roughly 3,000–4,000 · top up / buy extra credits / pause images · rec: top up today; heroes for the freeze candidates must be approved before Thu 19 Nov.
- [images] Approve or retake the 4 hero renders (AI renders): OBJ-152 Ink v2c, OBJ-002 Oxblood v1c, OBJ-038 Carbon v1c (sent 8 Nov, re-sent 11 Nov), OBJ-015 Chocolate v1c (11 Nov) · approve / retake per image · only after approval do other colours and the context shot get made.
- [images] Repo is public: the 8 Nov renders of 002, 038, 152 are already visible on GitHub; new render files are held back · make the repo private / allow renders in public · rec: private (same as the drawings line).
- [images] With the day-1 list unapproved, no product with an approved drawing is left without a hero. Next: render day-1 products from their reference photos without an approved drawing? · yes / wait for drawings · rec: yes for the simplest planters and objects, renders marked shape-to-confirm.
- [images] Hero colours used are the proposed ones from CONTENT_TO_SUPPLY 3d (002 Oxblood matte, 038 Carbon matte, 152 Ink gloss). The "mirror on the metal segment" for 002 and 038 is not shown: which part is mirror? · tell me / leave all-coated · rec: leave all-coated until the drawing says.
- [images] OBJ-001 reference photo carries a third-party maker mark (NM3), like 148/159 · redesign as our own / render anyway · rec: wait for the Polycraft design file and render from that. Skipped today.
- [images] Drive upload and production-book stickers for new renders need your yes · yes / not yet · rec: yes once heroes are approved.
- [drawings] GitHub repo is still **public** (checked 14 Nov). The import, the 11 Nov drafts and today's drafts are not pushed; 11 Nov's local work was lost with that run's workspace, so each run now sends its files to you as a zip · make the repo private / say what may be public (OBJ-190's drawings are already public on main) · rec: private, then the next run re-imports from Drive and pushes.
- [drawings] Approve or correct the DRAFT sets OBJ-173 (cube planter), OBJ-115 (tray), OBJ-075 (cylinder pair), sent 11 Nov · write "approved" or the change per product · rec: check sizes first, they are estimates. Their generators were lost; on approval I redraw from the sent PDFs.
- [drawings] OBJ-075: book says one planter Ø300 × 500; photo shows a pair. Draft is the pair (A Ø300 × 390, B Ø240 × 290 on a foot) · pair / single, sizes · rec: pair.
- [drawings] Drainage for OBJ-173 and OBJ-075 (none shows in the photos) · none / drain hole / loose inner pot · rec: loose inner pot, no hole.
- [drawings] OBJ-003 real size: your model says top 130.06, height 40 (units not stated); the book says about 900 × 380 · give diameter and height in mm.
- [drawings] Approve or correct the DRAFT sets OBJ-164 (corner shelf pair) and OBJ-149 (ashtray), sent 12 Nov · write "approved" or the change · rec: settle the two size lines below first.
- [drawings] OBJ-164 size: the reference photo's caption says 22 × 22 cm (drawn: top 220 × 220, drop 200 estimated); the book says about 250 × 250 × 60 · 220 / 250 / your size, and the drop · rec: 220 as the reference, drop from a sample.
- [drawings] OBJ-164 wall fixing: none shows in the photo · Production proposes a hidden fixing / keyhole slots in the top / adhesive · rec: Production proposes, you approve before the sample.
- [drawings] OBJ-172 ARRIS is live with no drawing; one photo cannot show its facets · send the maker's model, or photos from 3 sides with the height / Polycraft measures a sample / leave undrawn · rec: model or 3 photos, then I draw it the same day.
- [drawings] OBJ-100 candleholder reference carries another maker's engraved mark ("IT'S NOT OVER YET"), like 001, 148 and 159 · redesign as our own / drop / draw anyway · rec: drop for day 1. Not drawn. OBJ-176 (half-disc shelves) is also a recognisable designer piece with several versions: same question · rec: redesign as our own after launch.
- [all] Licences: PP Mori (web), Galak Round, logo lettering (Raftwork). No public launch without them.
- [faux books] Who prints them? No printer or binder, no sample, price or lead time, and the print files have no wrap allowance · ask two Cairo printers this week / hold to wave 2 / list as pre-order on 20 Nov · rec: ask this week, list as pre-order only if a maker confirms.
- [faux books] The 11 Medium print PDFs are in their Drive folders. Upload the S and L versions too, and what goes in the OBJ-189 (set of three) folder? · yes / not yet · rec: S and L when a maker is chosen; for OBJ-189 a short note pointing to the three sets' design folders.

## Content and product list

### Sat 14 Nov 2026
- Checked (read only): store 62 products, 10 active, nothing edited since 12 Nov 11:29 UTC; sheet (12 Nov) and book (11 Nov) unchanged by last-edit date. No content decision answered, no copy approval, so no copy drafted.
- Removed my decision line on the 4 tables in no collection: they are in Furniture since 13 Nov (catalogue session).
- Added a 14 Nov note to `plan/day1-product-list.md` (no change; store count corrected to 62; fallback if nothing by Tue 17 Nov is launch with the 10 live).
- Not done: no store, sheet, book or Drive writes.
- Next: fill CONTENT_TO_SUPPLY 3e and 3f as answers arrive; on Tue 17 Nov mark each candidate in or after-launch.

### Fri 13 Nov 2026
- Checked (read only): store 10 active, nothing changed since 12 Nov 11:29 UTC; sheet edited 12 Nov 10:59 UTC but its Products rows match the 12 Nov record; book unchanged since 11 Nov. No decision answered, no copy approval, so no copy drafted.
- Added section 3f to `website/docs/CONTENT_TO_SUPPLY.md`: every open answer, grouped by who gives it (Polycraft, Sabry). The Polycraft table can be sent as is. Target: answers by **Tue 17 Nov** to make Thu 19 Nov.
- Added a 13 Nov note to `plan/day1-product-list.md`: no change, freeze-day table stands, cut-off Tue 17 Nov for candidates.
- Not done: no store, sheet, book or Drive writes.
- Next: fill 3e and 3f as answers arrive; move candidates to live when Sabry activates them.

### Thu 12 Nov 2026 (freeze day)
- Read: store (read only; 67 products, **10 active**, 57 draft), product sheet and production book (both edited 11 Nov, so re-read in full), branch `claude/zen-newton-irxvlr` (not on main). No copy approval in this file, so no copy drafted.
- Found: Sabry named, priced and activated 10 products on 11–12 Nov: SLAB (020), BLOK (166), TORSO (167, with OBJ-196 as its 55 cm size), OCTA (190), CAIRN (195), SPAN (197), INGOT (198), PYRA (169), ARRIS (172), ROTA (099). The book added OBJ-196, 197, 198; the sheet added 191–195 and an approved OBJ-149 drawing that differs from the 12 Nov draft.
- Wrote the freeze-day table at the top of `plan/day1-product-list.md` (every OBJ id: title, category, process, drawing, images, in/out, reason). Recommendation: 10 live + 9 candidates, the rest after launch.
- Added section 3e to `website/docs/CONTENT_TO_SUPPLY.md`: price, size, finish and lead time for the live products exactly as recorded, with source, and a who-must-answer column. Gaps on every live product: Arabic, packed weight, name trademark check; lead time missing on BLOK, OCTA, SPAN, ARRIS, ROTA (CAIRN's is in the sheet only).
- Not done: no store, sheet, book or Drive writes. Decisions replaced: the 41-product approval and the (a)/(b)/(c) choice (overtaken by what went live), and the AI-render question (renders are on the live listings).
- Next: fill 3e as answers arrive; move candidates to live in the table when Sabry activates them.

## Product images

### Sat 14 Nov 2026
- Magnific balance **0** (of 20,000), same as 13 Nov. Below the 2,000 stop line, so **no renders today** (second day running).
- No hero answered (152, 002, 038, 015); day-1 freeze list not approved. Next product stays OBJ-149 (brushed).
- Nothing generated, uploaded or changed in the inventory. Stickers not changed.
- Next: once credits are topped up, OBJ-149 hero, then other colours and context shots for any approved hero. Time is short: 5 days to launch.

### Fri 13 Nov 2026
- Magnific balance **0** (of 20,000; 20,000 spent). Below the 2,000 stop line, so **no renders today**. 195 was left on 12 Nov; this session spent nothing since 11 Nov.
- No hero answered in this file (152, 002, 038, 015), day-1 list not approved. Next product stays OBJ-149 (brushed).
- Nothing generated, uploaded or changed in the inventory. Stickers not changed.
- Next: once credits are topped up, OBJ-149 hero, then other colours and context shots for any approved hero.

### Thu 12 Nov 2026
- Magnific balance **195** (of 20,000). Below the 2,000 stop line, so **no renders today**. 6,465 was left after this session on 11 Nov; about 6,270 went to other Magnific work since, not this session.
- No hero answered yet (152, 002, 038, 015), day-1 list not approved. Next product would have been OBJ-149 (sheet says rev 0 approved 11 Nov; the reference's proportions fit both drawing versions).
- Nothing generated, uploaded or changed in the inventory. Stickers not changed.
- Next: once credits are topped up, OBJ-149 hero (brushed), then other colours and context shots for any approved hero.

## Drawings and files

### Sat 14 Nov 2026
- Checked: repo still **public** (GitHub API, 14 Nov), no "approved" for any drawing in this file, nothing in Drive changed since 13 Nov. So no import push, no approval routine, no Drive upload, no sticker change.
- Step 1 not redone (fourth day): it cannot be pushed while the repo is public. The Drive export still holds everything.
- Step 2: no new drafts. Every freeze candidate without an approved drawing (149, 173, 075, 115, 164) already has a DRAFT waiting; ARRIS (172) still needs a model or photos.
- Found: three live products have drawing sets in Drive made 11 Nov outside this session: OBJ-195 rev 1, OBJ-197 rev 0, OBJ-198 rev 0 and rev 1 (PDF and production pack each). Not in this repo, not on the approved list. They come in with the import once the repo is private.
- Next: your answers on the 5 drafts; ARRIS once a model or photos arrive; then 171, 165, 175 after launch.

### Fri 13 Nov 2026
- Checked: repo still **public** (GitHub API, 13 Nov), no "approved" for any drawing in this file, main unchanged since 12 Nov. So no import push, no approval routine, no Drive upload, no sticker change.
- Step 1 not redone: it cannot be pushed while the repo is public (third day). The Drive export still holds everything.
- Step 2: every freeze candidate without an approved drawing (149, 173, 075, 115, 164) already has a DRAFT waiting for you, so **no new drafts today**. 171, 165, 175 are after launch; drafting them now would add to the five unanswered sets a week before launch.
- Looked at OBJ-172 ARRIS (live on the store, no drawing): the book has one photo of a faceted mirror-polished piece, about 800 × 600 × 1600. The back facets cannot be seen, so a drawing from that photo would be invented, not traced. Not drawn: see decisions.
- Next: your answers on the 5 drafts (redraw the 11 Nov three from the sent PDFs on approval); ARRIS once a model or more photos arrive; then 171, 165, 175 after launch.

### Thu 12 Nov 2026
- Checked: repo still public (GitHub search API: visibility public), no "approved" for any drawing in this file. So no import push, no approval routine, no Drive upload, no sticker change.
- Found: the 11 Nov import (410 files), the 3 drafts' generators and `objekt_sheet.py` never reached GitHub and were lost with that run's workspace. Step 1 not redone today: it cannot be pushed while the repo is public. The Drive export still holds everything.
- Two DRAFT sets made (5 A3 sheets each, EN/AR, SVGs, DXFs, nest; every PDF page rendered to PNG and looked at; DXFs read back, parts inside the sheet, 10 mm gaps; "DRAFT" present in the PDF text):
  - **OBJ-164** corner shelf pair: one kite blank, one fold (front face down to the wall corner). Top 220 × 220 from the reference caption, drop 200 estimated; fold 127.9° from flat; cut 1,035 mm per shelf. Book size (250 × 250 × 60) conflicts: see decisions.
  - **OBJ-149** ashtray: four 140 × 38 plates in a # with halving slots (4 × 19), a separate U-tray 95 × 95 × 34, R12 inside. 140 × 140 × 38 from the book; the rest estimated from the photos.
- Skipped: OBJ-100 (another maker's engraved mark on the reference) and OBJ-176 (recognisable designer piece). Rebuilt the shared helper as `venture/src/drawings/objekt_sheet.py`.
- Not pushed (public repo): drawings and generators were sent to Sabry as a zip in the run's message. Only this STATUS update is pushed.
- Next: your answers on the 5 open drafts; then OBJ-171, 165, 175 (no reference image in `images/`; I take it from the production book slide).

## Website (Shopify)
### 13 Nov 2026 (Fri)
- Ran: pulled main (f37ff7f); `npm ci`; `theme check` clean. Store confirmed OBJEKT / hs1a1c-ut. **No store writes.** CLI not logged in.
- Found: the live theme changed again, not logged: now `190236524768` "OBJEKT UX audit (draft 12 Nov)" (edited 12 Nov 08:41–09:03 UTC). Store still **public**, 10 active, 0 orders. Menus, pages, policies unchanged (3 typos still there).
- **Live theme now in git:** read all 67 live files through the Admin API (read only, no CLI needed) and wrote them into `website/theme` (38 differed, 4 were missing). Code files match the live MD5. `theme check` 50 files, no offenses; no font files. Dev theme `189754769632` is now behind; not pushed.
- Browser check (Playwright, 1440 and 375 px): 7 pages 200, no horizontal scroll, no placeholder text. Checkout with PYRA (no order): **PayPal only**, full price, no deposit.
### 12 Nov 2026 (Thu)
- Ran: pulled main (fccbb73); `npm ci`; `theme check` 48 files, no offenses. Store confirmed OBJEKT / hs1a1c-ut. **No store writes.** CLI not logged in.
- Found: store **public** (password protection off). Live theme was `190221484256` "OBJEKT hide single option (draft 12 Nov)", published 11 Nov ~23:15 UTC; 4 more draft themes made 11 Nov. 10 products active and on the Online Store; 0 orders. Menu `objekt-main` now Shop, About, Custom request; new page Custom request (form app "Powerful Form Builder").
- Browser check of the public site (Playwright, 1440 and 375 px): all 200, no horizontal scroll, no placeholder text. Checkout reached with PYRA in the bag (no order): Egypt address form, **PayPal the only payment**, total in EGP.
- Gaps on live products: all variants 0 kg (every order 118 EGP); SLAB, BLOK, SPAN and TORSO have no variant lead-time days. CAIRN, OCTA, SPAN, INGOT in no collection.
### 11 Nov 2026 (Wed)
- Ran: pulled main (760de90); `npm ci`; `theme check` 48 files, no offenses. Store confirmed OBJEKT / hs1a1c-ut. **No store writes.**
- Found the 10 Nov website work on an unmerged branch (`claude/handoff-section-7-shipping-umz7rf`). Brought its `website/` files onto main.
- QA launch check "no active product with placeholders" passes (0 active). Checkout, Paymob, browser QA: not tested.

**Pre-launch cleanup checklist (HANDOVER section 8; store re-read 13 Nov):**
- [x] OBJ-099: v2 Oxblood images in, variant linked, v1 removed (8 Nov)
- [x] Delete the 3 `[TEST]` products and 2 `[TEST]` articles (10 Nov)
- [x] 13 `preview-active` products back to draft (10 Nov); drop `preview-active` / `placeholder-data` tags only when real data is in
- [x] Remove the 4 reference photos of unknown rights and the 8 placeholder images (10 Nov)
- [x] `objekt-main` expanded (9 Nov; now Shop, About, Custom request)
- [x] Footer menus, Delivery & Returns page, 5 policies (10 Nov). Open: 3 typos in admin policies, lawyer check
- [ ] Shipping: packed weight on every launch product (all 0 kg on 13 Nov); checkout rate test (Egypt, under and over 15 kg)
- [ ] Paymob: Sabry signs in; then test mode, activate, capture Automatic, test order and refund (13 Nov: PayPal only)
- [x] QA launch check "no active product with `placeholder-data`, 9999.00 or [PLACEHOLDER]" passes (12 Nov; 13 Nov public pages show no placeholder text)
- [~] Sabry only: theme published and password removed (found 12 Nov, not logged); live theme changed again to `190236524768`; Paymob live still open. Horizon kept unpublished as rollback.
- [x] Live theme pulled into git (13 Nov, via Admin API; no CLI needed)

### Shopify catalogue
<!-- daily catalogue session; dated, newest first, last 3 entries -->

#### Fri 13 Nov 2026
- Ran: `get-shop-info` = OBJEKT / hs1a1c-ut, EGP. Pulled main (7fdf323). Read: products changed since 12 Nov 11:00 UTC (only SPAN 11:14 and INGOT 11:29 UTC, both after yesterday's 07:40 run), the 10 active products (collections, variant weights, SEO), the Furniture collection.
- Found: 62 products, **10 active**, nothing edited on the store since 12 Nov 11:29 UTC. **OCTA, CAIRN, SPAN, INGOT are now in Furniture** (manual, 18 products; not by this session, probably with the 12 Nov 11:14–11:29 edits), so that gap is closed; table updated. The content line on this can go. Still: all variants **0 kg**, SEO empty on all 10.
- No answer from Sabry on any catalogue or content line, no supplied value, no approved image, day-1 list not approved. So **no store writes**, nothing to log in CHANGELOG.
- Readiness: **0 of 19 complete**. Placeholders left on all drafts.

#### Thu 12 Nov 2026 (freeze day)
- Ran: `get-shop-info` = OBJEKT / hs1a1c-ut, EGP. Pulled main (22234fb). Read all 62 products (variants, weights, lead-time days, collections, channel count, metafields, media alt, Arabic translations) and the 5 collections.
- Found: Sabry activated **10 products** on 11–12 Nov himself (SLAB 020, BLOK 166, TORSO 167 + 196, OCTA 190, CAIRN 195, SPAN 197, INGOT 198, PYRA 169, ARRIS 172, ROTA 099). All 10 are on the Online Store channel. 52 drafts, all tagged `placeholder-data`. No duplicate OBJ codes. OBJ-099 colours settled by Sabry (Oxblood, Chocolate, Objekt Green, Putty, linked to the colour entries).
- **No store writes.** Every gap left on the live products needs Sabry's yes (CLAUDE.md: no live-product changes without approval), and no draft got a supplied value (no name, price, size, colour or approved image for any candidate). Day-1 list not approved.
- Gaps on the 10 live products, read from the store: all variants **0 kg**; **no Arabic** on any; **SEO title and description empty** on all; care and materials text empty on all. Lead-time days missing on SLAB (14–20 in its note), TORSO (14–30 in its note), BLOK and SPAN (none given). BLOK's 4 variants have no `fulfilment` value. CAIRN, OCTA, SPAN, INGOT in no collection. ARRIS and ROTA have no size; ARRIS shows 14–30 days and OCTA 7–14 days with no source recorded in the repo.
- Alt text: none of the live images says "AI render". That follows Sabry's 10 Nov rule (never mention renders in public text), which replaces this task's alt-text line; left as is.
- Readiness: **0 of 19 complete** (10 live, 9 candidates). Placeholders left on all drafts.

**Readiness (13 Nov; ✓ done, ~ partly, ✗ missing).** Live = active now. "Complete" needs all 12 checks.

| OBJ | Title | Named | Copy EN | Copy AR | Price | Lead time | Sizes | Variants | Images | Collection | Metafields | SEO | Placeholders gone | Complete |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OBJ-020 | SLAB (live) | ✓ | ✓ | ✗ | ✓ | ✗ note only | ✓ | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-166 | BLOK (live) | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ~ no mirror at sold heights | ✓ Furniture | ✗ no fulfilment, 0 kg | ✗ | ✓ | no |
| OBJ-167 + 196 | TORSO (live) | ✓ | ✓ | ✗ | ✓ | ✗ note only | ~ estimates | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-190 | OCTA (live) | ✓ | ✓ | ✗ | ✓ | ~ 7–14, source? | ✓ | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-195 | CAIRN (live) | ✓ | ✓ | ✗ | ✓ | ✓ 7–14 | ✓ | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-197 | SPAN (live) | ✓ | ✓ | ✗ | ✓ | ✗ | ~ height est. | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-198 | INGOT (live) | ✓ | ✓ | ✗ | ✓ | ✓ 14–30 | ✓ | ✓ | ✓ | ✓ Furniture | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-169 | PYRA (live) | ✓ | ✓ | ✗ | ✓ | ~ 3–5, source? | ~ approximate | ✓ | ✓ | ✓ T&L | ~ no care, 0 kg | ✗ | ✓ | no |
| OBJ-172 | ARRIS (live) | ✓ | ✓ | ✗ | ✓ | ~ 14–30, source? | ✗ | ✓ | ✓ | ✓ Objekts | ✗ no size, 0 kg | ✗ | ✓ | no |
| OBJ-099 | ROTA (live) | ✓ | ✓ | ✗ | ✓ | ✓ 7–14 | ✗ | ✓ 4 colours | ✓ | ✓ Objekts | ✗ no size, 0 kg | ✗ | ✓ | no |
| OBJ-002 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero pending | ✓ Furniture | ✗ | ✗ | ✗ | no |
| OBJ-038 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero pending | ✓ Furniture | ✗ | ✗ | ✗ | no |
| OBJ-152 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero pending | ✓ Furniture | ✗ | ✗ | ✗ | no |
| OBJ-194 | no draft yet | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ 1200 × 450 × 750 | ✗ | 2 renders, not approved | – | ✗ | ✗ | – | no |
| OBJ-149 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ two drawings | ✗ | ✗ | ✓ Objekts | ✗ | ✗ | ✗ | no |
| OBJ-173 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ Planters | ✗ | ✗ | ✗ | no |
| OBJ-075 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ Planters | ✗ | ✗ | ✗ | no |
| OBJ-115 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ T&L | ✗ | ✗ | ✗ | no |
| OBJ-164 | draft | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ Objekts | ✗ | ✗ | ✗ | no |

The other 43 drafts (after-launch, on hold or off-plan) are unchanged since the 11 Nov table (git history): 0 ready, placeholders in place. OBJ-194 gets a draft (FACET is only a suggestion, so titled OBJ-194) once Sabry puts it on the list.

What the live products still need, by who: **Polycraft** packed weight per variant (all 10), ARRIS size, ROTA size, SPAN height, TORSO side 300 vs 260; **Sabry** lead time for BLOK, SPAN and TORSO Small, the source of PYRA 3–5 / ARRIS 14–30 / OCTA 7–14 days, Arabic title and copy (or translator), SEO title and description (or say "write drafts"), care text.

#### Wed 11 Nov 2026
- Ran: `get-shop-info` = OBJEKT / hs1a1c-ut, EGP. Read all 50 products (all draft, no duplicate OBJ codes) and the 5 collections. Pulled main (4849649).
- **Store writes (CHANGELOG 11 Nov): created 8 drafts** that the plan and the book both list as IN: OBJ-020, 152, 156, 094, 103, 132, 068, 155. OBJ-020 has since become SLAB (live, by Sabry).
- Readiness: 0 of 41. Table replaced on 12 Nov (in git history).

## Faux books (design)
### 11 Nov 2026
- 11 designs in 3 sizes (S 14 × 20 × 2.0, M 18 × 25 × 2.8, L 23 × 30 × 3.5 cm), 33 print PDFs with bleed and marks, 3D mockups at size M. Spec: `plan/faux-books/PLAN.md`. Added to `plan/day1-product-list.md`, `plan/IMAGE-INVENTORY.md` and `.csv`, the objekt Product Sheet artifact, CLAUDE.md and IMPORT.md.
- Not in the print files: wrap allowance, final lettering (Inter stand-in until the fonts are licensed). No maker yet.
- Repo clean-up: draft artwork, 8 superseded render sets and an AI couch comp (built on another brand's photo) removed; `plan/` went from 112 MB to 55 MB. Reference photos added as `images/OBJ-178` to `188` (reference only), following the repo convention.
- Google product sheet: Products tab columns Full image and Design files were restyled as buttons on 11 Nov (labels renamed). Sabry approved (11 Nov): 12 empty Drive folders created (OBJ-178 to 189, next to the other design folders) and 12 rows added to Products (rows 134 to 145) and Design folders. The Image and Reference image links read from `main` and work once the faux-books branch is merged (done 11 Nov, see below). The sheet's Taxonomy has no Desk and book subcategory in Table & Living, so the rows use "Desk and Book Accessories", which maps to the old website category "Objects & Lighting".
- Decided and confirmed by Sabry 11 Nov: the books are sold as 2 website products (Faux book with design × size variants, Set of three); numbers OBJ-178 to 188 (designs) and OBJ-189 (set of three) are confirmed, no longer provisional.
- Uploaded to Drive on Sabry's yes (11 Nov): the 11 Medium print PDFs, one per design folder OBJ-178 to 188. S and L versions and the OBJ-189 folder are still empty (red in the product sheet).
- Branch merged to `main` on Sabry's yes (11 Nov, squash).
- Next: a maker brief (wrap allowance, bleed, spine thickness, price, lead time) and the licence for the fonts.
