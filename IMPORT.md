# What is in git, and what still lives elsewhere

Built 7 Nov 2026 from two handover packages: the website package (`objekt-website-handover-2026-11-07.zip`) and the venture export (`POLYCRAFT-EXPORT` on Google Drive, folder `1F3dXkvqeI4uzFQR4QmKhEpTbrSEpqOEq`).

## In this repo
- Website theme, docs, prototype (no fonts), tools config, agent briefs.
- Brand guidelines PDF, logo files, colour and finish docs.
- Plan files: assortment targets, Shopify import template, categories prompt, image inventory, house style.
- OBJ-099 renders as JPEG (5 v1 on the site, 2 v2 brand-colour recolours not yet on the site).
- `plan/faux-books/`: the faux books spec, print PDFs for all 11 designs in 3 sizes with their generator, 3D mockups (size M). Their reference photos are `images/OBJ-178.jpg` to `OBJ-188.jpg` (other brands, reference only). Draft versions were removed on 11 Nov 2026; they are in git history. About 55 MB, mostly the print PDFs and the 305 dpi cow and tiger textures, which the generator can recreate.
- Venture context, handover and memory notes (objekt and Polycraft only).
- `website/docs/CONTENT_TO_SUPPLY.md`: the "OBJEKT website: content to supply" intake document (exported 8 Nov 2026).
- `venture/artifacts/objekt-workspace_HysZRbjoMyneXH8Xbiipcn.html`: the workspace tracker page (its data is in the Drive export `workspace-db/`).
- Skills: objekt-drawings, objekt-naming, paymob-shopify.

## Still to bring in (from the Drive export or Sabry's Mac)
| What | Where now | Plan |
|---|---|---|
| `_plan/drawings/OBJ-nnn/` (approved PDF, SVG, DXF sets) | Drive export `project/_plan/drawings`, and `~/Desktop/POLYCRAFT/_plan/drawings` | add to git (`venture/drawings/`); production source of truth |
| `_plan/src/` generators (drawings, market research, workspace) | Drive export `project/_plan/src` | add to git (`venture/src/`) |
| `workspace-db/` (refs, decisions, log, tasks JSON) | Drive export | add to git (`venture/workspace-db/`); used to rebuild the workspace tracker |
| `artifacts/` (11 HTML copies) | Drive export | add to git (`venture/artifacts/`; the objekt workspace page is already there, re-exported 8 Nov) |
| Plan PDFs, DOCX, XLSX (business plan EN/AR, briefs, market research, cost template) | Drive export `project/_plan` | add to git (`venture/plan/`) |
| `_plan/images/OBJ-nnn/` (193 MB PNG renders) | Mac and product Drive folders | keep out of git; Drive folders stay the store |
| Reference photos and videos, `Polycraft 2.pdf`, `NEW PORTFOLIO IDEAS`, `YG` | `POLYCRAFT-REFERENCES.zip` on Drive | keep out of git (mixed rights; reference only) |
| Session transcripts | Drive export `transcripts/` | keep out of git |
| Font files | Sabry | never in git until licensed, and then only if the licence allows |

## Not carried over
- Anything from the unrelated software venture that shared the old account (notes, artifacts, renders, old git remote and history), by Sabry's instruction.
