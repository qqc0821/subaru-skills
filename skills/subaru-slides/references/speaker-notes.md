# Speaker Notes

## Method
- One note per slide, in slide order. Write what the presenter actually says out loud, conversationally.
- Because the script carries the narrative, keep slides visual-first: figures, quotes, full-bleed images,
  diagrams, one-line headlines - not paragraphs.
- Put citations and sources for external facts in the slide's notes; keep on-slide only what the audience
  must see (for example a required disclaimer).
- Do not put commentary about creating or checking the deck into the slides or notes.

## Where notes live
- Native builder: `slide.speakerNotes.textFrame.setText(...)`.
- HTML deck: a `data-speaker-notes` attribute on the slide section (or the runtime's notes contract).
- Image-only PPTX (Path B): notes are still possible as native notes; add them when assembling if the
  helper supports it, otherwise document the script alongside the deck.

## Animation
- Prefer declarative animations that export to native PowerPoint builds (for example a `data-anim` convention).
- Animate only when the order of reveal carries meaning (building a list, landing a number).
- One or two animated slides in a ten-slide deck is usually right; when in doubt, add none.
- Judge exported animations in desktop PowerPoint, not Keynote (its importer substitutes effects).
