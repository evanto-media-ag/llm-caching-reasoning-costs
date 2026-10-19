Ein Claude-Aufruf mit 7 200 Tokens Systemprompt: 1,45 Cent ungecacht. 1,81 Cent beim ersten Aufruf mit Cache. 0,15 Cent ab dem zweiten.

Prompt Caching spart rund 90 % – wenn man es richtig macht. Wer es falsch macht, zahlt beim ersten Aufruf 25 % mehr und spart danach nichts.

Wir haben am 19. Oktober zwölf Anbieter und Router mit denselben Aufrufen gemessen: OpenAI, Anthropic, xAI, Gemini, Mistral, IONOS, Cortecs, EU Router, Requesty. Drei Befunde:

→ Derselbe Text zählt bei Claude 58 % mehr Tokens als bei OpenAI. <!-- claim:C-053 -->
→ Über Router cacht Claude nur mit explizitem cache_control – ohne Marker 0 von 4 Treffern. <!-- claim:C-060 -->
→ Bei Open-Source-Modellen lag der berechnete Preis über Router bis zu 170 % über dem gelisteten. <!-- claim:C-057 -->

Der Auftakt unserer Serie, mit Vergleichsmatrix und Entscheidungshilfe. Alle Rohdaten liegen öffentlich auf GitHub.

👉 [Link zum Artikel]

#KI #LLM #PromptCaching #Kosten
