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
- gpt-4o-mini (cost-efficient, strong structured output quality)

## APIs Used
- NewsAPI: fetches German-language articles (last 7 days)
- Tagesschau RSS: https://www.tagesschau.de/xml/rss2/ (no key required)

## Usage
Called in main.py inside generate_report(). 
Input comes from format_articles_for_prompt().
Output is saved via save_report() to reports/.


## Decision Layer
Before calling the LLM, the agent validates:
- Minimum 3 articles available (fallback query if not met)
- At least 1 source active

After generation, the agent validates:
- All 5 required sections present: Zusammenfassung, Kernthemen, Trends, Risiken, Ausblick
- Regenerates once if any section is missing

## Audio Output
- Model: OpenAI TTS tts-1
- Voice: onyx
- Speed: 1.25x
- Format: MP3
- Input: first 4000 characters of report