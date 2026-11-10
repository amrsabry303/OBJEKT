# OBJEKT — Shopify website

One coherent project: a design-led Shopify Online Store 2.0 theme for OBJEKT (contemporary furniture and objects, Egypt). The founder (Sabry) is final decision-maker. Read this file first, then the doc for your task.

## Source of truth (docs/)
| File | Read when |
|---|---|
| PROJECT_BRIEF.md | brand, business goals, constraints |
| DESIGN_SYSTEM.md | any visual or CSS work |
| SITE_ARCHITECTURE.md | pages, nav, sections |
| SHOPIFY_ARCHITECTURE.md | any Liquid/theme work |
| PRODUCT_SCHEMA.md | metafields, variants, availability, tags |
| ROADMAP.md / TASKS.md | what to do next, who owns it |
| DECISIONS.md | before reopening anything already decided |
| QA_CHECKLIST.md / CHANGELOG.md | testing and release notes |

## Layout
- `prototype/` — static HTML/CSS/JS visual prototype (no build step). Serve: `python3 -m http.server 4173 --directory prototype` (also in `.claude/launch.json`).
- `theme/` — Shopify theme (not created yet; starts at Milestone 03, after founder approves the prototype).
- `.claude/agents/` — the seven subagents. `docs/` — shared documents.

## Operating rules
1. Lifecycle: BRIEF → DESIGN → REVIEW → APPROVAL → DEVELOPMENT → TESTING → ACCEPTANCE. Generated code is not "done" until reviewed and tested.
2. One owner per file or tightly coupled feature at a time (owner column in TASKS.md). Parallel code work uses branches or worktrees.
3. Disagreements go in DECISIONS.md with a proposed resolution; never silently overwrite another agent's work.
4. Report only what was actually run. "Not tested" is a valid status; "passed" without execution is not.
5. Never invent brand facts: history, designers, certifications, materials sourcing, production claims, prices, lead times. Placeholders are labelled "Placeholder" / "Sample" in the UI.
6. Official brand colors are exactly `#263A5A` (navy) and `#E2D9CF` (sand). Navy is a signature, not a theme. No gradients, gold, heavy shadows, discount widgets.
7. The logo exists (navy angular mark over a thin rounded OBJEKT wordmark) but the file is not in the repo yet. Until it is, the prototype wordmark is placeholder text; never redraw or approximate the logo.
7a. Fonts: PP Mori is the working typeface, loaded from gitignored `prototype/fonts/` (free files, local review only; founder will supply the web licence later). Never commit font files, deploy publicly or upload a theme containing them until the licence is held. Galak Round is unlicensed and unused. See DECISIONS D-013.
8. Shopify first: native inventory, variants, metafields, metaobjects, Online Store 2.0. No React/headless. Nothing hardcoded that a merchant should edit.
9. Never touch a live store, products, prices, orders, checkout or payment settings without explicit founder approval. Develop against an unpublished/dev theme. No credentials in files or prompts; use env vars / Shopify CLI auth.
10. Do not claim deposits, production tracking or Egyptian gateway support work in standard checkout. These are verification items (see SHOPIFY_ARCHITECTURE.md §Limits).
11. Keep docs short. If a doc is not read, delete it rather than let it rot. Update CHANGELOG.md when a milestone item is verified.

## Founder approval required
Brand direction and final aesthetic, major UX changes, positioning, pricing and payment policy, production and delivery promises, external costs, launch. Batch these as one review request with a recommendation and alternatives.

## Current state
7 Nov 2026: the theme is built and pushed to an unpublished theme (`189754769632`); Horizon is still live. Brand Guidelines V1 applied (D-026), OBJ-099 added, Paymob card app installed but not signed in. Launch target Fri 20 Nov 2026 is at risk. **Read `docs/HANDOVER.md` first**: access, commands, store state, open decisions and the pre-launch cleanup list.

10 Nov 2026: **Claude Code takes over. Read `docs/HANDOFF_2026-11-10.md` first** (footer done, Sabry's shipping, deposit and lead-time answers, the shipping plan, open questions, next tasks).
