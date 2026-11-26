#!/usr/bin/env bash
# Restores the agent tooling that lives OUTSIDE the repo (the cloud container is ephemeral).
# Skills in .claude/skills, .claude/commands, DESIGN.md and .mcp.json are committed and need nothing.
# Usage: bash scripts/setup-tooling.sh            (CLIs only)
#        bash scripts/setup-tooling.sh --all      (also FreeLLMAPI + OpenMontage in ../tools)
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.local/bin:$PATH"

command -v graphify-mcp >/dev/null || uv tool install 'graphifyy[mcp]'
command -v playwright-cli >/dev/null || npm install -g @playwright/cli@latest
graphify update . >/dev/null && echo "graphify graph rebuilt -> graphify-out/"

if [[ "${1:-}" == "--all" ]]; then
  TOOLS="$(cd .. && pwd)/tools"; mkdir -p "$TOOLS"
  [[ -d "$TOOLS/freellmapi" ]] || git clone --depth 1 https://github.com/tashfeenahmed/freellmapi.git "$TOOLS/freellmapi"
  (cd "$TOOLS/freellmapi" && npm install)
  [[ -d "$TOOLS/OpenMontage" ]] || git clone --depth 1 https://github.com/OpenMontageInc/OpenMontage.git "$TOOLS/OpenMontage"
  (cd "$TOOLS/OpenMontage" && make setup)
fi
echo "tooling ready"
