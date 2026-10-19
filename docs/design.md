# Blogserie: Prompt Caching, Thinking-Level und Kostentransparenz bei LLMs — Design

Stand: 2026-10-19 · Autor: svk (Entscheidungen) / Claude (Entwurf) · Status: Entwurf zur Freigabe ·
Anlage: `2026-10-18-blogserie-recherche.md`

## 1. Absicht und Warum

Entwickler und Projektleiter, die AI-Anwendungen planen oder bauen, kennen Tokens und Modellpreise, haben sich
aber nicht mit den drei Stellschrauben beschäftigt, die die Rechnung am stärksten verändern: **Prompt Caching**,
**Thinking-Level (Reasoning Effort)** und die **Wahl des Anbieters bzw. Routers**. Was davon möglich ist,
entscheidet der Modellanbieter oder Hoster, nicht die Plattform des Lesers.

Nach der Lektüre soll der Leser am nächsten Tag

1. **Kosten durchschauen**: wissen, aus welchen Token-Arten sich ein Preis zusammensetzt (Input, Cache-Read,
   Cache-Write, Output, Reasoning), wie man ihn korrekt nachrechnet und woher verlässliche Preisdaten kommen
   (Datenquellen wie models.dev/LiteLLM/OpenRouter, die auch unsere Catalog API speisen).
2. **Einstellmöglichkeiten kennen**: je Anbieter wissen, ob und wie gecacht wird, welche TTL gilt und welche
   Reasoning-Stufen es gibt.
3. **Begründet wählen**: „Wenn mir Feature X wichtig ist, nehme ich Anbieter/Router Y.“

Das Alleinstellungsmerkmal gegenüber den üblichen Vergleichstabellen: **jede Behauptung ist durch eine eigene,
öffentlich nachprüfbare Messung belegt**, und der Vergleich schließt **europäische/souveräne Router** (Cortecs,
EU Router) neben OpenRouter und Requesty ein.

## 2. Ziele, Nicht-Ziele, Anti-Ziele

**Ziele**
- Eine Serie aus Hauptartikel + 4 Vertiefungen, Deutsch und Englisch, auf evanto.de.
- Ein öffentliches GitHub-Repository mit Messskripten, Rohdaten (JSON) und den daraus erzeugten Tabellen.
- Eine Vergleichsmatrix mit Stichtag, in der jede Zelle auf eine Messung oder ausdrücklich auf
  „dokumentiert, nicht gemessen“ verweist.
- Code-Illustrationen aus `Evanto.ChatClients` und CompanyWizard, die zeigen, wie man die Unterschiede in einer
  Abstraktion kapselt — und wo das nicht geht.

**Nicht-Ziele**
- Kein Benchmark der Antwortqualität oder Latenz-Rennen (Latenz nur, wo sie Caching belegt).
- Kein vollständiger Preisvergleich aller Modelle; Preise nur als Beispiele für Mechanismen.
- Kein .NET-Tutorial; .NET ist Illustration, die Messungen sind plattformneutral.
- Batch-APIs, Flex/Priority-Tiers, Bild-/Audio-Preise: höchstens ein Satz mit Verweis.

**Anti-Ziele (wäre ein Misserfolg, auch wenn technisch alles stimmt)**
- Eine Behauptung im Text, die nicht gemessen oder als „nur dokumentiert“ markiert ist.
- Werbeton für CompanyWizard; der Artikel muss als neutraler Fachartikel bestehen.
- Eine Matrix ohne Stichtag, die in drei Monaten stillschweigend falsch ist.
- Ein API-Schlüssel, Kontoname oder interner Hostname im öffentlichen Repository oder in einem Screenshot.
- Unsere eigenen Bugs verschwiegen: die Fehlschläge aus der Praxis (s. 6.3) sind Teil des Werts.

## 3. Rahmenbedingungen

- **Kosten**: Messkosten sind ausdrücklich akzeptiert (svk). Trotzdem kleine Ausgaben (`max_tokens` niedrig),
  Effort-Abtastung mit kurzem Prompt; nur Caching-Läufe brauchen den großen Prompt.
