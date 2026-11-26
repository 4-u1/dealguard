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
command -v strix >/dev/null || uv tool install strix-agent
# Strix needs a running Docker daemon and its sandbox image
docker info >/dev/null 2>&1 || { (nohup dockerd >/tmp/dockerd.log 2>&1 &); for _ in $(seq 1 20); do docker info >/dev/null 2>&1 && break; sleep 1; done; }
graphify update . >/dev/null && echo "graphify graph rebuilt -> graphify-out/"

if [[ "${1:-}" == "--all" ]]; then
  TOOLS="$(cd .. && pwd)/tools"; mkdir -p "$TOOLS"
  [[ -d "$TOOLS/freellmapi" ]] || git clone --depth 1 https://github.com/tashfeenahmed/freellmapi.git "$TOOLS/freellmapi"
  (cd "$TOOLS/freellmapi" && npm install)
  [[ -d "$TOOLS/OpenMontage" ]] || git clone --depth 1 https://github.com/OpenMontageInc/OpenMontage.git "$TOOLS/OpenMontage"
  (cd "$TOOLS/OpenMontage" && make setup)
  # API keys are NOT stored anywhere: they are environment "Network secrets" injected by the proxy
  # (openrouter.ai, api.elevenlabs.io, 21st.dev). Tools only need a placeholder value.
  sed -i 's/^ELEVENLABS_API_KEY=$/ELEVENLABS_API_KEY=proxy-injected/' "$TOOLS/OpenMontage/.env"
  CFG="$TOOLS/freellmapi.config.json"
  if [[ ! -f "$CFG" ]]; then
    cat > "$CFG" <<EOF
{ "admin": { "email": "admin@localhost.dev", "password": "$(openssl rand -hex 12)" },
  "keys": [ { "platform": "openrouter", "key": "sk-or-v1-proxy-injected", "label": "proxy-injected" } ],
  "models": [
    { "platform": "openrouter", "modelId": "nvidia/nemotron-3.5-lightning:free", "displayName": "Nemotron 3.5 Lightning", "fallbackEnabled": true },
    { "platform": "openrouter", "modelId": "nvidia/nemotron-3.5-super-vl:free", "displayName": "Nemotron 3.5 Super VL", "fallbackEnabled": true },
    { "platform": "openrouter", "modelId": "google/gemma-4-31b-it:free", "displayName": "Gemma 4 31B", "fallbackEnabled": true } ],
  "routing": { "strategy": "balanced" } }
EOF
    chmod 600 "$CFG"
  fi
  echo "start FreeLLMAPI: cd $TOOLS/freellmapi && FREEAPI_CONFIG_PATH=$CFG NODE_USE_ENV_PROXY=1 npm run dev"
fi
echo "tooling ready"
