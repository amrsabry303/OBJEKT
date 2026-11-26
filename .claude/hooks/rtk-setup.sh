#!/usr/bin/env bash
# SessionStart: make sure RTK (https://github.com/rtk-ai/rtk) is installed and on PATH.
# Never blocks the session: any failure just means commands run without RTK.
cat >/dev/null  # drain hook input

BIN_DIR="$HOME/.local/bin"
if ! command -v rtk >/dev/null 2>&1 && [ ! -x "$BIN_DIR/rtk" ]; then
  curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh \
    | RTK_INSTALL_DIR="$BIN_DIR" sh >/dev/null 2>&1 || true
fi

# Expose ~/.local/bin to the Bash tool so rewritten `rtk ...` commands resolve.
if [ -n "${CLAUDE_ENV_FILE:-}" ] && [ -x "$BIN_DIR/rtk" ]; then
  echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$CLAUDE_ENV_FILE"
fi
exit 0