- **Schlüssel**: Dateien unter `~/.llm-keys/<anbieter>` (`gemini`, `xai`, `requesty`, `mistral`, `eurouter`,
  `openrouter`, `cortecs`), `chmod 600`; Cortecs aus eigenem Messschlüssel `~/.llm-keys/cortecs`, **nie** aus
  dem produktiven `~/.cortecs-sovereign-key`; Anthropic und OpenAI aus den
  Umgebungsvariablen `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` (Basis-URL `https://api.anthropic.com`).
  Für M7b/M7c zusätzlich (falls verfügbar): `openai-admin`, `anthropic-admin`, `xai-management`,
  `cortecs-management` unter `~/.llm-keys/`, sowie je ein eigener Messschlüssel `openai-measure` /
  `anthropic-measure` in einem eigenen Projekt bzw. Workspace.
  Schlüssel werden nie ausgegeben, geloggt oder in Rohdaten geschrieben; Rohdaten werden vor dem Commit auf
  Header/Schlüsselreste geprüft (Request-Header werden gar nicht erst archiviert).
- **OpenRouter**: Schlüssel besorgt svk noch; ist ausdrücklich wichtig. Messungen dafür laufen nach, sobald er da ist.
- **DeepSeek-eigene API**: kein Schlüssel ⇒ „dokumentiert, nicht gemessen“, sofern svk keinen nachliefert.
  Open-Source-Modelle (DeepSeek, Qwen, gpt-oss, ggf. GLM/Kimi) werden über die Router gemessen.
- **Zeitbezug**: Alle Aussagen tragen das Messdatum. Modellnamen und Faktoren ändern sich monatlich.
- **Sprache**: Deutsch und Englisch erscheinen gleichzeitig; Messdaten, Tabellen und Code sind identisch.
- **Hausregel**: im Deutschen nicht gendern.

## 4. Entschiedenes

### 4.1 Veröffentlichung (svk)
- **Ort**: evanto.de (Fachartikel, Evanto als Beratungs-/Entwicklungshaus). dev.to/Medium offen, später als
  Zweitveröffentlichung mit `canonical` auf evanto.de.
- **Hinweis**: je Teil ein LinkedIn-Beitrag (insgesamt 5).
- **Serie** statt Einzelartikel; **Deutsch + Englisch**.
- **Belege**: alle Behauptungen werden mit eigenen Messungen geprüft; Rohdaten und Skripte im
  **öffentlichen GitHub** von evanto.

### 4.2 Serie (Vorschlag Claude, von svk als Richtung bestätigt)

| # | Titel (Arbeitstitel DE) | Kern | Messungen |
|---|---|---|---|
| H | Was ein LLM-Aufruf wirklich kostet | Token-Arten als Denkmodell, die drei Hebel, Vergleichsmatrix mit Stichtag, Entscheidungshilfe „Wenn X wichtig, dann Y“ | verweist auf alle |
| 1 | Prompt Caching | Prefix-Caching-Prinzip; explizit vs. automatisch; TTL; Read-/Write-Faktoren; Mindestgröße; was den Cache bricht | M1–M4 |
| 2 | Thinking-Level | Parameter-Zoo und Skalen; `budget_tokens` vs. `effort`; verborgenes, aber bezahltes Reasoning; Effort ↔ Cache | M5–M6, M3 |
| 3 | Kostentransparenz | Formel; Feldnamen-Chaos (inkl. „input enthält Cache-Tokens oder nicht“); **Kosten per API abrufen: pro Aufruf (Router, xAI) vs. nur aggregiert mit Admin-Key (OpenAI, Anthropic) vs. gar nicht (Gemini, Mistral)**; Listenpreise per API vs. nur Webseite; Preisquellen und ihr Zusammenführen (Catalog); Tarifstufen (Langkontext, Off-Peak) | M7, M9 |
| 4 | Router im Vergleich | Cortecs, EU Router, Requesty, OpenRouter: was wird durchgereicht, Sticky Routing, Effort-Übersetzung, was „EU“ jeweils bedeutet; Open-Source-Modelle je Hoster | M8, M5 |

Reihenfolge: Hauptartikel zuerst, dann Teil 1 → 2 → 3 → 4 (svk, s. 9).

### 4.3 Ton und Produktbezug (Claude, Vermutung von svk bestätigt)
CompanyWizard erscheint als „unser Praxisfall“, nicht als Werbung. Catalog API wird dort genannt, wo es um
verlässliche Preisdaten geht. Je Teil höchstens ein kurzer Hinweis am Ende, kein Verkaufsabschnitt.

