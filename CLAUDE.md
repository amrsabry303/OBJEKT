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
- **Product sheet prefill (standing rule from Sabry, 11 Nov 2026).** Whenever a product is added or drawn, add or update its row in the OBJEKT MASTER PRODUCT SHEET (Products tab; also the Design folders and Variants tabs) with a **suggested product name** (objekt-naming rules, marked "suggested name, not approved") and the **sizes**. Take sizes from the approved or draft drawing sheet; if there is no drawing, put a suggestion or the size Sabry gave. Always label the source in the Comments cell and in your reply: FROM DRAWING, GIVEN BY SABRY, or SUGGESTION. Where things go: the suggested name in Products column S (`NAME Product type`); sizes on the Variants tab, **one row per size** with the same Product ID, Width, Depth and Height in mm (columns J to L) and the Size source in column M. **The artifact is the one Sabry means by "product sheet":** `objekt Product Sheet` (https://claude.ai/artifact/T2QcmFPN399m2XR8bwyHnB). Its data is the `products` collection (one doc per OBJ: `name_en`, `proposed`, `w`, `d`, `h`, `size_source` = DRAWING, GIVEN or SUGGESTION, `sizes` = extra sizes) and the product list is embedded in the page, so a new product needs a republish with its picture. Read the real drawing in the repo or the Drive folder for sizes; never fill a template size where a drawing exists. The master Google Sheet column S must use the same names as the artifact. Suggest the name straight away and do not ask Sabry to approve it (he said so on 11 Nov 2026); he will change it in the sheet if he wants. Just state the suggested name in the reply. Copying a row pastes fixed values in Family, Waiting on, Brand and Website category: set them by hand from the Taxonomy tab.
- **Product numbers (OBJ-nnn).** Never pick a number from memory, from this repo or from a folder listing. Before filing any new product, read the `Products` tab of the OBJEKT MASTER PRODUCT SHEET (Google Sheets id `1Krm6aj9hMFOTouAkw-fFMgDSDL2nklUN4Y2vJtTLqJk`, column A), take the highest number plus one, and check that no Drive folder `OBJ-nnn` exists for it. If the sheet cannot be read, stop and ask Sabry. Never upload to an `OBJ-nnn` Drive folder until the sheet row for that number is the same product. Say which number you took and from where.
- This repo holds objekt and Polycraft only. Dough internal docs live in omrmhd5/bake-dough under `docs/internal/`.

## Layout
| Folder | What |
|---|---|
| `venture/` | context, handover, memory notes, plan docs (workflow, design-file standard) |
| `brand/` | guidelines PDF, logo SVG/PNG, colour and finish docs |
| `plan/` | assortment targets, Shopify import template, image inventory, house style, OBJ-099 renders (JPEG) |
| `website/` | Shopify theme, docs (decisions, changelog, QA), prototype, tools |
| `.claude/skills/` | objekt-drawings, objekt-naming, paymob-shopify |
| `images/` | reference images OBJ-nnn.jpg (161, from the reference book; mixed rights, reference only, never proof of capability) |

Large originals (drawings, 193 MB of renders, reference photos and videos, transcripts) are not in git yet. See `IMPORT.md`.
