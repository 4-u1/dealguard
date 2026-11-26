# Graph Report - dealguard  (2026-11-26)

## Corpus Check
- 16 files · ~12,273 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 187 nodes · 274 edges · 11 communities (9 shown, 2 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `580be97a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DESIGN.md
- verify
- explain
- app_web.py
- TestDealGuard
- DealGuard
- DealGuard - Presentation Handoff
- services
- magic
- DealGuard — agent notes
- setup-tooling.sh

## God Nodes (most connected - your core abstractions)
1. `TestDealGuard` - 18 edges
2. `verify()` - 17 edges
3. `explain()` - 15 edges
4. `v()` - 15 edges
5. `DealGuard - Presentation Handoff` - 14 edges
6. `DealGuard` - 13 edges
7. `TfidfRetriever` - 9 edges
8. `services` - 9 edges
9. `TestLLMLayer` - 8 edges
10. `Handler` - 8 edges

## Surprising Connections (you probably didn't know these)
- `TestDealGuard` --uses--> `TfidfRetriever`  [INFERRED]
  test_dealguard.py → retriever.py
- `run()` --calls--> `verify()`  [EXTRACTED]
  app.py → verifier.py
- `build_response()` --calls--> `verify()`  [EXTRACTED]
  app_web.py → verifier.py
- `v()` --calls--> `verify()`  [EXTRACTED]
  test_dealguard.py → verifier.py
- `save20_fashion()` --calls--> `verify()`  [EXTRACTED]
  test_llm.py → verifier.py

## Import Cycles
- None detected.

## Communities (11 total, 2 thin omitted)

### Community 0 - "DESIGN.md"
Cohesion: 0.05
Nodes (36): Border Radius Scale, Brand & Accent, Breakpoints, Buttons, Cards & Containers, Collapsing Strategy, Colors, Components (+28 more)

### Community 1 - "verify"
Cohesion: 0.13
Nodes (7): run(), TfidfRetriever, tokenize(), _invalid(), parse_claim(), Result, verify()

### Community 2 - "explain"
Cohesion: 0.13
Nodes (7): build_facts(), _call_gemini(), explain(), grounding_problems(), _numbers(), save20_fashion(), TestLLMLayer

### Community 3 - "app_web.py"
Cohesion: 0.18
Nodes (4): build_response(), Handler, host_allowed(), TestWebConfig

### Community 5 - "DealGuard"
Cohesion: 0.13
Nodes (13): Architecture, Attribution, DealGuard, Demo, Example scenario, Files, Known limitations, Live Deployment (Render free plan) (+5 more)

### Community 6 - "DealGuard - Presentation Handoff"
Cohesion: 0.14
Nodes (14): 10. Limitations (be honest on stage), 11. Future improvements, 12. Suggested five slides (content only), 13. Arabic speaker notes, 1. Elevator pitch, 2. Problem, 3. What makes it distinctive, 4. Technologies (actual roles) (+6 more)

### Community 7 - "services"
Cohesion: 0.15
Nodes (12): key, sync, value, services, buildCommand, envVars, healthCheckPath, name (+4 more)

### Community 8 - "magic"
Cohesion: 0.25
Nodes (8): TWENTY_FIRST_API_KEY, graphify-mcp, npx, graphify, magic, playwright, @21st-dev/magic, @playwright/mcp

### Community 9 - "DealGuard — agent notes"
Cohesion: 0.33
Nodes (5): Before any UI work, Codebase questions, DealGuard — agent notes, Tests, Tooling outside the repo (ephemeral container)

## Knowledge Gaps
- **5 isolated node(s):** `@playwright/mcp`, `graphify-mcp`, `@21st-dev/magic`, `TWENTY_FIRST_API_KEY`, `PATH`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 96 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `verify()` connect `verify` to `explain`, `app_web.py`, `TestDealGuard`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **What connects `@playwright/mcp`, `graphify-mcp`, `@21st-dev/magic` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `DESIGN.md` be split into smaller, more focused modules?**
  _Cohesion score 0.05405405405405406 - nodes in this community are weakly interconnected._
- **Why does `v()` connect `TestDealGuard` to `verify`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Should `verify` be split into smaller, more focused modules?**
  _Cohesion score 0.1330049261083744 - nodes in this community are weakly interconnected._
- **Why does `explain()` connect `explain` to `verify`, `app_web.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `explain` be split into smaller, more focused modules?**
  _Cohesion score 0.12807881773399016 - nodes in this community are weakly interconnected._