## 5. Messprogramm

### 5.1 Behauptungsregister (zentrales Artefakt)
Jede Aussage, die im Text vorkommen soll, bekommt eine Zeile in `claims.yaml` (oder `.csv`) im Repository:

`id` · Behauptung (DE/EN) · Quelle (URL + Abrufdatum) · Anbieter/Modell · Messung (`M#`) · Status
(`bestätigt` / `widerlegt` / `abweichend` / `nicht messbar` / `nicht gemessen`) · Beleg (Pfad der Rohdatei) ·
Messdatum.

Regel: Der Text zitiert nur Zeilen mit Status `bestätigt`/`widerlegt`/`abweichend`; `nicht messbar` und
`nicht gemessen` erscheinen nur mit dieser Kennzeichnung. Widersprüche zwischen Doku und Messung sind
**Befunde**, nicht Fehler — sie gehören in den Text.

Startbestand: die Befunde der Recherche vom 2026-10-18 (Abschnitt 8) — jeder davon wird eine Register-Zeile.

### 5.2 Testaufbau
- **Großer Prompt**: fester, deterministischer Systemprompt mit ≈ 5 000 Tokens (über allen Mindestgrößen, auch
  4 096 bei Gemini), im Repository versioniert. Inhalt neutral (z. B. gemeinfreier Text).
- **Kleiner Prompt**: für Effort-Abtastung und für den Unter-Mindestgröße-Test.
- **Cache-Isolation**: jeder Lauf stellt dem Prompt eine eindeutige Lauf-ID voran, damit kein Treffer aus einem
  früheren Lauf das Ergebnis verfälscht (gilt nicht für M4/M8, wo Wiederholung gewollt ist).
- **Archiv**: pro Aufruf eine JSON-Datei mit Zeitstempel, Anbieter, Modell, Endpunkt, Request-Body (ohne Header),
  HTTP-Status, vollständigem Response-Body (bei Streaming: das letzte Usage-Ereignis plus Rekonstruktion),
  gemessener Dauer.

### 5.3 Messungen

| M | Was | Ablauf | Ergebnis |
|---|---|---|---|
| M1 | Cache-Write/Read | großer Prompt, Aufruf A, sofort Aufruf B identisch | gemeldete Read-/Write-Tokens, Kosten A vs. B |
| M2 | TTL | Aufruf B nach > TTL (5 min; bei Anthropic 1 h zusätzlich mit `ttl:"1h"`) | Treffer ja/nein |
| M3 | Cache-Bruch durch Einstellung | B mit anderem Effort/Thinking als A; ebenso geänderte Tools | Treffer ja/nein |
| M4 | Unter Mindestgröße | Prompt knapp unter der dokumentierten Grenze, zweimal | kein Treffer, kein Fehler? |
| M5 | Effort-Skala | jeder Wert `none, minimal, low, medium, high, xhigh, max` einzeln, kleiner Prompt | angenommen / 400 / stillschweigend umgesetzt (an Reasoning-Tokens erkennbar) |
| M6 | Verborgenes Reasoning | Effort `high`, Antwort mit zusammengefasstem/ausgelassenem Thinking | gemeldete Reasoning-Tokens vs. sichtbare Ausgabe |
| M7 | Kostenabgleich | Kosten aus Usage × öffentlichem Listenpreis am Messtag (Formel 6.2) vs. vom Anbieter per API gemeldeten Kosten — in drei Stufen, s. u. | Abweichung in %, je Stufe |
| M9 | Listenpreise per API | Preis-Endpunkte (OpenRouter, Cortecs, Requesty, EU Router, xAI `/v1/language-models`) am Messtag abrufen und gegen die Preisseiten und die Catalog API halten | Abweichungen, fehlende Felder (z. B. 1-h-Write, Reasoning) |
| M8 | Router-Cache-Stabilität | dasselbe Claude-Modell direkt + über Cortecs, EU Router, Requesty, OpenRouter, je 5 Folgeaufrufe mit großem Prompt; je Router zwei Varianten: (a) bestmöglich — explizites `cache_control` inkl. 1 h und Anbieter-Pinning/Sticky-Hinweis, (b) ohne beides | Trefferquote, Upstream-Anbieter je Aufruf (soweit gemeldet) |

