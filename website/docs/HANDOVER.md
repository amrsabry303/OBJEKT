# Handover: OBJEKT Shopify website

Written 7 Nov 2026 for a new Claude account taking over. The previous account's memory, chat history and local files are not available to you; everything you need is in this file, the repo docs and the handover package (section 11). Read this first, then `CLAUDE.md`, then the doc for your task.

## 1. What this is, in six lines
- A design-led Shopify Online Store 2.0 theme and store for **OBJEKT** (contemporary furniture and objects, made in Cairo by Polycraft). Egypt first, English and Arabic (RTL), currency EGP.
- Founder and final decision-maker: **Sabry**. Others: **Youssef Gaber** (owns the Polycraft factory), **Nour** (probable lead product designer). An Arabic translator is not named yet.
- **Launch target: Friday 20 Nov 2026** (13 days from this handover), scope option A: all products, every page, English plus Arabic. Checkpoints: Thu 12 Nov content freeze, Thu 19 Nov founder approval. **At risk** (see section 8).
- The theme is built, pushed to an **unpublished** theme and checked. The live theme is still Shopify's default Horizon; only the founder publishes.
- Not launch-ready: no real copy, prices, lead times, photography or Arabic; fonts and checkout are not cleared. Paymob is installed but not signed in.
- Be honest in every report: say what you ran and saw. "Not tested" is a valid status.

## 2. Hard rules (from the founder and `CLAUDE.md`)
1. Never touch the live store's products, prices, orders, checkout or payment settings without explicit founder approval. Develop only on the unpublished theme. Never publish the theme or remove the storefront password (that would expose Horizon). Nothing public without approval.
2. Credentials: never enter, store or ask for passwords, keys or HMAC secrets. The founder types the Shopify CLI login, storefront password and Paymob sign-in himself.
3. Never invent brand facts: history, designers, certifications, sourcing, production claims, prices, sizes, lead times. Placeholders are labelled "Placeholder" or "Sample" in the UI.
4. Brand colours, exactly: navy `#263A5A`, sand `#E2D9CF`. No gradients, gold, heavy shadows or discount widgets. Never redraw or approximate the logo; use the supplied SVGs.
5. Fonts: PP Mori (body) and Galak Round (headlines) are named in the brand guidelines but **not licensed for web**. Never commit font files or ship them in the theme (`prototype/fonts/` is gitignored and holds free local-only files). The theme names the fonts first in a stack and falls back to system fonts. See DECISIONS D-013.
6. Shopify first: native inventory, variants, metafields, metaobjects. No React or headless. Nothing a merchant should edit is hardcoded.
7. Do not claim deposits, production tracking or Egyptian gateway support work in standard checkout; they are verification items (D-010, D-015).
8. One owner per file or feature at a time; disagreements go in DECISIONS.md. Update CHANGELOG.md for every store write or verified item.
9. Write the word as **objekt / objekts** (not "object") in all visible text. Code identifiers such as the collection handle `objects` and the field `custom.objects` stay as they are.
10. Product names are not approved or trademark-cleared (see the naming skill). Do not rename products in Shopify without Sabry's choice. Until then titles are the OBJ code (for example OBJ-099).
11. Every product image generated so far is an **AI render**, not a photo of a made piece. Say so, and name the files `ai-render`.

Approval from the founder is needed for: brand direction and final aesthetic, major UX changes, positioning, pricing and payment policy, production and delivery promises, external costs, launch. Batch these into one review request with a recommendation and alternatives.

