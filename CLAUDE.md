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
