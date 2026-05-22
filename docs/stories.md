# docs/stories.md — dena Weekly Report Agent
# Agile Planning Artifacts

---

## Sprint Overview

| Story | Title | Estimate | Priority |
|-------|-------|----------|----------|
| US-01 | Industry Config & Agent Trigger | 1h | Core |
| US-02 | News Research via NewsAPI | 1.5h | Core |
| US-03 | News Research via Tagesschau RSS | 1h | Core |
| US-04 | Report Synthesis & Generation | 2h | Core |
| US-05 | Error Handling & Validation | 1.5h | Core |
| US-06 | Audio Report via TTS | 1h | Enhancement |
| US-07 | Report Delivery via Email | 1h | Enhancement |
| | **Total** | **9h** | |

---

## US-01: Industry Config & Agent Trigger

**As a** user  
**I want to** trigger the agent for a specific dena industry topic  
**so that** I receive a report relevant to my area of interest.

- **Estimate:** 1h
- **Dependencies:** none
- **Definition of Done:** Agent starts successfully via `python main.py --industry <key>`, loads the correct config from `industries.yaml`, and logs the selected topic

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-01-01 | Create `industries.yaml` with 5 dena topics | 20min | — | All 5 entries present with `label`, `newsapi_query`, `rss_keywords`, `rss_keyword_filter`, `report_topic` |
| US-01-02 | Parse CLI argument `--industry` in `main.py` | 20min | US-01-01 | Invalid key raises descriptive error; valid key loads correct config |
| US-01-03 | Validate required env variables on startup | 20min | — | Missing key raises descriptive error before any API call is made |

---

## US-02: News Research via NewsAPI

**As a** user  
**I want to** the agent to automatically fetch current dena-related articles from NewsAPI  
**so that** the report is based on verified, recent news from the last 7 days.

- **Estimate:** 1.5h
- **Dependencies:** US-01
- **Definition of Done:** Agent fetches ≥ 1 article from NewsAPI within the last 7 days for any configured industry, with retry logic active

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-02-01 | Integrate NewsAPI `/v2/everything` endpoint | 30min | US-01 | API call returns articles filtered by keyword and date range |
| US-02-02 | Filter results to last 7 days | 15min | US-02-01 | Articles outside the 7-day window are excluded |
| US-02-03 | Implement retry with broader query if < 3 articles returned | 30min | US-02-01 | Retry triggers automatically; result count logged before and after |
| US-02-04 | Abort with error if 0 articles after retry | 15min | US-02-03 | Exception raised with clear message; no further pipeline steps execute |

---

## US-03: News Research via Tagesschau RSS

**As a** user  
**I want to** the agent to supplement NewsAPI results with Tagesschau RSS articles  
**so that** the report includes German-language public broadcasting coverage without requiring an additional API key.

- **Estimate:** 1h
- **Dependencies:** US-01
- **Definition of Done:** Agent fetches and keyword-filters Tagesschau RSS articles; continues gracefully if feed is unreachable

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-03-01 | Parse Tagesschau RSS feed (`tagesschau.de/xml/rss2/`) | 30min | US-01 | Feed parsed and articles returned as list |
| US-03-02 | Apply keyword filter from `industries.yaml` | 15min | US-03-01 | Only articles matching configured keywords are included |
| US-03-03 | Merge and deduplicate with NewsAPI results | 15min | US-02-01, US-03-02 | Combined list contains no duplicate URLs or titles |

---

## US-04: Report Synthesis & Generation

**As a** user  
**I want to** receive a structured German-language report synthesized from the collected articles  
**so that** I can quickly understand the key developments in my selected dena topic.

- **Estimate:** 2h
- **Dependencies:** US-02, US-03
- **Definition of Done:** Report contains all 5 required sections, is saved as Markdown to `reports/`, and reflects content from at least 2 sources

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-04-01 | Format collected articles into structured prompt | 20min | US-02, US-03 | Prompt includes title, source, date, and summary per article |
| US-04-02 | Build LangChain chain with `SystemMessage` and `HumanMessage` | 30min | US-04-01 | LLM returns a response without error on first call |
| US-04-03 | Validate report contains all 5 sections: `Zusammenfassung`, `Kernthemen`, `Trends`, `Risiken`, `Ausblick` | 30min | US-04-02 | Validation passes or triggers regeneration automatically |
| US-04-04 | Save report as `reports/<topic>_report_YYYY-MM-DD.md` | 20min | US-04-03 | File exists at correct path with correct date in filename |
| US-04-05 | Justify LangChain over LangGraph in documentation | 20min | — | Architecture decision documented in README under "Design Decisions" |

