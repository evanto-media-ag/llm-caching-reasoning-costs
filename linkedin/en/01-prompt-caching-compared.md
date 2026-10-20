Your system prompt goes out with every API call — and is usually paid for in full every time.

Prompt caching changes that: the provider keeps the unchanged start of the prompt, and a hit costs only 5–10 % of the input price. <!-- claim:C-010 --> With Claude Sonnet 5, our 7,200-token prompt dropped from 1.45 to 0.15 cents per call. <!-- claim:C-092 -->

Sounds like a switch. It isn't. We measured caching at OpenAI, Anthropic, xAI, Gemini and Mistral with the same prompts and archived every API response.

The most surprising finding: changing the reasoning effort cost the whole cache at OpenAI, xAI and Gemini. At Claude Sonnet 5.5, it didn't. <!-- claim:C-064 --> If you choose the effort "intelligently" per message, you can lose the entire saving.

Also:
→ Below the minimum size (512 to 4,096 tokens), nothing is cached — no error, just a counter that stays at 0. <!-- claim:C-011 -->
→ Anthropic's 5-minute cache was gone after 5.5 minutes; OpenAI's wasn't. <!-- claim:C-062 -->
→ Grok 4.7 adds 1,152 of its own prompt tokens to every call. <!-- claim:C-054 -->

Part 1 of our series "What an LLM call really costs" — with tables per provider and the .NET trick that lets Claude hit the cache across several conversation turns. The opening article, linked in the post, gives the overview of all cost levers.

👉 [link to the article]

#AI #LLM #PromptCaching #APICosts #dotnet
