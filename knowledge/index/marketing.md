# Marketing — Doctoral Knowledge Index

## Quick Lookup

| Topic | Best Source | URL |
|-------|-------------|-----|
| Academic research | SSRN Marketing | https://www.ssrn.com/index.cfm/en/Marketing/ |
| Practitioner strategy | HBR Marketing | https://hbr.org/topic/marketing |
| Consumer behavior | Journal of Marketing Research | https://journals.ama.org/journal/jmr |
| Digital analytics | Think With Google | https://www.thinkwithgoogle.com/ |
| Market sizing | Statista | https://www.statista.com/ |
| Competitive intel | SimilarWeb | https://www.similarweb.com/ |
| Ad performance | Nielsen | https://www.nielsen.com/insights/ |
| SEO research | Ahrefs/SEMrush | https://ahrefs.com/ |

## Academic Journals

### Marketing-Specific (Top-Tier)
- **Journal of Marketing** — https://journals.ama.org/journal/jm
  Top ranked. American Marketing Association. Seminal theory.
- **Journal of Marketing Research** — https://journals.ama.org/journal/jmr
  Quantitative methods, experiments, consumer studies.
- **Journal of Consumer Research** — https://academic.oup.com/jcr
  Consumer psychology, qualitative + quantitative.
- **Marketing Science** — https://pubsonline.informs.org/journal/mksc
  Quantitative, modeling-heavy. Analytics and econometrics.
- **Journal of the Academy of Marketing Science** — JAMS

### Open Access
- **Journal of Business Research** (Elsevier, some OA)
- **Frontiers in Marketing** (new OA journal)
- **Marketing Letters** — Springer

### Practitioner-Academic Bridge
- **Harvard Business Review (Marketing)** — https://hbr.org/topic/marketing
- **MIT Sloan Management Review (Marketing)** — https://sloanreview.mit.edu/
- **Journal of Digital & Social Media Marketing** — https://www.henrystewartpublications.com/jdsmm

## Preprints & Working Papers
- **SSRN Marketing** — https://www.ssrn.com/index.cfm/en/Marketing/
- **AMA DocSIG** — Academic working papers
- **NBER (Consumer/Marketing)** — https://www.nber.org/papers?q=marketing

## Data Sources

### Consumer Behavior Data
- **Think With Google** — https://www.thinkwithgoogle.com/
  Consumer intent data, search trends, YouTube insights. Free.
- **Google Trends** — https://trends.google.com/
  Search interest over time. Free API via `pytrends`.
- **Pew Research Center** — https://www.pewresearch.org/
  Consumer attitudes, demographics, media. Free.
- **Nielsen Consumer Insights** — https://www.nielsen.com/insights/
  Some free content. Full reports paid.

### Market Research Data
- **Statista** — https://www.statista.com/
  Charts from 22,500+ sources. Limited free; full subscription.
- **eMarketer/Insider Intelligence** — https://www.emarketer.com/
  Digital marketing spend forecasts.
- **Forrester Research** — Technology marketing research.
- **Gartner** — Magic Quadrant reports.
- **IBISWorld** — Industry market sizing reports.

### Digital Marketing Data
- **SimilarWeb** — https://www.similarweb.com/
  Web traffic, competitive analysis. Limited free tier.
- **SEMrush** — https://www.semrush.com/
  SEO, PPC, content marketing data. Limited free.
- **Ahrefs** — https://ahrefs.com/
  Backlinks, keyword research, site audit.
- **Moz** — https://moz.com/ SEO metrics. Free basic tier.

### Social Media Analytics
- **Brandwatch** — https://www.brandwatch.com/ (social listening)
- **Sprout Social Insights** — https://sproutsocial.com/insights/ (free reports)
- **Buffer Analyze** — https://buffer.com/ (social data)
- **Socialbakers/Emplifi** — social media benchmarks

### Ad & Email Benchmarks
- **Mailchimp Benchmarks** — https://mailchimp.com/resources/email-marketing-benchmarks/
  Email open rates, CTRs by industry.
- **WordStream Benchmarks** — https://www.wordstream.com/blog/ws/2016/02/29/google-adwords-industry-benchmarks
  Google/FB Ads CTR, CPC, CVR by industry.
- **Facebook Ads Benchmarks** — from multiple free reports

## Frameworks & Canonical References

### Core Marketing Theory
- **Kotler & Keller** — Marketing Management (16th ed) — the MBA standard
- **Aaker** — Managing Brand Equity — brand strategy bible
- **Porter** — Competitive Advantage — positioning fundamentals
- **Cialdini** — Influence: The Psychology of Persuasion — behavior fundamentals
- **Godin** — Permission Marketing / This Is Marketing

### Digital Marketing
- **Chaffey & Ellis-Chadwick** — Digital Marketing (7th ed)
- **Vaynerchuk** — Jab, Jab, Jab, Right Hook (social media)
- **Ryan & Jones** — Understanding Digital Marketing

### Analytics & Quantitative
- **Eisenberg** — Always Be Testing (CRO)
- **Kaushik** — Web Analytics 2.0 (free PDF available)
- **Provost & Fawcett** — Data Science for Business (causal marketing analytics)

## SEO & Content Resources
- **Google Search Central** — https://developers.google.com/search/docs
  Official SEO documentation.
- **Moz Beginner's Guide to SEO** — https://moz.com/beginners-guide-to-seo
- **Backlinko** — https://backlinko.com/ (Brian Dean)
- **Search Engine Journal** — https://www.searchenginejournal.com/
- **Content Marketing Institute** — https://contentmarketinginstitute.com/

## APIs for Marketing Data

```python
# Google Trends via pytrends
from pytrends.request import TrendReq
pt = TrendReq()
pt.build_payload(["ChatGPT", "Bard"], timeframe="today 12-m")
interest = pt.interest_over_time()

# SimilarWeb (unofficial)
# Use web_fetch + parsing for public data

# Facebook Ads Library (no key, public)
import requests
resp = requests.get(
    "https://graph.facebook.com/v19.0/ads_archive",
    params={"access_token": "TOKEN", "ad_reached_countries": "US", "search_terms": "AI"}
)

# Google Ads API (requires OAuth)
from google.ads.googleads.client import GoogleAdsClient

# Twitter/X API v2
import tweepy
client = tweepy.Client(bearer_token="TOKEN")
tweets = client.search_recent_tweets(query="brand mention", max_results=100)
```

## Attribution & Measurement
- **Google Analytics 4 (GA4)** — https://developers.google.com/analytics/devguides/reporting/data/v1
- **Mixpanel API** — https://developer.mixpanel.com/
- **Amplitude Analytics** — https://developers.amplitude.com/
- **Segment CDP** — https://segment.com/docs/
- **Marketing Mix Modeling (MMM)**: Facebook's Robyn (R), Google's Meridian (Python)
  Robyn: https://github.com/facebookexperimental/Robyn
  Meridian: https://github.com/google/meridian
