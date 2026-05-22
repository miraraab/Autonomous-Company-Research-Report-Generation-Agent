# AGENTS.md

## Project Specification

**Goal:** Build an autonomous agent that monitors dena-relevant energy topics weekly,
synthesises findings from multiple news sources, and delivers a structured German
report as Markdown and audio to a defined recipient.

**Trigger:** Manual CLI command or scheduled execution
**Input:** Industry topic key (e.g. "energiewende", "gebaeude")
**Output:** Markdown report + MP3 audio file + email delivery
**Autonomy:** Fully autonomous after trigger — no human intervention required

---

## Agent: dena Weekly Report Agent

## Task
Autonomously research energy topics, synthesize findings from multiple sources,
generate a structured German report, convert it to audio, and deliver it by email.
Run once per week per industry topic with a single CLI command.

## Tools
1. **NewsAPI** – Fetch articles from the last 7 days via keyword query
2. **Tagesschau RSS** – Fetch public broadcaster feed (no API key required)
3. **LangChain + GPT-4o-mini** – Synthesise articles into structured report
4. **OpenAI TTS** – Convert report to MP3 audio (speed 1.25x, voice onyx)
5. **Resend API** – Deliver audio report by email

## Industries
Configured in `industries.yaml`. Available topics:
- `energiewende` – dena & Energiewende (default)
- `gebaeude` – Gebäude & Räume umbauen
- `energie_erzeugen` – Energie erzeugen & verteilen
- `digitalisierung` – Digitalisierung & Innovation
- `wirtschaft` – Wirtschaft transformieren

## Workflow
1. Load industry config from industries.yaml
2. Fetch articles from NewsAPI (keyword query, last 7 days)
3. Fetch articles from Tagesschau RSS (keyword filter)
4. Agent decision: evaluate article count and source diversity
   - < 3 articles → retry NewsAPI with broader fallback query
   - 0 articles → abort with RuntimeError
5. Merge and deduplicate articles from both sources
6. Generate structured German report via LangChain + GPT-4o-mini
7. Validate report completeness (all 5 required sections present)
   - Missing sections → regenerate report once
8. Save report as Markdown to reports/
9. Generate MP3 audio via OpenAI TTS
10. Send email with audio attachment via Resend

## Output Format
Markdown report with:
- Date and topic header
- Zusammenfassung (summary)
- Kernthemen (key topics)
- Trends & Marktentwicklung
- Risiken & Herausforderungen
- Ausblick (outlook)
- Quellenverzeichnis (sources)

## Error Handling
- Missing API keys → fail fast with EnvironmentError on startup
- API errors → exponential backoff retry (3 attempts)
- 0 articles → RuntimeError with clear message
- LLM errors → retry up to 3 times
- Email errors → logged as warning, agent continues
## Agent-Delegated Tasks

The following tasks were delegated to the agent during development:

| Task | Tool Used | Definition of Done |
|------|-----------|-------------------|
| Generate weekly energy report | LangChain + GPT-4o-mini | Report contains all 5 sections, valid German |
| Fetch and filter news articles | NewsAPI + Tagesschau RSS | Min. 1 article per source returned |
| Convert report to audio | OpenAI TTS | MP3 file saved, size > 0 bytes |
| Deliver report by email | Resend API | Email received at RECIPIENT_EMAIL |

Human review step: Report quality checked manually before activating Railway Cron schedule.