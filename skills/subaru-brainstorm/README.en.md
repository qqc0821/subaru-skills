# subaru-brainstorm

A brainstorming skill for reframing questions, developing alternative branches, and resuming a discussion later.

[中文](README.md)

After installation, ask your host Agent:

> Use $subaru-brainstorm to explore 50 possible uses for this product. Defer evaluation.

Or start with an open question:

> Use $subaru-brainstorm to explore how a team can keep a discussion going asynchronously.

Say “continue the third idea,” “combine these two,” “try another way of thinking,” or “turn this into a proposal.”
Referenced ideas retain their identity, and your own contributions remain part of the discussion.

Ask for a continuation summary when pausing. Paste it into your next conversation, or request a saved file
if the host supports file access. Resumption depends on that summary or file; permanent host memory is not assumed.

The core workflow needs conversation only. Search, saved files, diagrams, and other artifacts depend on host capabilities.
Without file tools you can still copy the summary. Ideas and simulated scenarios require real-world validation.

## Versions, updates, and stable releases

Read `metadata.version` in the installed `SKILL.md` for the package version. A `-dev.N` suffix marks unpublished development content, which may change before release; use CLI source records or a Git commit for exact revision tracking.

The default installation fetches the latest content from `main`, including unpublished changes. This differs from the latest stable release.

For [skills CLI](https://github.com/vercel-labs/skills#skills-update) installations, run project updates from the original project directory, or select global scope:

~~~bash
npx skills update subaru-brainstorm -p
npx skills update subaru-brainstorm -g
~~~

Updates use recorded sources and content, rather than selecting a stable Release from `metadata.version`. If an older CLI lacks the command or source records are missing, reinstall with the original `npx skills add` command, choosing the same agent and scope (add `--global` for global installations). Back up customizations first; reload the skill or start a new session as required by your host afterward.

For manually downloaded ZIPs or copied folders, download the desired branch or release again, back up the old folder, and replace the entire installed folder with the corresponding `skills/<name>/` folder to avoid retaining deleted files. Pulling the downloaded repository does not synchronize copied installations, and manual copies are not guaranteed to be tracked by the CLI.

Stable versions: [GitHub Releases](https://github.com/qqc0821/subaru-skills/releases). As of 2026-10-06, the remote has no Release or tag, so no stable version is available for installation. The historical `0.1.0` record does not establish a published stable release.

Once a release exists, choose an actual tag containing the desired skill:

~~~bash
# Template: replace <release-tag> with an existing tag from the Release page
npx skills add "https://github.com/qqc0821/subaru-skills/tree/<release-tag>" --skill subaru-brainstorm
~~~

A fixed tag installation retains that version and does not automatically switch to newer stable tags. Read the target release notes and reinstall using the new tag URL to upgrade. Reinstall without a tag to return to the default branch.
