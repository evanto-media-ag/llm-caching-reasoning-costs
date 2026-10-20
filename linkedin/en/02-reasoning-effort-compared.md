Reasoning models "think" before they answer — and that thinking is billed as output, the most expensive part of a call. One parameter sets how thoroughly they think: the reasoning effort.

Sounds like a simple control. But every provider names it differently, has different levels and reacts differently to values it doesn't know. We sent the seven common values from none to max to every model.

The models accepted between two (Mistral Medium) and seven (Claude via Cortecs). <!-- claim:C-063 --> <!-- claim:C-056 --> Everything else ended with HTTP 400.

Some observations:
→ Claude Sonnet 5.5 didn't think at all on our task up to xhigh — only at max. <!-- claim:C-068 -->
→ IONOS rejected high for Qwen3.8-27B but accepted xhigh. <!-- claim:C-070 -->
→ Routers accept values the provider itself rejects. Whether they arrive, you can't see. <!-- claim:C-056 -->
→ Claude Haiku 5.5 billed 53 thinking tokens for an eight-character answer — without showing one of them. <!-- claim:C-013 -->

Part 2 of our series "What an LLM call really costs" — with the full table per model and how reasoning effort interacts with the prompt cache.

👉 [link to the article]

#AI #LLM #Reasoning #APICosts
