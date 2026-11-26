# DealGuard — agent notes

## Before any UI work
- Read `DESIGN.md` (Stripe-inspired design system) and follow it.
- Use the skills in `.claude/skills/`: `design-taste-frontend`, `impeccable`, `web-design-guidelines`,
  `image-to-code` / `imagegen-frontend-web`, `21st-ui` (21st.dev is reached through the claude.ai connector, tools `mcp__Make__*`). For a UI review run `/web-interface-guidelines`
  or ask "Review my UI".
- Verify pages in a real browser with `playwright-cli` (skill) or the `playwright` MCP server.

## Codebase questions
- A graphify knowledge graph of the code lives in `graphify-out/` (`GRAPH_REPORT.md`, `graph.json`).
  Query it first: `graphify query "<question>"`, `graphify explain "<symbol>"`, or the `graphify` MCP server.
- After code changes: `graphify update .` (local, no LLM). `.graphifyignore` excludes `.claude/`.

## Tooling outside the repo (ephemeral container)
- Restore CLIs: `bash scripts/setup-tooling.sh` (add `--all` for FreeLLMAPI + OpenMontage in `../tools`).
- FreeLLMAPI (`../tools/freellmapi`, `npm run dev`): one OpenAI-compatible endpoint at
  `http://localhost:3001/v1` over free LLM tiers. Needs provider keys added in its UI.
- OpenMontage (`../tools/OpenMontage`): agentic video production; open it as its own workspace and
  follow its `AGENT_GUIDE.md`. `make preflight` lists which providers are configured.

## API keys
Keys live only as environment Network secrets (proxy-injected): `openrouter.ai`, `api.elevenlabs.io`,
`21st.dev` (unused: the connector replaces it). Never write real keys to files; tools get the placeholder `proxy-injected`.
Node tools need `NODE_USE_ENV_PROXY=1` to reach the network.
- FreeLLMAPI: start with `FREEAPI_CONFIG_PATH=../tools/freellmapi.config.json NODE_USE_ENV_PROXY=1 npm run dev`;
  use an explicit model (e.g. `nemotron-3.5-lightning`), since `auto` may hit stale free-model entries.

## Security testing (Strix)
- Skills: `penetration-testing-with-strix`, `find-security-vulnerabilities-in-code`, `web-app-penetration-testing`,
  `api-security-testing`, `owasp-top-10-testing`, `fix-security-vulnerabilities-with-strix`, and more.
- Only scan targets we own (this repo, local servers). Needs Docker (`dockerd`) + sandbox image
  `ghcr.io/usestrix/strix-sandbox` (pulled on first run).
- Run: `STRIX_LLM="openrouter/<free tool-capable model>" LLM_API_KEY=proxy-injected strix -n -t ./ -m quick`.
  Results land in `strix_runs/` (git-ignored).

## Tests
`python -m pytest -q`
