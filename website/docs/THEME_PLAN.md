# Theme plan: from prototype to Shopify (server-rendered)

Status: plan only. No Liquid exists, Shopify CLI is not installed, no store is connected. Everything below is what I would build; items marked **verify** were not confirmed and must be checked on a dev store before code depends on them.

## 1. The rule that fixes audit B-07
**Liquid renders every page's real content on the server. JavaScript only upgrades it.** The prototype did the reverse for the collection grid, the product buy box and the bag, so those three are rewritten, not ported. The test for every feature: with JavaScript off, a customer can still browse, filter, choose a finish, add to the bag, change the bag and reach checkout.

| Feature | Works without JS because | JS adds |
|---|---|---|
| Filter and sort | the drawer is a `<form method="get">` with real checkboxes; submitting reloads the page with `filter.*` and `sort_by` | no reload: fetch the section, swap the grid, `history.pushState` |
| Choose a finish | finishes are links or radios that load `?variant=ID`; the server renders that variant's state | swap the buy box and gallery without reload |
| Add to bag | `<form method="post" action="/cart/add">` | add via `/cart/add.js`, update the count, show errors inline |
| Bag edits | `<form action="/cart">` with `updates[]` and the ship-together/separately radios | quantity buttons via `/cart/change.js`, no reload |

## 2. Prototype to theme map
| Prototype | Theme file | Notes |
|---|---|---|
| `tokens.css` | `snippets/css-variables.liquid` + `config/settings_schema.json` | brand navy and sand fixed (not editable); neutrals and text grey editable |
| `base.css`, `home.css`, `product.css`, `collection.css`, `cart.css` | `assets/base.css` + one `{% stylesheet %}` per section | fixes B-10: nothing loads that a page doesn't use |
| `proto.js` | `assets/theme.js`: custom elements `<site-menu>`, `<reveal-on-scroll>` | each guarded so one failure cannot break the others (audit B-01) |
| `product.js` `state()` | **Liquid snippet `availability.liquid`** | see decision D-018: one source of truth |
| `collection.js` filter logic | `main-collection.liquid` + `<filter-drawer>` | counts come from Shopify, not our code |
| `cart.js` grouping and estimates | `main-cart.liquid` | grouping and estimates computed in Liquid |
| placeholder plates | `snippets/image.liquid` | real `image_url` with `srcset`; an editor-visible "no image" state |
| `assets/objekt-*.svg` | `assets/` + `snippets/logo.liquid` | licence of the lettering still to confirm (D-014) |

## 3. Collection (`main-collection.liquid`)
- `{% paginate collection.products by 24 %}`; sort via `?sort_by=` (`manual` = Featured, `price-ascending`, `price-descending`, `title-ascending`).
- Filters from `collection.filters` (Shopify Search & Discovery). Each `filter.values` entry gives `param_name`, `count`, `active`; zero-count values render disabled, as in the prototype. "Show N objects" is the form's submit button.
- **Confirmed in Shopify's docs:** Search & Discovery supports **variant metafield filters** (single line text, numbers, boolean, metaobject references), with URL parameters like `filter.v.m.custom.fulfilment=ready`. Documented limits: 25 filters per store, 100 values per filter, no filters on collections over 5,000 products. We would use about 8 filters. Swatch filters need the colour metaobject and its metafield **storefront access** switched on. ([filtering docs](https://shopify.dev/docs/storefronts/themes/navigation-search/filtering/storefront-filtering), [help center](https://help.shopify.com/en/manual/online-store/storefront-search/search-and-discovery-filters))
- **Verify:** that a product with one ready and one made-to-order variant appears under both "Ready to Deliver" and "Made to Order" (the prototype assumes yes). If not, mirror a product-level metafield with Shopify Flow.
- Categories are **collections** (D-019), now exactly four (D-021): Furniture, Table & Living, Objects, Planters. Product type (Shopify `product_type`) is a filter inside each; room, process, finish and colour are filters from tags or metafields; availability stays a filter (most products are made to order, D-023). The menu lists the four categories only. The prototype's `?cat=` becomes collection URLs.
- Price: use Shopify's built-in price range filter instead of the prototype's three bands.
- Card availability line (`product-card.liquid`): computed from the product's variants. Ready if any variant has `custom.fulfilment = ready` and stock, made to order if the rest are `made_to_order`, sold out if none. Hover image: second media item; on touch there is no swap (audit A-04, decision D-020).

