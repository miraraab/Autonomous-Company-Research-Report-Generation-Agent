# User Stories & Sprint Plan

## User Stories

### US-01: Artikel abrufen
**Als** Nutzer  
**möchte ich** aktuelle Artikel über dena der letzten 7 Tage abrufen  
**damit** der Report immer aktuell ist.

- **Estimate:** 2h
- **Abhängigkeit:** NewsAPI Key
- **Definition of Done:** API gibt min. 1 Artikel zurück, Fehler werden abgefangen

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-01-01 | Configure .env | 15min | - | .env file created with NEWSAPI_KEY |
| US-01-02 | Connect NewsAPI | 45min | US-01-01 | fetch_newsapi_articles() function returns articles |
| US-01-03 | Validate response | 30min | US-01-02 | Response structure verified, min 1 article returned |
| US-01-04 | Handle errors | 30min | US-01-02 | Exceptions caught and logged appropriately |

---

### US-02: Report generieren
**Als** Nutzer  
**möchte ich** einen strukturierten deutschen Report aus den Artikeln erhalten  
**damit** ich die Themen schnell überblicken kann.

- **Estimate:** 2h
- **Abhängigkeit:** US-01, OpenAI Key
- **Definition of Done:** Report enthält Zusammenfassung, Themen und Ausblick

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-02-01 | Connect Tagesschau RSS | 45min | - | fetch_tagesschau_articles() function returns feed entries |
| US-02-02 | Merge sources | 30min | US-02-01 | merge_and_deduplicate() combines NewsAPI and Tagesschau articles |
| US-02-03 | Deduplicate | 30min | US-02-02 | Duplicate articles removed by title similarity |
| US-02-04 | Format for prompt | 30min | US-02-03 | format_articles_for_prompt() creates structured text block |

---

### US-03: Report speichern
**Als** Nutzer  
**möchte ich** den Report als .md Datei gespeichert haben  
**damit** ich ihn später nachlesen kann.

- **Estimate:** 30min
- **Abhängigkeit:** US-02
- **Definition of Done:** Datei existiert unter reports/dena_report_DATUM.md

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-03-01 | Write system prompt | 30min | - | System message defined for energy analyst role |
| US-03-02 | Write user prompt | 30min | - | User message structured with article input and report format |
| US-03-03 | Call LangChain | 45min | US-03-01, US-03-02 | generate_report() invokes LangChain ChatOpenAI successfully |
| US-03-04 | Validate output | 30min | US-03-03 | Report contains all required sections with valid German text |

---

### US-04: Fehlerbehandlung
**Als** Nutzer  
**möchte ich** klare Fehlermeldungen erhalten  
**damit** ich weiß, wenn die API nicht erreichbar ist.

- **Estimate:** 1h
- **Abhängigkeit:** US-01, US-02
- **Definition of Done:** Bei API-Fehler wird Exception mit Beschreibung geworfen

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-04-01 | Save to reports/ | 15min | - | reports directory created and accessible |
| US-04-02 | Name file with date | 20min | US-04-01 | Filename format: reports/{topic}_report_YYYY-MM-DD.md |
| US-04-03 | Verify file exists | 15min | US-04-02 | File successfully written to disk with content |
| US-04-04 | Handle write errors | 10min | US-04-02 | IO errors caught and reported appropriately |

---

### US-05: Dokumentation
**Als** Entwickler  
**möchte ich** eine klare README mit Setup-Anleitung  
**damit** das Projekt reproduzierbar ist.

- **Estimate:** 1h
- **Abhängigkeit:** alle anderen Stories
- **Definition of Done:** README enthält Setup, Ausführung und Projektstruktur

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-05-01 | Write README setup section | 20min | - | Setup instructions with virtual env, dependencies, API keys |
| US-05-02 | Write run instructions | 20min | - | Clear steps to execute the agent with example output |
| US-05-03 | Add .env.example | 15min | - | .env.example template with all required variables |
| US-05-04 | Add project structure | 15min | - | File tree and directory descriptions documented |

---

## Sprint Plan

| Tag | Tasks | Status |
|-----|-------|--------|
| Tag 1 | Repo setup, API Keys, US-05 Start | ✅ |
| Tag 2 | US-01: NewsAPI Integration | ✅ |
| Tag 3 | US-02: OpenAI Report-Generierung | ✅ |
| Tag 4 | US-03: Speichern, US-04: Fehlerbehandlung | ✅ |
| Tag 5 | Tests, 2-3 Sample Reports, Dokumentation | ✅ |