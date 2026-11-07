# Design system (v0.1, pending founder approval)

Source of values: `prototype/css/tokens.css`. In the theme these become `settings_schema.json` color/font settings emitted as CSS variables in `snippets/css-variables.liquid`.

## Concept: "the catalogue plate"
Each piece is presented as a gallery plate: a flat field, one object, a hairline caption row (name · price · reference), and a small square marker for availability. Indexing, references and uppercase micro-labels give the publication feel; large tight grotesk headlines give confidence. Playfulness comes from scale shifts and offset composition, not decoration.

## Color
| Token | Value | Use |
|---|---|---|
| navy | `#263A5A` | brand exact — type, nav, key UI, one or two full-bleed sections |
| sand | `#E2D9CF` | brand exact — editorial sections, footer, image fields |
| paper (page ground) | `#E2D9CF` | default page; since D-026 the same as sand, per Brand Guidelines V1 |
| white | `#FCFBF9` | alternate image field, cards |
| ink | `#263A5A` | body text (navy, per the guidelines) |
| grey | `#B4AEA7` | hairlines and decoration only (2.02:1 on paper; never text) |
| grey-text | `#5F5A54` | **derived** secondary text; 6.27:1 on paper, 4.89:1 on sand |

Proportion target per screen: mostly paper/sand/photography; navy appears as text, hairlines and at most one large field. Measured: navy on paper 10.51:1, navy on sand 8.21:1, ink on paper 14.08:1.

## Typography
Since D-026: headlines Galak Round all caps, sub-headlines Galak Round sentence case (token `--font-display`, unlicensed, no file shipped), body PP Mori. The older notes below describe the first concept.
PP Mori once licensed (D-013), fallback Helvetica Neue → Arial. Instrument Sans (OFL) is no longer loaded; it remains an option if the licence is not bought. Founder-supplied PP Mori and Galak Round are not cleared for web use (DECISIONS D-013). If a licensed face replaces it, only `--font-sans` and the `@font-face` change; letter-spacing and size tokens may need re-tuning because the logo wordmark is a thin rounded letterform, which suggests a lighter, rounder voice for labels.
- Display: weight 500, tracking −0.035 to −0.045em, line-height ≈ 0.92–1.0, `clamp()` from 3rem to 9.5rem (h1).
- Body 15px/1.55. Secondary 13px.
- Labels: 12px, 500, uppercase, +0.12em — nav, availability, captions, section titles.
- Wordmark: the official OBJEKT logo SVG (`prototype/assets/objekt-wordmark.svg`, navy `#263A5A`), 22px high in the header, large in the footer. Thin monoline strokes: keep it navy on paper/sand, do not go below ~18px high, never faux-bold it. The lettering font is a demo font; licence unconfirmed (DECISIONS D-014).

## Space and grid
12 columns, gutter `clamp(14,1.6vw,24)`, side margin `clamp(20,4vw,56)`, section rhythm `clamp(72,11vw,168)`. Compositions are deliberately asymmetric: items sit on columns 1–7 / 9–12 / 2–5 / 7–12, with vertical offsets. Mobile collapses to 2 columns with full-width lead items.

## Components (prototype → Liquid)
- **Header:** 3-zone grid; nav left, wordmark centre, tools right; sticky, hairline bottom border. Mobile: Menu · wordmark · Bag; menu is a full-screen native `<dialog>` with an expandable Shop list.
- **Product plate** (`snippets/product-card.liquid`): image field, hover swaps to second image (lifestyle), caption row, availability line.
- **Availability marker:** solid navy square = Ready to Deliver; hollow square = Made to Order; lead time shown beside it. Not a badge. No other badges by default.
- **Text link:** uppercase label with a 1px underline that retracts on hover.
- **Category index:** large-type rows; hover/focus drives a sticky preview plate; siblings dim to 45%.
- **Placeholder plate:** flat field + geometric form + "Placeholder · type" tag. Never mistakable for product photography.

## Photography (three registers, balanced per page)
1. Editorial lifestyle — architectural framing, natural light, real shadows, restrained styling.
2. Sculptural studio — neutral or lightly textured ground; silhouette, proportion, surface.
3. Detail — macro of material transitions and finishes.
Ratios used: 4:5 portrait lead, 1:1, 3:4, 3:2 and 16:11 landscape. Hero full-bleed.

## Motion
Reveal on scroll 14px/0.9s ease, hover underline, image swap 420ms, menu fade 420ms. No parallax, scroll-jacking or page transitions. `prefers-reduced-motion` disables reveal and transitions. All motion CSS-only except one IntersectionObserver.

## Accessibility baseline
Visible 2px navy focus ring, skip link, a 44px minimum tap-target rule (**not yet met in the prototype**: audit A-03 found 20 smaller targets), landmarks, labelled form fields, native dialog focus trap and Esc. Hover-only affordances (image swap, category preview) always have a focus equivalent; category preview is decorative so is `aria-hidden`.
