# objekt faux books: plan and art direction (draft 18, 10 Nov 2026)

Status: proposal for Sabry. Decided so far (10 Nov): title typeface Galak Round; sold as singles and as a set of three; titles to be witty, in the line of "Objekts of Character"; made as a solid block, paper; day 1; a print set of three added (tiger, cow, stripe). Draft 5 (Sabry's review): colour audit, lighter type, logo as the signature. Draft 6: sizes fixed from Sabry's 10 × 25 × 4.5 cm. Draft 7: depth is 4.5 cm on all three (Sabry: 5.5 cm was not logical). Draft 8: width and length reset to real-book proportions (Sabry: the sizes would not look real). Draft 9: spine text in capitals (Sabry); first design flats drawn for all eleven volumes. Draft 10: spine redesigned (larger, reads along a stack, symbol only, fixed logo positions). Draft 11: prints wrap onto the spine (Sabry). Draft 12: tiger redrawn as a realistic pattern from a reference photo (Sabry). Draft 13: first renders of all eleven volumes and three sets. Draft 14: renders v2 with paper texture and soft shadows (Sabry). Draft 15: sets aligned (Sabry). Draft 16: one AI test render (FB-08). Draft 17: renders v4 with woven bookcloth texture; AI couch test (Sabry). Draft 18: couch comp with exact lettering overlaid (Sabry). Nothing is costed or sent to anyone.
Direction sheet: `faux-books-direction-sheet_diagram_v8.svg` (PNG copy beside it). It is a flat diagram with stand-in lettering, not a render and not a photo.

## 01 // the idea
A small library of decorative volumes that work as colour blocks with type on them. One format, our own titles, the eight objekt colours. Sold one at a time or as a stack of three.

What the five references share, and what we take:
- One flat colour per book, matte. We take this, in paper instead of cloth.
- One big title block and almost nothing else. We take this, in a lighter weight than the references.
- A series: the same title in several colours, stacked in threes. We take this.
- What we do not take: real titles and brand names (Dieter Rams, Taschen, Ralph Lauren, From The Archive, Heaven Mayhem, Sociotype). Those are other people's marks. Our books carry objekt titles only.
- The mixed-serif shelf (reference 3) is the commodity version. We stay away from it: no fake publishers, no gold foil, no mixed fonts.

## 02 // where it sits
- Website category: Table & Living. Internal category: Desk and book, which has a day-1 target of 2 and nothing in the library.
- Process: outside printer and binder. It is not one of the four factory processes, so it sits outside the process mix and cannot carry "Made at Polycraft, Cairo".
- Count: list it as **two products**, not eight. One product "faux book" with eleven variants (eight plain, three print), and one product "set of three" with three variants (plain A, plain B, print). That meets the Desk and book target of 2 and keeps the category under the 10% rule. Next free numbers look like OBJ-177 and OBJ-178; not assigned until you say so.
- Timing: **day 1** (Sabry, 10 Nov). Launch is Fri 20 Nov, ten days away. See section 06 for what that needs.

## 03 // art direction

**Colour.** Cover and lettering both come from `brand/COLOURS-FINISHES.md`. No ninth colour.

| Vol. | Cover | Lettering | Contrast | Size |
|---|---|---|---|---|
| 01 | Bone | Objekt Green | 5.6 : 1 | M |
| 02 | Putty | Chocolate | 6.1 : 1 | M |
| 03 | Carbon | Bone | 12.5 : 1 | L |
| 04 | Ink | Putty | 6.8 : 1 | L |
| 05 | Oxblood | Bone | 10.0 : 1 | S |
| 06 | Clay | Bone | 4.1 : 1 | S |
| 07 | Chocolate | Putty | 6.1 : 1 | L |
| 08 | Objekt Green | Bone | 5.6 : 1 | S |

**Colour audit (draft 5).** Contrast computed from the hex values with the WCAG formula. Screen values only: confirm on printed samples.
- Draft 4 failed twice. Oxblood with Clay lettering and Clay with Oxblood lettering were both 2.4 : 1, too low to read at a glance. Both now use Bone.
- Clay with Bone is 4.1 : 1. Fine for large title type, the weakest pair on the sheet. If a printed sample reads weak, keep Clay for the print set only.
- Carbon, Ink, Oxblood and Chocolate sit between 1.0 and 1.3 : 1 against each other. On a shelf they read as one dark mass, and in a stack two touching darks lose their edge. Rule: a set never has two of them. Ink is the weakest of the four, so it is a single only.
- Bone and Putty are only 1.7 : 1 apart. Never side by side in a stack without something between. Bone lettering on Putty is 1.7 : 1: never.
- Draft 4 had Carbon lettering on Bone and Putty. Changed to Objekt Green on Bone and Chocolate on Putty: same legibility, more colour, less like black-on-white stationery.
- Print set: cow patches changed from Carbon to Chocolate on Bone (10.1 : 1), softer and in the palette's own warmth. Stripe changed from Ink to Objekt Green, so the signature colour appears in the print set. Tiger stays Carbon on Clay (3.0 : 1, decorative only; the title sits on a cleared area).
- Sets: A = Carbon, Bone, Oxblood. B = Chocolate, Putty, Objekt Green. Print = Clay, Bone, Objekt Green. Each has one dark, one light, one colour.

Honest note: the references are loud (lime, pink, cobalt, orange). The objekt palette is quieter and darker, so our stacks read warmer and more grown-up. Oxblood, Clay and Objekt Green carry the colour.

**Type (revised, draft 5).** You said the stand-in felt very bold and compact, and the spacing needs testing at actual size. Draft 4 was Inter ExtraBold at tight tracking: not Galak Round, and heavier than it. Draft 5 sets Regular with open tracking. Still not tested in the real face (not licensed, not in git).
- Weight: Regular, never bold. Caps for titles, per the brand guide.
- Tracking: open by about 2% (draft 4 was about -2%).
- One size for every line of a title. Never shrink a line to fit.
- Three-line titles: longest line no wider than 70% of the cover. Line gap about 0.4 of the cap height. No line is a single short word, so "NOT A / BOOK", "OBJEKTS OF / CHARACTER", "USELESS / ON PURPOSE". Where three lines are needed, break for shape and keep the lines close in length.
- Optical edge: round and diagonal letters (O, C, J, T) hang slightly past the left margin so the edge looks straight. Done by eye in the final artwork.
- Top margin equals left margin.
- Spine: ALL CAPS, Regular, tracking about 5%. One size on every volume (about 16 mm type, 12 mm cap height, twice draft 9), up to two lines, line gap 0.4 of the cap height. Size is set by the longest line on the shortest book (DESIGN WORTH on the 20 cm Small) and by the 45 mm spine width.
- The numbers above are starting values. Test: print one S, one M and one L cover at actual size on the chosen stock and judge at arm's length, then adjust.

**Signature (revised, draft 5).** You said the small symbol felt disconnected from the titles. Draft 5 makes the logo the signature and stops using the symbol as decoration.
- Front: the title and nothing else. No symbol, no volume number.
- Back: the full objekt logo (symbol over wordmark), centred low, in the lettering colour.
- Spine, reading bottom to top: logo at the foot, then volume number, then title. Same position on every volume, so a stack reads as a family and the logo is the one thing every spine shares.
- Always the supplied logo file, never a retyped wordmark.
- Minimum logo width 25 mm in print (brand rule). The full logo laid along the spine at 25 mm is about 16 mm tall, so it fits the 45 mm spine, the same on all three sizes. The full logo, wordmark included, goes on every spine. Resolved.
- Option, not drawn: a blind-embossed symbol on the front. A paper wrap cannot do this cheaply; ask the maker if you want it priced.
- Logo colour is the cover's lettering colour, so the guide's one-colour rule holds. Still needs your OK as an addition to the six pairings in the guide.

**Titles (Sabry chooses).** Eight plain volumes, one title per colour. Each volume has one fixed size, so every set of three steps down. Line breaks as set on the sheet.

| Vol. | Title |
|---|---|
| 01 | NOT A / BOOK |
| 02 | SHELF / LIFE |
| 03 | HEAVY / READING |
| 04 | JUDGE / THE / COVER |
| 05 | OBJEKTS OF / CHARACTER |
| 06 | USELESS / ON PURPOSE |
| 07 | COFFEE / TABLE / BOOK |
| 08 | DESIGN / WORTH / NOTICING |

- Spares: NOTHING TO / READ · MADE TO BE / LOOKED AT · THINGS WITH / PRESENCE · STILL / LIFE · FORM HAS / OPINIONS · VOLUME OF / NOTHING · BETWEEN / FUNCTION AND / EXPRESSION.
- The brand word is written lowercase (objekts). Vol. 05 sets it in caps on the front because every front title is caps; the spine keeps it lowercase. Say if you want it lowercase on the front.
- English only, per the locked naming decision.
- "Vol." is a title number, not an edition number. Copies are not numbered (numbered editions belong to Brand 01).
- Sets of three: one L, one M, one S. Proposed fixed sets: plain A (03 + 01 + 05), plain B (07 + 02 + 08), print (09 + 10 + 11). Ink (04) and Clay (06) are singles only.

**The print set (Sabry, 10 Nov).** Three printed volumes beside the eight plain ones, sold as singles and as one set of three.

| Vol. | Title | Print | Colours | Lettering | Size |
|---|---|---|---|---|---|
| 09 | EASY / TIGER | tiger stripe | Clay ground, Carbon stripes | Bone | L |
| 10 | HOLY / COW | cow patch | Bone ground, Chocolate patches | Chocolate | M |
| 11 | BETWEEN / THE / LINES | stripe | Bone ground, Objekt Green bands and spine | Objekt Green | S |

- Flat graphic prints, drawn, not photographic fur. Two objekt colours each, so they stay in the palette.
- The print keeps clear of the title so the title reads.
- The drawings on the sheet are placeholders made in code. Final prints need to be drawn properly.
- Prints stay on these three only. The other eight stay plain.

**Material and finish.** Solid block, paper (Sabry, 10 Nov). Read as: a closed block that does not open, wrapped in printed paper, matte. To confirm: is the inside a block of blank pages (looks like a real book from the edge, heavier) or a plain board or foam core with a printed page edge? Colour and lettering print in one pass, so the printer can match the eight colours from the hex values and a sample. Matte only: uncoated stock or matte lamination. No gloss, no metallic, no dust jacket.

**Format (draft 8, checked against real books).** Sabry's 10 × 25 × 4.5 cm would not look real. The reason is the face: 10 × 25 is a 1 : 2.5 strip, a ruler or a clutch box. Real books are 1 : 1.25 to 1 : 1.45. The 25 cm length and 4.5 cm depth are real, so I kept them and changed the width.

What real books measure (retailer listings, not publisher spec sheets; they differ by a few mm):

| Book | Width × height × depth | Face ratio |
|---|---|---|
| [Ralph Lauren, Rizzoli, anniversary edition](https://new.completebook.com/book/9780847861118) | about 23.7 × 30.5 × 4.6 cm (9.3 × 12 × 1.8 in), about 3 kg | 1 : 1.29 |
| [Dieter Rams, Phaidon](https://piperpress.com.au/products/dieter-rams-as-little-design-as-possible) | about 21.1 × 27.7 × 4 cm, about 2 kg ([Soda Books](https://sodabooks.com/publications/product-design/dieter-rams/), [Finnish Design Shop](https://www.finnishdesignshop.com/en-ch/product/dieter-rams-as-little-design-as-possible)) | 1 : 1.31 |
| [Taschen, Design of the 20th Century, small edition](https://www.cocoli.com/en/at/produkte/design-des-20-jahrhunderts-good) | about 14 × 19.5 cm, spine up to 4.5 cm in one listing | 1 : 1.39 |
| [Decor faux book set, three sizes (Walmart listing)](https://www.walmart.com/ip/17325767393) | 22 × 15 × 4.5, 25 × 18.5 × 3.8, 27 × 17 × 4 cm | 1 : 1.47, 1 : 1.35, 1 : 1.59 |
| Coffee table books in general ([listing](https://storables.com/furniture/living-room-furniture/what-size-are-coffee-table-books)) | 9 × 12 up to 13 × 17 in (23 × 30 up to 33 × 43 cm) | about 1 : 1.3 |

- Real thickness runs about 3.8 to 5 cm for books and decor sets. 4.5 cm is right.
- Weak sources: the decor figures come from marketplace listings and some give set sizes, not single books. The Taschen size has outliers (20 × 15 × 4.8). Confirm with the maker's templates before any print file.

| Size | Width × length × depth | Face ratio | Real match |
|---|---|---|---|
| L | 23 × 30 × 4.5 cm | 1 : 1.30 | Ralph Lauren, coffee table book |
| **M** | **18 × 25 × 4.5 cm** | 1 : 1.39 | decor set (25 × 18.5), keeps Sabry's 25 cm length and 4.5 cm depth |
| S | 14 × 20 × 4.5 cm | 1 : 1.43 | Taschen small edition |

- Width steps 5, 4 cm and length steps 5, 5 cm, so a stack shows three clear steps.
- Depth is 4.5 cm on all three (Sabry, draft 7). One block thickness and one spine width for the maker. Lying flat, a set is 13.5 cm high.
- Weight: real large books weigh 2 to 3 kg. A solid block of blank pages at 23 × 30 × 4.5 cm would be about the same, which is heavy to ship across Egypt. For the Large, the board or foam core inside is the better option. Not measured or costed.
- Kept as an option, not recommended: the original 10 × 25 slim format. It reads as a clutch or a mailer box (like reference 1), not a book.
- Drawn to scale on the sheet.

**Front layout (draft 8).** With a 18 cm face the title goes back across, top left, as on most of the references. The along-the-length layout from draft 6 was only needed for the narrow 10 cm face; it stays on the sheet as an option.
- Title block at top left, margin 8% of the width on the left and top.
- Size rule: longest line at most 70% of the width. Cap height on the Medium is about 12 mm.
- The line-break rules above apply.

**The stack rule.** One dark, one light, one colour. Largest at the bottom.

**Images.** AI renders in the house style (`plan/HOUSE-STYLE.md`): low window sun, plaster, a stack on one of our tables or plinths. Named `ai-render`. Real photos replace them when samples exist.

## 04 // decisions

Decided: solid block in paper · Galak Round titles · singles and a set of three · day 1 · sizes from real books: M 18 × 25 × 4.5 cm, L 23 × 30 × 4.5 cm, S 14 × 20 × 4.5 cm.

Open:
1. Inside of the block: blank pages, or board or foam core.
2. Titles: approve or swap the eleven.
3. "objekts" lowercase on the front of Vol. 05, or caps like the rest.
4. Sets: the three fixed sets above, or pick one from each size.
5. Confirm the three sizes above, in particular Medium width 18 cm instead of 10 cm.
6. Price, and whether stock is made up front or made to order.

## 05 // blockers
- **Font and logo licence.** Galak Round, PP Mori and the logo lettering are not licensed for public or commercial use. Lettering on a product we sell is commercial use. This is the first thing to clear, and it does not depend on anyone but the foundries and you.
- **Maker.** No printer or binder identified. Their lead time decides whether real pieces exist by 20 Nov. Unknown.
- **Logo colour.** The brand guide lists six logo pairings, none on product colours. The symbol on a coloured cover needs your OK.
- **Cost, price, size, weight, lead time.** All unknown. Nothing here is costed.

## 06 // day-1 path (20 Nov)
The store can list the books on day 1 with AI renders, like every other product. Whether a customer can receive one that week depends on the maker, which I cannot check from here.

| When | What | Who |
|---|---|---|
| Now | Answer the open decisions. Start the font and logo licence. | Sabry |
| Now | Call a printer and binder: can they do a paper-wrapped solid block in three sizes, matte, eight colours, and how fast | Sabry or Youssef |
| After sizes are set | Print-ready flats (front, spine, back) for eleven volumes, with the three prints drawn properly | needs the licensed font files, supplied outside git |
| After the maker says yes | One sample per size. Check colour against the hex, lettering sharpness, corners, how the stack sits | maker, Sabry |
| Any time | AI renders: eleven singles, three set heroes, one context image. Named `ai-render` | Claude, on your go |
| Before launch | Names (objekt-naming), OBJ numbers, add to the day-1 list and Shopify draft. Nothing live without your yes | Claude drafts, Sabry approves |

If the licence or the maker is not confirmed in time, the honest options are: list as pre-order, or hold to the first drop after launch.

Not tested: everything. This is a paper plan and one diagram.

## 07 // spine and logo system (draft 10, Sabry's notes)

1. **Larger spine type.** The spine is 45 mm deep on every size, so one size fits all: about 16 mm type, 12 mm cap height, up to two lines. Draft 9 was half that. It is sized to the longest line on the shortest book, and the same size goes on the Large and Medium so stacks match.
2. **Reads along a stack.** Lying flat with spines out and the head to the right, a book's spine reads left to right, so a stack reads like a stack of labels. Standing on a shelf it reads bottom to top, the UK and European way. Spine titles are broken into two lines to suit the 45 mm depth: NOT A / BOOK, JUDGE THE / COVER, COFFEE TABLE / BOOK, DESIGN WORTH / NOTICING, BETWEEN / THE LINES. Fronts keep their own breaks.
3. **Symbol only on the spine.** The wordmark and the volume number are gone from the spine. The wordmark stays on the back, with the symbol. The volume number is now internal only (FB-nn). Say if you want it back on the spine.
4. **Fixed logo positions on every size.**
   - Spine symbol: 20 mm wide, 14 mm from the foot, centred across the spine.
   - Spine title: starts 10 mm after the symbol, so the symbol leads the title in a stack.
   - Back logo (symbol and wordmark): 40 mm wide, centred on the back, 14 mm from the foot. The same size and the same distance from the foot on the Small, Medium and Large. Before it was 28% of the width.
   - Everything is measured from the foot, so the same fixed numbers work for any size.
5. **Brand check.** `brand/BRAND.md` sets a 25 mm minimum for the full logo and says to use the symbol alone below that. The spine symbol is 20 mm, so it is within the symbol-only use. The logo colour on product colours still needs your OK.

## 08 // artwork (draft 3, 10 Nov)
Design flats for all eleven volumes are in `plan/faux-books/artwork/`: one SVG per volume (`FB-nn_title_flat_design-draft_v3.svg`) and `faux-books-flats_contact-sheet_v3.png`, which also shows the three sets lying flat. Each flat is back, spine and front at finished size in mm, drawn by `make_flats.py` (run `python3 make_flats.py <repo root>`). The v1 and v2 files are superseded versions.

What is in them:
- Front: title at top left, all caps, one size per title, longest line 70% of the width.
- Back and spine: per section 07.
- Prints (09, 10, 11) wrap round the spine as well as the front and back, so the print shows on a stack. The spine carries the icon only, never the wordmark.
  - Tiger (redrawn, draft 12): built the way a real tiger's coat is marked, from the reference photo Sabry sent (structure only, nothing traced: that photo is another brand's product, so it is a mood reference, not a source). The V line of the pattern runs down the spine, and the stripes sweep out over the back and front in V shapes pointing down. Each stripe is long and wavy, thick near the spine and tapering to a point, with ragged edges, and short broken dashes sit between them. Stripes stop short of the front title, the back logo and the spine icon, so those stay clear. The spine title sits over the stripes: Bone on Carbon and on Clay both read, but test it on a proof. Carbon on Clay as before; Chocolate on Clay is a softer option, closer to the dark brown in the photo (2.5 : 1 against 3.0 : 1).
  - Cow: patches continue across the fold. The back logo, the front title and the spine title and icon each have a clear zone, and two or three patches sit in the free head end of the spine.
  - Stripe: the bands run into a solid Objekt Green spine with Bone lettering, so the stripe wraps without crossing the title.
- Dashed lines show the folds. They are not part of the artwork.

What they are not:
- Not print-ready. No bleed, no wrap allowance, no board turn-in: the maker's template is not known.
- Lettering is Inter. Galak Round is not licensed, and the real face is rounder and wider, so every line breaks and sizes must be rechecked once the font file is supplied (kept outside git). A wider face may force the spine type smaller; the longest line is only a few mm from the limit.
- The tiger, cow and stripe drawings are made in code and are placeholders. The tiger is now close to a real coat pattern, but a designer should still tune it by eye. The cow patches are plain blobs and need the same attention.
- Colours are screen values from `brand/COLOURS-FINISHES.md`. Confirm against printed samples.
- Not tested at actual size on paper. Print one proof of each size before anything else.

## 09 // renders (draft 2, 10 Nov)
Renders of all eleven volumes and the three sets are in `plan/faux-books/renders/`: `FB-nn_title_3d-mockup_v2.jpg` (1600 × 2000, 4:5), three set images (`FB-set-A`, `FB-set-B`, `FB-set-print`) and `faux-books-renders_contact-sheet_v2.jpg`. The v1 files are the superseded first pass. The three set images are at v3 (aligned); the single books stay at v2.

What they are:
- 3D mockups built from the design flats, not AI renders and not photos. I used 3D instead of an AI image model because the type, logo and print placement have to stay exact; an image model redraws lettering.
- Scene follows `plan/HOUSE-STYLE.md`: plaster wall, a low window sun with a hard-edged light and shadow, a limestone-tone plinth, one clay vase as the only prop (a plain earth tone, never a brand colour).
- Singles stand at a three-quarter angle so the front and the spine show. Sets lie flat, spines out, head to the right, large at the bottom, aligned: spines flush on the same front plane and each book centred on the one below (v1 and v2 had a small stagger).
- Cover colours were checked against the brand hex values by sampling pixels: Clay, Objekt Green and Carbon land within a few points. Bone reads slightly warm under the sun. Putty and Bone are close and read as one family.

What v2 adds over v1 (Sabry: more realistic, paper texture, soft shadows):
- Paper texture: a fine fibre bump on every cover, spine and edge. The raking sun picks it up, so the matte paper reads as paper. Strength is a guess, not matched to a real stock.
- Soft shadows: the sun shadow is now blurred, and each book and the vase has a soft contact shadow where it meets the plinth.
- Rounded board edges instead of sharp box corners, so the edges catch light.
- A little film grain and a slight vignette, as `plan/HOUSE-STYLE.md` asks.
- Brand colours rechecked by sampling: Clay and Objekt Green are still within a few points of the hex values.

What they are not:
- Not product photography. Still CG: no board edge wear, no real page block, no printing artefacts. The paper grain is a generic texture, not scanned from the real stock. A real sample photo replaces these.
- The lettering is the Inter stand-in, not Galak Round.
- The cow patches and the stripe are still the placeholder prints.
- Page edges are a plain texture. Whether the block has real pages inside is not decided.
- No context image in a real room yet, which `plan/HOUSE-STYLE.md` asks for with each product. The vase and plinth scene is the studio version.
- Sizes are true to scale (L 23 × 30, M 18 × 25, S 14 × 20, all 4.5 cm deep), so the singles use different camera distances to fill the frame; the sets show the real size steps.
- Nothing has been uploaded to the store, Drive or anywhere else.

Source for regenerating them is in `renders/src/`.

### AI test render (FB-08, 10 Nov)
Sabry asked for one render to check an AI pass. I ran the FB-08 mockup through Ideogram 4.5 precise edit (80 credits, one image, Personal project in Magnific; the mockup was uploaded there for this). File: `renders/ai-test/FB-08_design-worth-noticing_ai-render_test_v1.jpg`. This is an AI render, not a photo.
- Good: the lettering and logo on the front and spine came back unchanged, letter for letter. The photographic feel is much stronger: real paper grain, plaster and limestone, believable light.
- Bad: a blurred smudge sits on the lower half of the front cover (a rectangular patch of different green with soft edges). The cover colour drifted, and the spine went much darker than the brand green. The grain is heavy and reads closer to rough card than fine printed paper. The framing shifted slightly and the vase grew.
- Verdict: not usable as is. It needs a retry or two (80 credits each) and a colour check against `brand/COLOURS-FINISHES.md`. Do not use it as product proof.

### Renders v4: texture matched to the reference photos (10 Nov)
Sabry: the AI test did not look real and the texture should match the reference images. Looking closely at references 4 and 5: they are woven linen bookcloth, matte, with a visible fine weave; a bright white page block recessed under overhanging boards; and a hinge groove about 1 cm from the spine. Printed lettering sits on the weave. v4 (`FB-nn_..._3d-mockup_v4.jpg`, `faux-books-renders_contact-sheet_v4.jpg`, sets at v4) now has:
- A woven plain-weave texture on every cover and spine, both as relief and as a tone overlay that also breaks up the printed ink, as on cloth.
- Page block bright white with fine page lines, recessed from the boards at head, foot and fore-edge.
- The hinge groove on the front and back covers, and rounder board edges.
- Softer sun shadows. Brand colours still within a few points of the hex values.
Limits: the weave is a generic plain weave at an exaggerated scale (about 0.7 mm thread pitch), so at thumbnail size it can read as a grid. Not scanned from a real cloth.

Material decision this raises: the references are cloth, but the plan says paper wrap. The real equivalent is a cloth-effect (linen-embossed) printed paper over a solid block, or real bookcloth with the lettering printed or foil stamped on it. Real cloth costs more and needs a binder. For the maker brief: ask for both options. Not decided.

### AI couch comp (Sabry, 10 Nov)
Sabry asked to show set A on the sofa from the references. I used reference 4 (the sofa photo, `4.jpg`) and a second Ideogram 4.5 precise edit (80 credits) with the set A mockup as the design reference. File: `renders/ai-test/FB-set-A_couch-comp_ai-render_test_v1.jpg`. AI render, not a photo.
- Good: much closer to a real photograph, since the sofa, floor and light are from a real photo. Woven cloth, white page block, believable shadows, and Oxblood reads true.
- Bad: the spine lettering is wrong. The middle spine reads "NA A BOOK", the bottom spine has a stray "PIF" beside HEAVY READING, and the logo marks are altered. The old brand name "(PA)PIERRE" is left on the middle book's spine, which must never appear. The middle book came out cream-yellow rather than Bone.
- The photo and the sofa belong to another brand (the books in it are by (PA)PIERRE). Reference only: this comp is for internal review and must not be published or used as product proof.
- Total AI spend so far: 160 credits (two edits).
- Next step if wanted: retry with stricter wording, or composite my exact spine artwork over the AI's spines (cheaper, exact lettering). Not done.

### Couch comp v2: exact lettering overlaid (10 Nov)
Sabry: overlay the exact spine artwork, and the first comp looked photoshopped. File: `renders/ai-test/FB-set-A_couch-comp_exact-lettering_v2.jpg`. Scripts in `renders/src/couch/`. No extra AI credits spent (still 160 in total).
- First attempt replaced each whole face with my artwork. That is what looked photoshopped: tiled grain, a patch on the cream spine, the hinge groove lost. Dropped.
- Final method: keep the photo's own cloth, shading and shadows. Erase only the AI's wrong lettering, grade each surface to the exact brand colour (Carbon, Oxblood, and Bone at 60% strength on the cream book), then set the exact lettering and logos from the design flats, warped to each surface in perspective.
- Now correct and exact: OBJEKTS OF CHARACTER on the cover, NOT A BOOK and HEAVY READING on the spines, with the real logo. The stray "PIF" and the "(PA)PIERRE" name are gone.
- Known limits: the three books are the same length in the AI image, so the 30, 25 and 20 cm steps of the real set are not shown (the spine colour is extended at the head end). The lettering is the Inter stand-in. The cream book is still slightly warmer than Bone. A few pixels of old lettering may remain on the black spine. The sofa and floor are from another brand's photo, so this is an internal comp, not for publishing or product proof.
- For a true-to-size set on this sofa, the way is to remove the AI books and place the 3D set into the photo with matched light. Not done.
