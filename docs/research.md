# Recherche zur Blogserie (2026-10-18) — Startbestand für das Behauptungsregister

Alles hier ist **ungeprüft** (Doku-Lektüre bzw. Code-Lesen), Grundlage für `claims.yaml`. Gehört zu
`2026-10-18-blogserie-llm-caching-thinking-kosten-design.md`. Doku gelesen am 2026-10-18; Seitendaten wo angegeben.

## A. Frontier-APIs

### OpenAI (Responses + Chat Completions)
- Caching **automatisch**, exakter Prefix; Mindestgröße 1 024 sichtbare Input-Tokens (GPT-5.6+; ältere abhängig von Tools/Bildern/Schema/Effort).
- `prompt_cache_key`: ältere Modelle → Routing (~15 Req/min pro Key); GPT-5.6+ → getrennte Cache-Abrechnung je Benutzer (verhindert Cache-Proben). `prompt_cache_breakpoint` laut OpenRouter **[auf OpenAI-Seite unbestätigt]**.
- Retention: ältere Modelle `prompt_cache_retention` = `in_memory` (≈5–10 min idle, max 1 h) oder `24h` (Default `24h` außer ZDR); GPT-5.6+ `prompt_cache_options.ttl` nur `30m`.
- Preis: GPT-5.6+ Read 0,1× (0,05× gpt-6.1-sol), **Write 1,25×**; ältere: Write gratis, Read 0,1× (gpt-5.5 $0.50 vs $5.00; gpt-5-mini $0.025 vs $0.25).
- Reasoning: Responses `reasoning.effort`, Chat Completions `reasoning_effort`; Werte `none, minimal, low, medium, high, xhigh, max` je Modell; GPT-6 Astra ohne `none`, GPT-6.1 Sol ohne `none`/`minimal`; Default `medium`; neu `reasoning.mode` = `standard`/`pro`.
- Reasoning-Tokens verborgen, als Output berechnet; `max_output_tokens` deckelt Reasoning + Antwort.
- Usage Responses: `input_tokens_details.cached_tokens`, `input_tokens_details.cache_write_tokens`, `output_tokens_details.reasoning_tokens`. Chat Completions: `prompt_tokens_details.cached_tokens`, `completion_tokens_details.reasoning_tokens` **[nur Sekundärquellen]**; Cache-Write-Feld dort **[unbestätigt]**.
- Reasoning über Züge per `encrypted_content` (`store:false`/ZDR) oder `previous_response_id`; `reasoning.context` = `current_turn`/`all_turns`. Kein Function Calling auf Chat Completions bei GPT-6 Astra / 6.1 Sol.
- Quellen: https://developers.openai.com/api/docs/guides/prompt-caching · …/guides/reasoning · …/pricing (Promo bis 2026-11-21)

### Anthropic (Messages API)
- **Explizit**: `cache_control` an bis zu 4 Blöcken. **Automatisch**: ein Top-Level-`cache_control:{type:"ephemeral"}`, wandert mit (belegt einen der 4 Slots; nicht auf Legacy-Bedrock).
- TTL 5 min Default, bei Treffer kostenlos verlängert; optional `"ttl":"1h"`; längere TTLs vor kürzeren.
- Preis: Write 1,25× (5 min) / **2× (1 h)**; Read 0,1× (meist), **0,05×** Opus 5.5 / Sonnet 5.5, **0,025×** Fable 5.1 / Mythos 5.1.
- Mindestgröße: 512 (5.x, Haiku 5.5); 1 024 (Opus 4.8, Sonnet 5, Sonnet 4.x, Opus 4/4.1); 2 048 (Opus 4.7, Haiku 3.5); 4 096 (Opus 4.5/4.6, Haiku 4.5). Darunter kein Cache, **kein Fehler**.
- Lookback 20 Blöcke. Pre-Warming mit `max_tokens:0`.
- Reasoning: `output_config.effort` = `low, medium, high, xhigh, max` je Modell; Default `high` (Opus 5.5 / Haiku 5.5: `medium`). `thinking`: `adaptive`, `disabled` (400 bei xhigh/max auf mehreren Modellen; immer 400 auf Opus 5.5), `between_tools` (Sonnet 5.5). `budget_tokens ≥ 1024` deprecated ab 4.6, **400 ab 4.7**.
- Effort pro Nachricht (Beta-Header `mid-conversation-output-config-2026-07-01`) ohne Cache-Verlust.
- Thinking voll berechnet unabhängig von `display` (`summarized`/`omitted`); frühere Thinking-Blöcke im Kontext als Input berechnet.
- Usage: `input_tokens` (nur nach letztem Breakpoint), `cache_creation_input_tokens`, `cache_read_input_tokens`, `cache_creation.{ephemeral_5m_input_tokens, ephemeral_1h_input_tokens}`, `output_tokens_details.thinking_tokens`. Gesamtinput = read + creation + input_tokens.
- Cache-Bruch: Tool-Änderung → alles; `tool_choice`, Bilder, Thinking-Konfig, `budget_tokens`, **Top-Level-Effort** → Nachrichten-Cache. Effort gleich Modell-Default bricht nicht.
- Quellen: https://platform.claude.com/docs/en/build-with-claude/prompt-caching · …/effort · …/extended-thinking · …/thinking-steering-and-cost