**Festlegungen zu M7/M8 (Claude):**
- **M7 in drei Stufen** (Kosten-APIs recherchiert 2026-10-19, Recherche-Anlage D2):
  - **M7a pro Aufruf aus der Antwort**: OpenRouter (`usage.cost`, zusätzlich `GET /api/v1/generation`), EU Router
    (`usage.cost_eur`, zusätzlich `/api/v1/generation?id=<x-request-id>`), xAI (`usage.cost_in_usd_ticks`),
    Requesty (`usage.cost`). Reiner Aufrufvergleich, normaler Schlüssel genügt.
  - **M7b pro Aufruf über eine Verwaltungs-API**: Cortecs liefert keine Kosten in der Antwort, aber je Trace in
    `GET /v1/manage/logs` (EUR je Versuch inkl. Fallbacks). Braucht einen **Management-Key**; dabei wird geprüft,
    ob `request_id` der Completion-`id` entspricht (selbst ein Befund).
  - **M7c aggregiert über Admin-APIs**: OpenAI (Usage 1m-Buckets + Costs täglich) und Anthropic (Usage 1m-Buckets
    ≈ 5 min Verzug + Cost-Report täglich) brauchen **Admin-Keys** und für einen sauberen Abgleich einen
    **eigenen Messschlüssel in einem eigenen Projekt/Workspace**, sonst mischt sich anderer Verkehr ein (der
    heutige `ANTHROPIC_API_KEY` wird u. a. von Claude Code genutzt). Abgleich: eigene Token-Logs gegen die
    1-Minuten-Buckets am Messtag, Kosten gegen den Tagesbericht frühestens am Folgetag. xAI-Management-API
    (Sekundenauflösung) als Gegenprobe zu M7a, falls ein Management-Key vorliegt.
  - **Nicht messbar**: Gemini (nur Cloud Billing je Projekt, Verzug bis > 1 Tag — höchstens als grobe
    Tagesprobe mit eigenem GCP-Projekt) und Mistral (Admin-API nur Enterprise, sonst Dashboard).
  - Für jede Stufe wird zusätzlich gezeigt, dass Usage-Felder + Listenpreis die Formel vollständig füllen — und
    wo nicht (z. B. OpenAI-Usage-API ohne Reasoning-Feld, Cortecs/Requesty-Aggregat ohne Cache-/Reasoning-Split).
- **Fehlen Admin-/Management-Keys** zum Messfenster, fällt die jeweilige Stufe auf `nicht gemessen` zurück; die
  übrigen Messungen laufen unverändert.
- **Referenzpreis** sind die öffentlichen Preisseiten am Messtag, archiviert im Repository (Text-Auszug +
  Abrufdatum; Cortecs in EUR, keine Umrechnung — Abweichungen werden je Währung angegeben). Die Catalog API wird
  in Teil 3 als *zusätzlicher* Abgleich gezeigt (stimmt unser Katalog mit den Preisseiten?), nicht als Referenz,
  damit Leser ohne Zugang nachrechnen können.
- **M8 (a) vs. (b)**: (a) zeigt, was der Router bestenfalls kann; (b) entspricht unserem heutigen Einsatz (6.3)
  und macht sichtbar, ob unsere Einschränkung eine Router-Grenze oder unsere eigene Wahl ist.

**Messfenster (Claude):** Die Matrix ist eine **Momentaufnahme** mit einem gemeinsamen Stichtag: alle Messungen
laufen in einem Fenster von wenigen Tagen vor der ersten Veröffentlichung, damit der Hauptartikel eine
konsistente Matrix hat. Die Skripte sind manuell wiederholbar (ein Befehl je Anbieter); kein CI, keine
Secrets im öffentlichen Repository. Eine spätere Nachmessung erzeugt eine neue datierte Matrix neben der alten.
Fehlt der OpenRouter-Schlüssel im Fenster, läuft OpenRouter nach und bekommt sein eigenes Messdatum.

### 5.4 Matrix der Ziele
Mindestens je ein Modell pro Zeile; Auswahl: aktuelles Flaggschiff, ggf. plus günstiges Modell, wenn sich die
Mechanik unterscheidet (z. B. Anthropic-Read-Faktor 0,1× vs. 0,05×).