---

## US-05: Error Handling & Validation

**As a** developer  
**I want to** the agent to handle API failures, missing data, and incomplete outputs gracefully  
**so that** the pipeline does not crash silently and failures are traceable.

- **Estimate:** 1.5h
- **Dependencies:** US-02, US-03, US-04
- **Definition of Done:** All defined error scenarios are handled without unhandled exceptions; all errors are logged with context

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-05-01 | Handle Tagesschau RSS unreachable (log warning, continue) | 20min | US-03 | Warning logged; pipeline continues with NewsAPI results only |
| US-05-02 | Handle LangChain timeout (retry once, then raise) | 20min | US-04-02 | One retry attempt logged; exception raised with message if retry fails |
| US-05-03 | Handle missing report sections (auto-regenerate) | 20min | US-04-03 | Regeneration triggered and logged; second attempt result accepted |
| US-05-04 | Handle missing env variables on startup | 15min | US-01-03 | Descriptive error names the missing variable; agent exits before any API call |
| US-05-05 | Log article count and source count after collection | 15min | US-02, US-03 | Log entry shows total articles, NewsAPI count, RSS count |

---

## US-06: Audio Report Generation

**As a** user  
**I want to** receive the report as an MP3 file  
**so that** I can listen to the weekly briefing on the go.

- **Estimate:** 1h
- **Dependencies:** US-04
- **Definition of Done:** MP3 file saved under `reports/` with correct filename, size > 10KB, voice `onyx` at speed `1.25x`

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-06-01 | Connect OpenAI TTS API with voice `onyx`, speed `1.25x` | 30min | US-04-04 | API returns audio stream without error |
| US-06-02 | Save MP3 as `reports/<topic>_report_YYYY-MM-DD.mp3` | 15min | US-06-01 | File exists at correct path, size > 10KB |
| US-06-03 | Handle TTS API errors | 15min | US-06-01 | Exception caught and logged; email step continues with text-only fallback |

---

## US-07: Report Delivery via Email

**As a** user  
**I want to** receive the report automatically by email every Monday  
**so that** I don't have to manually download or run anything.

- **Estimate:** 1h
- **Dependencies:** US-04, US-06
- **Definition of Done:** Email with Markdown report body and MP3 attachment delivered to `RECIPIENT_EMAIL`; Resend API returns HTTP 200

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-07-01 | Connect Resend API and send test email | 30min | — | Test email delivered; Resend returns HTTP 200 |
| US-07-02 | Attach MP3 to email | 20min | US-06-02, US-07-01 | Email received with audio attachment; attachment is playable |
| US-07-03 | Handle Resend delivery failure | 10min | US-07-01 | HTTP error status logged with code; no unhandled exception |

---

## Dependency Map

```
US-01 (Config & Trigger)
  ├── US-02 (NewsAPI)
  │     └── US-05 (Error Handling)
  ├── US-03 (Tagesschau RSS)
  │     └── US-05 (Error Handling)
  └── US-04 (Report Synthesis)
        ├── US-05 (Error Handling)
        ├── US-06 (Audio TTS)
        │     └── US-07 (Email Delivery)
        └── US-07 (Email Delivery)
```

---

## Deployment Story

**As a** user  
**I want to** the agent to run automatically every Monday at 06:30 CET without any manual action  
**so that** the weekly report arrives reliably without intervention.

- **Estimate:** 30min
- **Dependencies:** US-07
- **Definition of Done:** Railway Cron (`30 4 * * 1` UTC) triggers successfully; report and email delivered without manual execution

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-08-01 | Configure `railway.toml` with cron schedule | 15min | US-07 | Railway dashboard shows scheduled run at correct time |
| US-08-02 | Set all env variables in Railway Dashboard | 15min | US-01-03 | Agent runs successfully on Railway without local `.env` |