### xAI Grok
- **Automatisch**, exakter Prefix; `x-grok-conv-id` oder `prompt_cache_key` routen auf denselben Server. TTL, Mindestgröße, Write-Kosten nicht dokumentiert.
- Read ≈ 0,25× (grok-4.7/4.6: $0.50 vs $2.00), 0,15× (4.5), ≈0,16× (4.3/4.20). ≥ 200 k Tokens: doppelter Tarif für alle Tokens.
- `reasoning.effort`: 4.7/4.6 `low, medium, high, xhigh` (Default `high`); 4.5 bis `high`, `xhigh` → high; nicht abschaltbar; grok-4.20-multi-agent: Effort = Anzahl Agenten (4/16).
- Reasoning als Output, `reasoning_tokens`. Usage: CC `usage.prompt_tokens_details.cached_tokens`; Responses `usage.input_tokens_details.cached_tokens`.
- Verschlüsseltes Reasoning nur Responses-API (4.7 immer). Reasoning-Modelle lehnen `stop`, `presencePenalty`, `frequencyPenalty` ab.
- Quellen: https://docs.x.ai/developers/advanced-api-usage/prompt-caching · …/prompt-caching/usage-and-pricing · https://docs.x.ai/developers/model-capabilities/text/reasoning · https://docs.x.ai/developers/models

### Google Gemini
- Implizites Caching Default ab 2.5; Mindestgröße 4 096 (Gemini 4 Argon, 3.8 Flash, 3.6 Flash, 3.1 Pro), 2 048 (2.5 Flash/Pro); kein garantierter Treffer.
- Explizit `cachedContents` (v1beta), nur generateContent, nur Gemini 3 / 2.5; **nicht auf Gemini 4 Argon+ und nicht in der Interactions-API**; Default-TTL 1 h.
- Read 0,1× (2.5 Pro $0.125 vs $1.25); Speicher $4.50/1M/h (2.5 Pro, 3.1 Pro), $1.00 (2.5 Flash), $0.50 (3.8 Flash Promo).
- Gemini 3/4: `thinkingLevel` (Interactions `thinking_level`); Argon `low, medium (Default), high`, nicht abschaltbar; andere zusätzlich `minimal`. Gemini 2.5: `thinkingBudget` (`0` aus — nicht 2.5 Pro, Bereich 128–32768; `-1` dynamisch; Flash 0–24576). Gemini 4: `thinkingBudget` deprecated → Level mit Warnung; beide zusammen → 400.
- Thinking als Output; `max_output_tokens` inkl. Thinking. Usage generateContent `usageMetadata.thoughtsTokenCount`, `cachedContentTokenCount` **[Feldname auf aktueller Seite nicht gezeigt]**; Interactions `usage.total_cached_tokens`, `total_thought_tokens`.
- Quellen: https://ai.google.dev/gemini-api/docs/caching (2026-10-13) · …/generate-content/caching (2026-10-13) · …/thinking, …/generate-content/thinking (2026-10-14) · …/pricing (2026-10-16)

