# Eval: 内置 fallback 图片型 PPTX

**id:** `fallback-image-pptx`
**执行路径:** `fallback`

## Brief

使用 `subaru-slides` 内置的 `scripts/create_slides.py`，把三个仓库内置 WebP 样例装配为三页 16:9 图片型 PPTX。该案例只验证最低兜底链路，不声明文字可编辑、内容质量或 AI 图片生成质量。

## 最小复现

```bash
uv run skills/subaru-slides/scripts/create_slides.py \
  skills/subaru-slides/assets/style-samples/slide04-01-苏联构成主义-constructivism.webp \
  skills/subaru-slides/assets/style-samples/slide04-03-包豪斯-bauhaus.webp \
  skills/subaru-slides/assets/style-samples/slide04-06-工程蓝图-blueprint.webp \
  --layout fullscreen \
  --output evals/artifacts/fallback-image-pptx.pptx
```

## Claim boundary

- 验证图片型 PPTX 的装配、结构与渲染能力。
- 不验证可编辑文字、原生表格/图表、演讲备注或 AI 生成图片质量。