## 4. Product (`main-product.liquid`)
- Selected variant = `?variant=` else `product.selected_or_first_available_variant`. The server renders price, state, delivery text and button for that variant.
- `snippets/availability.liquid` is the **only** implementation of the rules in SHOPIFY_ARCHITECTURE.md: ready with stock, ready sold out, made to order, and nothing shown when lead-time or delivery data is missing.
- Variant switch: JS calls the **Section Rendering API** for the buy box (`?variant=ID&section_id=…`) and swaps the HTML; the gallery swaps instantly from a small JSON of `variant_id → media_id`. This keeps the rules in Liquid only, at the cost of a short network wait on each switch (mitigation: mark the box busy, keep the radio selection instant). Alternative considered: port `state()` to JS and ship a JSON of all variants, which is instant but means two copies of the rules.
- Add to bag: form posts `id`, `quantity`, `properties[_fulfilment]`, `properties[_lead_time_weeks]`. With JS, send **JSON `items`**, not `FormData`: community reports say `FormData` skipped the sold-out 422 in one case. Show the 422 `description` text inline. Shopify enforces stock; our client check is only a convenience. ([Cart API](https://shopify.dev/docs/api/ajax/reference/cart))
- Accordions read metafields (`story`, `materials_craft`, `care`, `dimensions`); empty ones are not rendered, so no placeholder text ships.
- Product JSON-LD in `snippets/product-jsonld.liquid`: one offer per variant; `availability` mapped from the same state. Made to order: validate `MadeToOrder` vs `PreOrder`/`BackOrder` with Google's Rich Results test (**verify**).

## 5. Bag (`main-cart.liquid`)
- Lines come from `cart.items`, grouped by the `_fulfilment` property. Lines are removed from the Shopify cart, never from our own storage (the prototype's localStorage bag disappears, which also removes audit B-12).
- Ship-together/separately: shown only when both groups exist (Liquid); `<input type="radio" name="attributes[delivery_preference]">` inside the cart form, saved when the cart form is submitted (works without JS). With JS, `/cart/update.js` with `attributes` (**verify** on the dev store; the Cart API reference documents the endpoint, but my search did not confirm the attribute behaviour).
- Estimates: ready days from `item.variant.metafields.custom.delivery_days_*` (else shop default); weeks from the line property. Nothing is shown if the data is missing.
- Hide underscore-prefixed properties in the bag display; staff still see them on the order (**verify** exactly where they appear in admin and in the order email).
- Checkout button: `name="checkout"`. The deposit note and the InstaPay flow are D-015: a manual payment method; customising the confirmation page beyond the payment-instructions text may depend on the Shopify plan (**verify**).

## 6. Theme editor
Homepage sections as listed in SITE_ARCHITECTURE.md, each with presets, empty states and sensible settings; collection header image and intro as section settings; the editorial interlude on the collection page as an optional block; product accordions as blocks that fall back to metafields; announcement bar optional. Brand colours are locked; fonts are a licensed `woff2` set in `assets/` (not a Google Fonts call).

## 7. Build order and acceptance
| Step | What | Done when (executed on a dev store, not assumed) |
|---|---|---|
| 1 | Scaffold, tokens, layout, header (mega panel), menu, footer, logo | `shopify theme check` clean; header works on keyboard and 375px |
| 2 | Metaobject and metafield definitions; seed 12 sample products incl. the 4-finish table | definitions visible in admin; staff can edit a product without code |
| 3 | `product-card`, collection with filters and sort | filters work with JS off; counts match; variant-metafield filter verified (§3) |
| 4 | Product page, availability snippet, section-rendered buy box, add to bag | all four finish states render correctly from data; 422 shown inline |
| 5 | Bag with delivery preference | attribute saved on cart and visible on the order |
| 6 | Home sections, editorial pages (The Edit, About) | all editable and reorderable in the editor |
| 7 | JSON-LD, SEO, favicon, fonts, image sizes, performance pass | Rich Results test; Lighthouse run on the dev store, results recorded |
| 8 | QA checklist, accessibility pass with a screen reader, rollback plan | QA_CHECKLIST.md items executed and dated |

## 8. What I need before step 1
1. ~~Founder: approve D-018 to D-020~~ **Approved 29 Oct 2026.**
2. **Founder:** a Shopify development store (or the real store's unpublished theme slot) and which plan it is on. I will not touch any live store, product, price or setting.
3. **Founder:** approval to install Shopify CLI on this machine. **Not given yet; install nothing until told.** The founder will send dev store access separately.
4. **Still open from earlier:** D-010 gateway, D-015 deposit percentage and hold time, D-016 fee for separate shipments, D-014 lettering licence, PP Mori web licence.

## 9. Arabic and RTL (now in scope, D-022) — planned in docs/ARABIC_PLAN.md
Every page ships in English and Arabic for the 20 Nov 2026 launch. What changes: language switching and `hreflang`; RTL layout (the CSS already prefers logical properties in places, but the prototype is LTR only and has never been tested in RTL: grids, the Shop panel, drawer direction, sliders and number formats all need a pass); an Arabic typeface (PP Mori may not include Arabic: **unchecked**); translated products, collections, menus, metafields and metaobjects (Shopify's translation tools, with a reported issue that translated variant metafields were not indexed for filters: re-check); Arabic text in the content document; Arabic QA by a native reader. The theme plan's eight steps stay, but each step now includes its Arabic version.

## 10. Not covered here
Search results page, account pages, 404, policy pages, and checkout appearance.
