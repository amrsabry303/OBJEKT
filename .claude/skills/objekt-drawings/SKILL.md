---
name: objekt-drawings
description: Make production design files for an objekt product (technical drawings, DXF cut files, assembly, cutting layout, bill of materials, bilingual English/Arabic). Use when Sabry asks to draw, revise or approve a drawing for any OBJ-nnn product, or asks how design files for production should be done.
---

# objekt production drawings

Sabry's standard for how a product goes from an approved design to Production. Built on OBJ-038 (side table) and modelled on his `Planter Drawing 2.pdf`. Read `references/Design-File-Standard.md` first; `references/example_generator_OBJ-038.py` is a working generator to copy and adapt.

## Context to hold

- Brand objekt: small objects, tables, lighting, planters, wall pieces. Egypt first. Production's owner is not decided, so say "Production", never a person's name.
- Flow per product: reference, design (Gate A, Sabry), drawing (Gate B, Sabry approves), Production makeability review (cost, prototype, lead time), then images and listing. The state lives in the objekt workspace artifact https://claude.ai/artifact/HysZRbjoMyneXH8Xbiipcn: stages Inbox, Shortlist, Design, Drawing queue, In drawing, Review, With Production, Pricing, Content, Ready to list, Live, Archive.
- Sabry decides per product whether a prototype is waived. Standing rule from Sabry (27 Oct 2026): always draw the exact design of the reference unless he specifies otherwise for that product. Set `freedom: exact` and `ours: true` on new products unless he says free or custom. Still note the reference source in the product's notes.
- No costs or prices on a drawing. No structural claims or stress figures. No engineering sign-off. We propose; Production decides tolerances, sheet size, joint method, welding, fixings and finish details.

## Steps

1. Read the product's workspace record first (`ArtifactData` list `refs`, `decisions`): stage, notes, freedom, prototype flag, parts, colours. Sabry edits live, so re-read before every write and pin writes with `if_version`.
2. Look at the reference photo (raw GitHub `images/OBJ-nnn.jpg`). If it is a photo of a real piece, trace shapes from it (OpenCV in a venv) and label the shape "traced from the photo, approximate" and every size "estimated from the photo". Ask Sabry for real dimensions or the original CAD.
3. Work out how the piece is actually built before drawing (parts, joints, which parts are separate). Sabry corrected OBJ-038 from one cross-halved plate to four separate legs; check the construction against the photo, and say what was inferred.
4. Build with a generator script (one per product, saved in `_plan/src/drawings/`). Output in `_plan/drawings/OBJ-nnn/`, files named `OBJ-nnn_revN_...`. Move older revisions to `superseded-revN/`; never delete.
5. Sheets, A3 landscape, English and Arabic on everything:
   - Views: front, side, plan, item balloons, the reference photo, overall height, colourways table.
   - Part sheet: each flat pattern at 1:2 with full dimensions, bought-in part positions (for example floor stoppers), joint detail, a DATA table.
   - Assembly: exploded view, detail of bought-in parts, a numbered proposed sequence.
   - Cutting layout: parts nested on one assumed sheet (1250 x 2500 x 3), total cutting length.
   - Bill of materials and numbered notes.
6. Title block (SIZE, SCALE, UNITS, MATERIAL, FINISH, DATE, sheet n/N, REV) with a status stamp above it. Stamp: "DRAFT, not approved, not engineered" until Sabry approves, then "Approved by Sabry <date>. Production review pending. Not engineered". It changes only on a real status change.
7. Colourways: use the objekt colour guide names and hex (Bone #E9E4D8, Putty #B9B2A5, Carbon #222222, Ink #1E2A44, Oxblood #5A1F25, Clay #A8553A, Chocolate #4A2A1B unconfirmed, Objekt Green #37613F). "Charcoal black" means Carbon. A mirror finish means stainless steel and a note flags the few skilled polishers. Mark paint system and gloss "to be confirmed" and CAPCI codes "to follow" until Sabry supplies them.
8. Files per product: PDF set, one SVG per sheet, one DXF per laser-cut part (mm, outline on layer CUT), one nested-sheet DXF (sheet on layer SHEET). No STEP unless it is a simple solid.
9. Verify before showing: render every PDF page to PNG with PyMuPDF and look at it (labels collide easily); read the DXF files back independently and check bounding boxes, vertex counts and that nested parts sit inside the sheet with the spacing claimed. Check the page count with PyMuPDF, not by counting bytes.
10. Show it: send the PDF with SendUserFile, and refresh the workspace page by re-embedding the SVG sheets as data URIs (see how `DRW` and `drwHtml` work in `_plan/src/objekt-workspace.html`), publishing the same URL with capabilities `{"db":{},"user":{}}`. The Drive connector cannot carry a PDF.
11. Upload the finished PDF and production-pack ZIP to the product's design folder in Drive (folder link is in the workspace `FOLDERS` map). Use Chrome: open the folder, add a hidden `<input type=file multiple>` by JavaScript, `file_upload` to it, then dispatch ONE synthetic `drop` DragEvent (dragenter, dragover, drop) on `document.elementFromPoint` in the empty area. A second drop raises a 'replace existing items' dialog: cancel it. Check the folder first so nothing is duplicated, and remove the input afterwards.
11. After Sabry approves: change the stamp, regenerate, move the product to "With Production" (`stage: ahmed`, label only says Production), set the drawing check, append a dated line to the notes, and build a zip of PDF, DXFs and reference photo for him to send. Add the approved PDF and the zip to `PACK` in `_plan/src/objekt-workspace.html` (base64, same shape as OBJ-002) so the card shows Download buttons, and republish with capabilities `{"db":{},"user":{},"downloads":true}`. Do not contact Production yourself.

## Pitfalls seen

- **Numbering clash (11 Nov 2026):** two new products were filed as OBJ-181 and OBJ-182 from a local guess, but those numbers were faux books in the master product sheet, and a pack went into the wrong Drive folder. Always take the number from the Products tab of the OBJEKT MASTER PRODUCT SHEET (id in `CLAUDE.md`) before naming files, and confirm the Drive folder belongs to that product before uploading.
- Arabic text in SVG renders in Chrome headless; right-align Arabic with `text-anchor: end`. Arabic wording is a draft and must be flagged for a technical reader before a factory sees it.
- Put the Arabic line directly under the English one, or in a mirrored right-hand column; do not run both in one block.
- A traced outline can contain artefacts where a part hides the shape in the photo (OBJ-038 had a bump at the bottom neck). Smooth it and say so.
- Heights from a photo shift when a bought-in part such as a rubber stopper is added; keep steel height and overall height as separate figures.
- Sabry is often on his phone: keep decisions to a few one-line answers.
- Moulded products (print-then-mould, GRP, Duco): no flat patterns or cutting layout. Use the OBJ-152 set (`_plan/src/drawings/make_obj152_rev1.py`): views, profile outlines, nesting or pairing sheet if the product is a set, pattern-and-mould sheet, BOM and notes. DXF is a half-profile (x = radius, y = height). Zips cannot go through the Artifact asset upload; the approved PDF can. When re-uploading an approved version to Drive over a draft with the same name, the 'replace existing items' dialog is the right choice (confirm it).
- After approval and the Drive upload, flip the product's sticker in the production book (deck 1OWzV1FMAQcFy0z4naVNmKQp3heqcLBgQYzlyOJDfIVY): shape `flag_NNN` on slide `slNNN`, yellow to green, text 'DESIGN FILE READY', and the 'Design file:' line in n_NNN and d_NNN to READY (in folder). Use updateShapeProperties and replaceAllText.