### Mistral
- `prompt_cache_key`; ob ohne Key gecacht wird unklar (Cortecs nennt „automatisch“). 64-Token-Blöcke, < 64 kein Treffer; Read 0,1×; TTL nicht dokumentiert; `prompt_tokens_details.cached_tokens`.
- Reasoning: Mistral Medium 3.5 Effort per Request (HF-Modellkarte); LiteLLM emuliert `reasoning_effort` für Magistral per Systemprompt **[kein nativer Parametername gefunden]**.
- Quellen: https://docs.mistral.ai/studio/conversations/advanced/prompt-caching · https://huggingface.co/mistralai/Mistral-Medium-3.5-128B · https://docs.litellm.ai/docs/providers/mistral

## B. Open-Source-Modelle (Eigenschaft des Hosters)
- **DeepSeek API** (`deepseek-flash` = V4.1-Flash, `deepseek-v4-pro`): automatischer Disk-Cache (best effort, Stunden–Tage); Hit Flash $0.006 vs $0.30 (0,02×), Pro $0.044 vs $1.32 (≈0,033×); Off-Peak −50 % (Peak 01–04 + 06–10 UTC Mo–Fr). Thinking Default an (`high`), `thinking:{type:"enabled"/"disabled"}`; `reasoning_effort` `low, high, max` (minimal→low, medium/xhigh→high). `reasoning_content` **muss bei Tools zurückgegeben werden**, sonst 400. Usage `prompt_cache_hit_tokens`, `prompt_cache_miss_tokens`. Quellen: https://api-docs.deepseek.com/guides/kv_cache · …/quick_start/pricing · …/guides/thinking_mode
- **vLLM**: Automatic Prefix Caching (V1 Default an **[unbestätigt]**, `--no-enable-prefix-caching`); `cached_tokens` nur mit `--enable-prompt-tokens-details`, V1 laut Issue leer **[Stand unbestätigt]**. `chat_template_kwargs`: Qwen3 `enable_thinking:false`, DeepSeek-V3.1 `thinking:true`, Gemma 4 `enable_thinking`; `reasoning_effort` `none` aus, low/medium/high an. Feld umbenannt `reasoning_content` → **`reasoning`** (Doku 2026-10-01). Quellen: https://docs.vllm.ai/en/latest/features/reasoning_outputs.html · …/automatic_prefix_caching.html · https://github.com/vllm-project/vllm/issues/16162
- **SGLang**: RadixAttention-Prefix-Cache **[Default/Usage unbestätigt]**; Parser `qwen3`, `deepseek-v3`, `kimi_k2`, `gpt-oss`; liefert `reasoning_content`. Quelle: https://docs.sglang.io/advanced_features/separate_reasoning.html
- **gpt-oss**: Harmony `Reasoning: low/medium/high` im System/Developer-Text (Default medium); Server mappen `reasoning_effort` **[Sekundärquellen]**.
- **Alibaba Model Studio (Qwen)**: implizit (nicht abschaltbar, min 256, Write 1×, Read 0,2×) oder explizit `cache_control` (min 1 024, 5 min TTL, Write 1,25×, Read 0,1×), gegenseitig exklusiv; `enable_thinking`. Quelle: https://www.alibabacloud.com/help/en/model-studio/user-guide/context-cache
- **Moonshot (Kimi)**: automatisch; K2.6 Hit ≈ $0.16 vs $0.95 **[Drittquelle]**.

