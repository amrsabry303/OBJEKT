# objekt product images: house style (set 2 Nov 2026)

One look for every AI render, so no scene experiments per product. Source: website design system register 2
("sculptural studio", `docs/DESIGN_SYSTEM.md` in the Shopify worktree, v0.1 pending Sabry) and the renders
OBJ-003 Oxblood v2 and OBJ-166 v4 stainless, which Sabry saw. Reviewed against these, not against the brand guide:
the guide has no photography section.

## Revision, 10 Nov 2026 (Sabry): look like a real photograph, not AI. This overrides the 2 Nov revision below.
Sabry: most renders look AI. He sent five references that look real (mood only, never copy them): a book on a shag rug with a hand in frame; a travertine, brushed-steel and leather stool on a seamless grey sweep; three cut-out side tables in red, black and white in a room with a plaster arch (this is the OBJ-038 reference); a pale green three-leaf table on a grey sweep; ash-wood vase, candleholder and tray set with dried flowers and lit candles on white. What they share:
- **Light: soft, large, directional daylight**, like a big window or a softbox from one side. Gentle gradient on the wall, soft-edged contact shadows under the object. **No hard sun patches, no light beams, no long dramatic cast shadows** (these read as AI; they replace the 2 Nov "low window sun" rule).
- **Background: plain and quiet.** Either a seamless studio sweep in pale warm grey or off-white, or a real room with one calm architectural feature (a plaster arch, a doorway edge). Matte floor with a faint, soft reflection. Lots of empty space around the object; the product is the subject.
- **Materials read true:** visible grain, pores, brushed lines and powder-coat texture; matte paint looks matte, steel shows soft long reflections. No plastic gloss, no waxy surfaces, no over-sharpening, no heavy film grain.
- **Camera like a real shoot:** eye level or slightly above, 50 to 85 mm look (no wide-angle distortion), straight verticals, whole object in frame, portrait 4:5. The product sits slightly off-centre with headroom.
- **Composition is intentional:** one product, or the same product in two or three of its colours staggered in depth (a family shot). Props only when they show use and belong to the product (candles in a candleholder, stems in a vase, a book on a table); at most one or two, neutral colours. Otherwise no props.
- **Human touch, only for lifestyle shots:** a hand or a sleeve at the edge of the frame is allowed; never a full person.
- Prompt wording that carries this: "professional interior product photograph, soft diffused daylight from a large window on the left, soft contact shadows, seamless pale warm grey backdrop / plain plaster room, matte floor with a faint soft reflection, true-to-life materials, 70 mm lens at eye level, generous negative space, no hard sunlight, no dramatic shadows, no text".
- Keep the fidelity rules below (exact shape, part counts, brand hex, check every render).

### First result with this style: OBJ-038 Carbon v2 (10 Nov, `imagen-nano-banana-2-1`, 65 credits, first try)
Reference: a tight crop of the product alone from the reference photo (no room), so the model keeps the shape and invents nothing from the reference scene. Prompt:
> Professional interior product photograph of the single side table from the reference image, keeping its exact design: <3 to 5 plain facts about the shape>. Only one table. Finish: matte Carbon powder coat, soft black #222222, fine satin texture, no gloss. Setting: seamless studio backdrop in pale warm grey (#DCD7D0) curving into the floor, matte floor with a faint soft reflection under the table. Light: soft diffused daylight from a large window on the left, gentle gradient on the backdrop, soft contact shadow under the feet. No hard sunlight, no light patches, no dramatic cast shadows, no props. Camera at a slightly high eye level, 70 mm lens look, slight three-quarter view, straight verticals, whole table in frame, placed slightly off-centre with generous empty space above. True-to-life materials, like a real catalogue photograph. No text.
Result: shape held (top, cross plates, rounded corners, feet, flower cut-out), reads as a photograph. Use this as the default product shot; make the family shot (two or three colours) and the in-room shot from it.

## Revision, 2 Nov 2026 (Sabry): real sunlight and objects in use (superseded on 10 Nov for the light; props rule still applies)
Sabry said the flat studio look reads as AI, and that real sun light and elements such as a vase, showing the product in use, look more real. He sent a reference photo: a dark plinth with a rough clay vase on top, hard window sunlight landing as a bright patch on the wall and floor, a long soft shadow on the wall, pale plaster walls, a wall edge or doorway framing the side. This overrides the "no props" and "soft diffused light" lines below for every new image. The vase photo is a mood reference only; do not copy it.
- Light: one low window sun, hard-edged bright patch on the wall and floor, a real cast shadow, warm highlights. Not a flat even studio light.
- In use: one or two props that fit the product, restrained and imperfect (a rough clay or ceramic vase on a plinth, a book or bowl on a table, a single branch). Never more than two. Props are plain neutral or earth tones, never brand-coloured.
- Imperfection: slightly irregular plaster, a visible edge of the room, slight film grain. Avoid symmetry and glossy perfection.
- Fidelity risk: props and hard light make the product harder to keep exact. Keep the product's silhouette clear, and check proportions after.

