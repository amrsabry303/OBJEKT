# Homepage prototype audit — 2026-10-29

Scope: `prototype/index.html` as committed at `47d2d6e`, in the in-app browser (desktop 1440 and 1024, mobile 375). Reviewed against the brief, DESIGN_SYSTEM.md, and the logo PDF the founder supplied (`projekt trial 4.pdf`, page 1 only viewed).

## Verdict
Structure, navigation and typography are sound and the menu behaves correctly. Three engineering defects need fixing before this is a base for Liquid, and the visual layer has one real problem: **the placeholder artwork (arches, circles, cylinders) is soft and generic, while the real OBJEKT mark is faceted and angular.** Judge the design on photography, not on these placeholders.

## Executed checks
| Check | Result |
|---|---|
| One `h1`, landmarks (header/nav/main/footer), no duplicate ids, `lang=en` | pass |
| All `role=img` placeholders labelled; decorative SVGs hidden | pass |
| Horizontal scroll at 375px | pass (scrollWidth 375) |
| Mobile menu: open by keyboard, Esc closes, focus returns to Menu, scroll-lock cleared, `aria-expanded` toggles | pass |
| Menu link closes menu and navigates | pass, but see A-02 |
| PP Mori loads (400 and 600 weights) | pass |
| Palette contrast: navy/paper 10.51, navy/sand 8.21, paper/navy 10.51, grey-text/paper 6.27, grey-text/sand 4.89, navy on hero floor 7.22 | pass |
| Tap targets at 375px | **fail**, A-03 |
| HTML structure | **fail**, A-01 |

## Not run (do not treat as passed)
`prefers-reduced-motion` emulation (CSS read only) · screen reader · real touch device / hover-less behaviour · Lighthouse / Core Web Vitals · tablet widths · Safari and Firefox · the image-swap hover state visually · PDF page 2 · no-JS rendering.

## Defects
| ID | Sev | Finding | Evidence | Fix |
|---|---|---|---|---|
| A-01 | major | `<figcaption>` is inside `<a>`, not a direct child of `<figure>`: invalid HTML, 5 product plates | counted 5 in DOM | put `<a>` around image only (or around image and caption inside a wrapper div, no `figure`), or keep figure > a-image + figcaption + link overlay |
| A-02 | major | Sticky header (64px) covers the top of any anchored section | `#collection` lands at `top: 0` after menu click | `section[id] { scroll-margin-top: var(--header-h) }` |
| A-03 | major | 20 interactive elements under 44px at 375px: Bag 37px high, wordmark 32, Menu 38 wide, all text links 20, footer links 30 | measured | min-height 44px via padding on header tools, footer links, text links. **My earlier DESIGN_SYSTEM claim of 44px targets was wrong and is corrected.** |
| A-04 | major (design) | Second-image hover has no touch equivalent, and the category preview pane is hidden on mobile, so mobile gets no category imagery | by construction; not tested on device | PDP/PLP gallery swipe; small thumbnail per category row on mobile |
| A-05 | minor | Availability, the key commercial signal, is 11px uppercase grey; 46 text nodes at 11px and 21 at 10px | measured | availability at 12–13px, solid/hollow marker larger (9–10px) and a one-line legend in the grid header |
| A-06 | minor | Hero height hard-codes the prototype bar (31px); on mobile the bar wraps to two lines, hero bottom at 829px vs 812px viewport | measured | use a CSS variable for the bar, or drop the calc in the theme (no bar there) |
| A-07 | minor | Google Fonts request still made although PP Mori is primary; fonts are 65–69 KB `.otf` each | resource list | theme: self-hosted `.woff2`, preload the two used weights, no third-party CSS |
| A-08 | minor | 35 of 52 links are `href="#"`; `#about` is an empty span | counted | expected for prototype; real routes in theme |
| A-09 | minor | Placeholder tags are 4.14–4.31:1 on two placeholder grounds, and unreadable where a tag overlaps the navy arch on mobile | computed / seen | placeholder-only; move tags to a consistent corner on a paper chip |
| A-10 | info | Menu opens with focus on the wordmark link, not the Close button | measured | focus Close first, or leave: acceptable |

