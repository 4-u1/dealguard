#!/usr/bin/env bash
# Runs Shannon (KeygraphHQ AI pentester) in this cloud container. Only against targets we own.
#   bash scripts/shannon.sh --validate-model     # model + target preflight only, no attack
#   bash scripts/shannon.sh                      # full pentest of the local DealGuard copy (~1-1.5h)
# Why the plumbing: Shannon refuses root, and its Docker worker has no network egress here, so model
# traffic goes through scripts/llm-relay.mjs (proxy injects the OpenRouter key) and the app is served
# on the Docker bridge for the worker to reach.
set -euo pipefail
cd "$(dirname "$0")/.."
REPO="$PWD"; LOG=/tmp/shannon-support; mkdir -p "$LOG"
MODEL="${SHANNON_AI_MODEL:-openrouter:nvidia/nemotron-3.5-lightning:free}"

docker info >/dev/null 2>&1 || { (nohup dockerd >"$LOG/dockerd.log" 2>&1 &); for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && break; sleep 1; done; }
getent group docker >/dev/null || groupadd docker
id shannon >/dev/null 2>&1 || useradd -m -s /bin/bash -G docker shannon
chgrp docker /var/run/docker.sock && chmod 660 /var/run/docker.sock
chmod o+rx "$(dirname "$REPO")" "$REPO"
install -o shannon -m 644 /root/.ccr/ca-bundle.crt /home/shannon/ca-bundle.crt
mkdir -p "$REPO/.shannon" && chown -R shannon "$REPO/.shannon"
grep -q host.docker.internal /etc/hosts || echo "172.17.0.1 host.docker.internal" >> /etc/hosts

pgrep -f llm-relay.mjs >/dev/null || (NODE_USE_ENV_PROXY=1 nohup node "$REPO/scripts/llm-relay.mjs" >"$LOG/relay.log" 2>&1 &)
pgrep -f "app_web.py 8766" >/dev/null || (DEALGUARD_HOST=172.17.0.1 DEALGUARD_ALLOWED_HOSTS=host.docker.internal nohup python "$REPO/app_web.py" 8766 >"$LOG/app.log" 2>&1 &)
sleep 2

cd /tmp
exec runuser -u shannon -- env HOME=/home/shannon PATH="$PATH" \
  HTTPS_PROXY="${HTTPS_PROXY:-}" HTTP_PROXY="${HTTP_PROXY:-}" https_proxy="${https_proxy:-}" \
  NO_PROXY="${NO_PROXY:-},host.docker.internal,172.17.0.1" no_proxy="${no_proxy:-},host.docker.internal,172.17.0.1" \
  NODE_EXTRA_CA_CERTS=/home/shannon/ca-bundle.crt SSL_CERT_FILE=/home/shannon/ca-bundle.crt NODE_USE_ENV_PROXY=1 \
  SHANNON_AI_MODEL="$MODEL" SHANNON_AI_API_KEY=proxy-injected SHANNON_AI_BASE_URL=http://host.docker.internal:8788/api/v1 \
  bash -c 'cd /home/shannon && npx -y @keygraph/shannon@latest start -u http://host.docker.internal:8766 -r "$0" "$@"' "$REPO" "$@"
