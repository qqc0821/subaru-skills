# Layout and Diagram Grammar

Read this when a slide contains a process, hierarchy, relationship diagram or repeated modules.
The foundation file defines the base unit, margins and tolerances.

## Roles before shapes

State each repeated object's role before building it: for example `node`, `connector`, `label`,
`warning` or `decision`. Equal roles use equal width, height, corner radius, padding and text role.
Use the same role metadata in native shape names when the builder supports it:

```text
role=node;group=journey;index=01
role=connector;group=journey
```

This metadata lets the PPTX validator compare only objects that are meant to match. It is optional
when the host cannot name shapes; in that case, the same checks remain manual QA items.

## Connections

- Default to horizontal, vertical or orthogonal elbow connectors.
- A diagonal connector requires an explicit spatial meaning and `allowDiagonal=true` in its metadata.
- Anchor a connector to shape edges. Do not leave unexplained gaps, floating arrows or lines through text.
- Use the builder's endpoint-arrow feature. Do not imitate an arrow with an unrotated triangle.
- A visual gap may represent a real break only when it has a visible label explaining the break.

## Emphasis and color

- Give each accent color one semantic role on a slide. Do not use a highlight color as decoration,
  status and warning at once.
- Any enlarged or filled emphasis object needs a visible reason such as “关键断点” or “当前决策”.
- Color never carries the only distinction; pair it with text, line style, icon or shape treatment.

## Composition review

- Align repeated modules to one axis and use the foundation base unit for gaps.
- Prefer one compositional system over a wall of unrelated cards.
- Check the full-size page for anchors and the montage for rhythm; neither replaces the other.
