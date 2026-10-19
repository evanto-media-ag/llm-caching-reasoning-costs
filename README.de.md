# LLM Prompt Caching, Reasoning Effort und Kostenabrechnung — gemessen

Reproduzierbare Messungen zur evanto-Artikelserie darüber, was ein LLM-Aufruf wirklich kostet:
Prompt Caching, Thinking-Level (Reasoning Effort) und Kostenabrechnung bei OpenAI, Anthropic,
xAI, Google Gemini, Mistral und den Routern Cortecs, EU Router, Requesty und OpenRouter.

Jede Behauptung der Artikel entspricht einer Zeile in `claims.csv`, und jede Zeile verweist auf
die rohe API-Antwort in `data/`, die sie belegt.

## Messung wiederholen

Voraussetzung: Python 3.12, keine Pakete. Eigene API-Schlüssel in `~/.llm-keys/<anbieter>`
ablegen (eine Datei je Anbieter, `chmod 600`).

```bash
python3 -m unittest
python3 run.py smoke
python3 run.py m1 --date 2026-10-20
```

## Lizenzen

Code: MIT (`LICENSE`). Daten in `data/`, `prices/`, `tables/`: CC BY 4.0 (`LICENSE-DATA`).
