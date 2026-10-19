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

## Inhalt

| Pfad | Inhalt |
|---|---|
| `lab/` | Python-Paket (nur Standardbibliothek): Request-Bau je API-Stil, Usage-Normalisierung, Kostenformel, Messungen M1–M9, Tabellen |
| `targets.json` | Gemessene Anbieter, Router und Modelle (nur Namen der Schlüsseldateien, keine Schlüssel) |
| `prompts/` | Großer (generierter) und kleiner Prompt |
| `data/<datum>/` | Ein JSON je API-Aufruf: Request-Body, Status, Response-Body, ausgewählte Response-Header – keine Request-Header, keine Schlüssel |
| `prices/<datum>/` | Preislisten per API, Zitate der Preisseiten, Auszüge öffentlicher Preisquellen |
| `tables/<datum>/` | Erzeugte Tabellen (`python3 run.py report --date <datum>`) |
| `claims.csv` | 85 Behauptungen mit Status und Beleg |
| `snippets/` | .NET-Codeauszüge aus den Artikeln |
| `diagrams/` | Diagramme (HTML + PNG) |

## Messungen

| ID | Was |
|---|---|
| M1 | Cache-Write, dann Read (identischer Aufruf A, dann B) |
| M2 | Cache nach 5,5 min (bei Anthropic 1 h TTL auch nach 61 min) |
| M3 | Bricht ein reiner Effort-Wechsel den Cache? |
| M4 | Knapp unter vs. knapp über der dokumentierten Mindestgröße |
| M5 | Welche Effort-Werte angenommen, abgelehnt oder umgesetzt werden |
| M6 | Gemeldete Reasoning-Tokens vs. sichtbare Ausgabe |
| M7 | Berechnete vs. vom Anbieter gemeldete Kosten |
| M8 | Cache-Stabilität über Router (5 Aufrufe, mit/ohne cache_control) |
| M9 | Listenpreise per API vs. Preisseiten vs. Kataloge |

Messdatum: 19.10.2026 (alle Ziele, einschließlich OpenRouter).

## Lizenzen

Code: MIT (`LICENSE`). Daten in `data/`, `prices/`, `tables/`: CC BY 4.0 (`LICENSE-DATA`).
