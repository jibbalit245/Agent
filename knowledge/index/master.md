# Master Knowledge Index
> Doctoral-level reference index across 12 domains. Use `knowledge_search` with
> `platform="index"` or search by domain keyword to find relevant source links.
> Then use `web_fetch` to pull the actual content.

## Domain Index

| Domain | File | Core Subtopics |
|--------|------|----------------|
| Computer Science / Code | `index/code.md` | Algorithms, systems, ML theory, PLT, databases |
| Physics | `index/physics.md` | QM, GR, statistical mechanics, condensed matter |
| Chemistry | `index/chemistry.md` | Organic, inorganic, physical, analytical, computational |
| Finance | `index/finance.md` | Quantitative, macro, markets, corporate, risk |
| News & Current Events | `index/news.md` | APIs, aggregators, primary sources, data feeds |
| Engineering | `index/engineering.md` | Mechanical, electrical, civil, materials, systems |
| Business | `index/business.md` | Strategy, operations, entrepreneurship, management |
| Psychology | `index/psychology.md` | Cognitive, behavioral, social, clinical, neuroscience |
| Marketing | `index/marketing.md` | Consumer behavior, digital, brand, analytics, strategy |
| Web Design & UI/UX | `index/webdesign.md` | UX research, design systems, accessibility, patterns |
| Mathematics | `index/math.md` | Analysis, algebra, topology, number theory, probability |
| Geometry | `index/geometry.md` | Euclidean, differential, algebraic, computational, applied |

## Quick Cross-Domain Lookups

### For empirical data
- Scientific: PubMed, arXiv, Semantic Scholar
- Economic: FRED, World Bank, IMF, OECD
- Social: ICPSR, GSS, Pew Research

### For formal knowledge
- Math/CS proofs: Lean4 Mathlib, Coq, ProofWiki
- Encyclopedic: Stanford Encyclopedia of Philosophy, Wikipedia (start point only)
- Terminology: MathWorld, NIST, ISO standards

### For current research
- Preprints: arXiv.org (CS/Math/Physics/Bio), SSRN (Econ/Finance/Social)
- Peer-reviewed: PubMed, Semantic Scholar, Unpaywall (open access layer)
- AI/ML specifically: Papers With Code, Hugging Face Papers, Arxiv Sanity

### For programmatic access
- Scholarly APIs: Semantic Scholar API, CrossRef, PubMed Entrez
- Data APIs: FRED API, World Bank API, Census Bureau API
- News APIs: NewsAPI.org, Guardian API, GDELT API

## Search Strategy

1. `knowledge_search` with domain keyword → get relevant index file
2. Read index file → identify best source URL for the subtopic
3. `web_fetch` the URL → extract specific information
4. Cross-reference with `council_consult` for complex or contested topics
