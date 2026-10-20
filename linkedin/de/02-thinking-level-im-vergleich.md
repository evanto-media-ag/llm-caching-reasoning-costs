Reasoning-Modelle „denken" vor der Antwort – und dieses Denken wird als Output bezahlt, den teuersten Teil eines Aufrufs. Über einen Parameter legen Sie fest, wie gründlich gedacht wird: den Thinking-Level (Reasoning Effort).

Klingt nach einem einfachen Regler. Nur heißt er bei jedem Anbieter anders, hat andere Stufen und reagiert unterschiedlich auf Werte, die er nicht kennt. Wir haben die sieben üblichen Werte von none bis max an jedes Modell geschickt.

Angenommen wurden zwischen zwei (Mistral Medium) und sieben (Claude über Cortecs). <!-- claim:C-063 --> <!-- claim:C-056 --> Alles andere endete mit HTTP 400.

Einige Beobachtungen:
→ Claude Sonnet 5.5 dachte bei unserer Aufgabe bis xhigh gar nicht – erst bei max. <!-- claim:C-068 -->
→ IONOS lehnte für Qwen3.8-27B den Wert high ab, akzeptierte aber xhigh. <!-- claim:C-070 -->
→ Router nehmen Werte an, die der Anbieter selbst ablehnt. Ob sie ankommen, sieht man nicht. <!-- claim:C-056 -->
→ Claude Haiku 5.5 berechnete 53 Thinking-Tokens für eine Antwort von acht Zeichen – ohne eines davon zu zeigen. <!-- claim:C-013 -->

Teil 2 unserer Serie „Was ein LLM-Aufruf wirklich kostet" – mit der vollständigen Tabelle je Modell und dem Zusammenspiel von Thinking-Level und Prompt-Cache.

👉 [Link zum Artikel]

#KI #LLM #Reasoning #APIKosten