## 3. Where everything lives
| Thing | Where |
|---|---|
| Repo snapshot | this folder (`theme/`, `docs/`, `prototype/`, `tools/`, `.claude/agents/`); see section 11 for how it moves |
| Shopify theme | `theme/` (Online Store 2.0, 48 files, `shopify theme check` clean) |
| Static prototype (reference only, finished) | `prototype/`; serve with `python3 -m http.server 4173 --directory prototype` |
| Docs | `docs/`: PROJECT_BRIEF, DESIGN_SYSTEM, SITE_ARCHITECTURE, SHOPIFY_ARCHITECTURE, PRODUCT_SCHEMA, ROADMAP, TASKS, DECISIONS (D-001 to D-026), QA_CHECKLIST, QA_REPORT_2026-10-30, CHANGELOG (every store write and verification, newest last), ARABIC_PLAN, THEME_PLAN |
| Brand source | `Objekt Brand Guidelines V1.pdf` (54 slides), logo SVGs and colour/finish docs in the package (`brand/`) |
| Product data and images (founder's working folder) | `~/Desktop/POLYCRAFT/_plan/` on the founder's Mac: `shopify-import-template.csv`, `website-categories-prompt.md`, `images/IMAGE-INVENTORY.csv`, `images/HOUSE-STYLE.md`, `images/OBJ-nnn/` (193 MB of PNG renders, not in the package) |
| Skills | `.claude/skills/objekt-naming` and `objekt-drawings` (in the package, `skills/`) |
| Paymob setup guide | `paymob-shopify/SKILL.md` in the package |
| Claude documents (private to the founder's account) | "OBJEKT website: content to supply" https://claude.ai/artifact/9xLUQrXT4LJuKZrRnJZSVP (intake document for all copy and specs, 10 sections) and "objekt workspace" https://claude.ai/artifact/HysZRbjoMyneXH8Xbiipcn (product workspace and production book). **Ask Sabry to share both** with the new account. |
| Drive | each product has a design folder on the founder's Google Drive (links are in the workspace document); AI renders are filed there too |

Note on git: the project now lives in its own private repository, `objekt-polycraft` (D-012 resolved 7 Nov 2026), with a clean history. The website is under `website/`.

## 4. Access the new account needs (nothing here is a credential)
| Access | State and what to ask for |
|---|---|
| Shopify store `hs1a1c-ut.myshopify.com` (name OBJEKT, plan **Basic**, EGP, Egypt) | Admin: https://admin.shopify.com/store/hs1a1c-ut. Staff owner is the founder (signs in with Google SSO). The new account's human needs staff or collaborator access, or the founder drives the admin. |
| Shopify connector (MCP) for Claude | The previous account used a connector scoped to this store (GraphQL Admin API **2026-10**). The new account must authorise the connector against this store; check `get-shop-info` returns OBJEKT, not another store (an earlier wrong store `hp6z9z-ck` was once connected and disconnected without changes). |
| Shopify CLI 5.x | Installed in `tools/` (`cd tools && npm ci`). Login is interactive and done by the founder or the new staff user. |
| Storefront password | Store is password protected. Needed only for `theme dev`; the founder types it. Admin sessions can view the unpublished theme without it (section 5). |
| Claude in Chrome | Used with the founder's permission for admin steps the API cannot do (Search & Discovery filters, Payments, theme share link, collection UI). Close tabs after use. |
| Paymob | Account is in **test mode** only. Sign-in is the founder's. |
| Image generation (Magnific) | Used for AI renders, plan about 20,000 credits, about 695 spent by 2 Nov. House style in `images/HOUSE-STYLE.md`. |

## 5. Working on the theme
Themes in the store: **Horizon (live, do not touch)**, **OBJEKT dev (unpublished), id `189754769632`**. A second dev theme (`189754802400`) may exist from `theme dev`.
```
cd tools && npm ci
./node_modules/.bin/shopify theme check --path ../theme                       # must stay clean
./node_modules/.bin/shopify theme push --path ../theme --theme 189754769632 \
    --store hs1a1c-ut.myshopify.com --nodelete                               # unpublished theme only
./node_modules/.bin/shopify theme dev --path ../theme --store hs1a1c-ut.myshopify.com   # founder types the storefront password; preview 127.0.0.1:9292
export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
./node_modules/.bin/lighthouse URL --only-categories=accessibility --chrome-flags="--headless=new --no-sandbox"
```
View the unpublished theme in the founder's logged-in Chrome: `https://hs1a1c-ut.myshopify.com/<path>?preview_theme_id=189754769632`. To show it to others without unlocking the store: theme preview bar, link icon, which copies a shareable link valid 2 days. Generated once on 2 Nov; none is stored.

Gotchas learned the hard way:
- `theme dev` can serve stale JSON templates or report "Section type does not refer to an existing section file" (upload-order race). Touch the section files, then the templates; a **full `theme push` succeeding is the proof the files are valid**.
- Shopify rejects section schema labels over 70 characters; `theme check` does not catch it.
- `{% render %}` arguments cannot contain filters: assign first, then pass.
- A `link_list` setting default may only be `main-menu` or `footer`; the header menu is set in `sections/header-group.json` to `objekt-main`.
- An input named `id` clobbers `form.id`; the product form is matched with `form.matches('#product-form')`.
- Cart lines are keyed `updates[item.key]`, never by position.
- Availability rules live **only** in `snippets/availability.liquid` (ready, made to order, sold out; made to order is the default, D-023).
- The preview pane cannot go below about 351px wide and has no real focus, so keyboard and focus behaviour need a real browser or device.
- Python scripts that contain Arabic need `# -*- coding: utf-8 -*-` and should be files, not heredocs.
- Admin API 2026-10 rejects deprecated fields (`Publication.name`, `Collection.ruleSet`, `collectionAddProducts`, `productDeleteMedia`). Use `fileDelete`, `productUpdate(collectionsToJoin)`, `collectionUpdate` sources, and `graphql_schema` to look up current names.
- Image upload: `stagedUploadsCreate`, then `curl` multipart POST to the returned URL with every returned parameter as `-F name=value` (file last), then `productUpdate` with `media` or `productSet`. Copy the signed values exactly; a mangled policy returns 403. Convert 6 MB PNGs to JPEG (`sips -s format jpeg -s formatOptions 88`) first.
- The **Objekts collection holds products by manual list**, not by tag. A new product needs `productUpdate(collectionsToJoin: [...])`. Check how Furniture, Table & Living and Planters hold theirs before assuming.
- Search & Discovery filters are configured in the admin UI only (6 filters; both Availability groups were kept on purpose). Saving a Colour filter with empty swatches shows a dialog that must be confirmed or the save silently fails.
- Lighthouse performance is noisy through the local proxy (71 to 100) and Best Practices is capped by plain HTTP; do not quote either as launch numbers. Accessibility 100 was measured on home, collection, product, About and an empty search.

## 6. What is built (all on the unpublished theme)
- **Layout and sections:** header (nested menu panel, mobile native `<dialog>` menu, language links), footer (newsletter form, link columns, language list), home (hero, featured products, editorial split, category index with silhouette icons, collection feature, The Edit), collection (toolbar, filter drawer from `collection.filters`, chips, sort, pagination 24, empty states), product (gallery, variant links, buy box refreshed by the Section Rendering API, accordions, JSON-LD, product tag), bag (grouped ready and made-to-order lines, ship together or separately choice only for mixed bags, deposit and separate-fee notes empty by default), search, 404, collections list, password page, blog, article, About, generic page.
- **Brand guidelines applied (D-026, 31 Oct):** sand page ground, navy text, midnight-navy footer with sand wordmark, Galak Round headlines (all caps) and sub-headlines, `// kicker` labels, 27 degree corner cut on the footer and feature section, silhouette icons exported from the guide (page 35), product tag (guide page 47). Midnight navy `#122948` and bronze `#9B6835` are theme settings with values **read from the PDF's colour cards** (its hex labels are template text); confirm with the designer.
- **Availability:** per variant, `custom.fulfilment` (ready or made_to_order), lead times in weeks, delivery days; sold-out ready variants are switched by hand (D-025).
- **Arabic:** locale file `locales/ar.json` is **my draft and needs a real translator**; RTL layouts use logical CSS properties but were only simulated with `dir="rtl"`. Arabic is added to the store but **unpublished**. Arabic fonts are not loaded (fallback stack).
- **SEO:** titles, canonical, noindex for cart, search, account and filtered or sorted collections, OG and Twitter tags, Organization, WebSite, Article, BreadcrumbList and Product JSON-LD. Meta descriptions are empty (founder copy).

## 7. State of the store (read on 7 Nov 2026)
- **53 products:** 16 active, 37 draft. 49 drafts were imported from the plan on 30 Oct (placeholder data); 13 carry the tag `preview-active` (12 activated for the preview plus **OBJ-099**, created 2 Nov with real renders); 3 active `[TEST]` products (TEST A ready, TEST B made to order, TEST C mixed, used to test the variant matrix). 50 products are tagged `placeholder-data`.
- **Placeholder data everywhere:** price 9999.00, lead time 8 to 10 weeks, "[PLACEHOLDER]" descriptions, dimensions "00 cm". Images: 4 reference photos of unknown rights on four products, 8 labelled placeholder images, OBJ-099 has 5 AI renders (the v1 set).
- **Collections (4, D-021):** Furniture (14), Table & Living (11), Objekts (17; handle `objects`), Planters (10), plus the default Home page collection.
- **Metafields:** 18 definitions in namespace `custom` and a `colour` metaobject with 7 entries (hex values not supplied yet). Colour vocabulary is the founder's official eight (Bone `#E9E4D8`, Putty `#B9B2A5`, Carbon `#222222`, Ink `#1E2A44`, Oxblood `#5A1F25`, Clay `#A8553A`, Chocolate `#4A2A1B`, Objekt Green `#37613F`; hex are screen approximations).
- **Menus:** `objekt-main` (used by the theme; currently one item "Shop" to all products, to be expanded), `main-menu`, `footer`. Pages: About, Contact. Blogs: The Edit (2 `[TEST]` articles), News (empty).
- **Languages:** English primary and published; Arabic added, unpublished.
- **Payments:** no Shopify Payments (not available in Egypt); PayPal "setup incomplete"; **Paymob Native Card Checkout app installed on 2 Nov** (cards plus Apple Pay), stopped at Paymob's sign-in page. Not activated, not in test mode yet, **Payment capture method not yet set to Automatic** (Paymob requires it), no test order or refund run. Follow `paymob-shopify/SKILL.md`. Shopify's Payments page states a **2% fee** on third-party-provider payments; confirm costs with the founder.
- **Orders:** none placed. Nothing in checkout has been tested.

## 8. What is left, in priority order
**Founder decisions and supplies (blocking):**
1. Paymob: sign in, then you tick Test mode, Activate, set capture to Automatic, run test orders and a refund (go live only after Paymob activates the account, then one real order and refund). Gateway decision D-010 stays open until then.
2. Deposits and made-to-order pre-payment (D-015) and the separate-shipment fee (D-016). Standard checkout does neither.
3. Final product list: the plan says 46 products, the store has 49 drafts plus OBJ-099. Variants for OBJ-166, 175, 176. Product names (not approved, not trademark-cleared; candidate list in the naming skill).
4. Real prices, lead times, sizes, descriptions, care, delivery and returns text, policies, meta descriptions, collection intros, About copy (the intake document lists all of it).
5. Photography or confirmation that AI renders go on the public site (they are labelled in alt text only), and rights for the 4 reference photos (remove them if unknown).
6. Arabic: name the translator, supply translation, glossary, typeface, numeral and currency format; publish Arabic only after real review.
7. Licences: PP Mori web licence, Galak Round licence, the logo lettering licence (the logo PDF embeds "Raftwork Demo Regular"). No public launch before these (D-013, D-014).
8. Confirm the guide's extra colours (midnight, bronze), the tagline "YOUR OBJEKTS OF HAPPINESS" (appears only on guide mockups), and the launch scope (content document section 11).
9. D-012: a proper repository for this project.

**Known follow-up on OBJ-099 (found while packing this handover):** on 2 Nov, after OBJ-099 was uploaded, two Oxblood recolours to the brand hex `#5A1F25` were made (`OBJ-099_ai-render_oxblood_sunlight-limestone_v2-brand-colour.png` and `..._oxblood_context-dining_v2-brand-colour.png`, in `_plan/images/OBJ-099/`). The site still shows the v1 Oxblood images, which the founder judged off-colour. Swap them: upload the v2 JPEGs, link the Oxblood variant to the new colour image, delete the v1 Oxblood media with `fileDelete`, keep the originals. Ink, Objekt Green and Putty were not recoloured.

**Before any public launch (cleanup checklist):**
- Delete the 3 `[TEST]` products and 2 `[TEST]` articles.
- Set the 13 `preview-active` products back to draft or replace their placeholder data with real data; remove `placeholder-data` tags only when real.
- Remove the 4 reference photos of unknown rights and the 8 placeholder images.
- Expand the `objekt-main` menu and footer menus; connect the delivery page; add the policies.
- Founder alone: publish the theme, remove the storefront password, switch Paymob to live. Keep Horizon unpublished as the rollback.
- Launch check in QA_CHECKLIST: "no active product carries `placeholder-data`, 9999.00 or '[PLACEHOLDER]'" currently **fails by design**.

**Not yet run (see QA_CHECKLIST and QA_REPORT):** checkout in test mode, EGP at checkout, deposit flow, order data reaching fulfilment staff, real Arabic and RTL output, hreflang, real keyboard and screen-reader passes, loading licensed fonts, smart collections Ready/Made to Order, the password page (never viewed), gift card template (only if gift cards are sold), Rich Results test and sitemap, a real phone and tablet, RTL for the new silhouettes, tag and cut footer, per-colour image on click for OBJ-099.

## 9. Standing facts about the business (so you do not relitigate)
- Egypt first. The factory is Youssef's, outside the holding company. Unlicensed character work is sunset. Brand names are English words or abstract coinages. The launch brand is **objekt** alone (testing the waters), furniture included; six internal families and four website categories (Furniture, Table & Living, Objects shown as "Objekts", Planters).
- Day-one process mix agreed with Youssef on 29 Oct: about 30 metal (at most 10 curved), about 18 print-then-mould, 5 to 10 printed direct.
- Drawings follow the reference exactly unless Sabry says otherwise (production drawings are a separate workstream with its own skill).
- Every image generated for a product is saved locally in `_plan/images/OBJ-nnn/` (`OBJ-nnn_ai-render_<colour>_<scene>_vN.png`) and in the product's Drive folder. Each product should have one image per colour plus one in-context image (low sun, plaster and limestone, restrained props). OBJ-099 is the first product on the site with that set.
- `~/Desktop/POLYCRAFT` is a reference folder, not a portfolio: it mixes delivered work, AI renders and other studios' posts. Never treat an image there as proof of what the factory can build.

## 10. How to work with Sabry
Short answers, plain words, no hype. He gives a one-line instruction ("Collection page", "Keep both", "nth pending"): do it, verify it, report only what ran. Lead with the result; list what was not checked. Ask only when a decision is genuinely his. He is happy for you to drive his Chrome for admin steps (close the tabs afterwards) and to push to the unpublished theme; ask before anything public, costly or outward-facing.

## 11. The handover package
Folder `handover/` in this worktree (gitignored) and a zip of it, `objekt-website-handover-2026-11-07.zip`:
- `repo/` snapshot of the tracked files at the last commit (theme, docs, prototype without fonts, tools config without `node_modules`, agents). No credentials; checked by search before packing.
- `brand/` guidelines PDF, logo SVGs and PNGs, BRAND.md, COLOURS-FINISHES.md, the colour and finish PDF.
- `plan/` the import template CSV, the website-categories prompt, the image inventory and house style, and the OBJ-099 renders as JPEG (`OBJ-099-renders-jpeg/`: the five v1 files that are on the site plus two `v2-brand-colour` Oxblood recolours that are **not** on the site, see section 8).
- `skills/` the naming and drawings skills. `paymob-shopify/SKILL.md`.
- `HANDOVER.md` (this file).
- **Not included on purpose:** font files (unlicensed), the 193 MB of original renders, `node_modules`, anything from the other projects in the same home repository, and any credential.

First steps for the new Claude: (1) read this file, `CLAUDE.md`, `docs/DECISIONS.md`, the last 100 lines of `docs/CHANGELOG.md`; (2) confirm store access with `get-shop-info` (must say OBJEKT, `hs1a1c-ut`); (3) `cd tools && npm ci`, run `theme check`; (4) ask Sabry to share the two Claude documents and to restart the Paymob sign-in; (5) pick up section 8.