| Ziel | Zugang | M1–M4 | M5–M6 | M7 | M8 |
|---|---|---|---|---|---|
| Anthropic direkt | `ANTHROPIC_API_KEY` | ✓ (explizit + automatisch, 5m + 1h) | ✓ | M7c | Referenz |
| OpenAI (Responses) | `OPENAI_API_KEY` | ✓ (inkl. `prompt_cache_key`, Retention) | ✓ | M7c | — |
| OpenAI (Chat Completions) | dto. | M1 | M5 | — | — |
| xAI Grok | `xai` | ✓ (inkl. `x-grok-conv-id`) | ✓ | M7a (+ M7c) | — |
| Google Gemini | `gemini` | ✓ (implizit; explizit nur wo noch angeboten) | ✓ (`thinkingLevel`/`thinkingBudget`) | nicht messbar | — |
| Mistral | `mistral` | ✓ (mit/ohne `prompt_cache_key`) | ✓ | nicht messbar | — |
| Cortecs | `~/.llm-keys/cortecs` | Claude + 1–2 Open-Source-Modelle | ✓ | M7b | ✓ |
| EU Router | `eurouter` | dto. | ✓ | M7a | ✓ |
| Requesty | `requesty` | dto. (inkl. `auto_cache`) | ✓ | M7a | ✓ |
| OpenRouter | `openrouter` (folgt) | dto. | ✓ | M7a | ✓ |
| DeepSeek API | — | nicht gemessen | — | — | — |

### 5.5 Werkzeug (Entscheidung Claude)
Messung per **rohem HTTP**, damit Leser jeder Plattform sie nachvollziehen können: je Messung eine lesbare
Request-Datei (JSON-Body + `curl`-Aufruf), dazu ein schlankes Ausführungsskript, das Aufrufe in der richtigen
Reihenfolge/mit Wartezeiten feuert und archiviert, sowie ein Auswerteskript, das aus den Rohdaten die Tabellen
erzeugt. Sprache des Skripts bleibt dem Bauenden überlassen (Kriterien: ohne Installation lauffähig, für
Nicht-.NET-Leser lesbar). Der .NET-Code tritt nur in den Code-Kästen der Artikel auf.

## 6. Inhalte aus unserem Code (für die Kästen „So haben wir es gelöst“)

### 6.1 Quellen
- `/Users/svk/dev/evanto/lib/ai/chatclients` — `EvChatClientExtensions.cs`, `EvChatClientFactory.cs`,
  `EvOpenAIResponsesChatClient.cs`, `CustomFieldsPolicy.cs`, README-Abschnitte „OpenAI: Responses API“ und
  „Reasoning Effort & Prompt Caching“, Tests `EvChatClientReasoningCachingTests.cs`, `EvReasoningCachingE2ETests.cs`.
- CompanyWizard — `.claude/references/reasoning-effort-prompt-caching.md`, `ModelCostCalculator.cs`,
  `TurnTokenUsage.cs`, `UsageRecordBooking.cs`, `ChatClientManager.cs`, `ModelRequestSettings.cs`,
  `ModelCatalogService.cs`, `CatalogModelFilter.cs`.
- cw-catalog — `ModelsDevMapper.cs`, `LiteLlmMapper.cs`, `ModelSourceMerger.cs`, `OpenRouterPriceCheck.cs`,
  `CortecsModelListParser.cs`, `ModelPricing.cs`, `ReasoningEffortLevels.cs`.

### 6.2 Kernstücke
- **Kostenformel** (`ModelCostCalculator`): `billedInput = max(0, Input − CacheRead − CacheWrite)`; Read-Preis
  `?? Input`; Write-Preis je TTL `?? Input`; Reasoning steckt in Output.
- **Einheitliche Effort-Einstellung** mit Vorrang Request → `Reasoning.Effort` → Einstellung; `max` nur bei
  Anthropic; `none → low` bei Claude.
- **Anthropic über die Raw-Factory**: `output_config.effort` + `cache_control` mit TTL, weil der Adapter beides
  nicht kennt.
- **Cache-Writes verstecken sich** in `AdditionalCounts["CacheCreationInputTokens"]` (keine M.E.AI-Eigenschaft).
- **Preisdaten zusammenführen** im Katalog: models.dev bestimmt den Bestand, LiteLLM liefert genauere Preise
  inkl. 1-h-Write, OpenRouter nur als Gegenprobe (> 25 % Abweichung wird geloggt), Router-Preise je Hoster als
  eigene Einträge (Cortecs in EUR).

