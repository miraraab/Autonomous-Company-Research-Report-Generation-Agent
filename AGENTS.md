AGENTS.md
Agent: dena Weekly Report Agent
Aufgabe
Sammle wöchentlich aktuelle Nachrichten über die Deutsche Energie-Agentur (dena) und die Energiewende, und erstelle daraus einen strukturierten deutschen Report.
Tools

NewsAPI – Rufe Artikel der letzten 7 Tage ab (Query: "dena Energiewende", Sprache: Deutsch)
Tagesschau RSS – Public broadcaster feed, no API key required
OpenAI (GPT-4o-mini via LangChain) – Generiere einen strukturierten Report aus den Artikeln

Workflow

Load industry config from industries.yaml
Artikel der letzten 7 Tage von NewsAPI abrufen
Artikel formatieren und zusammenführen
Report mit OpenAI generieren (Zusammenfassung, Themen, Ausblick)
Report als .md Datei speichern

Output-Format
Markdown-Report mit:

Datum
Zusammenfassung (2-3 Sätze)
Aktuelle Themen (3-5 Punkte)
Trends & Ausblick
Quellen

Fehlerbehandlung

Leere API-Antwort → Exception mit Hinweis
HTTP-Fehler → Status-Code und Meldung ausgeben
Kein API Key → dotenv wirft Fehler beim Start

Industries

energiewende – dena & Energiewende (default)
gebaeude – Gebäude & Räume umbauen
energie_erzeugen – Energie erzeugen & verteilen
digitalisierung – Digitalisierung & Innovation
wirtschaft – Wirtschaft transformieren