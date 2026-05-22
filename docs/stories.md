### US-06: Audio-Report generieren
**Als** Nutzer  
**möchte ich** den Report als MP3 erhalten  
**damit** ich ihn unterwegs hören kann.

- **Estimate:** 1h
- **Abhängigkeit:** US-02
- **Definition of Done:** MP3 Datei unter reports/ gespeichert, Länge > 0 bytes

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-06-01 | Connect OpenAI TTS | 30min | US-02 | API call returns audio stream |
| US-06-02 | Save MP3 to reports/ | 15min | US-06-01 | File exists with correct naming |
| US-06-03 | Handle TTS errors | 15min | US-06-01 | Fallback logged if TTS fails |

---

### US-07: Report per Mail versenden
**Als** Nutzer  
**möchte ich** den Report automatisch per E-Mail erhalten  
**damit** ich nichts manuell herunterladen muss.

- **Estimate:** 1h  
- **Abhängigkeit:** US-02, US-06  
- **Definition of Done:** E-Mail mit Report-Text und MP3-Anhang erfolgreich zugestellt

| Task ID | Task | Estimate | Depends On | Definition of Done |
|---------|------|----------|------------|--------------------|
| US-07-01 | Connect Resend API | 30min | - | Test email delivered successfully |
| US-07-02 | Attach MP3 | 20min | US-06, US-07-01 | Email contains audio attachment |
| US-07-03 | Handle send errors | 10min | US-07-01 | Exceptions caught, error logged |