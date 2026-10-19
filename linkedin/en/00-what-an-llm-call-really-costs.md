A Claude call with a 7,200-token system prompt: 1.45 cents uncached. 1.81 cents on the first call with caching. 0.15 cents from the second call on.

Prompt caching saves about 90 % — if you do it right. If you do it wrong, the first call costs 25 % more and you save nothing afterwards.

On 19 October, we measured twelve providers and routers with the same calls: OpenAI, Anthropic, xAI, Gemini, Mistral, IONOS, Cortecs, EU Router, Requesty. Three findings:

→ The same text counts 58 % more tokens on Claude than on OpenAI. <!-- claim:C-053 -->
→ Through routers, Claude caches only with explicit cache_control — without the marker, 0 of 4 hits. <!-- claim:C-060 -->
→ For open-weight models via routers, the charged price was up to 170 % above the listed one. <!-- claim:C-057 -->

The opening of our series, with a comparison matrix and a decision guide. All raw data is public on GitHub.

👉 [link to the article]

#AI #LLM #PromptCaching #Costs
