# subaru-skills

A Chinese-first [Agent Skills](https://agentskills.io/) repository that currently provides presentation-building capability.

[中文](README.md) · [Changelog](CHANGELOG.md) · [Provenance and licensing](PROVENANCE.md)

## Skills in this repository

| Skill | Capability | Docs |
|---|---|---|
| `subaru-slides` | From a topic, source material, or existing document to an editable PPTX / HTML deck: content structuring, style selection, construction, and delivery QA | [Guide](skills/subaru-slides/README.en.md) · [SKILL.md](skills/subaru-slides/SKILL.md) |

Install with the [skills CLI](https://github.com/vercel-labs/skills):

~~~bash
npx skills add qqc0821/subaru-skills                          # into the current project
npx skills add qqc0821/subaru-skills --global                 # into the user-level skill directory
npx skills add qqc0821/subaru-skills --skill subaru-slides    # only subaru-slides
~~~

Then hand the task to your host Agent, for example: `Use $subaru-slides to turn this market analysis into a 10-slide executive presentation.`

Without the CLI, copy `skills/<name>/` into your Agent's skill directory.

## Repository layout

- `skills/<name>/` — independently installable skill packages; install only the ones you need;
- `schemas/`, `tools/`, `tests/`, `evals/`, `docs/` — development and regression harness, not installed with the skill; see [AGENTS.md](AGENTS.md).

## Development and quality gates

~~~bash
make check      # links / consistency / assets / style system / installability (the only mandatory gate)
make test       # tool smoke tests and unit tests
make doctor     # probe the current machine

make validate PPTX=deck.pptx
make render   PPTX=deck.pptx OUT=preview/
make montage  DIR=preview/ OUT=montage.webp
~~~

## License

Original repository content is released under the [MIT License](LICENSE). `skills/subaru-slides` is derived from `huashu-slides`, whose audit baseline had no root LICENSE; read [PROVENANCE.md](PROVENANCE.md) before redistribution.
