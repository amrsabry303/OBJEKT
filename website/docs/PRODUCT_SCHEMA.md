# Product schema

Three kinds of data, kept apart on purpose:
1. **Editorial labels** — what the customer sees on the plate (few): availability marker, optionally one of "New" / "Edition". Controlled by a single `custom.label` text field.
2. **Shopping filters** — material, finish, colour, aesthetic, character, availability, category, price.
3. **Internal metadata** — reference, lead-time notes, production notes, supplier. Never rendered.

Metafields are defined in the Shopify admin (namespace `custom`, so staff can edit them in the product page without code). Lists of vocabulary are **metaobjects** so staff can add a new finish or colour without touching the theme.

## Metaobject definitions
| Type | Fields |
|---|---|
| `material` | name, handle, description, swatch image |
| `finish` | name, description |
| `colour` | name, hex, swatch image (image wins over hex) |
| `aesthetic` | name |
| `character` | name |
| `lead_time_terms` | headline, body (deposit/cancellation wording — **text supplied by founder, not generated**) |

Seed vocabulary from the brief (editable, not confirmed products): Aesthetic — Sculptural, Organic, Architectural, Minimal, Playful, Timeless. Material — Walnut, Stainless Steel, Travertine, Ceramic, Glass, Oak. Finish — Brushed, Polished, Matte, Textured, Natural. Colour — Oxblood, Chrome, Sand, Olive, Espresso, Ivory. Character — Statement, Understated, Expressive, Refined.

## Product metafields
| Key | Type | Used for |
|---|---|---|
| `custom.reference` | single line | reference/code shown on product page |
| `custom.short_description` | multi-line | editorial intro |
| `custom.story` | rich text | accordion: The Story |
| `custom.materials_craft` | rich text | accordion: Materials & Craftsmanship |
| `custom.care` | rich text | accordion: Care |
| `custom.dimensions` | rich text or JSON | accordion: Dimensions (type-specific rows) |
| `custom.materials` | list of metaobject `material` | spec + filter |
| `custom.finishes` | list of `finish` | spec + filter |
| `custom.aesthetics` | list of `aesthetic` | filter + curated collections |
| `custom.character` | `character` | filter |
| `custom.label` | single line | the one optional editorial label |
| `custom.configurable` | boolean | shows "Configure your piece" |
| `custom.complementary` | list of products | IN GOOD COMPANY override |
| `custom.internal_notes` | multi-line | internal; not output by theme |

## Variant metafields
| Key | Type | Notes |
|---|---|---|
| `custom.fulfilment` | single line, choices `ready` / `made_to_order` | the availability switch; filterable |
| `custom.lead_time_weeks_min`, `_max` | integer | required when made to order |
| `custom.delivery_days_min`, `_max` | integer | optional override of shop default |
| `custom.colour` | `colour` | swatch |
| `custom.finish` | `finish` | variant finish |

Shopify option names: use native options (e.g. Finish, Size). A variant's image comes from the variant's featured media so the gallery follows the swatch.

## Product-type dimension templates
One product template; the dimensions accordion renders whichever rows exist (W, D, H, seat height, diameter, weight, cable length, capacity). New types need no code.

## Rules
- Availability is decided per variant; a product can mix ready and made-to-order variants (e.g. Walnut ready; Oxblood and Stainless Steel made to order).
- `Ready to Deliver` / `Made to Order` collections are smart collections on `custom.fulfilment`. (Product-level collection membership if any variant matches: confirm Shopify supports this rule on variant metafields; otherwise mirror to a product-level metafield via Flow/app.)
- **When a ready variant sells out (D-025):** staff switch it by hand to `made_to_order`, add its lead time weeks, and turn on continue selling when out of stock; switch it back to `ready` (and continue selling off) when stock returns. The Ready filter matches `custom.fulfilment` regardless of stock, so skipping this leaves a sold-out variant under "Ready to deliver".
- Never display every attribute as a badge. Filters live in the filter drawer; specs live in the spec list.
- Do not hardcode prices, quantities, lead times or delivery windows in the theme.

## Prototype mapping (`prototype/js/product.js`)
The prototype's `PRODUCT.variants[]` is the JSON the Liquid theme must emit per product: `id, finish, swatch, price, fulfilment (ready|made_to_order), qty, days[min,max] | weeks[min,max]`. One `state()` function derives sold out / ready / made to order; the theme should port that function, not redefine it. Sample finishes: Walnut ready (qty 4), Oak ready (qty 0, shows sold out), Oxblood and Stainless Steel made to order. All values are sample data.

