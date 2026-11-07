---
name: polycraft-folder-mixed-provenance
description: ~/Desktop/POLYCRAFT is a reference folder, not a portfolio — it mixes real delivered work with AI renders and other studios' Instagram posts.
metadata:
  type: reference
---

`/Users/sabry/Desktop/POLYCRAFT` (84 jpgs, 19 mp4s, `Polycraft 2.pdf` — 44 pages, image-only, no extractable text). **Do not treat it as a portfolio.** It contains three distinct piles:

- **Delivered work** (photographed in situ): mirror-polished stainless pyramid + standing sculpture, faceted metal reception desks incl. a Steelcase-branded one, rooftop GRP sectionals/ottomans/loungers, painted low-poly animals, lacquered credenza, planters, pendant lamps. A product-code system exists (`STP-03` drawing carries the Polycraft arrow logo).
- **AI-generated renders**, identifiable by a sparkle watermark in the lower-right — the Mercurius fan-back chair, beige faceted sofa, most side tables/consoles, the steel bear in a lobby. Brand names already in circulation in these: **VERTEX · Outdoor Living**, **MERCURIUS' · The Geometric Collection**.
- **Other studios' work**: `denerog` (Kazan) Instagram posts, a white low-poly owl with a likes overlay, folded-metal animals installed on Broadway.

**Why:** Assuming any given image proves manufacturing capability will produce wrong claims about what the factory can build.

**How to apply:** No tooling for this folder on the machine — no ImageMagick, ffmpeg, or PIL. Use `sips -Z 640` to make thumbnails, then read them. Related: [[polycraft-venture-constraints]].
