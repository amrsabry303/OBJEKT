# Audit: all four prototype pages — 2026-10-29

Scope: `index.html`, `collection.html`, `product.html`, `cart.html` at commit `e82d6ca`, in the in-app browser at 1440 and 375px. Follows `AUDIT_HOMEPAGE_2026-10-29.md`; items from that audit are tracked below, not repeated.

## Verdict
The four pages hold together as one system and the commerce logic that matters (per-variant availability, stock cap, ship together/separately, filter counts) behaved correctly in every case I ran. Three defects are worth fixing before the theme build: a script failure that disables the menu on every page (B-01), a "Shop" link that never reaches the shop (B-02), and filter groups that a screen reader cannot tell apart (B-03). The largest gap is not a bug: the collection grid, the product buy box and the bag render only through JavaScript, so the Liquid theme must server-render them (B-07).

## What was executed
| Check | Home | Collection | Product | Bag |
|---|---|---|---|---|
| One `h1`, landmarks, `lang`, unique title, meta description | pass | pass | pass | pass |
| Duplicate ids / broken `aria-*`, `for`, `<use>` references | none | none | none | none |
| Every interactive element has an accessible name | pass | pass | pass | pass |
| Local links resolve (files and `index.html#anchors`) | pass | pass | pass | pass |
| Tap targets under 44px, desktop and 375px | 0 | 0 | 0 | 0 |
| Horizontal overflow, desktop and 375px | 0 | 0 | 0 | 0 |
| Text contrast (computed from CSS backgrounds, AA) | pass except placeholder tags | pass except placeholder tags | **fail: sold-out option (B-04)** | pass |
| Skip link works (collection) | – | pass | – | – |
| Header bag count in sync with the bag (home, collection, product, bag) | pass | pass | pass | pass |
| Invalid `?variant=` (999, abc) falls back to Walnut | – | – | pass | – |
| Invalid filter/sort parameters ignored, valid ones kept | – | pass | – | – |
| Gradients in CSS | none | none | none | none |
| `prefers-reduced-motion` rule present (read, not emulated) | yes | yes | yes | yes |
| Corrupt saved bag | **fail (B-01)** | | | |

Earlier same-day runs still stand for: all four product variant states, stock cap, filter/sort/clear, drawer Esc and focus return, bag quantity/remove/empty state, delivery-choice visibility, and subtotal arithmetic.

## Not run (do not treat as passed)
Screen reader on any page · real phone or touch (hover image swap, gallery swipe, drawer) · Lighthouse or any throttled performance run · reduced-motion emulation · no-JS rendering beyond reading the HTML · Safari/Firefox · tablet widths · the pages as served by Shopify. An LCP reading (9.7s) was discarded: it was taken in a background pane and is not meaningful. CLS read 0 on the collection page, indicative only.

## Defects
| ID | Sev | Page | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| B-01 | major | all | Unexpected saved-bag data (`{"lines":"x"}`) makes `proto.js` throw at `refresh()`, which aborts the whole script: the mobile menu and reveal stop working on every page, and the bag page throws too | reproduced; console `c.lines.reduce is not a function` | validate shape in `OBJ.load()` and isolate init steps in the theme so one module cannot disable the menu |
| B-02 | major | all | "Shop" in the header goes to the homepage category section (`#categories` / `index.html#categories`), never to `collection.html`; the mobile menu's category list has the same problem except "All Objects" | read from DOM | Shop → collection page (or the shop panel); each category → its collection URL |
| B-03 | major | collection | Filter groups are `details > ul` with no `fieldset/legend` or `role=group`; a screen reader hears "Walnut" without "Material" | 0 fieldsets, no group roles | wrap each group in `fieldset` with `legend`, or `role=group aria-labelledby`. Needs a screen reader pass to confirm the experience |
| B-04 | minor | product | Sold-out option text is 3.23–3.50:1 (opacity .55) but the option is selectable, so it is not exempt | computed | drop the opacity; mark sold-out with the strike marker and a stronger-contrast grey instead |
| B-05 | minor | bag | Image link and name link on each line go to the same place: 3 redundant tab stops | 3 lines | `tabindex="-1" aria-hidden="true"` on the image link |
| B-06 | minor | home, collection | `<br>` inside `h1` joins words in `textContent` ("Objectsof Character.", "AllObjects"); how assistive tech reads it was not tested | measured | put a space before `<br>` |
| B-07 | major (theme constraint) | collection, product, bag | Without JavaScript: collection shows no products, product shows an empty finish list and an empty buy button, bag shows no lines | measured text without JS: collection 329 chars, product 1,156, bag 383 | Liquid must render the first state server-side; JS enhances |
| B-08 | minor | all | No favicon: a 404 on every load | fetch `/favicon.ico` = 404 | add favicon from the mark (once SVG approved) |
| B-09 | minor | all | 17–30 links per page are `href="#"` (Search, Account, footer, plates); there is no search, account, 404, About, The Edit or policy page | counted | expected for prototype; list belongs in the theme plan |
| B-10 | minor | all | Google Fonts is still requested although PP Mori leads the stack; PP Mori ships as `.otf` (65–69 KB each); `home.css` loads on every page although cart/product use a fraction (A-07) | files and request list | theme: self-hosted `.woff2`, preload two weights, split CSS per section |
| B-11 | info | all | About 25 literal hex colours outside the tokens, all in placeholder art and sample swatches | grep | acceptable now; in the theme swatches come from metaobjects and placeholders vanish |
| B-12 | info | bag | Lines snapshot price and stock cap when added, so they go stale if product data changes | by construction | Shopify's server-side cart removes this; the theme must surface add-to-cart errors from `/cart/add.js` |

