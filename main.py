"""
Autonomous Energy Research & Report Generation Agent
=====================================================
Industry: Energy / Energiewende
APIs:     1) NewsAPI       - Current news articles (last 7 days)
          2) Tagesschau RSS - Public broadcaster feed (no key required)
LLM:      OpenAI GPT-4o-mini via LangChain
Output:   Structured Markdown report saved to reports/
"""

import os
import time
import logging
import argparse
import base64
import yaml
import feedparser
import requests
import openai
import resend
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
load_dotenv(override=True)

NEWSAPI_KEY    = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

NEWSAPI_URL    = "https://newsapi.org/v2/everything"
TAGESSCHAU_RSS = "https://www.tagesschau.de/xml/rss2/"

MAX_RETRIES    = 3
RETRY_BACKOFF  = 2   # seconds (doubles each attempt)
MAX_ARTICLES   = 8   # per source


# ── Validation ─────────────────────────────────────────────────────────────────
def validate_env() -> None:
    """Fail fast if required environment variables are missing."""
    missing = [k for k in ("NEWSAPI_KEY", "OPENAI_API_KEY") if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing)}\n"
            "Copy .env.example to .env and fill in your API keys."
        )


def load_industry(key: str) -> dict:
    """Load industry config from industries.yaml."""
    with open("industries.yaml", "r", encoding="utf-8") as f:
        industries = yaml.safe_load(f)
    if key not in industries:
        available = ", ".join(industries.keys())
        raise ValueError(f"Unknown industry '{key}'. Available: {available}")
    cfg = industries[key]
    log.info("Industry loaded: %s", cfg["label"])
    return cfg


# ── Retry helper ───────────────────────────────────────────────────────────────
def fetch_with_retry(url: str, params: dict, source_name: str) -> requests.Response:
    """
    GET request with exponential-backoff retry.
    Raises on permanent failure after MAX_RETRIES attempts.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response
            if response.status_code == 429:
                wait = RETRY_BACKOFF ** attempt
                log.warning(
                    "%s – rate limited (429). Retry %d/%d in %ds …",
                    source_name, attempt, MAX_RETRIES, wait,
                )
                time.sleep(wait)
            elif response.status_code >= 500:
                wait = RETRY_BACKOFF ** attempt
                log.warning(
                    "%s – server error %d. Retry %d/%d in %ds …",
                    source_name, response.status_code, attempt, MAX_RETRIES, wait,
                )
                time.sleep(wait)
            else:
                # 4xx client error – no point retrying
                raise ValueError(
                    f"{source_name} returned {response.status_code}: {response.text[:200]}"
                )
        except requests.exceptions.Timeout:
            wait = RETRY_BACKOFF ** attempt
            log.warning("%s – timeout. Retry %d/%d in %ds …", source_name, attempt, MAX_RETRIES, wait)
            time.sleep(wait)
        except requests.exceptions.ConnectionError as exc:
            raise ConnectionError(f"{source_name} – connection failed: {exc}") from exc

    raise RuntimeError(f"{source_name} – all {MAX_RETRIES} retries exhausted.")


# ── Article filtering ──────────────────────────────────────────────────────────
def is_relevant(article: dict, keywords: list[str]) -> bool:
    """Check if any keyword word appears in the combined title + description text."""
    combined_text = (article.get("title", "") + " " + article.get("description", "")).lower()
    # Split keywords into individual words for flexible matching
    words = []
    for kw in keywords:
        words.extend(kw.lower().split())
    return any(word in combined_text for word in words)


# ── Tool 1: NewsAPI ────────────────────────────────────────────────────────────
def fetch_newsapi_articles(query: str = '"erneuerbare Energien" OR "Energiewende" OR "dena"') -> list[dict]:
    """
    Fetch recent German-language news articles via NewsAPI.
    Returns a list of normalised article dicts.
    """
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    log.info("Tool 1 – NewsAPI: querying '%s' …", query)
    response = fetch_with_retry(
        url=NEWSAPI_URL,
        params={
            "q":        query,
            "from":     week_ago,
            "language": "de",
            "sortBy":   "publishedAt",
            "pageSize": MAX_ARTICLES,
            "apiKey":   NEWSAPI_KEY,
        },
        source_name="NewsAPI",
    )

    raw_articles = response.json().get("articles", [])
    if not raw_articles:
        log.warning("NewsAPI – no articles found for query '%s'.", query)
        return []

    articles = [
        {
            "source":      art.get("source", {}).get("name", "Unknown"),
            "title":       art.get("title", ""),
            "description": art.get("description", ""),
            "published":   art.get("publishedAt", "")[:10],
            "url":         art.get("url", ""),
            "origin":      "NewsAPI",
        }
        for art in raw_articles
        if art.get("title") and "[Removed]" not in art.get("title", "")
    ]

    keywords = ["Energie", "Solar", "Wind", "Klimaschutz", "dena"]  # Broad energy-related keywords
    articles = [art for art in articles if is_relevant(art, keywords)]

    log.info("NewsAPI – %d articles retrieved.", len(articles))
    return articles


# ── Tool 2: Tagesschau RSS ─────────────────────────────────────────────────────
def fetch_tagesschau_articles(keywords: list = None) -> list[dict]:
    """
    Fetch relevant entries from the Tagesschau public RSS feed.
    Filters by keywords (case-insensitive). No API key required.
    """
    log.info("Tool 2 – Tagesschau RSS: fetching feed …")
    feed = feedparser.parse(TAGESSCHAU_RSS)

    if feed.bozo and not feed.entries:
        log.error("Tagesschau RSS – feed parse error: %s", feed.bozo_exception)
        return []

    keywords = keywords or ["Energie"]
    matched = []
    for entry in feed.entries:
        title   = entry.get("title", "")
        summary = entry.get("summary", "")
        if any(kw.lower() in title.lower() or kw.lower() in summary.lower() for kw in keywords):
            matched.append({
                "source":      "Tagesschau",
                "title":       title,
                "description": summary,
                "published":   entry.get("published", "")[:10],
                "url":         entry.get("link", ""),
                "origin":      "Tagesschau RSS",
            })
        if len(matched) >= MAX_ARTICLES:
            break

    if not matched:
        log.warning("Tagesschau RSS – no entries matched keywords %s.", keywords)

    log.info("Tagesschau RSS – %d articles retrieved.", len(matched))
    return matched


# ── Data merging & formatting ──────────────────────────────────────────────────
def merge_and_deduplicate(source_a: list[dict], source_b: list[dict]) -> list[dict]:
    """Merge two article lists and remove duplicates by title similarity."""
    combined = source_a + source_b
    seen_titles: set[str] = set()
    unique = []
    for art in combined:
        key = art["title"].lower()[:60]
        if key not in seen_titles:
            seen_titles.add(key)
            unique.append(art)
    log.info("Merged sources – %d unique articles total.", len(unique))
    return unique


def format_articles_for_prompt(articles: list[dict]) -> str:
    """Convert article list to a structured text block for the LLM prompt."""
    lines = []
    for i, art in enumerate(articles, 1):
        lines.append(
            f"{i}. [{art['published']}] {art['title']}\n"
            f"   Quelle: {art['source']} ({art['origin']})\n"
            f"   {art['description']}\n"
            f"   URL: {art['url']}"
        )
    return "\n\n".join(lines)


# ── Tool 3: LangChain / OpenAI report generation ───────────────────────────────
def generate_report(articles_text: str, topic: str = "dena & Energiewende") -> str:
    """
    Use LangChain + GPT-4o-mini to synthesise a structured German report
    from the provided article summaries.
    """
    log.info("LangChain – generating report …")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0.3,
        max_tokens=1500,
    )

    system_msg = SystemMessage(content=(
        "Du bist ein erfahrener Energiewende-Analyst. "
        "Du analysierst aktuelle Medienberichte sachlich und präzise. "
        "Deine Reports sind klar strukturiert, faktenbasiert und auf Deutsch verfasst. "
        "Erfinde keine Informationen – stütze dich ausschließlich auf die gegebenen Artikel."
    ))

    user_msg = HumanMessage(content=f"""
