# News & Current Events — Knowledge Index

## Quick Lookup

| Need | Best Source | URL |
|------|-------------|-----|
| General API (multi-source) | NewsAPI.org | https://newsapi.org/ |
| Real-time search | GDELT | https://api.gdeltproject.org/ |
| Wire service | AP News | https://developer.ap.org/ |
| Quality international | Guardian | https://open-platform.theguardian.com/ |
| Tech/startup news | Hacker News API | https://hacker-news.firebaseio.com/ |
| Financial news | Reuters | https://www.reuters.com/ |
| Government/official | GovInfo | https://api.govinfo.gov/ |
| Social signals | Reddit API | https://www.reddit.com/dev/api/ |

## News APIs (Programmatic Access)

### Free / Freemium
- **NewsAPI.org** — https://newsapi.org/
  100 requests/day free. 80,000+ sources. English + 14 languages.
  Endpoints: /v2/top-headlines, /v2/everything (search back 1 month free)
  Python: `pip install newsapi-python`

- **GDELT Project** — https://www.gdeltproject.org/
  Completely free. Real-time event detection from global news.
  API: https://api.gdeltproject.org/api/v2/doc/doc
  Also has full-text search across 152 languages.

- **Guardian Open Platform** — https://open-platform.theguardian.com/
  Free tier: 500 requests/day. Full article text available.
  High-quality journalism, well-tagged.

- **Hacker News (Algolia API)** — https://hn.algolia.com/api
  Tech news, discussion. Completely free, no key needed.
  Firebase API: https://hacker-news.firebaseio.com/v0/

- **Reddit API** — https://www.reddit.com/dev/api/
  Social news aggregation. 60 req/min free (OAuth).
  Python: `pip install praw`

- **GNews.io** — https://gnews.io/
  Free: 100 requests/day. Google News aggregator alternative.

### Premium (Institutional)
- **Bloomberg API** — https://www.bloomberg.com/professional/product/apis/
- **Dow Jones DNA** — https://developer.dowjones.com/
- **LexisNexis** — https://www.lexisnexis.com/en-us/professional/academic/
- **Refinitiv Eikon** — https://developers.refinitiv.com/

## Primary Source News (Direct)

### International Wire Services
- **Reuters** — https://www.reuters.com/ (most trusted wire)
- **AP (Associated Press)** — https://developer.ap.org/ (API available)
- **AFP (Agence France-Presse)** — https://www.afp.com/en/agency/afp-news-agency
- **Bloomberg** — https://www.bloomberg.com/

### Quality Journalism
- **The Guardian** — https://www.theguardian.com/ (progressive, strong international coverage)
- **BBC News** — https://www.bbc.com/news (reliable international)
- **The Economist** — https://www.economist.com/ (subscription, authoritative)
- **Financial Times** — https://www.ft.com/ (global finance/economics/politics)
- **NYT** — https://www.nytimes.com/ (US, international)
- **Washington Post** — https://www.washingtonpost.com/
- **Der Spiegel** (Germany) — https://www.spiegel.de/international/
- **Le Monde** (France) — https://www.lemonde.fr/en/

### Specialized by Domain
- **Tech:** TechCrunch, Ars Technica, The Verge, Wired
- **Science:** Nature News, Science News, New Scientist, PhysOrg
- **Finance/Business:** WSJ, Bloomberg, FT, Fortune
- **Policy:** Politico, The Hill, Vox (policy), ProPublica
- **Global South:** Al Jazeera, South China Morning Post, The Hindu

## Fact-Checking & Verification
- **Reuters Fact Check** — https://www.reuters.com/fact-check/
- **AP Fact Check** — https://apnews.com/hub/ap-fact-check
- **Snopes** — https://www.snopes.com/
- **PolitiFact** — https://www.politifact.com/
- **Full Fact (UK)** — https://fullfact.org/

## News Data & Research Tools
- **Media Bias/Fact Check** — https://mediabiasfactcheck.com/
  Source reliability ratings.
- **AllSides** — https://www.allsides.com/
  Multi-perspective news display.
- **Mediacloud** — https://mediacloud.org/
  Academic media analysis platform.
- **Global Database of Events, Language, and Tone (GDELT)**
  https://www.gdeltproject.org/ — 500+ million events from 1979-present.

## Search Strategies for News

### Current events (last 30 days): web_search
Best: site:reuters.com OR site:apnews.com OR site:bbc.com [topic]

### Historical news: GDELT or NewsAPI /everything with date range

### Institutional/government news: GovInfo.gov API
https://api.govinfo.gov/ (Congressional Record, Federal Register, etc.)

### Academic news research:
- **ProQuest Historical Newspapers** (via library)
- **Newspaper Archive** — https://newspaperarchive.com/
- **Chronicling America** (US 1770-1963, free) — https://chroniclingamerica.loc.gov/

## Python Quickstart

```python
import requests

# NewsAPI
resp = requests.get(
    "https://newsapi.org/v2/everything",
    params={"q": "artificial intelligence", "language": "en", "pageSize": 10},
    headers={"X-Api-Key": "YOUR_KEY"}
)
articles = resp.json()["articles"]

# Guardian API
resp = requests.get(
    "https://content.guardianapis.com/search",
    params={"q": "climate change", "show-fields": "bodyText", "api-key": "YOUR_KEY"}
)

# Hacker News (no key needed)
top_ids = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()
story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{top_ids[0]}.json").json()
```
