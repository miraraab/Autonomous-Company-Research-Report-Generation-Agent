# Skill: Report Generation

## Beschreibung
Generiert einen strukturierten deutschen Energiewende-Report aus rohen Nachrichtenartikeln via OpenAI.

## Input
- Liste von Artikeln (Titel, Beschreibung, Datum, Quelle)

## Output
- Markdown-Report mit Datum, Zusammenfassung, Themen, Ausblick, Quellen

## Prompt-Strategie
- Rolle: "Du bist ein Energiewende-Analyst"
- Temperatur: 0.3 (sachlich, wenig Variation)
- Sprache: Deutsch
- Struktur vorgegeben via Markdown-Headings im Prompt

## Modell
- gpt-3.5-turbo (kostengünstig, ausreichend für strukturierte Reports)