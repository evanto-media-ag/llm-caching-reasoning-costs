Routers such as Cortecs, EU Router, Requesty or OpenRouter bundle many models behind one API. That's convenient, and the European providers also promise processing in the EU. What they do with prompt caching and prices is rarely in the brochure.

For context: prompt caching keeps the unchanging start of a prompt at the provider, and at Claude a hit costs a tenth of the input price or less. <!-- claim:C-010 -->

We measured the four routers with the same calls as Anthropic direct:

→ Claude through a router without cache_control: 0 of 4 cache hits. With cache_control: 4 of 4 — at all four. <!-- claim:C-060 -->
→ The router picks the upstream — and with it, whether caching happens. Without a preference, Cortecs sent Claude to Google Vertex: no cache. Pinned to Bedrock: cache. <!-- claim:C-030 -->
→ The same prompt counted 5,426 or 7,238 tokens, depending on the upstream. <!-- claim:C-083 -->
→ For gpt-oss-120b, the charged price ranged from 80 % below to 170 % above the listed one. <!-- claim:C-057 --> <!-- claim:C-086 -->
→ "EU" means something different at every router.

Disclosure: we use Cortecs as our partner for Managed AI. We measured with separate accounts and didn't share results in advance.

Part 4 and the end of our series "What an LLM call really costs".

👉 [link to the article]

#AI #LLM #EU #Routers #APICosts