## C. Router
- **Cortecs**: Caching je Upstream; `cache_control` nur Bedrock-Claude (~1 024 min, ~5–60 min TTL); automatisch bei Vertex Gemini, Azure, Mistral, Inceptron, Tensorix, Aki, Entrim, Arkane, Sference; sonst kein Caching. Caching-Seite: `prompt_tokens_details.{cached_tokens, cache_creation_tokens}`, `cost_details.{prompt_cost, cache_read_cost, cache_write_cost, completion_cost}`; API-Referenz: **nur** `prompt/completion/total_tokens` (Widerspruch). `reasoning_effort` `low/medium/high`, still ignoriert wo nicht unterstützt; Claude → Budget **1024/2048/4096**; `thinking` via `extra_body`. Routing: `preference`, `eu_native`, `allowed_providers`, `provider_order`, `quantizations`, `enable_model_fallback`, `allow_zero_data_retention`; **kein Sticky Routing dokumentiert**. Quellen: https://docs.cortecs.ai/usage/prompt-caching · …/routing/reasoning.md · …/api/chat-completions.md · …/routing/routing-concept.md
- **Requesty**: `requesty.auto_cache` (Default je Client), manuelles `cache_control` inkl. `ttl:"1h"`; `prompt_tokens_details.{cached_tokens, caching_tokens}`; `reasoning_effort` + `max, min, none` oder Budget-String; Claude low 1024 / medium 8192 / high 16384 / max = Modellmax − 1; `xhigh` nur bestimmte OpenAI-Modelle. EU-Endpunkt `router.eu.requesty.ai` hält nur Requesty-Verarbeitung in der EU. Quellen: https://docs.requesty.ai/features/auto-caching · …/manual-caching · …/reasoning.md · …/eu-routing.md
- **OpenRouter**: reicht `cache_control` durch (inkl. Top-Level-automatisch, 1 h); Sticky Routing 10 min, nur wenn Cache-Read günstiger, **aus bei `provider.order`**; `session_id`/`x-session-id`/`prompt_cache_key`. Einheitliches `reasoning` (`effort none…max`, `max_tokens`, `exclude`, `enabled`); Claude-Budget `max(min(max_tokens×ratio, 128k), 1024)`, Ratio 0,95/0,8/0,5/0,2/0,1. Usage immer: `prompt_tokens_details.{cached_tokens, cache_write_tokens}`, `completion_tokens_details.reasoning_tokens`, `cost`, `cost_details.upstream_inference_cost` (BYOK), `cache_discount`. Quellen: https://openrouter.ai/docs/guides/best-practices/prompt-caching · …/reasoning-tokens · …/usage-accounting · https://openrouter.ai/docs/api/api-reference/models/get-models
- **EU Router** (eurouter.ai, recherchiert 2026-10-19): Usage enthält `cost`, `cost_currency`, `cost_eur`, `cost_details`, `is_byok`, `prompt_tokens_details.{cached_tokens, cache_write_tokens}`, `completion_tokens_details.reasoning_tokens`. Cache-Tokens berichtet und bepreist; **kein dokumentiertes `cache_control`-Durchreichen, kein Sticky Routing** (Fallback könnte Cache brechen **[UV]**). Reasoning: `reasoning`-Objekt, `reasoning_effort`, `include_reasoning`; Modell-Liste mit `reasoning.supported_efforts`, `mandatory`. EU: „inference processed inside the EU“; Filter `data_residency` (eu/eea/de), `eu_owned`, `max_retention_days` (0 = ZDR), `data_collection: deny`; Anbieter u. a. Scaleway, Azure, Mistral, GreenPT; Abrechnung Monatsplan + EUR-Guthaben, Umrechnung zum EZB-Tageskurs, „no markup“, Mindestguthaben 0,10 € (sonst 402). Gründung 2026 **[Drittquelle]**. Quellen: https://eurouter.ai/docs (…/api/chat, …/api/generation, …/api/models, …/concepts/credits, …/concepts/routing, …/concepts/providers)

## D. Preisdatenquellen
- **models.dev** (`/api.json`, MIT): `cost.cache_read`, `cost.cache_write` (USD/1M), `cost.reasoning`, `reasoning` (bool); `last_updated`; **keine 1-h-Write/Stufen**.
- **OpenRouter `/api/v1/models`**: `pricing.input_cache_read`, `input_cache_write` (5 min), `input_cache_write_1h`, `internal_reasoning`; `reasoning.{default_effort, supported_efforts, mandatory, supports_max_tokens}`; `overrides[]` (Größe/Zeitfenster); USD/Token als String.
- **LiteLLM** `model_prices_and_context_window.json`: `cache_read_input_token_cost`, `cache_creation_input_token_cost`, `…_above_1hr`, `*_above_200k/272k_tokens`, `*_batches/_flex/_priority`, `prompt_cache_min_tokens`, `output_cost_per_reasoning_token`, `supports_*_reasoning_effort`, `reasoning_effort_levels`, `default_reasoning_effort`; kein Off-Peak.
- **Helicone** `/api/llm-costs`: `prompt_cache_read_per_1m`, `prompt_cache_write_per_1m`; keine 1-h/Reasoning/Stufen.
- Aggregator-Faktoren veraltet: OpenRouter-Doku nennt OpenAI Read 0,25×/0,5×, Gemini 0,25×, DeepSeek 0,1× — Anbieterseiten aktuell 0,1× / 0,1× / ≈0,02–0,033×.

