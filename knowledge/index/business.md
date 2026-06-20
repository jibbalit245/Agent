# Business — Doctoral Knowledge Index

## Quick Lookup

| Topic | Best Source | URL |
|-------|-------------|-----|
| Strategy cases | HBR | https://hbr.org/ |
| Academic research | SSRN Management | https://www.ssrn.com/index.cfm/en/Management/ |
| Macro analysis | McKinsey Global Institute | https://www.mckinsey.com/mgi |
| Startup data | Crunchbase | https://www.crunchbase.com/ |
| Industry analysis | IBISWorld | https://www.ibisworld.com/ |
| Executive education | Wharton Knowledge | https://knowledge.wharton.upenn.edu/ |
| Business law | Westlaw/LexisNexis | institutional access |
| Competitive intel | Owler / SimilarWeb | https://www.owler.com/ |

## Practitioner Journals & Magazines

### Open Access / Free
- **Harvard Business Review** — https://hbr.org/
  Case studies, frameworks, leadership. 3 free articles/month.

- **MIT Sloan Management Review** — https://sloanreview.mit.edu/
  Technology, innovation, strategy. Some free.

- **McKinsey Insights** — https://www.mckinsey.com/insights
  Industry analysis, reports. Mostly free.

- **BCG Henderson Institute** — https://www.bcg.com/publications
  Strategy, digital transformation. Free.

- **Deloitte Insights** — https://www2.deloitte.com/us/en/insights.html
  Industry and function reports. Free.

- **Wharton Knowledge** — https://knowledge.wharton.upenn.edu/
  Research summaries from Wharton faculty. Free.

- **Stanford Social Innovation Review** — https://ssir.org/
  Nonprofit, philanthropy, social enterprise. Open access.

- **Strategy+Business** (PwC) — https://www.strategy-business.com/
  Thoughtful strategy writing. Free.

### Peer-Reviewed Academic (Subscription)
- **Strategic Management Journal** — https://onlinelibrary.wiley.com/journal/10970266
- **Academy of Management Review** — https://journals.aom.org/journal/amr
- **Academy of Management Journal** — https://journals.aom.org/journal/amj
- **Journal of Business Venturing** — https://www.sciencedirect.com/journal/journal-of-business-venturing
- **Administrative Science Quarterly** — https://journals.sagepub.com/home/asq
- **Harvard Business Review** (academic citations acceptable)

## Working Papers & Preprints

- **SSRN Management** — https://www.ssrn.com/index.cfm/en/Management/
  Working papers. Free.

- **NBER** — https://www.nber.org/papers
  Economics/business research. 90 days after release: free.

- **IZA Discussion Papers** — https://www.iza.org/publications/dp
  Labor economics and HR. Free.

- **World Bank Research** — https://openknowledge.worldbank.org/
  Development, trade, policy. Open access.

## Market Research & Industry Data

### Free
- **Statista (limited)** — https://www.statista.com/ (some free charts)
- **Pew Research** — https://www.pewresearch.org/ (social/consumer data)
- **CB Insights (limited)** — https://www.cbinsights.com/research/
- **Crunchbase (basic)** — https://www.crunchbase.com/
- **SEC EDGAR** — https://www.sec.gov/edgar/ (public company data)
- **Fortune 500** — https://fortune.com/ranking/fortune500/
- **Inc. 5000** — https://www.inc.com/inc5000/

### Subscription (Institutional)
- **IBISWorld** — Industry reports with market size, forecasts
- **Mintel** — Consumer insights, market reports
- **Forrester Research** — Technology/business strategy
- **Gartner** — IT and technology market research
- **Bloomberg Intelligence** — Industry analysis

## Business Frameworks & Case Libraries

### Case Studies
- **Harvard Business School Cases** — https://www.hbs.edu/faculty/research/pages/case-collection.aspx
  Gold standard business cases. Small fee per case.
- **MIT Sloan Cases** — https://mitsloan.mit.edu/LearningEdge/
- **Stanford GSB Cases** — https://www.gsb.stanford.edu/experience/learning/cases

### Strategy Frameworks
- Porter's Five Forces, Value Chain
- Blue Ocean Strategy — https://www.blueoceanstrategy.com/
- Jobs-to-be-Done: https://jobs-to-be-done.com/
- OKRs: https://www.whatmatters.com/
- Business Model Canvas: https://www.strategyzer.com/

## Startup & Venture Resources
- **Y Combinator Library** — https://www.ycombinator.com/library
  Essays on building startups. Free.
- **Paul Graham Essays** — https://paulgraham.com/articles.html
  Foundational startup thinking.
- **First Round Review** — https://review.firstround.com/
  Operator-focused management writing.
- **Andreessen Horowitz (a16z)** — https://a16z.com/
  VC perspective on tech trends.
- **Sequoia Arc** — https://www.sequoiacap.com/articles/

## Business Law & Compliance
- **Cornell LII** (US law, free) — https://www.law.cornell.edu/
- **SEC Regulations** — https://www.sec.gov/divisions/corpfin/
- **US Code** — https://uscode.house.gov/
- **GDPR Text** — https://gdpr-info.eu/
- **CPRA/CCPA** — https://oag.ca.gov/privacy/ccpa

## Textbook References

### Strategy
- **Porter** — Competitive Strategy / Competitive Advantage
- **Rumelt** — Good Strategy/Bad Strategy
- **Christensen** — The Innovator's Dilemma

### Operations
- **Chase, Aquilano & Jacobs** — Operations Management
- **Chopra & Meindl** — Supply Chain Management
- **Nahmias** — Production and Operations Analysis

### Finance for Business
- **Brealey, Myers & Allen** — Principles of Corporate Finance
- **Damodaran** — Corporate Finance (free materials: https://pages.stern.nyu.edu/~adamodar/)

### Leadership & Organization
- **Mintzberg** — The Rise and Fall of Strategic Planning
- **Collins** — Good to Great
- **Edmondson** — The Fearless Organization

## Data & Analytics for Business

```python
# Company data via Yahoo Finance
import yfinance as yf
company = yf.Ticker("MSFT")
financials = company.financials
balance_sheet = company.balance_sheet
earnings = company.earnings

# SEC EDGAR full-text search
import requests
resp = requests.get(
    "https://efts.sec.gov/LATEST/search-index/efts/v1/hits?q=%22artificial+intelligence%22&dateRange=custom&startdt=2024-01-01",
    headers={"User-Agent": "Research agent@email.com"}
)
```
