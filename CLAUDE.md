## TBD

### Additional Notes

- Never `kill`/`pkill` by name substring. Prefer `timeout <N> <cmd>` so processes self-terminate.
  If you must kill: resolve exact PIDs in one tool call, then kill those PIDs in a **separate**
  call. Write long-running PIDs into your task's `.temp/` so cleanup is exact.
- `rm` is auto-permitted only under a `.temp/` directory; other `rm` works but stalls on human
  review — keep deletable things inside `.temp/`.
- **Subagents never run `git commit`/`git add`** or any history-mutating git command. Read-only
  git is fine. The "manager" agent can make commits at task boundaries.