## D2. Kosten per API abrufen (recherchiert 2026-10-19)

Kein Anbieter liefert Kosten als Response-Header; Kosten pro Aufruf stehen, wo vorhanden, im Response-Body.

| Anbieter | Kosten pro Aufruf | Aggregiert | Auth | Auflösung / Verzug | Token-Aufteilung | Zuordnung |
|---|---|---|---|---|---|---|
| OpenAI | nein (nur `usage`, `x-request-id`) | `GET /v1/organization/usage/completions`, `GET /v1/organization/costs` | **Admin-Key** | Usage 1m/1h/1d; Costs nur 1d; Verzug undokumentiert | Usage: `input_cached_tokens`, `input_uncached_tokens`, `input_cache_write_tokens`, `output_tokens`; **kein Reasoning-Feld**; Costs nur `amount` je `line_item` | `group_by` project_id, api_key_id, model …; Header `OpenAI-Project` |
| Anthropic | nein (nur `usage`) | `GET /v1/organizations/usage_report/messages`, `GET /v1/organizations/cost_report` | **Admin-Key** `sk-ant-admin01-…` (keine Workspace-Keys, nicht für Einzelkonten) | Usage 1m/1h/1d, Daten ≈ 5 min; Cost nur 1d | `uncached_input_tokens`, `cache_read_input_tokens`, `cache_creation.ephemeral_5m/1h_input_tokens`, `output_tokens` (inkl. Thinking); Cost in Cent nach `token_type` | Usage nach api_key_id, workspace_id, model …; **Cost nur nach workspace_id/description** |
| xAI | **ja**: `usage.cost_in_usd_ticks` (10¹⁰ Ticks = 1 USD), inkl. Cache-Rabatt + Server-Tools; Streaming im letzten Chunk | `POST management-api.x.ai/v1/billing/teams/{team_id}/usage` | **Management-Key** | `timeUnit` Sekunde…Monat | Cache/Reasoning auf Kostenseite nicht gezeigt **[UV]** | `groupBy` description (Modell); nach Key **[UV]** |
| Gemini API | nein | nur Cloud Billing (SKU, BigQuery-Export **[UV]**) | GCP | Stunden bis > 1 Tag | — | nur Projekt |
| Mistral | nein | Admin-API **nur Enterprise**, sonst Dashboard | — | täglich | Dashboard: Modell, Input/Output | Workspace |
| OpenRouter | **ja**: `usage.cost`, `cost_details.upstream_inference_cost`; `GET /api/v1/generation?id=` mit `total_cost`, `cache_discount`, `native_tokens_*` inkl. reasoning/cached, `provider_name` | `GET /api/v1/key` (usage daily/weekly/monthly); Activity-API (30 Tage, **Management-Key**, Pfad **[UV]**) | normaler Key | `/generation` mit kurzem Verzug | voll | ein Key je Lauf |
| Cortecs | **nein im Response**; pro Trace in `GET /v1/manage/logs` (`request_id`, `attempts[]` mit `cost` EUR, Provider, Modell; max. 24 h je Abfrage) | `GET /v1/manage/usage` (1h…1Y), `/manage/budgets`, `/manage/balance` | **Management-Key** | — | `cache_read_tokens`, `cache_write_tokens` (Teilmengen von Input), Output; **kein Reasoning**; Preise EUR je Typ | `group_by` key_name, model, provider …; `request_id` = Completion-`id`? **[UV]** |
| Requesty | **ja**: `usage.cost` (USD); Streaming mit `include_usage` | `GET api-v2.requesty.ai/v1/manage/org/usage` | Bearer (Management-Key? unklar) | hour/day/month, max. 100 Tage | nur Input/Output/Total + `spend`; **kein Cache/Reasoning** | `group_by` api_key_id, model_used, provider_used, `extra.<metadata>` via `extra_body.requesty.metadata` |
| EU Router | **ja**: `usage.cost_eur`, `cost_details`; `GET /api/v1/generation?id=<x-request-id>` mit `cost_eur`, `cost_native`, `exchange_rate`, Cache-Tokens (kein Reasoning) | **keine Verlaufs-API** (nur Dashboard), `/api/v1/credits` | normaler Key `eur_…` | — | Cache read/write | per Request-ID |

