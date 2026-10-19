# LLM prompt caching, reasoning effort and cost reporting — measured

Reproducible measurements behind the evanto article series on what an LLM call really costs:
prompt caching, reasoning effort ("thinking level") and cost reporting across OpenAI, Anthropic,
xAI, Google Gemini, Mistral and the routers Cortecs, EU Router, Requesty and OpenRouter.

Every claim in the articles maps to a row in `claims.csv`, and every row points to the raw
API response in `data/` that backs it.

## Re-run a measurement

Requirements: Python 3.12, no packages. Put your own API keys into `~/.llm-keys/<provider>`
(one file per provider, `chmod 600`).

```bash
python3 -m unittest
python3 run.py smoke
python3 run.py m1 --date 2026-10-20
```

## What's in here

| Path | Content |
|---|---|
| `lab/` | Python package (standard library only): request builders per API style, usage normalisation, cost formula, measurement runners M1–M9, report tables |
| `targets.json` | Providers, routers and models measured (key file names only, no keys) |
| `prompts/` | Large (generated) and small prompt |
| `data/<date>/` | One JSON per API call: request body, status, response body, kept response headers — no request headers, no keys |
| `prices/<date>/` | Price listings via API, pricing-page quotes, public price-source subsets |
| `tables/<date>/` | Generated tables (`python3 run.py report --date <date>`) |
| `claims.csv` | 85 claims with status and evidence path |
| `snippets/` | .NET code excerpts quoted in the articles |
| `diagrams/` | Diagrams (HTML + PNG) |

## Measurements

| ID | What |
|---|---|
| M1 | Cache write then read (identical call A, then B) |
| M2 | Cache after 5.5 min (and 61 min for Anthropic 1 h TTL) |
| M3 | Does changing only the effort break the cache? |
| M4 | Just below vs. just above the documented minimum size |
| M5 | Which effort values are accepted, rejected or remapped |
| M6 | Reported reasoning tokens vs. visible output |
| M7 | Computed cost vs. cost reported by the provider |
| M8 | Cache stability through routers (5 calls, with/without cache_control) |
| M9 | List prices via API vs. pricing pages vs. catalogues |

Measurement date: 2026-10-19 (OpenRouter to follow with its own date).

## Licenses

Code: MIT (`LICENSE`). Data in `data/`, `prices/`, `tables/`: CC BY 4.0 (`LICENSE-DATA`).
