import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not NEWSAPI_KEY or not OPENAI_API_KEY:
    raise ValueError("Fehler: NEWSAPI_KEY oder OPENAI_API_KEY nicht in .env gesetzt!")


# --- Step 1: Fetch articles from NewsAPI (last 7 days) ---
def fetch_dena_articles():
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": "dena Energiewende",
            "from": week_ago,
            "language": "de",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": NEWSAPI_KEY,
        },
    )

    if response.status_code != 200:
        raise Exception(f"NewsAPI Fehler: {response.status_code} - {response.text}")

    articles = response.json().get("articles", [])

    if not articles:
        raise Exception("Keine Artikel gefunden.")

    print(f"{len(articles)} Artikel gefunden.")
    return articles


# --- Step 2: Format articles for prompt ---
def format_articles(articles):
    formatted = []
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Kein Titel")
        description = article.get("description", "Keine Beschreibung")
        published = article.get("publishedAt", "")[:10]
        source = article.get("source", {}).get("name", "Unbekannt")
        formatted.append(f"{i}. [{published}] {title} (Quelle: {source})\n   {description}")
    return "\n\n".join(formatted)


# --- Step 3: Generate report with OpenAI via LangChain ---
def generate_report(articles_text):
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=OPENAI_API_KEY,
        temperature=0.3,
    )

    prompt = f"""
Du bist ein Energiewende-Analyst. Basierend auf den folgenden aktuellen Artikeln der letzten 7 Tage,
erstelle einen strukturierten deutschen Report über die Deutsche Energie-Agentur (dena) und die Energiewende.

ARTIKEL:
{articles_text}

Erstelle einen Report mit folgender Struktur:

# dena Weekly Report – {datetime.now().strftime("%d.%m.%Y")}

## Zusammenfassung
(2-3 Sätze zu den wichtigsten Entwicklungen der Woche)

## Aktuelle Themen
(3-5 Kernthemen mit je 2-3 Sätzen)

## Trends & Ausblick
(Was entwickelt sich gerade, was ist zu erwarten?)

## Quellen
(Liste der verwendeten Artikel)

Schreibe präzise, sachlich und auf Deutsch.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


# --- Step 4: Save report as .md file ---
def save_report(report_text):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/dena_report_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report gespeichert: {filename}")
    return filename


# --- Main ---
def run_agent():
    print("Agent gestartet...")

    print("Schritt 1: Artikel abrufen...")
    articles = fetch_dena_articles()

    print("Schritt 2: Artikel formatieren...")
    articles_text = format_articles(articles)

    print("Schritt 3: Report generieren...")
    report = generate_report(articles_text)

    print("Schritt 4: Report speichern...")
    filename = save_report(report)

    print(f"\nFertig! Report: {filename}")
    print("\n--- REPORT VORSCHAU ---")
    print(report[:500] + "...")


if __name__ == "__main__":
    run_agent()