Analysiere die folgenden aktuellen Artikel über das Thema „{topic}" und erstelle einen strukturierten Wochenreport.

ARTIKEL (Quellen: NewsAPI & Tagesschau RSS):
{articles_text}

Erstelle einen Report mit exakt dieser Struktur:

# Energiewende Weekly Report – {datetime.now().strftime("%d.%m.%Y")}
**Thema:** {topic}
**Quellen:** NewsAPI, Tagesschau RSS
**Artikel analysiert:** {articles_text.count(chr(10)+chr(10)) + 1}

---

## 1. Zusammenfassung
(3–4 Sätze: Die wichtigsten Entwicklungen der Woche auf einen Blick)

## 2. Kernthemen der Woche
(3–5 Themen. Für jedes Thema: Titel, 2–3 Sätze Analyse, Relevanz)

## 3. Trends & Marktentwicklung
(Was sind aktuelle Richtungen, politische Signale oder technologische Entwicklungen?)

## 4. Risiken & Herausforderungen
(Welche Hindernisse oder Kontroversen tauchen in den Berichten auf?)

## 5. Ausblick
(Was ist in den nächsten Wochen zu erwarten?)

## 6. Quellenverzeichnis
(Nummerierte Liste aller verwendeten Artikel mit Quelle und Datum)

