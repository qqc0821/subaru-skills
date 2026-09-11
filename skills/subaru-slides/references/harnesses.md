# Harness Adapters

The skill is harness-agnostic. These are the only tools that differ; everything else (shell, file read/write/search)
works the same everywhere.

| Need | Claude Code | Codex | DSH | Cursor |
|---|---|---|---|---|
| Ask the user | `AskUserQuestion` | `request_user_input` / chat | `ask_user_question` | `AskQuestion` |
| Show/preview a file | `SendUserFile` | preview surface | attach images / present | open in editor |
| Screenshot | Claude Preview MCP | Codex Browser | `ego-browser` / read_image | cursor-ide-browser |
| Present deliverable | `SendUserFile` | file link | `present` | open file |
| Image generation | host capability | `imagegen` | host capability | host capability |

## Rules
- Detect don't assume: run `scripts/detect_capabilities.py` and branch on the result.
- If a harness lacks an "ask" tool, ask in chat and wait.
- If a harness lacks a preview/render tool, say visual verification was not performed.
- Never hard-code a single harness's path or tool name as required.
