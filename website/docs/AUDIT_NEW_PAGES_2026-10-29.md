# Audit: Shop panel, The Edit, story and About — 2026-10-29

Scope: `edit.html`, `article.html`, `about.html` and the Shop panel (present in all seven headers), at commit `8c539f5`, in the in-app browser at 1440, 900 and 375px. Method as in `AUDIT_ALL_PAGES_2026-10-29.md`.

## Verdict
The new pages are structurally clean and read as part of the same system; the copy makes no claims. One accessibility defect in the Shop panel (C-02) should be fixed before the theme build, and one heading-text regression (C-01) repeats a bug already fixed elsewhere.

## Executed
| Check | Edit | Story | About | Panel |
|---|---|---|---|---|
| One `h1`, landmarks, unique title, meta description, skip target | pass | pass | pass | n/a |
| Duplicate ids, broken `aria-*` / `<use>` references | none | none | none | none |
| Accessible names on every control and image | pass | pass | pass | pass |
| All local links and anchors resolve (incl. `#objects`, `?topic=`) | pass | pass | pass | pass |
| Tap targets under 44px, 1440 and 375px | 0 | 0 | 0 | 0 |
| Horizontal overflow, 1440 and 375px | 0 | 0 | 0 | 0 |
| Text contrast (computed, CSS backgrounds) | pass except placeholder tags (4.14:1) | same | same | pass, measured while open |
| Opens on keyboard focus, Tab enters it, Esc (focus inside) closes and returns focus | – | – | – | pass |
| Opens on mouse hover, stays open when the pointer moves into it, closes after leaving | – | – | – | pass |
| Panel sits above the sticky collection toolbar | – | – | – | pass (hit-test) |
| Panel layout at 900px | – | – | – | pass, no overflow |
| Topic filter: valid topic, invalid topic falls back to All | pass | – | – | – |
| Copy scan for unsupported claims (handmade, sustainable, founded, certified, award…) | none | none | none | none |

## Not run
Screen reader · real touch device, including panel behaviour on tablets wider than 880px · Lighthouse · reduced-motion emulation · no-JS rendering (read only) · Safari and Firefox · panel at widths between 881 and 1000px beyond the 900px check.

## Defects
| ID | Sev | Where | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| C-01 | minor | Edit | `The<br>Edit` makes the heading text "TheEdit". The same bug was fixed on two pages (B-06) and came back on the new one | measured | space before `<br>`; add "spaces around line breaks" to the build checklist |
| C-02 | major (a11y) | Panel | When the panel is opened by the mouse, Esc does not close it, because the key handler listens only inside the panel's list item. WCAG 1.4.13 requires hover-opened content to be dismissible without moving the pointer | hovered Shop, pressed Esc: still visible | listen for Esc on `document` while the panel is open |
| C-03 | open question | Panel | On tablets and touch laptops wider than 880px, hover does not exist. Whether the first tap opens the panel or goes straight to the collection was not tested | not run | test on a real device; if poor, use the disclosure-button pattern (button toggles panel, separate "All Objects" link inside) |
| C-04 | minor | Story, mobile | The image pair stacks two full-width 4:5 images, which makes the page very long | seen at 375px | one 3:2 image, or a horizontal swipe row, below 880px |
| C-05 | minor | all | 15 placeholder `#` links on each new page (footer, search, account, plates) | counted | expected in prototype |
| C-06 | info | Edit | The topic filter needs JavaScript; without it every topic link shows all stories. In Shopify, topics are blog tags with real URLs, so this goes away in the theme | by construction | none now |
| C-07 | info | Story | "Next story" links to the same page | by construction | placeholder |

Carried over: A-04 (hover-only image swap, no touch equivalent), A-05 (31 to 44 labels per page at 10 to 11px), A-09 (placeholder tag contrast), B-07 (JS-built regions, not applicable to these three static pages).

## Aesthetic read
- **The Edit** is the strongest of the new pages: the large navy title, topic rule and asymmetric grid read as an editorial index, not a blog list, and the filtered state falls back to an even grid.
- **The story page** has a good reading measure (about 56 characters), a clear side column and a pull quote that uses the brand navy well. It depends entirely on the photography; the placeholder shapes carry no atmosphere.
- **About** is the most template-like: alternating text and image blocks are a familiar pattern, and four sections with identical structure feel mechanical. The principles strip is the best part, and the opening statement works as a typographic moment. Real photography and a less uniform rhythm (one full-bleed image, one pull quote) would help; that is a design call for the founder, not a defect.
- **The Shop panel** is calm and quick to scan; the availability links with the solid and hollow markers carry the product logic into navigation.

## Recommended
Fix C-01 and C-02 (small), test C-03 on a real tablet, then decide whether About should vary its rhythm.

## Fix pass — same day
| ID | Result |
|---|---|
| C-01 | fixed: `The <br>Edit`; heading text now reads "The Edit". No other unspaced `<br>` remains in the prototype pages (searched) |
| C-02 | fixed: Esc is now handled on the document and closes the panel however it was opened. Verified: (A) opened by hover, Esc with the pointer still on Shop: closed; (B) leaving and returning reopens it; (C) opened by focus, Esc: closed, focus stays on Shop; (D) Tab into the panel, Esc: closed, focus returns to Shop |

Regression checked: topic filter still works; the mobile menu still opens at 375px with no overflow. Open: C-03 (touch behaviour of the panel on wide tablets, needs a real device), C-04 to C-07, and everything under "Not run".
