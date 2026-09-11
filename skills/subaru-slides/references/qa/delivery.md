# Delivery

## Before you hand off
- [ ] The final file opens (render succeeded) and has the expected slide count.
- [ ] Fonts are resolved (or a documented fallback is stated).
- [ ] Speaker notes are attached where they exist.
- [ ] Every automated check you ran is recorded; every check you could **not** run is stated.

## Receipt
Produce a short receipt (JSON or markdown) with:
- file path and byte size / sha256 (if available)
- slide count
- font family/families used
- native chart/table counts
- QA results, and a **claim boundary**: what was verified vs not
  (e.g. "structural + layout checks only; not opened in Microsoft PowerPoint; not checked in Google Slides")

## Do not overclaim
- A successful export does not prove the app opens it correctly.
- A chart working in PowerPoint does not prove it works in Google Slides.
- Do not claim a template was followed unless you compared against the source.

## Delivery message
Give the user the path, one line on what was produced, and any caveats. Do not narrate the process,
do not paste validation jargon, and do not list every command you ran.
