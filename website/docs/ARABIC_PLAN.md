# Arabic and RTL plan, against Friday 20 November 2026

Written 30 October 2026. Estimates are mine and unproven; nothing below has been built or tested on Shopify. Founder requirement: every page in English and Arabic at launch (D-022).

## 1. Verdict
**The code is not the bottleneck; content and decisions are.** The prototype already mirrors well, and the RTL code work is small (about two dozen rules plus one font). What decides 20 November is: a Shopify dev store, 46 products' worth of English and Arabic copy, photography, an Arabic typeface, and the payment and licence decisions. With 15 working days (Sunday to Thursday) and none of those in hand today, **a full bilingual launch of all 46 products and every page is unlikely**. A smaller first launch that is fully bilingual is realistic if specific inputs arrive on specific dates (section 7). The choice of scope is yours (D-024, proposed below).

## 2. What I checked
| Check | Result |
|---|---|
| Does the PP Mori file contain Arabic? | **No.** 0 Arabic letters or Arabic-Indic digits in all three files (438 mapped characters, Latin only). The free files are what I could test; whether the paid web family adds Arabic is **unverified**: ask Pangram Pangram |
| Prototype with `dir="rtl"` | header, nav, tools, product-page columns and finish rows mirror correctly with no code (collection filter rows were not checked closely and their counts sit on the wrong side); **five real breaks** (section 3) |
| Shopify can give a theme each language's direction | yes: `shop_locale.direction` returns `rtl` or `ltr`; `lang` from `request.locale.iso_code` ([docs](https://shopify.dev/docs/api/liquid/objects/shop_locale), [theme requirements](https://shopify.dev/docs/storefronts/themes/store/requirements)). The exact pair of attributes still needs a dev store test |
| Products, collections, pages, articles, metafields and metaobject entries translatable | yes, in Translate & Adapt or a CSV export ([help](https://help.shopify.com/en/manual/international/localization-and-translation)); **not confirmed:** Arabic in that app's list, and the earlier reported issue that translated variant metafields were not indexed for filters |
| Checkout in Arabic | **unverified.** Shopify lists 33 pre-translated checkout languages; I could not confirm Arabic is one, nor how checkout renders RTL ([checkout language](https://help.shopify.com/en/manual/checkout-settings/checkout-language)). Needs a dev store |
| Shopify's own recent themes support RTL | yes per Shopify's help text; ours is custom, so we own that work |

## 3. What breaks in the prototype in RTL (all fixable)
1. **Skip link makes the page about 10,000px wide and blank** (`left: -9999px`; in RTL the overflow scrolls). Use `inset-inline-start`. Found by test.
2. **Hero copy lands on the artwork.** The text mirrors to the right, the image does not. Real photography needs a text-safe area for each direction; this is an art-direction decision, not CSS.
3. **Fixed left/right rules (24 lines found by search; not every one breaks):** `.link::after`, `.cats li a:hover padding-left`, `.legend` and `.fo .ct margin-left`, `.line__price` and `.specs dd text-align: right`, mobile gallery counter `right:`, drawer `margin: 0 0 0 auto` and `translateX` animations, panel `left/right: 0` (fine), placeholder tags `left:`. Convert to logical properties (`inset-inline-start`, `margin-inline-start`, `text-align: start/end`).
4. **JavaScript that assumes left-to-right:** the gallery counter divides `scrollLeft` (negative in RTL). Direction-aware scrolling in the sliders.
5. **Directional characters:** the "→" arrows in the category index must point the other way; an email field and codes like `OBJ-166` need isolation (`dir="ltr"`, `<bdi>`) inside Arabic sentences.

## 4. Typography
- **Arabic face:** needed. Choose one that pairs with PP Mori Regular and is licensed for web. Free options under the SIL Open Font License to evaluate first: Noto Sans Arabic, IBM Plex Sans Arabic (licence to confirm at download). Load by `unicode-range` so Latin stays PP Mori.
- **Rules that differ in Arabic:** no `letter-spacing` (it breaks the joined letters; our labels use 0.12em and headings negative tracking: override under `:lang(ar)`); no uppercase (use weight and size for the label style); larger size (about +10% for equal visual weight) and looser line height (1.6 to 1.8); numerals decision (below).
- **Numerals and currency:** Western digits (9,800) or Arabic-Indic (٩٬٨٠٠)? Currency as "EGP" or "ج.م"? **Founder choice**; the VAT note "includes 14% VAT" needs Arabic wording.
- **Logo:** the supplied wordmark is Latin only; plan to use it on both languages unless you have an Arabic lockup.

## 5. Content and translation
- Every field in the content document needs English and Arabic; the document now asks for both. About 15 fields per product plus category, type, tag, page and policy text.
- **A named translator or reviewer** (native, familiar with design vocabulary) must exist before translation starts; machine drafts must be reviewed by a person before publishing.
- A short **glossary first** (category, product type, tag, process and finish names), so product copy stays consistent.
- Shopify setup: add Arabic as a language in the right market, theme locale files (`locales/ar.json` plus schema translations), Translate & Adapt for products, collections, menus, pages, metafields and metaobjects, `hreflang` (Shopify generates it for published languages: verify), notification emails, and the manual-payment instructions for the InstaPay deposit in Arabic (**verify** whether they can be set per language).

## 6. What Arabic adds to each of the eight theme steps
| Step | Added Arabic and RTL work |
|---|---|
| 1 Scaffold, tokens, header, footer | `lang` and `dir` from the locale; logical-property CSS from day one; Arabic font loading; language switcher; `locales/en.json` and `ar.json` |
| 2 Definitions and seed data | translatable metaobjects and metafields; Arabic names for categories, types, tags |
| 3 Cards, collections, filters | RTL drawer and filter rows; Arabic filter labels; sorting and counts in either numeral system |
| 4 Product page, availability, add to bag | direction-aware gallery and counter; Arabic availability and lead-time strings from the same Liquid snippet; bidi isolation of codes and numbers |
| 5 Bag and delivery choice | Arabic for the together/separately text; RTL quantity and price columns |
| 6 Home, editorial pages | hero text-safe areas per direction; Arabic About and Edit copy |
| 7 SEO, performance | Arabic titles and descriptions, `hreflang`, Arabic font weight budget |
| 8 QA | RTL pass on every page; **review by a native reader**; screen reader in Arabic; checkout and emails in Arabic |

## 7. Schedule (estimate)
Egypt's working week is Sunday to Thursday, so **15 working days** remain. Dates are what I need, not promises I can make alone.

| When | Build (me) | Needed from you (hard dates) |
|---|---|---|
| **By Sun 1 Nov** | nothing can start without these | dev store and its plan; approval to install Shopify CLI; scope option A, B or C; name of the Arabic translator or reviewer; the 46-product list |
| **Week 1, Sun 1 to Thu 5 Nov** | steps 1 and 2: theme scaffold, RTL foundation, locale files, definitions, seed data | Arabic typeface choice; colour guide values; numerals and currency choice; deposit % and hold time; payment decision; first products' English copy |
| **Week 2, Sun 8 to Thu 12 Nov** | steps 3 to 5: collections, filters, product pages, bag, InstaPay deposit flow | **content freeze Thu 12 Nov**: English and Arabic for the launch products, policies, terms, About; photography delivered for the launch products |
| **Week 3, Sun 15 to Thu 19 Nov** | steps 6 to 8: home, pages, SEO, full QA in both languages | founder review Mon 16 to Tue 17; fixes Wed 18; **founder launch approval Thu 19 Nov** |
| **Fri 20 Nov** | launch if every check below passes | |

**Go or no-go checkpoints:** Sun 1 Nov (store, CLI, scope, translator in place?), Thu 5 Nov (copy for the first products arriving?), Thu 12 Nov (content freeze met?), Thu 19 Nov (QA passed in both languages?). A missed checkpoint triggers a scope cut, decided by you, not by me.

## 8. Scope options (D-024). **Founder chose A on 30 Oct 2026.**
| Option | What launches 20 Nov | Risk |
|---|---|---|
| **A. Everything** | all 46 products, every page, English and Arabic | highest: needs all 46 products' copy, photography and Arabic by 12 Nov. I do not expect it |
| **B. Smaller, fully bilingual (recommended)** | the four category pages, 12 to 20 chosen products with complete English and Arabic data and photography, product pages, bag and InstaPay deposit, About and policies; The Edit and the remaining products added after launch | moderate: depends on the Sun 1 Nov and Thu 12 Nov dates |
| **C. English first** | the same pages in English only, Arabic added in the following weeks | lowest, but conflicts with your requirement that every page be bilingual at launch |

## 9. QA that will actually be run
RTL and LTR at 1440, 900 and 375px on every template; skip link, menu, drawer, gallery and bag in RTL; keyboard order in RTL; contrast with the Arabic font; Arabic screen reader pass if a device is available; translated metafield filters; checkout and order emails in Arabic; native-reader proofread signed off by a person. Anything not run will be reported as not run.

## 10. Open questions
Numerals and currency format · Arabic typeface and whether PP Mori's paid family has Arabic · whether checkout and manual-payment instructions work in Arabic · whether translated variant metafields filter correctly · who the Arabic translator is · which option (A, B or C).

## 11. Option A: what it requires (agreed 30 Oct)
Minimum set per product for all 46 by Thu 12 Nov, each in English and Arabic: title, short description, dimensions, price including 14% VAT, lead time in weeks, process, finish, colour and room tags, and two photographs (one studio, one detail). The dated list of founder deliverables is in the content document (section 11) and in section 7 above. If a checkpoint is missed I will say the same day which part of A can no longer be done and offer the cut; you decide.

## 12. RTL fixes done in the prototype (30 Oct, task T-24)
Fixed and checked in the browser: the skip link no longer makes the page 10,000px wide (every page: 0 overflow in RTL and LTR at 1440 and 375px, 28 combinations); the 24 fixed left/right lines are logical properties (placeholder tags, links, filter counts, drawer side and slide direction, prices, specs, bag option, gallery counter); the gallery counter reads the scroll position correctly in RTL; category arrows flip; Arabic pages set letter-spacing and uppercase to normal; text links keep a 44px minimum width. A test hook shows any page mirrored: add `?lang=ar` (English text, mirrored layout; the theme will use the Shopify locale instead).
**Not done:** the hero text still lands on the artwork in RTL (needs real photography with a text-safe area per direction); no Arabic text has been set or read; no Arabic font is loaded (the system font stands in); email fields and product codes inside Arabic sentences are not yet isolated; no screen reader pass.

