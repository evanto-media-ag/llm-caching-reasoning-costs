As soon as several teams or customers use the same AI application, the question comes up: who causes which part of the bill? The provider's monthly invoice doesn't help — it knows no projects and no customers. You have to price every API call yourself.

That takes three things: the right token counts, current prices and a formula that brings both together. We measured at twelve providers and routers how well that works.

Where the provider reports costs in the response, our formula matched to the cent: 0.0 % deviation at xAI, Requesty, EU Router and Cortecs. <!-- claim:C-020 --> <!-- claim:C-039 --> <!-- claim:C-059 --> OpenAI's daily costs from the admin API matched exactly as well. <!-- claim:C-090 -->

The rest is manual work:
→ Every provider names the cache fields differently — and Anthropic doesn't count cached tokens in input. <!-- claim:C-014 -->
→ Cortecs reports costs as an integer in micro-euros — that isn't documented anywhere. <!-- claim:C-059 -->
→ Anthropic blocks its cost API for individual organisations, even with an organisation-wide key. <!-- claim:C-087 -->

And to be self-critical: our own price catalogue had the right prices, but three of the measured models were missing. <!-- claim:C-077 -->

Part 3 of our series "What an LLM call really costs".

👉 [link to the article]

#AI #LLM #APICosts #Controlling
