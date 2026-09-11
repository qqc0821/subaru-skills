# Illustrations and AI Images

## Which slides get illustrations (Path A / B')
1. Cover - always.
2. Key insight slides - the "aha" moments.
3. Closing - optional but impactful.
4. Data-heavy slides - charts/diagrams instead of AI art.

## The golden rule: describe mood, do not micro-manage
Short prompts > long prompts. Constraints kill diversity. Do **not** specify color ratios, layout
positions, character poses, or negative constraints such as "NOT Snoopy".

| Don't | Do |
|---|---|
| Specify color ratios (60/25/15) | Describe the mood ("warm like a Sunday comic page") |
| Dictate layout ("title centered, image right") | Reference a specific aesthetic ("Peanuts comic strip") |
| Add negative constraints ("NOT Snoopy") | Let the model interpret the style |
| List every visual element | Describe what the viewer should feel |

## Base style prompt (once per deck, <=5 lines)
Read the chosen preset `../styles/<id>.md` - its `Base Style Prompt` block is canonical.
Append it to every per-slide prompt; do not repeat style details in each slide.

## Per-slide prompt structure
```
Create a [style] slide about [topic].

[Base Style]

DESIGN INTENT: [1 sentence - what the viewer should FEEL]

TEXT TO RENDER:
- Title: "[exact text]"
- Body: "[exact text]"

[Optional: 1-2 sentences of scene/mood. Let the model decide composition.]
```

## Technical rules
- Always specify resolution: `2048x1152` (16:9) for crisp text.
- Always include "no text in image" for Path B' base images (text is overlaid natively).
- For Path B, include all text verbatim and keep Chinese titles <=8 characters.
- Generate in parallel batches of 3-5 when the host supports it.
- Verify text accuracy after generation; regenerate with simplified text if wrong.

## Custom character style
Treat "Doraemon style" or "Studio Ghibli" as a **style reference**, not a request to draw copyrighted characters.
Extract the visual DNA and write it as a custom preset under `../styles/custom-<slug>.md`:
shape language, line quality, palette, character proportions, background treatment, emotional tone.