### Carried over from the homepage audit
A-04 hover-only image swap, no touch equivalent (still open, collection too) · A-05 availability is 12px now, but 31–42 small labels per page remain at 10–11px · A-08 dead links (B-09) · A-09 placeholder tag contrast 4.14:1 · A-10 menu opens with focus on the wordmark.

## Aesthetic read, across the four pages
- **What holds:** one consistent system. Header, type, hairlines, the solid/hollow availability marker and the faceted placeholder geometry repeat on every page, and navy stays a signature (title, buttons, a few fields). The product page is the strongest: sticky information column, finish rows that double as availability, and the four photo registers recolouring with the finish. The collection's large navy title and drawer feel editorial rather than retail.
- **What is weak:** the 12-up grid is monotone. Every card is one centred object on a flat 4:5 field, so the page reads as a catalogue of identical plates; it will not until real photography and mixed crop ratios (studio, lifestyle, detail) arrive. Hierarchy below the headline is still flat (see A-05). The bag is functional but plain: it has the least brand character of the four.
- **Gaps against the brief:** no Shop panel, search, The Edit, About, account or 404; the photographic registers are not yet demonstrated on the collection page; deposit and made-to-order terms are placeholders (D-015, D-017).

## Recommended order
1. B-01, B-02, B-05, B-06 (quick, safe).
2. B-03 and B-04 (accessibility, small), then a screen reader pass on collection and product.
3. Decide how the theme server-renders the three JS-built regions (B-07) before writing any Liquid.
4. Remaining design gaps: A-04 touch equivalent, Shop panel, hierarchy of small labels, bag character.

## Fix pass — same day
| ID | Result |
|---|---|
| B-01 | fixed and verified. `OBJ.load()` now drops anything that is not a valid line, and each init step in `proto.js` runs in its own guard. Tested three bad stored values (`{"lines":"x"}`, non-JSON text, and a mix of garbage plus one valid line with an invalid `pref`): bag page and menu worked each time; the mixed case kept only the valid line (qty 2, EGP 19,600). Earlier console errors in the same session came from the old file |
| B-02 | fixed. "Shop", all seven menu categories and the five homepage category rows now go to `collection.html`, with `?cat=` or `?av=` where the collection page supports it. Menu "Made to Order" opens the collection with that filter on (6 objects) |
| B-03 | fixed in markup: 7 `fieldset`/`legend` groups in the filter drawer. **Not confirmed with a screen reader** |
| B-04 | fixed: sold-out option text is now 4.89:1 on its selected background and 6.27:1 on paper (was 3.23 to 3.50) |
| B-05 | fixed: bag line image links are out of the tab order (one tabbable link per line) |
| B-06 | fixed: `textContent` of the headings is now "Objects of Character." and "All Objects" |

Regression after the fixes: product variant states, collection filters and counts, product-to-bag flow and subtotal, and at 375px 0 small targets and 0 overflow on all four pages. Not re-run: contrast on every page, keyboard pass, and everything listed under "Not run". Open: B-07 to B-12 and the carried-over A items.

## Polish pass — 29 Oct, after the new-page fixes
| ID | Result |
|---|---|
| B-08 | fixed: `assets/favicon.svg` (the mark, navy; sand in dark mode), linked from all seven pages |
| B-10 | partly fixed: the Google Fonts request and both preconnects are gone from all seven pages (checked in the HTML and in loaded stylesheets). Still open for the theme: fonts are `.otf`; use self-hosted `.woff2`, split `home.css` per section |
| A-04 | fixed per D-020: `@media (hover: none)` hides the hover image layer; still present with a mouse |
| A-05 | partly fixed: uppercase labels are 12px everywhere (was 11px). The 10px placeholder tags are unchanged |
| C-04 | fixed: story image pair is 3:2 on phones (335 x 223 px at 375 wide) |
| new | product page finish rows and the bag's summary wrapped at 881 to 1100px; the information column now takes 5 of 12 columns there (337px at 900px; all finish rows single-line) |

Re-checked: 0 small tap targets and 0 overflow at 375px on all seven pages; no overflow at 1440px; header spacing at 900px (44px gap between nav and logo). Cached stylesheets in the preview pane hid two of these changes until forced to reload: remember when testing by hand. Not run: contrast after the label change, screen reader, Lighthouse, real touch device.
