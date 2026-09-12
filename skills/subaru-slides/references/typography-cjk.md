# Chinese Typography

## Font stacks
- Heading: PingFang SC Bold / Microsoft YaHei Bold / Source Han Sans Bold / Noto Sans SC Bold;
  serif option: Source Han Serif SC / Songti SC.
- Body: PingFang SC / Microsoft YaHei / Source Han Sans / Noto Sans SC.
- Max 2 families; heading >= 36pt, body >= 18pt; title:body about 3:1.

## Cross-machine fidelity
Two acceptable strategies:
1. **Subset-embed** the fonts by the characters actually used (smallest, most reliable).
2. **System fallback stack** documented to the user, accepting fallback differences.
Never rely on a font that exists only on the author's machine without saying so.

## Measurement
- CJK glyphs are about 1.0 em wide; Latin about 0.5 em. For mixed text, estimate per character
  (about 0.55 em for mostly-Latin runs, 1.0 em for mostly-CJK runs) and size every text box from
  the wrapped line count rather than from a fixed height.
- Line height about 1.25 for CJK.

## AI image + Chinese (Path B / B')
- Keep titles <= 8 characters and body lines <= 30 characters.
- Avoid rare characters; keep text away from busy visual areas.
- Verify every rendered slide; regenerate with shorter text if wrong.

## Path A / B' native text
- Text must be native so it can be edited and searched.
- When authoring OOXML directly, set the East Asian font (`a:ea`) in addition to the Latin font.
