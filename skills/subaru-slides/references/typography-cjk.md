# Chinese Typography

Read `../styles/foundation.json` before choosing a type scale. The profile, not a
style preset, controls minimum sizes. Default to `meeting-room`; choose `large-room`
for distant projection and `screen-reading` only when the deck is not presented at distance.

## Type and fit

- Treat 18pt as the hard floor for body and diagram-node text. Data labels may use 16–17pt
  only when the rendered slide remains readable; footnotes/source text are the only 10–12pt roles.
- Do not use automatic shrink-to-fit for content roles. Shorten, split or recompose the copy first.
- Use one CJK sans family for most decks, with at most one deliberate display or serif exception.
  Avoid Thin/Light weights for text below 20pt.
- Chinese glyphs are roughly 1em wide and Latin glyphs about 0.55em. Estimate mixed text by
  wrapped lines, not a fixed text-box height. Keep CJK line height within the foundation range.

## Font resolution and delivery

1. Use the user's template or brand font when it is available and licensed for the requested output.
2. For a portable deck, probe the foundation's portable CJK candidates first.
3. Otherwise choose the target-platform candidate: Windows, macOS or Linux. Never assume PingFang
   exists outside macOS, or Microsoft YaHei outside Windows.
4. Report the resolved family and fallback. For a view-only deck, subset embedding is acceptable;
   for an editable handoff, embed all characters when the font licence permits it.
5. If no CJK candidate is available, stop the native-font claim and disclose the substitution risk.

## Native PPTX requirements

- Text must remain native in Path A/B'.
- Set the East Asian typeface (`a:ea`) and language tag (for example `zh-CN`) in addition to the
  Latin typeface. Set East Asian major/minor theme fonts when the builder supports themes.
- Run `scripts/detect_fonts.py --locale zh-CN` before build when target availability matters.
- Verify the exported PPTX has `a:ea` on CJK text and render every slide. Font presence and a clean
  local render do not prove a recipient has the same font.

## AI image + Chinese

- Keep titles <= 8 characters and body lines <= 30 characters.
- Avoid rare characters; keep text away from busy visual areas.
- Verify every rendered slide; regenerate with shorter text if wrong.
