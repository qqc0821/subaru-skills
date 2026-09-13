# Workflow Details

`SKILL.md` owns the canonical Step 0–7 flow. This file keeps only collaboration settings,
checkpoint payloads and exception handling that should not be duplicated in the router.

## Settings to confirm

If the user has not specified them, confirm:

- **Collaboration mode:** Full Auto (one final checkpoint), Guided (outline/style/preview,
  default), or Collaborative (checkpoint per slide and illustration).
- **Audience, duration, goal and tone.** Infer only when the brief makes them unambiguous.
- **Output form:** editable PPTX, visual PPTX or HTML deck.

## Checkpoints

| Checkpoint | Show | Continue when |
|---|---|---|
| 1 | Slide-by-slide outline: assertion title, up to four points, visual type | User approves or adjusts |
| 2 | Three style candidates with one-liner, palette and sample | User selects a direction |
| 3 | Two or three key slides (all slides in Collaborative mode) | User approves or requests revision |
| 4 | Final path, QA receipt and claim boundary | User accepts delivery |

Full Auto combines checkpoints 1–3 into one approval. When the user does not respond,
use the stated default mode and make the smallest reversible assumption.

## Exceptions and fallback

- Run the capability probe before promising a construction path.
- If a capability is missing, state the limitation and follow the next available path:
  `A → B' → C → B → fallback`.
- If rendering is unavailable, run structural checks and explicitly state that visual QA
  was not performed.
- If a template or brand source is provided, compare the rendered result against it;
  successful import alone does not prove template fidelity.
- Before delivery, render every slide when possible, run the QA checklist, and report
  which checks were and were not performed.