## Launch catalogue structure (D-021, 30 Oct 2026) — supersedes the vocabulary above where they differ
- **Category** = Shopify collection (4). **Product type** = sub-category (one per product): Furniture: coffee tables, side and bedside tables, stools and benches, pedestals and plinths, chairs and lounge seating. Table & Living: trays, bowls and baskets, coasters and trivets, tissue and paper holders, desk and book. Objects: candleholders, ashtrays and incense holders, vases, decorative sculpture, statement sculpture, shelves, wall art and photo displays, mirrors. Planters: floor, tabletop, planter screens.
- **Tags** (filters): process: metal, curved metal, moulded, printed. Finish: mirror polish, brushed, lacquered, powder-coated. Colour (objekt colour guide): Bone, Putty, Carbon, Ink, Oxblood, Clay, Objekt Green. Room: living, dining, bedside, desk, entry, balcony. Material is not a launch filter; "process" covers how a piece is made.
- The `colour` metaobject now holds these seven names; **hex values come from the objekt colour guide** (not yet supplied; prototype swatches are placeholders).
- Replaced for launch: colours Oxblood/Chrome/Sand/Olive/Espresso/Ivory (original brief; Oxblood survives). Aesthetic and character stay optional metadata, not filters.
- **Made to order is the default** (D-023): `custom.fulfilment` defaults to `made_to_order`; lead time is required for those variants and is shown instead of stock. Ready variants remain the exception.
- Variants: OBJ-166 (two heights), OBJ-176 (four colours), OBJ-175 (modular panels) are single products with variants.
- Everything customer-facing exists in English and Arabic (D-022): title, description, collection text, metaobject names and metafield text must be translatable.
- Workspace mapping (provisional, from the workspace Launch flag): Furniture 11, Table & Living 11, Objects 16, Planters 10, one unmapped (OBJ-107 cutlery). Target 14/9/14/9 = 46. Full table in the content document, section 3c.

## Implemented in the OBJEKT store (30 Oct 2026, founder-approved "step 2"; store hs1a1c-ut)
Definitions only; 0 products exist. All in namespace `custom`; all readable by the storefront except `internal_notes`.
- **Metaobject `colour`** (translatable, storefront-readable): fields `name` (required) and `hex` (colour, empty until the objekt colour guide is supplied). Seven entries, names only: Bone, Putty, Carbon, Ink, Oxblood, Clay, Objekt Green.
- **Product fields (12):** `reference`, `short_description`, `story`, `materials_craft`, `care`, `dimensions`, `process` (choices: metal, curved metal, moulded, printed), `finishes` (mirror polish, brushed, lacquered, powder-coated), `rooms` (living, dining, bedside, desk, entry, balcony), `colours` (list of `colour`), `complementary` (list of products), `internal_notes` (not on the storefront).
- **Variant fields (6):** `fulfilment` (choices: `ready`, `made_to_order`), `lead_time_weeks_min`, `lead_time_weeks_max`, `delivery_days_min`, `delivery_days_max` (whole numbers, 0 or more), `colour` (one `colour`).
- **Decision to confirm:** the founder's brief said "tags" for process, finish, colour and room. They were built as structured metafields with fixed choices (they filter per group, are translatable, and cannot be mistyped); Shopify's free-text product tags cannot be grouped that way. Tags can still be added or mirrored if the founder's other workflow depends on them.
- **Limits found:** Shopify refused the admin-filter option on the variant `fulfilment` field, so it was created without it. Whether storefront filters can use it is still to be tested on the theme. Product-level `process`, `finishes` and `rooms` allow smart collection rules and admin filtering.

## Draft products in the store (30 Oct 2026)
49 drafts from the provisional workspace list, titled by OBJ code. Conventions used: handle `obj-nnn`; vendor `objekt`; product type = workspace sub-category (for example `Side Tables and Bedside Tables`, `Pedestals and plinths`); tags = website category, product type, OBJ code (the founder's process, finish, colour and room are structured fields, still empty); SKU = OBJ code; `custom.reference` = OBJ code; `custom.internal_notes` = workspace name and status; variant `custom.fulfilment = made_to_order` (default per D-023, not a confirmed fact per product); inventory untracked, policy `continue`; price at Shopify's 0.00 placeholder (must be set before activation). No product can be activated meaningfully until a price, lead time and photos exist.

### Placeholder data in the draft products (30 Oct 2026): remove before launch
Tag `placeholder-data` marks every affected product (Shopify admin: Products, filter by that tag). Values: price 9999.00; lead time 8 to 10 weeks; description, short description "[PLACEHOLDER] ... [نص مؤقت]"; dimensions "00 cm"; rooms, process and finishes guessed (see CHANGELOG). Not set: colours, story, materials and craft, care, companions, images. **Launch rule:** no product may be activated while it still has the `placeholder-data` tag; the QA checklist now says so.


## Shipping size (set per item when listing, Sabry 10 Nov 2026)
The variant **weight** is the size flag for shipping. It is not the real weight.
- Small item: weight **0 kg** (default). Standard delivery, 118 EGP.
- Large item: weight **1 kg** on every variant. Large item delivery, 1,200 EGP.
- Rates (General profile, Egypt): Standard delivery when cart weight ≤ 0.5 kg; Large item delivery when ≥ 1 kg. So the cart pays one fee, the higher one: any large item makes the order 1,200 EGP.
- Do not enter real weights in the weight field; it would change the rate. If real weights are needed later, store them in a metafield.