## Aesthetic audit against the brief's ten criteria
1. **Premium design brand?** The type system and layout rhythm read editorial and calm. The artwork does not yet: flat arches and circles look like stock "Scandi minimal" illustration. Not a verdict on the brand, because no photography exists.
2. **Photography dominates?** Structurally yes (full-bleed hero, 4:5 lead plates, split story). Unproven until real images replace the forms.
3. **Avoids generic Shopify?** Layout yes. The placeholder geometry is the generic part.
4. **Typography refined?** PP Mori Regular at display size with tight tracking works. Weakness: nearly everything small is the same 11px caps label, so section titles ("Selected Objects", "The Edit") are too quiet and the hierarchy flattens below the headline.
5. **Navigation effortless?** Yes at this scope. Missing: Shop panel, working search.
6. **Discovery and purchase?** Not testable until collection and product pages exist.
7. **Ready vs made to order clear?** Distinguishable, but the 7px solid/hollow square is subtle and unexplained. See A-05.
8. **Mobile as beautiful as desktop?** Hero and plates yes; category section is the weak spot (A-04).
9. **Staff-manageable?** Not applicable until theme.
10. **Own identity?** Partly, and the logo changes the answer (below).

### What the logo changes
- The OBJEKT mark is a single faceted polygon: chamfered, asymmetric, small corner radii, one diagonal cut. The sister marks on the same sheet (SUBJEKT, JEKT) are the same language: angular furniture/animal silhouettes. The prototype's soft arches and circles contradict it. **Recommendation:** redraw the placeholder forms as chamfered polygons with small radii and one diagonal cut, and let image crops and the Edit plates echo that angle. This is also what makes OBJEKT look unlike its references.
- The logo wordmark is thin, monoline, wide, uppercase, with a J that sits on the baseline. The prototype header wordmark is 600 weight with 0.22em tracking: much heavier. It is a placeholder, but when the real logo goes in, expect the header to need a lighter, smaller treatment and a horizontal or wordmark-only version; the supplied lockup is stacked (mark above wordmark).
- The wordmark is **not** Galak Round (checked by rendering both: the J and terminals differ) and not PP Mori either, so it is likely custom or a third face. Ask the founder.
- Heaviest element in the prototype is the near-black stool plate (`#252525`); it reads off-palette next to navy and sand. Replace with a navy or sand ground.
- The footer's giant wordmark is a strong device; with the real logo, test the mark alone at that scale.
- The sheet shows a three-logo family (SUBJEKT dark green, OBJEKT navy, JEKT rust). Whether SUBJEKT and JEKT are sister brands, past concepts, or alternatives is not stated. I have not assumed; it affects whether the site needs a wider palette.

## Recommended order
1. A-01, A-02, A-03 (mechanical, safe).
2. Rework placeholder geometry to the logo's faceted language; strengthen section titles and the availability marker (A-05).
3. Supply OBJEKT logo as SVG with a header-size version; then integrate.
4. Re-audit, including the not-run items.

## Fix pass — same day
Re-run with the same checks after changes (desktop 1440, mobile 375):

| ID | Result |
|---|---|
| A-01 | fixed: `figure`/`figcaption` replaced with `article` + `div.cap`; DOM count of both = 0 |
| A-02 | fixed: `[id] { scroll-margin-top }`; `#collection` now lands at 65.1px under a 65px header (was 0) |
| A-03 | fixed: 0 interactive elements under 44px at 375px (was 20); text links now use a 44px box with a pseudo-element underline (also removes the gradient-based underline) |
| A-05 | partly fixed: availability text 12px (was 11), marker 9px (was 7), legend line added above the grid. Section titles and the 46 remaining 11px labels are unchanged |
| A-06 | fixed for the prototype: bar height measured by script into `--bar-h`; hero bottom 813px vs 812px viewport (1px rounding) |
| Shapes | placeholder objects, hero, story strata and collection redrawn as chamfered polygons with small radii; near-black stool replaced with navy on deeper sand |
| Regressions caught and fixed during this pass | desktop-only header links reappeared on mobile; hero label collided with the navy block |

Open: A-04, A-07, A-08, A-09, A-10, and everything under "Not run". Note: the new hero block (diagonal roof over a rectangle) is close in spirit to the real mark. As a placeholder that is fine; before real imagery or any graphic use of the mark, the founder should decide whether the mark may be used as a recurring device. Not re-run: contrast, keyboard menu test, no-JS.
