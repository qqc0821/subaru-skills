# subaru-skills

A Chinese-first [Agent Skills](https://agentskills.io/) repository for presentation building and brainstorming.

[中文](README.md) · [Changelog](CHANGELOG.md) · [Provenance and licensing](PROVENANCE.md)

## Skills in this repository

| Skill | Capability | Docs |
|---|---|---|
| `subaru-slides` | From a topic, source material, or existing document to an editable PPTX / HTML deck: content structuring, style selection, construction, and delivery QA | [Guide](skills/subaru-slides/README.en.md) · [SKILL.md](skills/subaru-slides/SKILL.md) |
| `subaru-brainstorm` | Reframe questions, switch thinking methods, retain branches, resume from summaries, and develop proposals or experiments | [Guide](skills/subaru-brainstorm/README.en.md) · [SKILL.md](skills/subaru-brainstorm/SKILL.md) |

Install with the [skills CLI](https://github.com/vercel-labs/skills):

~~~bash
npx skills add qqc0821/subaru-skills                          # into the current project
npx skills add qqc0821/subaru-skills --global                 # into the user-level skill directory
npx skills add qqc0821/subaru-skills --skill subaru-slides    # only subaru-slides
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm # only subaru-brainstorm
~~~

Then hand the task to your host Agent, for example: `Use $subaru-slides to turn this market analysis into a 10-slide executive presentation.`

Without the CLI, copy `skills/<name>/` into your Agent's skill directory.

## Versions, updates, and stable releases

Read `metadata.version` in the installed `SKILL.md` for the package version. A `-dev.N` suffix marks unpublished development content, which may change before release; use CLI source records or a Git commit for exact revision tracking.

The default installation fetches the latest content from `main`, including unpublished changes. This differs from the latest stable release.

For [skills CLI](https://github.com/vercel-labs/skills#skills-update) installations, run project updates from the original project directory, or select global scope:

~~~bash
npx skills update subaru-slides subaru-brainstorm -p
npx skills update subaru-slides subaru-brainstorm -g
~~~

Updates use recorded sources and content, rather than selecting a stable Release from `metadata.version`. If an older CLI lacks the command or source records are missing, reinstall with the original `npx skills add` command, choosing the same agent and scope (add `--global` for global installations). Back up customizations first; reload the skill or start a new session as required by your host afterward.

For manually downloaded ZIPs or copied folders, download the desired branch or release again, back up the old folder, and replace the entire installed folder with the corresponding `skills/<name>/` folder to avoid retaining deleted files. Pulling the downloaded repository does not synchronize copied installations, and manual copies are not guaranteed to be tracked by the CLI.

Stable versions: [GitHub Releases](https://github.com/qqc0821/subaru-skills/releases). As of 2026-10-06, the remote has no Release or tag, so no stable version is available for installation. The historical `0.1.0` record does not establish a published stable release.

Once a release exists, choose an actual tag containing the desired skill:

~~~bash
# Template: replace <release-tag> with an existing tag from the Release page
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>"
~~~

A fixed tag installation retains that version and does not automatically switch to newer stable tags. Read the target release notes and reinstall using the new tag URL to upgrade. Reinstall without a tag to return to the default branch.

## Repository layout

- `skills/<name>/` — independently installable skill packages; install only the ones you need;
- `schemas/`, `tools/`, `tests/`, `evals/`, `docs/` — development and regression harness, not installed with the skill; see [AGENTS.md](AGENTS.md).

## Development and quality gates

~~~bash
make check      # links / consistency / assets / style system / installability (the only mandatory gate)
make test       # tool smoke tests and unit tests
make doctor     # probe the current machine
make eval-brainstorm # conversation evidence and semantic review gate; missing real runs cannot pass

make validate PPTX=deck.pptx
make render   PPTX=deck.pptx OUT=preview/
make pixel-qa DIR=preview/            # pixel-level render QA: wrapped digits, oversized glyphs, band cuts
make montage  DIR=preview/ OUT=montage.webp
~~~

## License

Original repository content is released under the [MIT License](LICENSE). `skills/subaru-slides` is derived from `huashu-slides`, whose audit baseline had no root LICENSE; read [PROVENANCE.md](PROVENANCE.md) before redistribution.
