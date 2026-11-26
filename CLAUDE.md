# DealGuard — agent notes

## Before any UI work
- Read `DESIGN.md` (Stripe-inspired design system) and follow it.
- Use the skills in `.claude/skills/`: `design-taste-frontend`, `impeccable`, `web-design-guidelines`,
  `image-to-code` / `imagegen-frontend-web`, `21st-ui`. For a UI review run `/web-interface-guidelines`
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

## Tests
`python -m pytest -q`
