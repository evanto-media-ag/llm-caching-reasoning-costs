Ihr Systemprompt geht mit jedem API-Aufruf mit – und wird meist jedes Mal voll bezahlt.

Prompt Caching ändert das: Der Anbieter hält den unveränderten Anfang des Prompts vor, ein Treffer kostet nur noch 5–10 % des Input-Preises. Bei Claude Sonnet 5 sank unser 7 200-Token-Prompt so von 1,45 auf 0,15 Cent pro Aufruf.

Klingt nach einem Schalter. Ist es nicht. Wir haben Caching bei OpenAI, Anthropic, xAI, Gemini und Mistral mit denselben Prompts gemessen und jede API-Antwort archiviert.

Der überraschendste Befund: Ein Wechsel des Thinking-Levels hat bei OpenAI, xAI und Gemini den kompletten Cache gekostet. Bei Claude Sonnet 5.5 nicht. Wer den Effort pro Nachricht „intelligent" wählt, kann damit die ganze Ersparnis verspielen.

Außerdem:
→ Unter der Mindestgröße (512 bis 4 096 Tokens) wird still nicht gecacht – keine Fehlermeldung, nur ein Zähler, der auf 0 bleibt. 
→ Der 5-Minuten-Cache von Anthropic war nach 5,5 Minuten weg, der von OpenAI nicht. 
→ Grok 4.7 bringt in jeden Aufruf 1 152 eigene Prompt-Tokens mit. 

Teil 1 unserer Serie „Was ein LLM-Aufruf wirklich kostet" – mit Tabellen je Anbieter und dem .NET-Kniff, mit dem Claude den Cache über mehrere Gesprächszüge trifft. Den Überblick über alle Kostenhebel gibt der Auftaktartikel, verlinkt im Beitrag.

👉 https://evanto.de/de/blog/prompt-caching-im-vergleich

#KI #LLM #PromptCaching #APIKosten #dotnet
