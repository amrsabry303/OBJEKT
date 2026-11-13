# Live theme vs repo, 12 Nov 2026

> **13 Nov 2026 update:** the live (MAIN) theme is now `190236524768` "OBJEKT UX audit (draft 12 Nov)" (created 12 Nov 08:41 UTC, last edited 09:03 UTC, publish not logged). On 13 Nov all 67 of its files were read through the Admin API (`theme.files` bodies) and written into `website/theme` on main, so the repo now matches the live theme: every liquid, css, js and svg file matches the live MD5; the JSON files carry Shopify's header comment and its formatting (content as served). `theme check`: no offenses. No font files. The table below is the 12 Nov record, kept for history.

Live (MAIN) theme: `190221484256` "OBJEKT hide single option (draft 12 Nov)", published 11 Nov 2026 ~23:15 UTC (not logged by any session). Read via Admin API `theme.files` (MD5). Repo = `website/theme` on main at fccbb73. JSON templates may differ only by Shopify's header comment; liquid, css, js and locales differ in content. Pull with the CLI: `shopify theme pull --theme 190221484256 --path ../theme` (login needed).

| File | Live MD5 | Repo MD5 |
|---|---|---|
| `assets/card.css` | 38a114c8f7511f3d7064165f4c7485cb | f4a2107012552824dde0512b5689cefc |
| `assets/header-zara.css` | 14c4b3b8dcf9a8d513c58c573de321c1 | MISSING |
| `assets/look.css` | c0d3b3447a77eade9607db62d327ce2b | MISSING |
| `assets/product.css` | c85747f135a8c2b0b8dd2fbcf0b7545b | c8bad426e26bf4672e36f39b62e8761f |
| `assets/product.js` | 8a2436c7328093f247a9c087f538be48 | 69edd8cf34a9e13fdef626941f077b98 |
| `assets/theme.js` | d8e546120fe05339c0d749cd357cb678 | 9e7f5145f55c88ad542c3840378567c7 |
| `config/settings_data.json` | 2e200127faa379ca8dbebcf8a841085f | 8a80554c91d9fca8acb82f023de02f11 |
| `locales/ar.json` | ee933678e1f9335d79c14fa883868da5 | 1bd4e6311a92e0baec8cdde2b1cf0390 |
| `locales/en.default.json` | 3acfd94bde851eca7f3d84ec72363af6 | 09bef06bbf8025b47196ca3b0647f144 |
| `sections/footer-group.json` | 093f1c8c33dc68fee8af49ef1e003423 | b55c9a24dc576254e7708fff2a429e2d |
| `sections/header.liquid` | 6b73d79365cd80ce906f0743fa69a6a9 | e33273174ccc5cb728412d60885bc31f |
| `sections/main-cart.liquid` | 7d06c4d47ac2196428a3462647c69f3b | 75926d1106059490aabb0ca36fc7b41d |
| `sections/main-collection.liquid` | 01a84326bbae6367d1beec5ee7ae6715 | 94d3ac70a23531c7e3dae4dc33c82dbf |
| `sections/main-custom-request.liquid` | 7b763e142aa1ff88fc5bb565e09328e8 | MISSING |
| `sections/main-product.liquid` | eed795f34bb039770a25d7276a1b3d67 | 8b57741443a3b51cc95213c2ddb998ce |
| `snippets/cart-lines.liquid` | 0a371d03d9dce13d8dda854c6613eeaf | 729a2f815a3ece87c308fd5d5455c114 |
| `snippets/product-card.liquid` | 730fa03c003bfd226e727e269735e0cf | 4293a715051d4da4f67e7414a95d6c79 |
| `templates/404.json` | f14a0bd594f4fee47b13fc09543098ff | 5997118b0bdb18872caeb79bfa49074f |
| `templates/article.json` | ad666c671b57f7ddd96f57b9b9703a19 | 0e6312f67f39046d3e136d3d4a9eb421 |
| `templates/blog.json` | 1b2596dd835ba7c66ec160587daf94fe | 8d12e589097476dc58dd66793bb0a337 |
| `templates/cart.json` | 303baefb39480ffae3db47be11554431 | e9f583e1c69d0e74fbe1d6c4bd2f8bd8 |
| `templates/collection.json` | d365b2f79389ca1a8ac048dc220a2148 | 270333c20d76bb2613b39000366506eb |
| `templates/list-collections.json` | c2bcb59a50ebc391f0c62a9185edc08e | e52e1dc46e1d2bff7c99d5c69bd011a8 |
| `templates/page.custom-request.json` | a7aa6a6547ba29adaa899248a609c20d | MISSING |
| `templates/page.json` | d8085538dc93d34f2457f8df79e37e50 | 5e958ef7f7c0dfad15b889754bfdf44e |
| `templates/password.json` | 035669da9beb69c1de87c26913ae8fec | 854d6f6b32b5d02cea5524b6eb71a260 |
| `templates/product.json` | ce6ad32b13ebf9c3b055bfcc6eadaca6 | 1b0cfa746902d17fe5ab827a3fe54785 |
| `templates/search.json` | 442da8cb11eaff2e7b57908088739d00 | 41bbaa2a472d615adffb20d7c66103fc |

All 67 live files: no font files.