Schreibe präzise, sachlich und professionell.
""")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke([system_msg, user_msg])
            log.info("LangChain – report generated successfully.")
            return response.content
        except Exception as exc:
            wait = RETRY_BACKOFF ** attempt
            log.warning("LLM error (attempt %d/%d): %s. Retrying in %ds …", attempt, MAX_RETRIES, exc, wait)
            time.sleep(wait)

    raise RuntimeError(f"LLM report generation failed after {MAX_RETRIES} attempts.")


# ── Output ─────────────────────────────────────────────────────────────────────
def save_report(report_text: str, topic: str = "energiewende") -> str:
    """Save the report as a Markdown file in the reports/ directory."""
    os.makedirs("reports", exist_ok=True)
    slug = topic.lower().replace(" ", "_").replace("/", "-")[:30]
    filename = f"reports/{slug}_report_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)
    log.info("Report saved → %s", filename)
    return filename

def generate_audio(report_text: str, report_path: str) -> str:
    """Convert report text to MP3 audio via OpenAI TTS."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    # Trim to ~4000 chars (approx 7 minutes spoken)
    audio_input = report_text[:4000]
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="onyx",
        input=audio_input,
        speed=1.25,
    )
    
    audio_path = report_path.replace(".md", ".mp3")
    response.stream_to_file(audio_path)
    log.info("Audio saved → %s", audio_path)
    return audio_path


def send_email(audio_path: str, report_topic: str) -> None:
    """Send audio report via Resend."""
    resend.api_key = os.getenv("RESEND_API_KEY", "").strip()
    log.info("Resend Key geladen: %s...", resend.api_key[:8])
    recipient = os.getenv("RECIPIENT_EMAIL")
    
    if not resend.api_key or not recipient:
        log.warning("Resend not configured – skipping email.")
        return
    
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": recipient,
        "subject": f"dena Audio Report – {datetime.now().strftime('%d.%m.%Y')} – {report_topic}",
        "html": f"<p>Dein wöchentlicher dena Report als Audio-Datei.</p><p>Thema: {report_topic}</p>",
        "attachments": [{
            "filename": audio_path.split("/")[-1],
            "content": base64.b64encode(audio_bytes).decode("utf-8"),
        }],
    })
    log.info("Email sent → %s", recipient)



# ── Orchestration ──────────────────────────────────────────────────────────────
def run_agent(
    newsapi_query: str = '"erneuerbare Energien" OR "Energiewende" OR "dena"',
    rss_keywords: list = None,
    report_topic: str = "dena & Energiewende",
) -> str:
    """
    Full autonomous pipeline:
      1. Validate environment
      2. Fetch articles from NewsAPI       (Tool 1)
      3. Fetch articles from Tagesschau RSS (Tool 2)
      4. Merge & deduplicate results
      5. Generate structured report via LangChain (Tool 3 / LLM)
      6. Save report to disk
    Returns the path to the saved report file.
    """
    log.info("═══ Agent started ═══")

    # Step 0 – environment check
    validate_env()

    # Step 1 – Tool 1: NewsAPI
    newsapi_articles = fetch_newsapi_articles(query=newsapi_query)

    # Step 2 – Tool 2: Tagesschau RSS
    rss_keywords = rss_keywords or ["Energie"]
    tagesschau_articles = fetch_tagesschau_articles(keywords=rss_keywords)

    # Step 3 – merge
    if not newsapi_articles and not tagesschau_articles:
        raise RuntimeError("No articles retrieved from either source. Cannot generate report.")

    all_articles = merge_and_deduplicate(newsapi_articles, tagesschau_articles)
    
    # Agent decision: evaluate source quality
    if len(all_articles) < 3:
        log.warning("Agent: insufficient articles (%d). Retrying NewsAPI with broader query...", len(all_articles))
        fallback_articles = fetch_newsapi_articles(query="Energie OR Klimaschutz OR Deutschland")
        all_articles = merge_and_deduplicate(all_articles, fallback_articles)

    if len(all_articles) == 0:
        raise RuntimeError("Agent: no articles from any source after fallback. Aborting.")

    log.info("Agent decision: proceeding with %d articles from %d sources",
             len(all_articles),
             len(set(a['origin'] for a in all_articles)))

    articles_text = format_articles_for_prompt(all_articles)

    # Step 4 – report generation
    report = generate_report(articles_text, topic=report_topic)

    # Agent decision: validate report completeness after generation
    required_sections = ["Zusammenfassung", "Kernthemen", "Trends", "Risiken", "Ausblick"]
    missing = [s for s in required_sections if s not in report]
    if missing:
        log.warning("Agent: report incomplete, missing sections: %s. Regenerating...", missing)
        report = generate_report(articles_text, topic=report_topic)

    # Step 5 – save
    filepath = save_report(report, topic=report_topic)

    # Step 6 – audio generation
    audio_path = generate_audio(report, filepath)

    # Step 7 – email delivery
    send_email(audio_path, report_topic)

    log.info("═══ Agent finished → %s ═══", filepath)

    # Preview
    print("\n" + "─" * 60)
    print(report[:600] + "\n…")
    print("─" * 60)

    return filepath


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Energy Research Agent")
    parser.add_argument(
        "--industry",
        default="energiewende",
        help="Industry key from industries.yaml (default: energiewende)"
    )
    args = parser.parse_args()
    cfg = load_industry(args.industry)
    run_agent(
        newsapi_query=cfg["newsapi_query"],
        rss_keywords=cfg["rss_keywords"],
        report_topic=cfg["report_topic"],
    )