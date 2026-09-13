# Presentation Prompt Templates

Stable, platform-agnostic prompts for outlining a presentation and generating slide
visuals. Load this file on demand; style details belong in `../styles/<id>.md`, and
image-generation principles belong in `illustrations.md`.

## 1. Content generation

### Full presentation outline

```text
Create a [X]-slide presentation about [topic].

Audience: [who will watch]
Duration: [minutes]
Goal: [inform / persuade / educate]
Tone: [professional / conversational / academic]

Structure:
- Opening: [problem, story or data point]
- Body: [logical, chronological or priority order]
- Close: [action, summary or discussion]

For each slide provide:
- Title as a conclusion sentence, not a topic label
- No more than four supporting points
- One suggested visual type (chart, diagram, photo or illustration)

Brand constraints, if any:
- Colors: [primary / secondary / accent]
- Fonts: [heading / body]
- Logo or footer rule: [placement]
```

### Business report

```text
Create a [X]-slide report for [audience] about [industry or decision].
Use the sequence: context → problem → evidence → options → recommendation → next steps.
Make every title a decision-relevant conclusion. Keep each slide to one idea and four
supporting points or fewer. Mark where a native chart, table or diagram is needed.
```

### Educational / training

```text
Design a lesson about [concept] for [learner level].
Introduce one concept at a time, give one concrete analogy, then one real-world example
and one short takeaway. Use plain language, one key insight per slide and visuals that
make the relationship or process easier to understand.
```

### Research to presentation

```text
Analyze the supplied research and select the three or four findings that change a
decision. Build a narrative: question → evidence → implication → action. Preserve
units, dates, uncertainty and source traceability. Suggest a native chart or diagram
wherever a visual comparison is more precise than prose.
```

### Problem → solution → result

```text
Generate a slide outline using Problem → Solution → Result.
For each section, state the claim, the minimum evidence needed and the visual that makes
the claim obvious. Remove repeated context and keep the close focused on one action.
```

### Long document to slides

```text
Turn the supplied document into a [X]-slide presentation.
Extract only claims that support the audience's decision. Give each slide a concise
assertion title, up to four points, and a suggested visual. Preserve important numbers,
qualifiers and source references; omit filler and repeated background.
```

## 2. Slide image prompts (Path B / B')

The selected style preset is the canonical source for palette, typography and base
style. Do not copy a second palette into this template.

### Per-slide template

```text
Create a [style] presentation slide about [topic].

[Paste the Base Style Prompt from ../styles/<id>.md]

DESIGN INTENT: [One sentence describing what the viewer should feel or understand.]

TEXT TO RENDER:
- Title: "[exact text]"
- [Optional label or body]: "[exact text]"

VISUAL NARRATIVE: [One or two sentences describing the subject, action, atmosphere
and meaning. Let the model decide composition; do not prescribe coordinates or a grid.]
```

For Path B', add `no text in image` because text is overlaid as native objects. For
Path B, include all visible text verbatim and verify it after generation.

### Cover prompt

```text
Create a [style] cover slide for [topic].

[Base Style Prompt]

DESIGN INTENT: The opening should feel [curious / confident / urgent / welcoming].

TEXT TO RENDER:
- Title: "[short assertion]"
- Subtitle: "[one-line context]"

VISUAL NARRATIVE: A scene or metaphor that makes the topic immediately recognizable
and leaves room for the title to remain legible.
```

### Insight prompt

```text
Create a [style] slide that makes this insight memorable:
"[one-sentence insight]"

[Base Style Prompt]

DESIGN INTENT: The viewer should leave understanding [specific implication].

TEXT TO RENDER:
- Title: "[assertion]"
- Key evidence: "[number, quote or short label]"

VISUAL NARRATIVE: Use one clear metaphor, relationship or contrast. Keep decorative
detail subordinate to the evidence.
```

## 3. Text and verification rules

For Chinese text rendered inside an AI image:

1. Keep titles to eight characters or fewer when possible.
2. Keep body lines to roughly 30 characters or fewer.
3. Prefer common characters and short labels.
4. Split dense copy into multiple labels instead of shrinking it.
5. Check every generated image for spelling, missing characters and contrast.
6. If text is wrong, simplify the wording or move the text to native PowerPoint objects.

Before generating, verify:

- [ ] The slide has one claim and a clear audience outcome.
- [ ] The visual narrative explains meaning, not coordinates.
- [ ] The chosen preset supplies the base style; no competing palette is introduced.
- [ ] Path B' explicitly keeps text out of the base image.
- [ ] Text is short enough to verify and render reliably.
- [ ] A chart, table or diagram is native when it carries editable evidence.
- [ ] The final image will be inspected before delivery.
