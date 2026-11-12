# objekt launch status

Launch Fri 20 Nov 2026. Content freeze Thu 12 Nov. Founder approval Thu 19 Nov.

Three daily sessions work on this repo, one section each. Each session updates **only its own section** (date it, newest first, keep the last 3 entries) and the shared decision list. Sabry answers decisions in one line.

## Decisions needed from Sabry
<!-- one line each: [workstream] question · options · recommendation. Remove when answered. -->
- [content] Freeze list (12 Nov): the 10 live products + 9 that may still join by 19 Nov if each gets name, price and approved image (OBJ-002, 038, 152, 194, 149, 173, 075, 115, 164); all other drafts go live weekly after launch. Table: `plan/day1-product-list.md` · yes / edit · rec: yes. Note: 0 planters live, only 2 pieces under 2,000 EGP.
- [content] 4 live products are in no collection, so they do not show on the Furniture page: OCTA (190), CAIRN (195), SPAN (197), INGOT (198) · catalogue session adds them to Furniture / you do it · rec: catalogue session, on your yes.
- [content] ARRIS (172) is live with no drawing, size or lead time; PYRA (169) shows 3–5 days and "approximate" sizes with no recorded source · ask Polycraft today / put ARRIS back to draft until sized · rec: ask Polycraft today; draft ARRIS if no size by Tue 17 Nov.
- [content] OBJ-149 has two drawings: sheet says rev 0 approved 11 Nov (about 220 × 220 × 60, brushed); the drawings session made a different DRAFT 12 Nov (140 × 140 × 38, book size) · keep 11 Nov / keep 12 Nov · rec: keep your approved 11 Nov one, drop the draft.
- [content] Branch `claude/zen-newton-irxvlr` holds the 11–12 Nov records for 020, 166, 167, 194, 197, 198 (not on main) · merge / leave · rec: merge once the repo is private.
- [content] OBJ-148 and OBJ-159 references are named third-party products · redesign as our own / drop · rec: drop for day 1.
- [content] 15 store drafts not on the plan (OBJ-035, 039, 052, 074, 086, 090, 093, 107, 112, 141, 146, 150, 168, 170, 174) · archive / keep as drafts · rec: keep as drafts, never activate.
- [website] **The store is public** since 11 Nov ~23:15 UTC: password off, theme "OBJEKT hide single option (draft 12 Nov)" is live, Horizon unpublished, 10 products buyable. Not in any repo log. Was this your go? · keep live / put the password back until 19 Nov · rec: if not intended, password back today (only you can).
- [website] Checkout offers **PayPal only**; Paymob is not signed in, and checkout takes the full price (no 50% deposit). Sign in to Paymob so I can run test mode · rec: today, live orders can already come in.
- [website] All live variants weigh 0 kg, so **every order pays 118 EGP**, even a 28,000 EGP table · send packed weights per product (catalogue session enters them) · rec: weights from Polycraft by Tue 17 Nov.
- [website] The live theme has work that is in no git branch (Custom request page with form app, side-pane header, quick add, option tiles; 23 files differ). Log in the Shopify CLI once so I can pull it into the repo · rec: yes, before any more theme edits.
- [website] Fix 3 small typos in admin policies (Settings → Policies): Shipping "1,200 EGP.." ; Privacy contact ends "2240.</span>." ; Refund and Shipping headings run into the first sentence · connector cannot write policies.
- [website] Lawyer check on 48-hour returns, non-refundable deposit and governing law: the policies are now public · who checks, by when · rec: this week.
- [website] Branch `claude/handoff-section-7-shipping-umz7rf` still holds 10 Nov non-website work not on main (OBJ-167/003 renders, Arabic pack, Polycraft sheet). Website part now on main · merge rest / leave · rec: merge after the repo is private.
- [website] Arabic for the menu, About, collection intros and SEO text: send to the translator, or launch English only? · translator / EN only · rec: translator before 19 Nov.
- [catalogue] Colours per product: the book's colours are proposals. Confirm the colours each product is sold in (start with the 10 that have drawings or renders) · list per OBJ · rec: confirm in CONTENT_TO_SUPPLY 3d, then I build the colour variants.
- [catalogue] Online Store channel: no product is published to the Online Store channel, so an activated product may not show on the site · I add the channel to the day-1 drafts now (they stay hidden while draft) / you do it at launch · rec: I add it once the day-1 list is approved.
- [catalogue] OBJ-099 colours: store has Oxblood, Ink, Objekt Green, Putty; book has Objekt Green, Bone, Putty · keep store / switch to book · rec: keep store (renders exist for those four).
- [images] **Magnific credits 195 of 20,000 (12 Nov).** Image runs are stopped until topped up. At ~65 per render, the 4 hero follow-ups plus the 9 freeze candidates need roughly 3,000–4,000 · top up / buy extra credits / pause images · rec: top up before Sat 14 Nov so heroes can be finished by 19 Nov.
- [images] Approve or retake the 4 hero renders (AI renders): OBJ-152 Ink v2c, OBJ-002 Oxblood v1c, OBJ-038 Carbon v1c (sent 8 Nov, re-sent 11 Nov), OBJ-015 Chocolate v1c (11 Nov) · approve / retake per image · only after approval do other colours and the context shot get made.
- [images] Repo is public: the 8 Nov renders of 002, 038, 152 are already visible on GitHub; new render files are held back · make the repo private / allow renders in public · rec: private (same as the drawings line).
- [images] With the day-1 list unapproved, no product with an approved drawing is left without a hero. Next: render day-1 products from their reference photos without an approved drawing? · yes / wait for drawings · rec: yes for the simplest planters and objects, renders marked shape-to-confirm.
- [images] Hero colours used are the proposed ones from CONTENT_TO_SUPPLY 3d (002 Oxblood matte, 038 Carbon matte, 152 Ink gloss). The "mirror on the metal segment" for 002 and 038 is not shown: which part is mirror? · tell me / leave all-coated · rec: leave all-coated until the drawing says.
- [images] OBJ-001 reference photo carries a third-party maker mark (NM3), like 148/159 · redesign as our own / render anyway · rec: wait for the Polycraft design file and render from that. Skipped today.
- [images] Drive upload and production-book stickers for new renders need your yes · yes / not yet · rec: yes once heroes are approved.
- [drawings] GitHub repo is still **public** (checked 12 Nov). The import, the 11 Nov drafts and today's drafts are not pushed; 11 Nov's local work was lost with that run's workspace, so each run now sends its files to you as a zip · make the repo private / say what may be public (OBJ-190's drawings are already public on main) · rec: private, then the next run re-imports from Drive and pushes.
- [drawings] Approve or correct the DRAFT sets OBJ-173 (cube planter), OBJ-115 (tray), OBJ-075 (cylinder pair), sent 11 Nov · write "approved" or the change per product · rec: check sizes first, they are estimates. Their generators were lost; on approval I redraw from the sent PDFs.
- [drawings] OBJ-075: book says one planter Ø300 × 500; photo shows a pair. Draft is the pair (A Ø300 × 390, B Ø240 × 290 on a foot) · pair / single, sizes · rec: pair.
- [drawings] Drainage for OBJ-173 and OBJ-075 (none shows in the photos) · none / drain hole / loose inner pot · rec: loose inner pot, no hole.
- [drawings] OBJ-003 real size: your model says top 130.06, height 40 (units not stated); the book says about 900 × 380 · give diameter and height in mm.
- [drawings] Approve or correct the DRAFT sets OBJ-164 (corner shelf pair) and OBJ-149 (ashtray), sent 12 Nov · write "approved" or the change · rec: settle the two size lines below first.
- [drawings] OBJ-164 size: the reference photo's caption says 22 × 22 cm (drawn: top 220 × 220, drop 200 estimated); the book says about 250 × 250 × 60 · 220 / 250 / your size, and the drop · rec: 220 as the reference, drop from a sample.
- [drawings] OBJ-164 wall fixing: none shows in the photo · Production proposes a hidden fixing / keyhole slots in the top / adhesive · rec: Production proposes, you approve before the sample.
- [drawings] OBJ-100 candleholder reference carries another maker's engraved mark ("IT'S NOT OVER YET"), like 001, 148 and 159 · redesign as our own / drop / draw anyway · rec: drop for day 1. Not drawn. OBJ-176 (half-disc shelves) is also a recognisable designer piece with several versions: same question · rec: redesign as our own after launch.
- [all] Licences: PP Mori (web), Galak Round, logo lettering (Raftwork). No public launch without them.
- [faux books] Who prints them? No printer or binder, no sample, price or lead time, and the print files have no wrap allowance · ask two Cairo printers this week / hold to wave 2 / list as pre-order on 20 Nov · rec: ask this week, list as pre-order only if a maker confirms.
- [faux books] The 11 Medium print PDFs are in their Drive folders. Upload the S and L versions too, and what goes in the OBJ-189 (set of three) folder? · yes / not yet · rec: S and L when a maker is chosen; for OBJ-189 a short note pointing to the three sets' design folders.

