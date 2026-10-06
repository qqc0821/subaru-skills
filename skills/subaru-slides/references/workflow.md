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
| 1 | Slide-by-slide outline: purpose-appropriate title, up to four points, visual type; add a visual plan when assets are needed | User approves or adjusts |
| 2 | Complete same-copy directions when exploring design; retain the user's accepted baseline when refining | User selects a direction or has already authorized its use |
| 3 | Cover and representative content/product/evidence pages together (all slides in Collaborative mode) | User approves or has authorized execution; inspect before expanding |
| 4 | Final path, QA receipt and claim boundary | User accepts delivery |

Existing authorization applies to these checkpoints. A request to execute an agreed plan does
not require repeated approval. For optional unanswered choices, state a small reversible assumption;
silence does not approve a choice that requires user input.

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
