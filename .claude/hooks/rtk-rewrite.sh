#!/usr/bin/env bash
# PreToolUse(Bash): let RTK compress command output (`rtk hook claude`).
# If RTK is not installed, do nothing and the command runs unchanged.
if command -v rtk >/dev/null 2>&1; then
  exec rtk hook claude
elif [ -x "$HOME/.local/bin/rtk" ]; then
  exec "$HOME/.local/bin/rtk" hook claude
fi
cat >/dev/null
exit 0
