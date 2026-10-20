Sobald mehrere Teams oder Kunden dieselbe KI-Anwendung nutzen, kommt die Frage: Wer verursacht welchen Teil der Rechnung? Die Monatsrechnung des Anbieters hilft da nicht – sie kennt keine Projekte und keine Kunden. Man muss jeden API-Aufruf selbst bepreisen.

Dafür braucht es drei Dinge: die richtigen Token-Zahlen, aktuelle Preise und eine Formel, die beides zusammenbringt. Wir haben bei zwölf Anbietern und Routern nachgemessen, wie gut das gelingt.

Wo der Anbieter die Kosten in der Antwort mitliefert, stimmte unsere Formel auf den Cent: 0,0 % Abweichung bei xAI, Requesty, EU Router und Cortecs. <!-- claim:C-020 --> <!-- claim:C-039 --> <!-- claim:C-059 --> Auch die Tageskosten der OpenAI-Admin-API passten exakt. <!-- claim:C-090 -->

Der Rest ist Handarbeit:
→ Jeder Anbieter nennt die Cache-Felder anders – und Anthropic zählt Cache-Tokens nicht im Input mit. <!-- claim:C-014 -->
→ Cortecs liefert Kosten als Ganzzahl in Mikro-Euro – dokumentiert ist das nirgends. <!-- claim:C-059 -->
→ Anthropic sperrt die Kosten-API für Einzelorganisationen, selbst mit organisationsweitem Schlüssel. <!-- claim:C-087 -->

Und selbstkritisch: Unser eigener Preiskatalog hatte die richtigen Preise, aber drei der gemessenen Modelle fehlten. <!-- claim:C-077 -->

Teil 3 unserer Serie „Was ein LLM-Aufruf wirklich kostet".

👉 [Link zum Artikel]

#KI #LLM #APIKosten #Controlling
