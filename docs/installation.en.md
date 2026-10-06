# Installation, updates and versions

[Back to home](../README.en.md)

## Install a skill

Choose one package, then reload it as required by your host. Check slides licensing in [PROVENANCE](../PROVENANCE.md) first.

~~~bash
npx skills add qqc0821/subaru-skills --skill subaru-brainstorm
npx skills add qqc0821/subaru-skills --skill subaru-slides
~~~

Read `metadata.version` in the installed `SKILL.md` for the package version. A `-dev.N` suffix marks unpublished development content, which may change before release; use CLI source records or a Git commit for exact revision tracking.

The default installation fetches the latest content from `main`, including unpublished changes. This differs from the latest stable release.

For [skills CLI](https://github.com/vercel-labs/skills#skills-update) installations, run project updates from the original project directory, or select global scope:

~~~bash
npx skills update subaru-slides subaru-brainstorm -p
npx skills update subaru-slides subaru-brainstorm -g
~~~

Updates use recorded sources and content, rather than selecting a stable Release from `metadata.version`. If an older CLI lacks the command or source records are missing, reinstall with the original `npx skills add` command, choosing the same agent and scope (add `--global` for global installations). Back up customizations first; reload the skill or start a new session as required by your host afterward.

For manually downloaded ZIPs or copied folders, download the desired branch or release again, back up the old folder, and replace the entire installed folder with the corresponding `skills/<name>/` folder to avoid retaining deleted files. Pulling the downloaded repository does not synchronize copied installations, and manual copies are not guaranteed to be tracked by the CLI.

Stable versions: [GitHub Releases](https://github.com/qqc0821/subaru-skills/releases). A read-only remote tag check on 2026-10-07 returned no tags; no stable tag can be installed. This task created no Release. Consult actual Release records for later status; the historical `0.1.0` record does not establish a published stable release.

Once a release exists, choose an actual tag containing the desired skill:

~~~bash
# Template: replace <release-tag> with an existing tag from the Release page
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>"
~~~

A fixed tag installation retains that version and does not automatically switch to newer stable tags. Read the target release notes and reinstall using the new tag URL to upgrade. Reinstall without a tag to return to the default branch.