## Every product needs a context image (Sabry, 2 Nov 2026)
Besides the product shots (one per colour), each product gets at least one image in context: a real room, the product in use, low sun, same aesthetics (plaster walls, limestone, linen, stoneware, plain wood). Use the product's own finished render as the image reference so the product does not change, and ask for a wide 3:2 composition "so the set is clearly part of the room, not filling the frame". One or two plain props only (napkin, plate, chair edge). Used for OBJ-099 Oxblood (dining table, 65 credits, one shot, no retry needed). Count it in the product's images.
Context ideas by family: candleholders and vases on a dining table or console; tables with a book, cup and a lamp; stools and benches beside a bed or in an entry; planters in a sunlit corner; wall pieces above a console; lighting on a bedside or desk; sculpture on a plinth in a hall.

### Sunlight edit prompt that worked (OBJ-166 v6, `ideogram-4-5` + `preciseEdit`, 80 credits)
Run it on a finished clean render (the base scene below) to add light and a prop without changing the product:
> Keep both plinths exactly as they are: same shapes, sizes, proportions, positions, camera angle and <finish>. Change the light and add one prop. Light: a single low window sun coming from the right, casting a hard-edged bright patch of sunlight on the wall and floor behind and beside the <object>, with long soft cast shadows falling across the wall and floor, warm highlights. The wall is slightly irregular pale warm plaster with a visible room edge at the left, and the floor is smooth pale plaster with a faint sheen. On top of <the shorter one / the table> stands one rough, hand-made earthenware clay vase in muted terracotta brown, smaller than the top. Subtle film grain, natural and imperfect, like a real photograph. No text.
Result: proportions held, looked like a photograph. Say "smaller than the top" or the vase comes out too big. Carbon needed no extra wording. Two-step cost: 65 (clean render) + 80 (sunlight edit), or one step with nano banana if the geometry does not need holding.

## The scene (base, before the revision above)
- Smooth matte plaster wall and floor, pale and slightly grey warm sand (#E1D9CF). Clean, unmarked, even.
- Light from one side, one real shadow under the object, contact point visible.
- One product per image (a pair only for a product sold in two sizes). Props per the revision above.
- Low three-quarter view, whole object in frame, 4:5 portrait, 2k.
- The object sits on the floor; its base is visible, never buried.

## Prompt template (nano banana 2.1, `imagen-nano-banana-2-1`, 65 credits)
> Sculptural studio product photograph of the single <object description> from the reference image, keeping its exact design: <3 to 5 plain facts about the shape, counts and positions of parts>. Only one <object>. <Material and finish, with the brand colour name and hex>. Pale, slightly grey warm sand wall and floor (#E1D9CF), smooth plaster, clean and unmarked, not orange and not peach. Soft diffused natural light, a soft real shadow on the floor, slight three-quarter view from a low angle, whole <object> in frame, no props, no text.

Pass the product's reference photo as an `image` reference. Count = 1.

## Lessons (cost about 700 credits to learn)
- Say "pale slightly grey warm sand" with the hex. Plain "sand" gives beach sand; "concrete" or "textured" gives a brutalist wall.
- Spell out part counts and positions ("three legs at 120 degrees, third partly visible behind").
- Numbers in the prompt (220 mm, 1000 high) are ignored. For plain boxes and plates only, build a grey geometry model from the drawing, then edit it in place with `ideogram-4-5` + `preciseEdit` (80 credits). That keeps proportions exactly, but it takes the backdrop words literally, so test the wall wording first. Do not do this for curved or complex pieces.
- Do not draw foot or fixing markers on the geometry model; they come out as dark dots.
- Two generations at once can hit a provider quota error (not charged). Run one at a time.
- Check each render for: part count, leg or part shape, colour against the brand hex, wall colour, base visible.

## Colours (official, from COLOURS-FINISHES.md)
Bone #E9E4D8, Putty #B9B2A5, Carbon #222222, Ink #1E2A44, Oxblood #5A1F25, Clay #A8553A, Chocolate #4A2A1B, Objekt Green #37613F. Matte powder coat unless the product says otherwise. Mirror or brushed for exposed metal.

## Files
- Local: `_plan/images/OBJ-nnn/OBJ-nnn_ai-render_<colour>_<scene>_vN.png`. Keep superseded versions.
- Drive: the product's design folder (upload with the Chrome method; one hidden input per file, one drop).
- Every image is an AI render, not a photo of a prototype. Replace with real photos when the first pieces exist.
- Budget: about 65 credits per image; plan one image per product plus a retry allowance of about 40 percent.
