# Finance — Doctoral Knowledge Index

## Quick Lookup

| Subtopic | Best Source | URL |
|----------|-------------|-----|
| Macroeconomic data | FRED | https://fred.stlouisfed.org/ |
| Academic papers | SSRN Finance | https://www.ssrn.com/index.cfm/en/Finance/ |
| SEC filings | EDGAR | https://www.sec.gov/cgi-bin/browse-edgar |
| Options pricing | OptionMetrics | https://optionmetrics.com/ |
| Equity data | Yahoo Finance | https://finance.yahoo.com/ |
| Fixed income | SIFMA | https://www.sifma.org/resources/research/ |
| Central bank research | BIS | https://www.bis.org/research/ |
| Risk models | RiskMetrics | https://www.msci.com/riskmetrics |

## Free Data Sources & APIs

### Macroeconomic Data
- **FRED (Federal Reserve Economic Data)** — https://fred.stlouisfed.org/
  800,000+ time series. GDP, inflation, unemployment, rates, etc.
  API: https://fred.stlouisfed.org/docs/api/fred/
  Python: `pip install fredapi`

- **World Bank Open Data** — https://data.worldbank.org/
  Development indicators for 200+ countries. Free API.
  Python: `pip install wbdata`

- **IMF Data** — https://www.imf.org/en/Data
  WEO, IFS, BOPS. CSV downloads and JSON API.

- **OECD.stat** — https://stats.oecd.org/
  Economic statistics for OECD members. Free API available.

- **BEA (Bureau of Economic Analysis)** — https://www.bea.gov/data
  US GDP, national accounts. API: https://apps.bea.gov/api/

- **BLS (Bureau of Labor Statistics)** — https://www.bls.gov/developers/
  CPI, PPI, employment. Free API.

### Market Data
- **Yahoo Finance** — https://finance.yahoo.com/
  `yfinance` Python library: `pip install yfinance`
  Real-time + historical prices, options chains, fundamentals.

- **Alpha Vantage** — https://www.alphavantage.co/
  Free tier: 25 requests/day. Equities, forex, crypto, indicators.

- **Quandl / NASDAQ Data Link** — https://data.nasdaq.com/
  Free datasets include Fed data; premium for equity fundamentals.

- **SEC EDGAR** — https://www.sec.gov/cgi-bin/browse-edgar
  All public company filings. Full-text search.
  EDGAR API: https://efts.sec.gov/LATEST/search-index/

- **WRDS (Wharton Research)** — https://wrds-www.wharton.upenn.edu/
  CRSP, Compustat, OptionMetrics. Institutional access required.

### Fixed Income & Derivatives
- **SIFMA** — https://www.sifma.org/resources/research/
  Bond market data, statistics, issuance data.

- **FINRA TRACE** — https://www.finra.org/investors/learn-to-invest/types-investments/bonds/bond-data
  Corporate bond transaction reporting.

- **CME Group** — https://www.cmegroup.com/market-data/
  Futures/options settlement prices. Some free historical data.

## Academic Research

### Preprints & Working Papers
- **SSRN Finance** — https://www.ssrn.com/index.cfm/en/Finance/
  Working papers from top researchers. Pre-publication.

- **NBER Working Papers** — https://www.nber.org/papers
  National Bureau of Economic Research. Macro, finance, labor.

- **BIS Working Papers** — https://www.bis.org/publ/work.htm
  Bank for International Settlements research. Free.

- **Fed Reserve Research** — https://www.federalreserve.gov/pubs/feds/
  FEDS (Finance & Economics Discussion Series). Free.

### Peer-Reviewed Journals
- **Journal of Finance** — https://afajof.org/journal-of-finance/
- **Review of Financial Studies** — https://academic.oup.com/rfs
- **Journal of Financial Economics** — https://www.sciencedirect.com/journal/journal-of-financial-economics
- **Journal of Portfolio Management** — https://jpm.iijournals.com/
- **Journal of Financial and Quantitative Analysis** — https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis

## Quantitative Finance

### Textbooks
- **Hull** — Options, Futures, and Other Derivatives (10th ed)
  The derivatives bible. Every quant has read this.
- **Shreve** — Stochastic Calculus for Finance (2 vols)
  Mathematical finance. Ito calculus, Black-Scholes, term structure.
- **Glasserman** — Monte Carlo Methods in Financial Engineering
- **Brigo & Mercurio** — Interest Rate Models (Theory and Practice)
- **Gatheral** — The Volatility Surface
- **Bouchaud & Potters** — Theory of Financial Risk (econophysics perspective)

### Computational Finance
- **QuantLib** — https://www.quantlib.org/
  Open source C++/Python library for quant finance.
- **PyPortfolioOpt** — https://pyportfolioopt.readthedocs.io/
  Portfolio optimization (Markowitz, Black-Litterman, etc.)
- **Zipline** — https://github.com/quantopian/zipline
  Algorithmic trading backtester (Python).
- **Backtrader** — https://www.backtrader.com/
  Python backtesting framework.

## CFA & Professional Resources
- **CFA Institute Research** — https://www.cfainstitute.org/en/research
  Research Foundation free publications. High quality.
- **CFA Curriculum** (free extracts) — https://www.cfainstitute.org/en/programs/cfa/curriculum

## Risk & Regulation
- **Basel Committee Documents** — https://www.bis.org/bcbs/publications.htm
- **IOSCO** — https://www.iosco.org/library/pubdocs/
- **FSB (Financial Stability Board)** — https://www.fsb.org/publications/

## Python Finance Stack

```python
# Core libraries
import yfinance as yf          # Market data
import fredapi                  # FRED macro data
import pandas_datareader as pdr # Multiple sources
import quantstats as qs         # Performance analytics
from scipy.stats import norm    # Stats

# Fetch stock data
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="5y")
info = ticker.info  # Fundamentals

# FRED data
from fredapi import Fred
fred = Fred(api_key='your_key')
gdp = fred.get_series('GDP')
fed_rate = fred.get_series('DFF')
```