**Listenpreise per API:**

| Quelle | Endpunkt | Auth | Felder |
|---|---|---|---|
| OpenRouter | `GET /api/v1/models`, je Anbieter `/models/{a}/{s}/endpoints` | keine | USD/Token: prompt, completion, internal_reasoning, input_cache_read/write, overrides |
| Cortecs | `GET /v1/models` (`extended=true` je Upstream) | optional | je 1M: input, output, cache_read_cost, cache_write_cost; `currency` (Default EUR) |
| Requesty | Modell-Liste | optional | USD/Token: input_price, output_price, cached_price, caching_price (Beispiel auch 5m/1h), Größenstufen |
| EU Router | `GET /api/v1/models` (`/endpoints` mit Key) | keine | wie OpenRouter inkl. internal_reasoning, Cache read/write, `currency` |
| xAI | `GET /v1/language-models` | API-Key | USD-Cent je 100M: prompt, cached_prompt, completion, Langkontext, Suche |
| Anthropic | `/v1/models` | API-Key | **keine Preise** |
| OpenAI, Mistral, Gemini API | — | — | nur Webseiten **[UV]** |
| Google Cloud | Cloud Billing Catalog API | GCP | ob Gemini-API-SKUs enthalten sind **[UV]** |

Quellen: developers.openai.com/cookbook/examples/completions_usage_api · platform.claude.com/docs/en/manage-claude/usage-cost-api · docs.x.ai/developers/cost-tracking, …/rest-api-reference/management/billing · ai.google.dev/gemini-api/docs/billing · docs.mistral.ai/admin/billing-usage/usage-limits · openrouter.ai/docs/use-cases/usage-accounting, …/api-reference/get-a-generation, …/api-reference/limits · docs.cortecs.ai/api/management-api.md · docs.requesty.ai/features/cost-tracking.md, …/api-reference/endpoint/manage-org-get-usage.md · eurouter.ai/docs/api/generation

## E. Unser Code (Praxisfall)
- **cw-catalog**: models.dev primär (Bestand, Limits, Effort), LiteLLM Anreicherung (Preise ersetzen models.dev; Cache-Preise feldweise LiteLLM vor models.dev; 1-h-Write nur aus LiteLLM), OpenRouter nur Gegenprobe (> 25 % geloggt). Nightly, Vorschläge → Freigabe → Publish. Allowlist openai/anthropic/mistral/gemini. Router als eigene Einträge je (Provider, ApiModelId); Cortecs EUR, `cache_write_cost` nur als 5-min-Write wenn ≥ Input (filtert Gemini-Speicherpreis, #61). Effort-Vokabular `none, low, medium, high, xhigh, max`; `null` = unbekannt, `[]` = keine Steuerung. Lücken: Cortecs-Mischpreis über Upstreams, Level-Preise manuell, 1-h-Write fast nirgends.
- **Evanto.ChatClients**: Anthropic über Raw-Factory (`output_config.effort`, Top-Level-`cache_control` + Systemprompt-Breakpoint), `none → low`, `max` nur Anthropic, `max_tokens 16000`; OpenAI direkt über Responses-API (`store:false`, `reasoning.encrypted_content`); Router + OpenAI-kompatible über Chat Completions mit `reasoning_effort`; Mistral-SDK verwirft Effort vermutlich still **[ungetestet]**; Gemini/Ollama Mapping **[unbestätigt]**.
- **CompanyWizard**: `ModelCostCalculator` (Formel siehe Design 6.2), `TurnTokenUsage` (Cache-Writes aus `AdditionalCounts["CacheCreationInputTokens"]`), `UsageRecordBooking` (TTL zur Buchungszeit), Grenzen siehe Design 6.3.
