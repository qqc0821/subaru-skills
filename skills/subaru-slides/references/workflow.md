# Workflow

End-to-end flow. SKILL.md is the router; this file has the operational detail.

## Step 0 - Capability probe
Run `scripts/detect_capabilities.py` (add `--json` for machine output).
It reports what the host supports and recommends a path. Never promise a path the host cannot run.

## Step 1 - Choose path
| Path | Product | Requires | Read |
|---|---|---|---|
| A | native editable PPTX | native builder (artifact-tool / python-pptx) | `paths/path-a-native.md` |
| B' | AI visual base + native text | image generation + native builder | `paths/path-b2-hybrid.md` |
| C | single-file HTML deck (exportable) | deck-stage / HTML->PPTX converter | `paths/path-c-html.md` |
| B | full AI visual PPTX | image generation | `paths/path-b-visual.md` |
| fallback | image-only PPTX | python-pptx + Pillow (bundled) | `paths/path-b-visual.md` |

Recommendation order: **A -> B' -> C -> B -> fallback**. If a capability is missing, say so explicitly and use the next path.

## Step 2 - Confirm settings (ask the user)
- **Collaboration mode:** Full Auto (1 checkpoint) / **Guided** (3 checkpoints, default) / Collaborative (per slide).
- **Audience, duration, goal, tone** if not already given.
- **Output form:** editable PPTX / visual PPTX / HTML deck.

## Step 3 - Content structuring
Read `content-structure.md`. Produce a slide-by-slide outline (title = assertion sentence, <=4 points).
**Checkpoint 1:** show the outline table, ask to approve/adjust.

## Step 4 - Style selection
Read `../styles/index.json`. Match the topic against `theme_recommendations`, then `formality` and `path@@.
Pick **3 candidates** with different directions (not three of the same family).
**Checkpoint 2:** show the 3 candidates with their one-liner + sample, ask the user to pick.
(Optional) If the host can render, generate one cover preview per candidate and show images, not prose.

## Step 5 - Build
Follow the chosen path file. For AI imagery, read `illustrations.md` and the style preset `../styles/<id>.md`.
**Checkpoint 3:** show 2-3 key slides (or all, in Collaborative mode); ask approve/regenerate.

## Step 6 - Assemble and preview
Render every slide to an image and inspect them (see `qa/render-and-validate.md`).
Use a contact sheet only for deck-level flow, never as a substitute for per-slide review.

## Step 7 - QA and delivery
Run `qa/checklist.md`, then `qa/delivery.md`.
**Checkpoint 4:** present the file path, ask if any slide needs adjustment.

## Collaboration modes
| Mode | Checkpoints |
|---|---|
| Full Auto | 1 (topic only) |
| Guided (default) | 3 (outline / style / preview) |
| Collaborative | per slide + per illustration |