## Content and product list

### Thu 12 Nov 2026 (freeze day)
- Read: store (read only; 67 products, **10 active**, 57 draft), product sheet and production book (both edited 11 Nov, so re-read in full), branch `claude/zen-newton-irxvlr` (not on main). No copy approval in this file, so no copy drafted.
- Found: Sabry named, priced and activated 10 products on 11–12 Nov: SLAB (020), BLOK (166), TORSO (167, with OBJ-196 as its 55 cm size), OCTA (190), CAIRN (195), SPAN (197), INGOT (198), PYRA (169), ARRIS (172), ROTA (099). The book added OBJ-196, 197, 198; the sheet added 191–195 and an approved OBJ-149 drawing that differs from the 12 Nov draft.
- Wrote the freeze-day table at the top of `plan/day1-product-list.md` (every OBJ id: title, category, process, drawing, images, in/out, reason). Recommendation: 10 live + 9 candidates, the rest after launch.
- Added section 3e to `website/docs/CONTENT_TO_SUPPLY.md`: price, size, finish and lead time for the live products exactly as recorded, with source, and a who-must-answer column. Gaps on every live product: Arabic, packed weight, name trademark check; lead time missing on BLOK, OCTA, SPAN, ARRIS, ROTA (CAIRN's is in the sheet only).
- Not done: no store, sheet, book or Drive writes. Decisions replaced: the 41-product approval and the (a)/(b)/(c) choice (overtaken by what went live), and the AI-render question (renders are on the live listings).
- Next: fill 3e as answers arrive; move candidates to live in the table when Sabry activates them.

### Wed 11 Nov 2026
- Sheet (26 Oct) and book (2 Nov) unchanged; checked by last-edit date. No content decision answered yet.
- Recorded Sabry's 10 Nov lead time (30–45 days, made to order, 50% deposit) as a store-wide note in CONTENT_TO_SUPPLY 3d. Per-product lead time left blank until Polycraft confirms each fits.
- Added a freeze-eve check to `plan/day1-product-list.md`: shortlist 0 of 10 complete; fallback if nothing arrives by 12 Nov.
- No copy drafted: not approved in this file.
- Next: on Sabry's answers, mark final in/out and fill the shortlist rows as Polycraft data arrives.

### Mon 9 Nov 2026
- Sheet (last edit 26 Oct) and book (last edit 2 Nov) unchanged since the first run; no re-read needed. No decision answered yet, so the 41/4/16 recommendation stands.
- Updated image status for OBJ-002, 038, 152 (hero AI renders made 8 Nov, pending approval) in the day-1 list and CONTENT_TO_SUPPLY 3d. 9 products now have AI renders; none approved for the site.
- Added a freeze shortlist to `plan/day1-product-list.md`: 7 products with a drawing (001, 002, 038, 152, 166, 167, 169) and 3 with a prototype (003, 137, 099), each with what Sabry and what Polycraft must answer.
- OBJ-166 heights: still 850/1000 mm (book) vs 700/1000 mm (template). No other source in the repo settles it; Polycraft must confirm.
- No copy drafted: not approved in this file.
- Next: if (b) is chosen, turn the shortlist answers into CONTENT_TO_SUPPLY rows as they arrive; if the list is approved, mark the final in/out.

## Product images

### Thu 12 Nov 2026
- Magnific balance **195** (of 20,000). Below the 2,000 stop line, so **no renders today**. 6,465 was left after this session on 11 Nov; about 6,270 went to other Magnific work since, not this session.
- No hero answered yet (152, 002, 038, 015), day-1 list not approved. Next product would have been OBJ-149 (sheet says rev 0 approved 11 Nov; the reference's proportions fit both drawing versions).
- Nothing generated, uploaded or changed in the inventory. Stickers not changed.
- Next: once credits are topped up, OBJ-149 hero (brushed), then other colours and context shots for any approved hero.

### Wed 11 Nov 2026
- Magnific balance **6,530** at start, **6,465** at end (65 spent: 1 render). Note: 15,840 was left after 8 Nov; about 9,300 went to other Magnific work since (OBJ-167 and OBJ-003 room composites, OBJ-173 mood, social mock-ups, a 3D test), not this session.
- No 8 Nov hero answered yet, so no other colours or context shots. Day-1 list not approved, so worked the approved-drawing list: the only one left with no images is OBJ-015 (on hold). OBJ-012 skipped (recommended out, wave-2 sofa); OBJ-001 still skipped (maker mark).
- OBJ-015 Chocolate: v1 kept first try (two crossing plates, seat ledge, leather back, seat and lumbar cushions match the photo; own room, not the reference's). Frame drifted olive (hue 27°, sat 0.51) → recoloured to Chocolate #4A2A1B inside a hand-drawn product-only mask, leather and vase excluded → v1c (plate median now 74,41,27 vs 74,42,27). Frame and leather now read close in tone.
- **Render files not pushed**: the repo is public (same reason as the drawings run). v1 and v1c are in Magnific and were sent to Sabry; only STATUS and the inventory are pushed. Inventory .md and .csv updated. Nothing uploaded to Drive, stickers not changed.
- Approvals: none yet. Next: on approval, other colours and context shots for the approved heroes; then the 3 drawing drafts (173, 115, 075) once approved, or day-1 list products from the reference photo if Sabry says so.

### Sun 8 Nov 2026
- First run. Magnific balance 16,100 at start, **15,840** at end (260 spent: 4 renders × 65). Day-1 list not yet approved, so worked the approved-drawing products, simplest first. Drawings not yet in `venture/drawings/`, so all three came from the reference photo (cropped, own house scene, reference room not copied).
- OBJ-152 Ink pair: v1 rejected (left table lost its waist), v2 kept; hue drifted to 208°, recoloured to Ink 221° inside a product box mask → v2c.
- OBJ-002 Oxblood: v1 kept first try; hue 4° → recoloured to 354° inside a solid product silhouette (floor untouched) → v1c.
- OBJ-038 Carbon: v1 kept first try; plates had a teal cast → neutralised inside a product mask → v1c. Cut-out shape is close to, not identical to, the reference.
- Files: `plan/images/OBJ-{002,038,152}/` (JPEG, 2000 px). Inventory .md and .csv updated. Nothing uploaded to Drive, stickers not changed.
- Approvals: none yet. Next: other colours and context shots for approved heroes; then OBJ-015 (hold) or day-1 list products.

## Drawings and files

### Thu 12 Nov 2026
- Checked: repo still public (GitHub search API: visibility public), no "approved" for any drawing in this file. So no import push, no approval routine, no Drive upload, no sticker change.
- Found: the 11 Nov import (410 files), the 3 drafts' generators and `objekt_sheet.py` never reached GitHub and were lost with that run's workspace. Step 1 not redone today: it cannot be pushed while the repo is public. The Drive export still holds everything.
- Two DRAFT sets made (5 A3 sheets each, EN/AR, SVGs, DXFs, nest; every PDF page rendered to PNG and looked at; DXFs read back, parts inside the sheet, 10 mm gaps; "DRAFT" present in the PDF text):
  - **OBJ-164** corner shelf pair: one kite blank, one fold (front face down to the wall corner). Top 220 × 220 from the reference caption, drop 200 estimated; fold 127.9° from flat; cut 1,035 mm per shelf. Book size (250 × 250 × 60) conflicts: see decisions.
  - **OBJ-149** ashtray: four 140 × 38 plates in a # with halving slots (4 × 19), a separate U-tray 95 × 95 × 34, R12 inside. 140 × 140 × 38 from the book; the rest estimated from the photos.
- Skipped: OBJ-100 (another maker's engraved mark on the reference) and OBJ-176 (recognisable designer piece). Rebuilt the shared helper as `venture/src/drawings/objekt_sheet.py`.
- Not pushed (public repo): drawings and generators were sent to Sabry as a zip in the run's message. Only this STATUS update is pushed.
- Next: your answers on the 5 open drafts; then OBJ-171, 165, 175 (no reference image in `images/`; I take it from the production book slide).

### Wed 11 Nov 2026
- **OBJ-190 side table (Sabry, 11 Nov):** drawn from his 3 photos and 55 x 55 x 45 cm, redrawn after his correction (top has 4 Vs = 8 sides; each leg one V matching the top), approved by Sabry the same day, finish brushed stainless, number confirmed. Set: `venture/drawings/OBJ-190/` (PDF, 5 SVG, 4 part DXFs, nest DXF), generator `venture/src/drawings/make_obj190_rev0.py`. Uploaded to a new Drive folder OBJ-190 on his yes; added to the Google product sheet (Products row 146, Design folders) and the day-1 list. Next: Production review; ask him for real dimensions or the CAD.
- Step 1: 410 files from the Drive export (POLYCRAFT-EXPORT) are in a local commit: `venture/drawings/` (8 products with superseded revs), `venture/src/` (21 generators and tools), `venture/workspace-db/` (115 JSON), `venture/artifacts/` (10 pages), `venture/plan/` (7 PDF, DOCX, XLSX). Sizes checked against Drive, no font files. IMPORT.md ticked.
- **Not pushed.** The GitHub repo is public, and the push was blocked because it would publish the business plans, partner deck, cost template and drawings. Everything from this run exists only in the run's workspace until the repo is private (or you say what may be public). See decisions.
- Step 2: day-1 products with no approved drawing: 35 of the 41 (approved: 002, 038, 152, 166, 167, 169; OBJ-001's file sits with Production). Simplest first, sheet metal: 173, 115, 075, then 100, 164, 176, 149, 171, 165, 175, 132, 020, 068, 080, 072, 125, 172. Moulded or printed (own set type): 142, 156, 004, 099, 145, 147, 151, 154, 104, 069, 094, 095, 103, 085, 155. OBJ-003 waits on its real size; OBJ-137 has a prototype.
- Three DRAFT sets made (5 sheets, SVGs, DXFs, nest; PDFs rendered to PNG and checked, DXFs read back, nests inside the sheet): **OBJ-173** mirror cube planter 150 (one cross blank, 4 welded corners), **OBJ-115** tray 400 × 280 × 45 (one blank, 2 folds, 2 hand slots, no welds), **OBJ-075** floor planter pair, A Ø300 × 390 and B Ø240 × 290 on a foot ring. All sizes estimated, drawn exactly from the reference. New shared helper `venture/src/drawings/objekt_sheet.py` (prints PDFs with Playwright on Linux).
- No approvals written in this file yet, so no approval routine, Drive upload or sticker change.
- Next: your answers on the 3 drafts; then 100, 164, 176.

## Website (Shopify)
### 12 Nov 2026 (Thu)
- Ran: pulled main (fccbb73); `npm ci`; `theme check` 48 files, no offenses. Store confirmed OBJEKT / hs1a1c-ut. **No store writes.** CLI not logged in.
- Found: store **public** (password protection off). Live theme is `190221484256` "OBJEKT hide single option (draft 12 Nov)", published 11 Nov ~23:15 UTC; 4 more draft themes made 11 Nov. 10 products active and on the Online Store; 0 orders. Menu `objekt-main` now Shop, About, Custom request; new page Custom request (form app "Powerful Form Builder").
- Browser check of the public site (Playwright, 1440 and 375 px): home, Furniture, all products, SLAB, TORSO, Custom request, Delivery & Returns all 200, no horizontal scroll, no placeholder text, no font files. Checkout reached with PYRA in the bag (no details entered, no order): Egypt address form, **PayPal the only payment**, total in EGP.
- Gaps on live products: all variants 0 kg (every order 118 EGP); SLAB, BLOK, SPAN and TORSO have no variant lead-time days, so the buy box shows no days (SLAB and TORSO have it only as product text) — catalogue session to fill `lead_time_days_min/max`. CAIRN, OCTA, SPAN, INGOT in no collection (already on the list).
- Repo vs live theme: 23 files differ, 4 live files not in git (`header-zara.css`, `look.css`, `main-custom-request.liquid`, `page.custom-request.json`). Checksums saved in `website/docs/LIVE_THEME_2026-11-12.md`. Not pulled (needs CLI). No theme push: 189754769632 is no longer the theme that matters.
### 11 Nov 2026 (Wed)
- Ran: pulled main (760de90); `npm ci`; `theme check` 48 files, no offenses. Store confirmed OBJEKT / hs1a1c-ut. **No store writes.**
- Found the 10 Nov website work on an unmerged branch (`claude/handoff-section-7-shipping-umz7rf`). Brought its `website/` files onto main; theme files now match the unpublished theme by checksum. Before this, a push from main would have undone the 10 Nov theme changes.
- Store re-read matches the 10 Nov log: 50 products, 0 active, no `[TEST]` items; menus, Delivery & Returns page and 5 policies in place. Shipping policy now has the 15 kg / 1,200 EGP line. Three small typos left in admin policies.
- QA launch check "no active product with placeholders" passes (0 active). Checkout, Paymob, browser QA: not tested (no sign-in, no CLI login, preview behind password).
### 10 Nov 2026 (Tue)
- Cleanup (Sabry's yes): 3 test products and 2 test articles deleted; 13 preview-active products to draft; 4 unknown-rights photos and 8 placeholders deleted.
- Delivery & Returns page and footer link; Sabry pasted the 5 policies; `footer-policies` lists them. Showroom footer column and Contact page (address, WhatsApp). The Edit hidden from the main menu. OBJ-099 alt text without render mention.
- Shipping, Egypt only: Standard delivery 118 EGP up to 15 kg, Large order delivery 1,200 EGP over 15 kg. Every product needs its packed weight (all 0 kg now). Lead time shown in days (new variant fields; theme updated). Footer menu: Shop, Support, Policies.

**Pre-launch cleanup checklist (HANDOVER section 8; store re-read 12 Nov):**
- [x] OBJ-099: v2 Oxblood images in, variant linked, v1 removed (8 Nov)
- [x] Delete the 3 `[TEST]` products and 2 `[TEST]` articles (10 Nov)
- [x] 13 `preview-active` products back to draft (10 Nov); drop `preview-active` / `placeholder-data` tags only when real data is in
- [x] Remove the 4 reference photos of unknown rights and the 8 placeholder images (10 Nov)
- [x] `objekt-main` expanded: Shop, The Edit, About (9 Nov)
- [x] Footer menus, Delivery & Returns page, 5 policies (10 Nov). Open: 3 typos in admin policies, lawyer check
- [ ] Shipping: packed weight on every launch product; checkout rate test (Egypt, under and over 15 kg)
- [ ] Paymob: Sabry signs in; then test mode, activate, capture Automatic, test order and refund
- [x] QA launch check "no active product with `placeholder-data`, 9999.00 or [PLACEHOLDER]" passes (12 Nov: 10 active, none has them; PYRA sizes say "approximate, to confirm")
- [~] Sabry only: theme published and password removed (found 12 Nov, not logged); Paymob live still open. Horizon kept unpublished as rollback.
- [ ] Live theme pulled into git (needs CLI login)

### Shopify catalogue
<!-- daily catalogue session; dated, newest first, last 3 entries -->

#### Wed 11 Nov 2026
- Ran: `get-shop-info` = OBJEKT / hs1a1c-ut, EGP. Read all 50 products (all draft, no duplicate OBJ codes) and the 5 collections. Pulled main (4849649).
- Nothing new from Sabry or Polycraft per product since 8 Nov (no name, price, size, colour or image approval). Store-wide answers (10 Nov: 50% deposit, 7–14 or 30–45 days per item, shipping by weight) set no per-product value, so no existing product changed.
- **Store writes (CHANGELOG 11 Nov): created 8 drafts** that the plan and the book both list as IN but were missing: OBJ-020, 152, 156 (Furniture), 094, 103 (Table & Living), 132 (Objekts), 068, 155 (Planters). Same build as the other drafts: OBJ-code title, placeholders, `placeholder-data` tag, made_to_order, right collection. No lead time, colours, variants, images or weight. Read back: 58 products, 0 active.
- Seen: no product (old or new) is on the Online Store channel (`resourcePublicationsCount` 0). Activating alone may not put them on the site. See decisions.
- Day-1 list still not approved: the 41 below are the agreed set. The 4 on hold (015, 049, 148, 159) and the 15 off-plan store drafts are not in the table.
- Readiness: **0 of 41 ready to activate.** Placeholders left in place on all.

**Readiness (11 Nov; ✓ done, ✗ missing)**

| OBJ | Collection | Named | Copy EN | Copy AR | Price | Lead time | Sizes | Variants | Images | Collection | Metafields | SEO | Placeholders gone | Ready |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OBJ-002 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero AI render pending | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-003 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-020 (new 11 Nov) | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-038 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero AI render pending | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-137 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-142 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-152 (new 11 Nov) | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | hero AI render pending | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-156 (new 11 Nov) | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-165 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-166 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-167 | Furniture | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-001 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-094 (new 11 Nov) | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-095 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-103 (new 11 Nov) | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-104 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-115 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-169 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-171 | Table & Living | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-004 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-099 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | 4 colours, not confirmed | 5 AI renders on store, use not approved | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-100 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-125 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-132 (new 11 Nov) | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-145 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-147 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-149 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-151 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-164 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-172 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-175 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-176 | Objekts | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-068 (new 11 Nov) | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-069 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-072 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-075 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-080 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-085 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-154 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-155 (new 11 Nov) | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |
| OBJ-173 | Planters | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ | no |

What every product lacks: approved name (EN, AR), price incl. VAT, lead time type (7–14 or 30–45 days, Polycraft), real dimensions, packed weight, colours actually offered (then variants), approved images, short description, story, materials, care, SEO title and description. Extra: OBJ-166 heights (850 vs 700 mm), OBJ-175 panel options, OBJ-176 four colours, OBJ-099 colours (store vs book), OBJ-152 and OBJ-156 sold as pair or each.

#### Sun 8 Nov 2026 (first run)
- Ran: `get-shop-info` = OBJEKT / hs1a1c-ut, EGP. Read all 53 products (titles, status, type, tags, collections, variants, metafields), the 4 collections and the `colour` metaobjects.
- Day-1 list not approved yet, so I worked only on the 33 products that the plan, the production book and the store all agree on. The 8 agreed by plan and book but not in the store (OBJ-020, 068, 094, 103, 132, 152, 155, 156) are **not created**; I create them as drafts the day the list is approved.
- Structure checked on the 33: titles are OBJ codes, every one is in the right collection for its plan category, type and tags match, `custom.reference` set, fulfilment `made_to_order` with placeholder lead time. No duplicate OBJ codes.
- Store writes (CHANGELOG 8 Nov): `colour` metaobjects got their hex from `brand/COLOURS-FINISHES.md`, and the missing eighth colour **Chocolate** was added; OBJ-099's four colour variants and product colour list now link to the colour entries. Read back OK. Not seen in a browser.
- Not written: no prices, sizes, lead times, copy, variants or images. Nothing in CONTENT_TO_SUPPLY or STATUS is supplied by Sabry or Polycraft yet (section 3d is all "proposed" or blank), and no render is approved for the site.
- Seen: OBJ-148 (on hold, rec. drop) is **active** (`preview-active`) with a reference photo. Website session's revert list covers it.
- Readiness: **0 of 33 ready to activate.** Placeholders (9999.00, [PLACEHOLDER], 00 cm, `placeholder-data`) left in place on all.

Readiness table of 8 Nov replaced by the 11 Nov table above (in git history).

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
