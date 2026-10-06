# subaru-skills

Chinese-first [Agent Skills](https://agentskills.io/) for presentations and idea exploration. Start with your own material or question and produce something you can inspect and develop further.

[中文](README.md) · [Three worked examples](examples/README.en.md) · [Installation and updates](docs/installation.en.md) · [Provenance and licensing](PROVENANCE.md)

![Actual cover of the original management presentation proposing a small knowledge-library pilot](examples/management-report/preview.webp)

An original six-slide example with native chart, table and diagram. Business data is explicitly fictional. [Download PPTX](examples/management-report/deck.pptx) · [Input and verification limits](examples/management-report/README.md).

## Complete one small task first

Start with brainstorm, which needs no third-party runtime:

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm
~~~

> Use $subaru-brainstorm to explore new uses for a team knowledge library. Give eight different mechanisms; do not rank them yet.

Reload the skill or start a new session as required by your host. If `$skill-name` syntax is unavailable, request the named skill in plain language. Without the CLI, place `skills/<name>/` in a directory supported by your host.

Third-party redistribution permission for `subaru-slides` remains unresolved; read [PROVENANCE.md](PROVENANCE.md) first. After checking the applicable license, install it separately:

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

> Use $subaru-slides to turn this material into six Chinese executive slides. Full Auto, prefer editable PPTX and retain sources and notes. Explain alternatives when tools are missing.

## Choose a skill for the job

| Your job | Skill | Entry |
|---|---|---|
| Turn topics or documents into reports, lessons or technical presentations | `subaru-slides` | [Guide](skills/subaru-slides/README.en.md) · [Worked case](examples/rag-sharing/README.md) |
| Explore options, move beyond repetitive ideas, develop proposals or resume discussions | `subaru-brainstorm` | [Guide](skills/subaru-brainstorm/README.en.md) · [Saved result](examples/knowledge-library/result.md) |

Prefer native objects for text, tables, charts and diagrams that must be edited. Missing native construction triggers an explained fallback; image-only PPTX does not restore native text. Image generation is optional. Each package's `SKILL.md` owns runtime behavior.

## Inspect inputs and results

| Example | Actual output | Evidence limit |
|---|---|---|
| [Management report: a knowledge-library pilot](examples/management-report/README.md) | Six-slide PPTX, chart, table, diagram and notes | Original fictional scenario; no customer or business outcome evidence |
| [Technical sharing: RAG and sources](examples/rag-sharing/README.md) | Six-slide PPTX, two flows, evaluation checklist and notes | Original teaching material; no RAG service or benchmark run |
| [Idea exploration: knowledge-library uses](examples/knowledge-library/README.md) | Eight mechanisms, a branch, experiment card and resume summary | One assistant-authored result; no multi-turn user interview or executed experiment |

The decks were authored directly in this Codex session using local skill guidance, built with python-pptx and rendered slide by slide with LibreOffice. Fonts are not embedded. PowerPoint, Keynote, Google Slides and recipient fonts were not tested. These cases do not establish automatic loading or execution in every host; end-to-end CLI installation/update remains unverified.

## Versions and licenses

Packages are unpublished development content. Read `metadata.version` in each `SKILL.md`. Default installation tracks `main`, not a stable release. Fixed installations must use an actual tag in [Releases](https://github.com/qqc0821/subaru-skills/releases). [Full update/version instructions](docs/installation.en.md).

The root [MIT LICENSE](LICENSE) covers original content only. Brainstorm and the new examples are original; third-party slides documents and sample images have separate boundaries in [PROVENANCE.md](PROVENANCE.md).

## Documentation and contributions

The [static documentation source](site/README.md) includes matching Chinese/English question guides, downloads and release status. Local construction and manual GitHub Pages deployment are prepared; this does not establish that the website is online.

For feedback, provide the host, command, input and specific failure: [open an issue](https://github.com/qqc0821/subaru-skills/issues). Engineering guidance: [AGENTS.md](AGENTS.md). Publishing/discovery maintenance: [operations guide](docs/discovery.md).

~~~bash
make check       # repository gate, including site links and metadata
make test        # tools and builder tests
make doctor      # local capability probe
make site        # build to output/site/ with no third-party dependency
~~~

See [CHANGELOG.md](CHANGELOG.md) for history.
