# Site architecture

## Navigation
Desktop: `SHOP · COLLECTIONS · THE EDIT · ABOUT` left (Shop opens the four categories; D-021), wordmark centre, `SEARCH · ACCOUNT · BAG (n)` right. Driven by Shopify menus (`main-menu`, `footer-*`); Shop opens a minimal panel (categories, availability links, one featured plate): prototyped; opens on hover or keyboard focus, Esc closes. Disclosure-button pattern and screen-reader behaviour not yet tested.
Mobile: `MENU · wordmark · BAG`; menu is full-screen, Shop expands inline (built).

## Shop categories (Shopify collections, editable; D-021)
Menu order: **Furniture · Table & Living · Objects · Planters**. Nothing else is in the menu. Each collection has English and Arabic titles and a one-line description. Product types (sub-categories) drive a filter inside each category; process, finish, colour, room, price and availability are filters. Lighting (wave 2) joins Objects; "Wall" may split off later. Details: PRODUCT_SCHEMA.md.

## Pages → templates
| Page | Template | Status |
|---|---|---|
| Home | `index.json` | prototype built |
| Collection list | `list-collections.json` | not designed |
| Category / collection | `collection.json` (+ optional `collection.editorial.json`) | not designed |
| Product | `product.json` (+ `product.made-to-order` optional only if a layout truly differs) | not designed |
| The Edit index / story | `blog.json` / `article.json` (blog handle `the-edit`) | prototype built (`edit.html`, `article.html`) |
| About | `page.about.json` | prototype built (`about.html`) |
| Search, cart, account, 404, policies | standard OS2.0 templates | not designed |

## Homepage sections (all reorderable in the theme editor)
1. Hero (image/video, label, headline, one link) → `hero`
2. Selected Objects (curated product list, asymmetric layout presets) → `selected-objects`
3. Editorial story split → `editorial-split`
4. Shop by category index with preview → `category-index`
5. Featured collection, immersive → `collection-feature`
6. The Edit stories → `edit-stories`
7. Footer group (newsletter, support, shipping, policies, social, contact) → `footer`

## Listing page requirements
Editorial header with optional large image; responsive grid; second-image hover; names, EGP prices, availability line; filters (Availability, Category, Material, Finish, Colour, Aesthetic, Character, price) via Shopify Search & Discovery; sorting; touch-friendly filter drawer on mobile.

## Product page requirements
Gallery mixing studio, lifestyle, detail and material shots (swipe on mobile); name, reference, price, short description, material, finish, dimensions, availability, delivery estimate, purchase action; accordions: The Story, Materials & Craftsmanship, Dimensions, Care, Delivery & Returns; "IN GOOD COMPANY" complementary products (Shopify Search & Discovery recommendations + manual metafield override). Variant switch updates price, images, availability, delivery text and button (PRODUCT_SCHEMA.md).
