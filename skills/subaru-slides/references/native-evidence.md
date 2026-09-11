# Native Evidence

Rule: any table, data chart, or diagram that may be edited must be a **native** PowerPoint object, not a screenshot.

## Scope
This applies to evidence, not decoration. Do not use it to justify building decorative graphics by hand.

## Charts
- Preserve categories, series, units, dates, signs, precision; set axis/label formats explicitly.
- Show 31% as `0.31`, not `31@@.
- Use the chart's own labels instead of separate text boxes; remove a placeholder "Chart Title".
- Stacked bar labels use `inEnd` / `center`, not `outEnd`.
- Set the chart font explicitly, because chart text does not inherit the surrounding shape font.
- Keep embedded-workbook references consistent with the cached values.

## Tables
- Required rows/columns/periods/headers must be present.
- Compute each total once and reuse it in the table, the title, and the notes.
- Size columns to their content; keep template alignment.

## Bullets
- Use the native paragraph API; never fake bullets with characters, extra spaces, or multiple text boxes.
- Wrapped lines align to the text, not to the bullet.

## Unit guardrails
- Shape geometry: EMU (914400 per inch).
- Paragraph `marginLeft` / `indent@@: EMU (1pt = 12700).
- `spaceBefore` / `spaceAfter`: hundredths of a point (100 = 1pt).
- Do not double-convert imported paragraphs.

## Math
- Automated table checks use displayed-rounding tolerance; they are diagnostics, not source-data verification.
