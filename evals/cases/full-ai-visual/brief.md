# Eval: 全 AI 视觉页（Path B）

**id:** `full-ai-visual`
**执行路径:** `B`

## Brief

使用五张固定的完整 AI 视觉样例，验证 Path B 的图片型 PPTX 装配、结构和逐页渲染。固定输入用于保证回归可复现；图片模型本身的生成质量不属于本案例的自动判定范围。

## 最小复现

```bash
uv run skills/subaru-slides/scripts/create_slides.py \
  skills/subaru-slides/assets/style-samples/slide04-01-苏联构成主义-constructivism.webp \
  skills/subaru-slides/assets/style-samples/slide04-02-浮世绘-ukiyo-e.webp \
  skills/subaru-slides/assets/style-samples/slide04-03-包豪斯-bauhaus.webp \
  skills/subaru-slides/assets/style-samples/slide04-06-工程蓝图-blueprint.webp \
  skills/subaru-slides/assets/style-samples/slide04-10-敦煌壁画-dunhuang.webp \
  --layout fullscreen \
  --output evals/artifacts/full-ai-visual.pptx
```

## 交付

把生成的 deck 另存为 `evals/artifacts/full-ai-visual.pptx`，然后运行 `make eval`。

## Claim boundary

- 自动验证固定 AI 视觉页的装配、PPTX 结构与可渲染性。
- 人工逐页检查裁剪、变形和主要文字可读性。
- 不验证本轮图片生成模型的提示词遵循、文字准确率或跨批次风格一致性。