### 6.3 Praxislehren (bewusst erzählen)
- Der Top-Level-`cache_control` von Anthropic traf über mehrere Züge nie ⇒ zusätzlicher Breakpoint am
  Systemprompt; eine Datumsnachricht pro Zug musste aus dem gecachten Anfang heraus.
- gpt-5.x lehnte Tools + Effort auf `/chat/completions` ab ⇒ Umstieg auf die Responses-API, zustandslos mit
  `store:false` + verschlüsseltem Reasoning.
- Ein Claude-Modell hinter einem Router bekommt bei uns kein explizites Caching und kein `max`.
- `CustomFieldsJson` überschreibt Body-Felder bedingungslos — ein `reasoning_effort` dort gilt für jedes Modell
  des Kontos.
- Grenzen der Buchung: abgebrochene Streams buchen nichts, alte Datensätze werden nicht nachberechnet,
  Cortecs-Mischpreis bei mehreren Upstream-Anbietern.

### 6.4 Regeln für Code-Kästen
Höchstens ~15 Zeilen je Ausschnitt, gekürzt aber lauffähig gedacht, mit Link auf die Quelle (Zitieren und
Verlinken freigegeben, s. 9). Ist die Quelle nicht öffentlich erreichbar, wird der Ausschnitt im Messrepository
abgelegt und dorthin verlinkt.

## 7. Artefakte

1. Öffentliches GitHub-Repository (evanto-Organisation): Skripte, Prompts, Rohdaten, `claims.yaml`, erzeugte
   Tabellen, README (DE/EN) mit Anleitung zum Nachmessen, Lizenz.
2. Fünf Artikel × zwei Sprachen als Markdown-Entwürfe (Format für evanto.de bleibt dem Bauenden überlassen,
   bis das CMS bekannt ist).
3. Fünf LinkedIn-Beiträge × zwei Sprachen, jeder mit einem gemessenen Befund als Aufhänger — erst nach den Messungen.
4. Diagramme: mindestens (a) Token-Arten eines Aufrufs, (b) Prefix-Cache und was ihn bricht, (c) Weg einer
   Anfrage durch einen Router.

## 8. Startbestand des Behauptungsregisters (Recherche 2026-10-18, ungeprüft)

Kurzfassung; die vollständigen Tabellen und Quell-URLs liegen in
`docs/superpowers/specs/2026-10-18-blogserie-recherche.md` und gehen 1:1 ins Register.

