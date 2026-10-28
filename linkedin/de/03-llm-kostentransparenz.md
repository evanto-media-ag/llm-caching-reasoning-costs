„Der Anbieter rechnet doch pro API-Key ab." Stimmt. Und das beantwortet genau eine Frage: Welche Anwendung hat das verbraucht?

Alle anderen Fragen beantwortet der Key nicht:
→ Welcher Kunde? Ein SaaS-Produkt bedient hundert Kunden über denselben Code. Hundert Keys verteilen und rotieren skaliert nicht – ohne Kosten pro Kunde kennt man aber weder Marge noch Ausreißer.
→ Was kostet ein Vorgang? Eine bearbeitete Rechnung, ein beantwortetes Ticket, ein Agentenlauf: Erst die Stückkosten zeigen, ob sich KI rechnet.
→ Wann ist das Budget erreicht? Ein Agentenlauf soll vorher stoppen, nicht am Monatsende. Die Admin-APIs helfen da kaum: OpenAI liefert Kosten nur tageweise, EU Router hat gar keine Kosten-API.
→ Was kostet alles zusammen? Bei mehreren Anbietern und Routern liegen die Kosten in mehreren Dashboards – in Dollar, Euro und Mikro-Euro.
→ Hat die Optimierung gewirkt? Ob Prompt Caching spart, sieht man nur an den Cache-Tokens pro Aufruf.

Die Antwort ist immer dieselbe: jeden Aufruf selbst bepreisen. Wir haben bei zwölf Anbietern und Routern gemessen, wie gut das gelingt – wo der Anbieter die Kosten mitliefert, lag unsere Formel bei 0,0 % Abweichung.

Teil 3 unserer Serie „Was ein LLM-Aufruf wirklich kostet".

👉 https://evanto.de/de/blog/llm-kostentransparenz

#KI #LLM #APIKosten #Controlling
