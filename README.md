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

## Licenses

Code: MIT (`LICENSE`). Data in `data/`, `prices/`, `tables/`: CC BY 4.0 (`LICENSE-DATA`).
