# Shopify architecture (plan — nothing here is built or tested yet)

Online Store 2.0, Liquid, JSON templates, vanilla JS (custom elements, no framework), modular CSS. Start from an empty/minimal theme scaffold (not a purchased theme) so no generic template look leaks in. Shopify CLI is **not installed** on this machine and no store is connected; install and authenticate only with founder approval, develop on an unpublished theme.

## Theme structure
```
theme/
  assets/        base.css  components.css  sections.css  theme.js  product-form.js  (fonts self-hosted .woff2)
  config/        settings_schema.json  settings_data.json
  layout/        theme.liquid  password.liquid
  locales/       en.default.json  ar.json (later)
  sections/      header  footer  hero  selected-objects  editorial-split  category-index
                 collection-feature  edit-stories  main-collection  main-product
                 main-article  main-blog  main-page  main-cart  collection-header  in-good-company  ...
  snippets/      css-variables  product-card  availability  delivery-estimate  swatch  price
                 media-gallery  responsive-image  accordion  icon
  templates/     index.json  collection.json  product.json  blog.json  article.json  page.about.json
                 cart.json  list-collections.json  search.json  customers/*.json  404.json
```
Prototype mapping: `tokens.css` → `css-variables.liquid` + settings; `home.css` blocks → per-section `{% stylesheet %}`; `proto.js` → `theme.js`; placeholder plates → `responsive-image` snippet with an editor-visible "no image" state.

## Data model
See PRODUCT_SCHEMA.md. Merchant-editable: product/variant metafields and metaobjects (admin), blocks and settings in sections, menus, collections, blog articles. Zero product or inventory values in code.

## Availability and delivery logic
Source of truth is the **variant**: `inventory_policy`, `inventory_quantity`, and variant metafield `custom.fulfilment`.

| Variant state | Shown | Add action |
|---|---|---|
| `fulfilment = ready` and qty > 0 | READY TO DELIVER, "n available" only if ≤ threshold (setting), delivery window from `custom.delivery_days_*` or shop default | Add to Bag |
| `fulfilment = ready` and qty = 0 | Sold out (never silently converted to made to order) | disabled; optional notify-me |
| `fulfilment = made_to_order` | MADE TO ORDER, lead time from `custom.lead_time_weeks_min/max`, terms text from a shop-level metaobject | "Made to order" (or "Configure your piece" if product `custom.configurable` is true) |
Made-to-order variants need `inventory_policy = continue` (Shopify's "continue selling when out of stock") so the cart accepts them; ready variants keep `deny`, which is the overselling guard. Theme must never show "n available" for made-to-order variants.
**Superseded by THEME_PLAN.md §4 and D-018 (rules live only in Liquid; buy box re-rendered via the Section Rendering API).** Earlier idea, kept for reference: variant change → JS reads a JSON blob rendered by Liquid per variant (price, fulfilment, qty band, lead time, featured media id, SKU) and updates price, label, delivery text, button, gallery. Use the Section Rendering API fallback for no-JS and for URL `?variant=` deep links. Delivery text is computed from those fields; if data is missing it shows nothing rather than a guessed promise.

## Cart and order handling
Line-item properties/attributes tag made-to-order lines (`_fulfilment`, `_lead_time`) so order notes and fulfilment staff can see them. Mixed carts (ready + made to order) are allowed (D-009). The cart asks one question when it contains both: ship together, or separately. The answer is saved as cart attribute `delivery_preference` (`together` | `separate`) and copied to the order for staff. Shipping-fee rule for `separate` is open (D-016).

## Limits and verification items (do not assume)
1. **Deposits / partial payment** (founder direction: InstaPay with proof upload, see D-015 for the assessment): standard Shopify checkout charges the full amount (or uses Shopify's own pre-order/deferred-payment features where available on the plan). A deposit-then-balance flow needs a compatible app or draft-order/payment-link process. Not decided; needs an app or process choice and cost approval.
2. **Production management:** Shopify does not track manufacturing stages. Needs a spreadsheet/app process or an integration; out of theme scope.
3. **Egyptian payment gateways:** compatibility with Shopify checkout (EGP currency, local cards, wallets, cash on delivery) must be verified against the actual plan and region before commitments. Shopify Payments availability in Egypt must be checked rather than assumed. Treated as a separate workstream (QA §Commerce).
4. **Filters on metafields:** storefront filtering via Shopify Search & Discovery needs the metafield definitions to be filterable; confirm variant-level filter support on the target plan.
5. **Customisation ("Configure your piece"):** v1 = finish/material variants only. Free-form configuration needs an app; out of v1.
6. **Arabic / RTL:** not in the brief; design uses logical properties where cheap so it can be added.

## Performance and SEO
Responsive `srcset` via `image_url`, `loading=lazy` below the fold, hero eager with `fetchpriority=high`, `font-display: swap`, ≤ ~30 KB gz JS target, no render-blocking third parties. Product JSON-LD generated from Liquid (name, image, sku, brand, offers with `availability` mapped from the same variant state; made-to-order → `PreOrder`/`BackOrder` choice to be validated with Google's tester). Canonical, OG, `hreflang` later.

## Prototype mapping: bag (`prototype/cart.html`, `js/cart.js`)
Prototype stores `{lines[], pref}` in localStorage under `objekt-proto-cart`. Theme equivalent: lines from Shopify cart, `delivery_preference` via cart attributes, per-line `_fulfilment` and `_lead_time_weeks` as line item properties (the prototype's 'Prototype data' panel shows the intended payload). The stock cap on ready lines mirrors `inventory_policy = deny`; Shopify enforces it at add-to-cart and checkout, and the theme must show the error from `/cart/add.js`, not rely on the client check. Delivery estimates are computed from the lines' own data (max of the minimums, max of the maximums).