1. OpenAI cacht automatisch ab 1 024 Tokens; GPT-5.6+: Read 0,1×, **Write 1,25×** (ältere Modelle Write gratis); TTL `30m` bzw. `in_memory`/`24h`.
2. Anthropic: explizit bis 4 Breakpoints oder automatisch per Top-Level-`cache_control`; Write 1,25× (5 min) / 2× (1 h); Read 0,1× / 0,05× / 0,025× je Modell; Mindestgröße 512–4 096 je Modell, darunter still kein Cache.
3. Anthropic: Top-Level-Effort- und Thinking-Wechsel brechen den Nachrichten-Cache; Effort pro Nachricht als Beta ohne Cache-Verlust; `budget_tokens` ab 4.7 → 400.
4. Anthropic: Thinking wird voll berechnet, auch wenn zusammengefasst/ausgelassen.
5. xAI: automatisch, `x-grok-conv-id`/`prompt_cache_key` für Routing; Read ≈ 0,15–0,25×; Reasoning nicht abschaltbar; ≥ 200 k Tokens doppelter Tarif.
6. Gemini: implizites Caching ab 2.5, Mindestgröße 2 048/4 096; explizites Caching nicht auf Gemini 4; Read 0,1× + Speicherkosten/h; `thinkingLevel` vs. `thinkingBudget`, beide zusammen → 400.
7. Mistral: `prompt_cache_key`, 64-Token-Blöcke, Read 0,1×; ob ohne Schlüssel gecacht wird, unklar.
8. DeepSeek: Disk-Cache, Read 0,02–0,033×, Off-Peak −50 %; `reasoning_content` muss bei Tools zurückgegeben werden.
9. Open-Source-Modelle: Caching und Thinking-Schalter sind Eigenschaft des Hosters (`enable_thinking`, `thinking`, `reasoning_effort`, vLLM-Feldumbenennung `reasoning_content → reasoning`).
10. Cortecs: Caching je Upstream-Anbieter, `cache_control` nur Bedrock-Claude; Effort → Claude-Budget 1024/2048/4096; kein Sticky Routing dokumentiert; Doku widerspricht sich bei Usage-Feldern.
11. Requesty: `auto_cache`; `caching_tokens` = Writes; Effort → Claude-Budget bis 16 384; EU-Endpunkt hält nur die Requesty-Verarbeitung in der EU.
12. OpenRouter: reicht `cache_control` inkl. 1 h durch; Sticky Routing 10 min, aus bei `provider.order`; Kosten in jeder Usage-Antwort.
13. Preisquellen: models.dev ohne 1-h-Write und Stufen; LiteLLM mit 1-h-Write und `_above_*`; OpenRouter mit `overrides` (Zeitfenster/Größe); Cache-Faktoren in Aggregator-Doku teils veraltet.
14. Usage-Felder: Anthropic `input_tokens` **ohne** Cache-Tokens, OpenAI-Stil `prompt_tokens` **mit**.
15. EU Router: Kosten in EUR je Aufruf (`cost_eur`) + `/generation` per Request-ID; Cache-Tokens berichtet, aber kein dokumentiertes `cache_control`-Durchreichen und kein Sticky Routing; Reasoning über `reasoning`/`reasoning_effort`; EU-Filter `data_residency`, `eu_owned`, `max_retention_days`; „no markup“, EZB-Tageskurs.
16. Kosten per API: pro Aufruf nur bei OpenRouter, EU Router, xAI, Requesty (Antwort) und Cortecs (Management-Logs); OpenAI/Anthropic nur aggregiert mit Admin-Key (Usage 1 min, Kosten täglich; OpenAI-Usage ohne Reasoning-Feld, Anthropic-Kosten nur je Workspace); Gemini nur Cloud Billing; Mistral nur Enterprise. Kein Anbieter liefert Kosten als Header.
17. Listenpreise per API: OpenRouter, Cortecs, Requesty, EU Router, xAI ja; Anthropic `/v1/models` ohne Preise; OpenAI, Mistral, Gemini nur Webseiten.

## 9. Entscheidungen vom 2026-10-19 (svk)

- **Neutralität**: neutrale Darstellung aller Anbieter/Router, **keine Vorab-Abstimmung** mit Providern.
  Offenlegung (Claude): ein Satz in Teil 4 und im Hauptartikel, dass Evanto Cortecs als Partner für Managed AI
  nutzt — stärkt die Neutralität, ändert keine Bewertung.
- **Cortecs-Messkonto**: svk hinterlegt einen eigenen Schlüssel (erwartet als `~/.llm-keys/cortecs`); das
  produktive Managed-AI-Konto (`~/.cortecs-sovereign-key`) wird **nicht** für Messungen verwendet. Abschnitt 3
  und 5.4 gelten entsprechend.
- **Reihenfolge**: **Hauptartikel zuerst**, danach Teil 1 → 2 → 3 → 4; der Hauptartikel wird mit jedem Teil
  um Verweise ergänzt. Da alle Messungen im gemeinsamen Fenster *vor* der ersten Veröffentlichung laufen, ist
  die Matrix beim Erscheinen vollständig. Fehlt OpenRouter dann noch (Claude): Zeile „folgt“, wird mit eigenem
  Messdatum nachgetragen; die Veröffentlichung wartet nicht darauf.
- **Code**: Ausschnitte aus `Evanto.ChatClients` und CompanyWizard dürfen zitiert und verlinkt werden.
- **GitHub**: Konto `svkaenel` verbunden, Organisation `evanto-media-ag`. Repository wird neu angelegt;
  Vorschlag Name (Claude): `evanto-media-ag/llm-caching-reasoning-costs`, öffentlich. Anlegen erst nach
  ausdrücklicher Bestätigung (öffentlich sichtbar).

## 10. Dem Bauenden überlassen

- Konkrete Modellauswahl je Anbieter nach den Kriterien in 5.4.
- Skriptsprache und Repository-Struktur (Kriterien in 5.5).
- Wortlaut, Länge, Überschriften der Artikel innerhalb der Gliederung 4.2; Diagrammwerkzeug.
- Umgang mit Messwiederholungen (Anzahl Läufe für Stabilitätsaussagen), solange die Rohdaten aller Läufe archiviert werden.
