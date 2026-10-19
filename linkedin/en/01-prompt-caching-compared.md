Changing the reasoning effort cost the whole prompt cache at OpenAI, xAI and Gemini. At Claude Sonnet 5.5, it didn't. <!-- claim:C-064 -->

If you choose the effort "intelligently" per message, you can lose the entire cache saving.

More results from Part 1 of our measurements:

→ Below the minimum size (512 to 4,096 tokens), nothing is cached — no error, just a counter that stays at 0. <!-- claim:C-011 -->
→ Anthropic's 5-minute cache was gone after 5.5 minutes; OpenAI's wasn't. <!-- claim:C-062 -->
→ Grok 4.7 adds 1,152 of its own prompt tokens to every call. <!-- claim:C-054 -->

Plus: how we got Claude's cache to hit across several conversation turns in .NET.

👉 [link to the article]

#AI #LLM #PromptCaching #dotnet
