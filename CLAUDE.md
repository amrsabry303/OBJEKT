# objekt / Polycraft: project rules

Read this first. Then the file for your task:
- Venture, brand and production rules: `venture/CONTEXT.md` (locked decisions, do not relitigate) and `venture/memory/`.
- Website (Shopify theme and store): `website/CLAUDE.md`, then `website/docs/HANDOVER.md`.
- Production drawings: `.claude/skills/objekt-drawings/` and `venture/plan/Design-File-Standard.md`.
- Product naming: `.claude/skills/objekt-naming/`. Payments: `.claude/skills/paymob-shopify/`.

## What this is
Sabry and Youssef Gaber (owner of the Polycraft factory, Cairo) are building a holding company of design brands. The factory stays Youssef's. **objekt** is the single launch brand: Shopify launch **Fri 20 Nov 2026**, Egypt first, English and Arabic, 40–60 products in four website categories (Furniture, Table & Living, Objekts, Planters).

## Rules that apply everywhere
- Sabry decides. Short answers, plain words. Report what you ran and saw; "not tested" is a valid status.
- Never invent facts: prices, costs, sizes, lead times, history, certifications, production claims. No price in any document is costed.
- Every product image so far is an AI render, not a photo. Name files `ai-render` and say so.
- Draw the reference exactly unless Sabry says free or custom.
- Every render uses the product's approved drawing for dimensions and proportions, and its colours and finishes (named from `brand/COLOURS-FINISHES.md`). No approved drawing: do not guess. Say so, mark the render "shape-to-confirm", and use the reference photo's shape and the proposed colour only until a drawing exists. Record the drawing, dimensions and colour used in `plan/IMAGE-INVENTORY`.
- Every render created is added to the **objekt Image Picker** artifact (https://claude.ai/artifact/KDRckqJG31spXN2owEB2ck, private, pinned) so Sabry can choose Hero and colour there. Name it `OBJ-nnn_ai-render_<colour>_<view>_<drawing-or-no-drawing>_vN.jpg` and add it under its product. Read the artifact before republishing; keep it under the 16 MB page limit (the page is about 8 MB, so use the `assets` capability the artifact declares, not more embedded base64). Pushing to the picker is not approval: approval, Drive upload and the public site still need Sabry's yes, and render files stay out of git while the repo is public.
- **One session per product.** Sabry gives a product (photo or link); open a new session for it, number it with the next free OBJ (check `images/` and `plan/IMAGE-INVENTORY.csv`; Sabry can override). A product session is **done** only when: (1) the drawing set is approved, (2) the renders are approved in the Image Picker, (3) the Shopify listing is live. Until then report where it stands against those three. Going live still needs Sabry's clear yes; never activate a product or touch the live store without it.
- Brand: use the supplied logo files in `brand/`, never a typed or redrawn wordmark. Product colours only from `brand/COLOURS-FINISHES.md`.
- Fonts (Galak Round, PP Mori) and the logo lettering are **not licensed for public or commercial use**. Never commit font files.
- Nothing public, sent, uploaded, published or paid without Sabry's clear yes. Never touch the live store's products, prices, orders, checkout or payments without approval. Never handle passwords or keys.
- Write the brand word as objekt / objekts in visible text.
- This repo holds objekt and Polycraft only. Dough internal docs live in omrmhd5/bake-dough under `docs/internal/`.

## Layout
| Folder | What |
|---|---|
| `venture/` | context, handover, memory notes, plan docs (workflow, design-file standard) |
| `brand/` | guidelines PDF, logo SVG/PNG, colour and finish docs |
| `plan/` | assortment targets, Shopify import template, image inventory, house style, OBJ-099 renders (JPEG) |
| `plan/faux-books/` | faux books: 11 designs in 3 sizes. Spec `PLAN.md`, print PDFs and generator `print/`, 3D mockups `renders/` (reference photos are `images/OBJ-178` to `188`) |
| `website/` | Shopify theme, docs (decisions, changelog, QA), prototype, tools |
| `.claude/skills/` | objekt-drawings, objekt-naming, paymob-shopify |
| `images/` | reference images OBJ-nnn.jpg (161, from the reference book; mixed rights, reference only, never proof of capability) |

Large originals (drawings, 193 MB of renders, reference photos and videos, transcripts) are not in git yet. See `IMPORT.md`.
