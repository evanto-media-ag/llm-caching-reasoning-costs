Router wie Cortecs, EU Router, Requesty oder OpenRouter bündeln viele Modelle hinter einer API. Das ist bequem, und die europäischen Anbieter versprechen dazu Verarbeitung in der EU. Was sie mit Prompt Caching und Preisen machen, steht selten im Prospekt.

Zur Einordnung: Prompt Caching hält den gleichbleibenden Anfang eines Prompts beim Anbieter vor, ein Treffer kostet bei Claude ein Zehntel des Input-Preises oder weniger. <!-- claim:C-010 -->

Wir haben die vier Router mit denselben Aufrufen gemessen wie Anthropic direkt:

→ Claude über einen Router ohne cache_control: 0 von 4 Cache-Treffern. Mit cache_control: 4 von 4 – bei allen vier. <!-- claim:C-060 -->
→ Der Router wählt den Upstream – und damit, ob gecacht wird. Cortecs schickte Claude ohne Vorgabe zu Google Vertex: kein Cache. Auf Bedrock gepinnt: Cache. <!-- claim:C-030 -->
→ Derselbe Prompt zählte je Upstream 5 426 oder 7 238 Tokens. <!-- claim:C-083 -->
→ Bei gpt-oss-120b lag der berechnete Preis zwischen 80 % unter und 170 % über dem gelisteten. <!-- claim:C-057 --> <!-- claim:C-086 -->
→ „EU" heißt bei jedem Router etwas anderes.

Offenlegung: Wir nutzen Cortecs als Partner für Managed AI. Gemessen haben wir mit separaten Konten, ohne Vorab-Abstimmung.

Teil 4 und Abschluss unserer Serie „Was ein LLM-Aufruf wirklich kostet".

👉 [Link zum Artikel]

#KI #LLM #EU #Router #APIKosten
