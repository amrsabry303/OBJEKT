# objekt: product workflow (design to social)

Applies to every OBJ-nnn. Owner of production is left unnamed: the role is "Production".
Sabry decides at three gates only. Everything between gates is Claude's.

## The line

| # | Stage | Who | Output | Exit |
|---|-------|-----|--------|------|
| 1 | Reference | Sabry | photo or link, one line of intent | enters Inbox |
| 2 | Design | Claude | 2-3 original variants (not a copy), dimensions proposed, 2-3 colourways with paint system and finish | **GATE A** |
| 3 | Technical drawing | Claude | dimensioned front/side/top (PDF + SVG), DXF for plate parts, STEP for simple solids | **GATE B** |
| 4 | Makeability and cost | Production | go / change request, cost, lead-time band, prototype | go + cost + prototype |
| 5 | Shoot | Claude | catalogue set and website set in the agreed look | **GATE C** |
| 6 | Listing and social | Claude | EN/AR copy, Shopify row, social posts | live |

Gates:
- **A, design:** Approve / Change (say what) / Reject. Colour: accept mine or give yours.
- **B, drawing:** Approve / Change. Approval means "this is what Production reviews", not engineering sign-off.
- **C, images:** Approve / Retake. Each product is checked against the real piece.

Rules that hold the line together:
- Nothing is cut before B and a Production "go".
- Nothing goes live until the piece has an approved design and a cost. A prototype is required by default.
- **Sabry decides per product** whether a prototype is waived (flag `proto: required | waived`). A waived product is listed from renders and sold made to order. Production still gives a go and a cost before listing.
- Real prototype photos are the source for the shoot when a prototype exists. Otherwise the shoot uses renders, marked as renders in the file, and they are replaced when the piece exists. Whether the shop page says "render" is Sabry's call.
- Costs and prices come only from Production. Claude never fills them.
- Only original designs. A reference is inspiration; nothing copied is sold. (Superseded 27 Oct for drawings: see memory/objekt-exact-by-default.md.)

## Chats and agents

One chat per stage, working in batches of about 5 products, not one chat per product. The shared state is the **objekt workspace** plus a **spec card** per product (OBJ-nnn.md: approved design, dimensions, colourway, paint system, finish, decisions, links). A new chat reads the card and starts cold.

| Chat | Job | Parallel agents |
|------|-----|-----------------|
| Hub | status, gate decisions, weekly plan, backups | none |
| Design | stage 2 for a batch; makes the A-cards | one per product |
| Drawing | stage 3 for approved designs; makes the B-cards | one per product (cap 4 at once) |
| Imagery | stage 5; look standard, fidelity check per product | one per product, plus a checker |
| Content | stage 6: EN/AR copy, Shopify CSV, social calendar | copy, Arabic review, CSV validation |

Each agent works on its own product folder and does not read the others' output. A separate checker agent reads the drawing against the approved design before it reaches Sabry.

## Cadence (written 27 Oct, 24 days to 20 Nov)

- **Mon:** A-cards for the next batch arrive.
- **Wed:** B-cards for last week's approved designs.
- **Fri:** C-cards, plus the weekly status and one backup.
- Sabry sees at most five decisions at a time, each answerable in one line from a phone.
- Work in progress is capped at 10 products between gates.

Rough path for launch: batch 1 (about 10 simplest designs) through B by Fri 6 Nov, Production data by Fri 13 Nov, freeze Mon 16 Nov. The 20-at-launch target depends on Production's turnaround and prototypes.

## Needs from outside the line

- A named Production contact and a way to reach them (not yet decided).
- Costs, lead times, weekly output, accepted file formats.
- Trademark and domain status, tracked separately.

## Decisions recorded 27 Oct 2026

- **Design freedom:** set per product: `exact`, `free` or `custom`. (Default changed to exact on 27 Oct; see memory/objekt-exact-by-default.md.) Claude proposes dimensions; Sabry modifies if needed.
- **Prototype:** required by default; Sabry flags exceptions as `waived`.
- **Customer and price:** design-aware Cairo homes, EGP 4k-90k band.
- **Pricing:** hybrid. Claude benchmarks the market and Production gives cost; Sabry sets each price.
- **Colour:** follow the objekt colour guide (Objekt Green #37613F signature).
- **Coffee tables:** launch in objekt; revisit the objekt/subjekt boundary after launch.
- **Delivery:** all of Egypt from day one.
- **Payment:** Paymob. Made-to-order takes a 50% deposit; stock items are paid in full.
- **Social:** Instagram only.
- **Approvals:** decision cards live in the objekt workspace (Approve / Change / Reject), not in chat.
- **No colour:** stainless and other bare-metal products carry no colour; material and finish (brushed or mirror) are set instead.

## Workspace audit, 27 Oct 2026

Ready to list = 12 checks (ours, design approved, spec set, drawing approved, prototype, Production confirmed, cost, price, lead time, all shots, copy EN and AR, shipping weight and size). Products Production already makes skip design, drawing and prototype.
