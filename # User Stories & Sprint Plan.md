# User Stories & Sprint Plan

## User Stories

### US-01: Artikel abrufen
**Als** Nutzer  
**möchte ich** aktuelle Artikel über dena der letzten 7 Tage abrufen  
**damit** der Report immer aktuell ist.

- **Estimate:** 2h
- **Abhängigkeit:** NewsAPI Key
- **Definition of Done:** API gibt min. 1 Artikel zurück, Fehler werden abgefangen

---

### US-02: Report generieren
**Als** Nutzer  
**möchte ich** einen strukturierten deutschen Report aus den Artikeln erhalten  
**damit** ich die Themen schnell überblicken kann.

- **Estimate:** 2h
- **Abhängigkeit:** US-01, OpenAI Key
- **Definition of Done:** Report enthält Zusammenfassung, Themen und Ausblick

---

### US-03: Report speichern
**Als** Nutzer  
**möchte ich** den Report als .md Datei gespeichert haben  
**damit** ich ihn später nachlesen kann.

- **Estimate:** 30min
- **Abhängigkeit:** US-02
- **Definition of Done:** Datei existiert unter reports/dena_report_DATUM.md

---

### US-04: Fehlerbehandlung
**Als** Nutzer  
**möchte ich** klare Fehlermeldungen erhalten  
**damit** ich weiß, wenn die API nicht erreichbar ist.

- **Estimate:** 1h
- **Abhängigkeit:** US-01, US-02
- **Definition of Done:** Bei API-Fehler wird Exception mit Beschreibung geworfen

---

### US-05: Dokumentation
**Als** Entwickler  
**möchte ich** eine klare README mit Setup-Anleitung  
**damit** das Projekt reproduzierbar ist.

- **Estimate:** 1h
- **Abhängigkeit:** alle anderen Stories
- **Definition of Done:** README enthält Setup, Ausführung und Projektstruktur

---

## Sprint Plan

| Tag | Tasks | Status |
|-----|-------|--------|
| Tag 1 | Repo setup, API Keys, US-05 Start | ✅ |
| Tag 2 | US-01: NewsAPI Integration | ✅ |
| Tag 3 | US-02: OpenAI Report-Generierung | ✅ |
| Tag 4 | US-03: Speichern, US-04: Fehlerbehandlung | ✅ |
| Tag 5 | Tests, 2-3 Sample Reports, Dokumentation | ✅ |