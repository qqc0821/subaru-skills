# Per-Slide QA Checklist

Run this on **every** slide at full size (contact sheets are for deck-level flow only).

## Layout
- [ ] No content outside the slide boundary.
- [ ] No unintended overlap (text over text, text over image edge).
- [ ] Text does not overflow its box; content text did not use unbounded shrink-to-fit.
- [ ] Tables do not overflow; columns fit their content.
- [ ] Footers/page numbers do not collide with content.
- [ ] Decorative rules/connectors are not dangling or misaligned; process connectors are orthogonal unless a diagonal is intentional and labelled.

## Readability
- [ ] Text roles follow the chosen foundation profile; body and diagram nodes meet their hard minimums.
- [ ] Text contrast against its background is sufficient (especially over images).
- [ ] Chinese renders correctly (no missing glyphs / boxes), with East Asian font and language fields present in native PPTX.

## Content
- [ ] No placeholder text ("Chart Title", "lorem", "xxxx", "TODO").
- [ ] Titles are assertions and read as a coherent story in order.
- [ ] Charts/tables carry the intended data and units.

## Consistency
- [ ] Same element sits in the same position across equivalent slides.
- [ ] Same-role diagram nodes use the same size, radius and internal padding; arrows point in the intended direction.
- [ ] Section dividers and repeated labels look identical.
- [ ] Colors and fonts match the chosen style preset and the foundation's font resolution; each accent color has one clear meaning on the slide.
