# Psychology — Doctoral Knowledge Index

## Quick Lookup

| Subtopic | Best Source | URL |
|----------|-------------|-----|
| All psychology literature | PsycINFO | https://www.apa.org/pubs/databases/psycinfo |
| Biomedical + psych | PubMed | https://pubmed.ncbi.nlm.nih.gov/ |
| Open-access papers | PsyArXiv | https://psyarxiv.com/ |
| Neuroscience | NeuroVault | https://neurovault.org/ |
| Philosophy of mind | SEP | https://plato.stanford.edu/ |
| Replication database | OSF | https://osf.io/ |
| Clinical guidelines | APA | https://www.apa.org/practice/guidelines |
| DSM/diagnostic | APA Online | https://www.appi.org/ |

## Primary Literature Sources

### Open Access / Free Databases
- **PubMed / MEDLINE** — https://pubmed.ncbi.nlm.nih.gov/
  25M+ biomedical citations. Full text via PubMed Central (PMC).
  API: https://www.ncbi.nlm.nih.gov/books/NBK25497/

- **PubMed Central (PMC)** — https://www.ncbi.nlm.nih.gov/pmc/
  Full-text articles only. 9M+ free.

- **PsyArXiv** — https://psyarxiv.com/
  Preprints for psychological science. Open Science Framework.

- **OSF (Open Science Framework)** — https://osf.io/
  Preregistrations, data, code. Replication studies.
  Replication Markets: https://www.replicationmarkets.com/

- **Frontiers in Psychology** — https://www.frontiersin.org/journals/psychology
  Fully open access. High volume.

- **PLOS ONE** — https://journals.plos.org/plosone/
  Open access multidisciplinary. Psychology/cognitive science.

- **PsycNET (APA)** — https://psycnet.apa.org/
  Authoritative but mostly subscription. Some free abstracts.

### Preprint Servers
- **PsyArXiv** — https://psyarxiv.com/ (psychology)
- **bioRxiv** — https://www.biorxiv.org/ (neuroscience papers)
- **MetaArXiv** — https://osf.io/preprints/metaarxiv (meta-analysis/methodology)
- **SocArXiv** — https://osf.io/preprints/socarxiv (social psychology, sociology)

## Key Journals by Subdiscipline

### Cognitive Psychology
- **Psychological Review** — https://www.apa.org/pubs/journals/rev (theory papers)
- **Cognition** — https://www.sciencedirect.com/journal/cognition
- **Journal of Experimental Psychology: General** — APA
- **Psychological Science** — https://journals.sagepub.com/home/pss

### Social & Personality
- **Journal of Personality and Social Psychology** — https://www.apa.org/pubs/journals/psp
- **Personality and Social Psychology Bulletin** — SPSP
- **Social Psychological and Personality Science** — https://journals.sagepub.com/home/spp

### Clinical & Abnormal
- **Journal of Abnormal Psychology** — APA
- **Journal of Consulting and Clinical Psychology** — APA
- **Behaviour Research and Therapy** — Elsevier
- **Clinical Psychology Review** — Elsevier

### Developmental
- **Developmental Psychology** — APA
- **Child Development** — SRCD
- **Developmental Science** — Wiley

### Neuroscience
- **Neuron** — https://www.cell.com/neuron/home
- **Journal of Neuroscience** — https://www.jneurosci.org/
- **Nature Neuroscience** — https://www.nature.com/neuro
- **eLife (Neuroscience)** — https://elifesciences.org/ (open access)

## Databases & Tools

### Neuroimaging Data
- **NeuroVault** — https://neurovault.org/
  Shared fMRI/PET statistical maps. Open.
- **OpenNeuro** — https://openneuro.org/
  MRI/EEG datasets. BIDS format. Open.
- **HCP (Human Connectome Project)** — https://www.humanconnectome.org/
  Structural + functional MRI at high resolution.

### Behavioral Data
- **ICPSR (Inter-university Consortium)** — https://www.icpsr.umich.edu/
  Social science data archive. Free with registration.
- **UK Biobank** — https://www.ukbiobank.ac.uk/
  500,000 participant cohort. Application required.
- **GSS (General Social Survey)** — https://gss.norc.org/
  American social attitudes since 1972. Free.

### Cognitive Tests & Batteries
- **NIH Toolbox** — https://nihtoolbox.org/
- **Cognitron** — https://cognitron.co.uk/
- **CANTAB** — https://www.cambridgecognition.com/cantab/

## Reference Works

### Clinical
- **DSM-5-TR** — APA, definitive diagnostic manual
- **ICD-11 Mental Disorders** (WHO, free) — https://icd.who.int/
- **PDR (Physicians' Desk Reference)** — prescribing info

### Academic Texts
- **Kahneman** — Thinking, Fast and Slow
- **Gray & Bjorklund** — Psychology (textbook)
- **Nolen-Hoeksema** — Abnormal Psychology
- **Gazzaniga, Heatherton & Halpern** — Psychological Science
- **Kandel et al.** — Principles of Neural Science (neuroscience bible)
- **Damasio** — Descartes' Error (emotion + cognition)

### Philosophy of Mind
- **Stanford Encyclopedia of Philosophy** — https://plato.stanford.edu/
  Free, peer-reviewed, scholarly. Topics: consciousness, intentionality, mental causation.
- **Internet Encyclopedia of Philosophy** — https://iep.utm.edu/

## Research Methods & Statistics
- **Open Stats Lab** — https://sites.trinity.edu/osl/
  R and JASP exercises using published datasets.
- **JASP (free statistical software)** — https://jasp-stats.org/
- **G*Power (power analysis)** — https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower
- **Meta-analysis tools:** RevMan (Cochrane), metafor (R)

## Python for Psychology Research

```python
# PubMed search
from Bio import Entrez
Entrez.email = "your@email.com"
handle = Entrez.esearch(db="pubmed", term="working memory[Title] AND 2023:2024[DP]")
record = Entrez.read(handle)
ids = record["IdList"]

# PsyArXiv preprints via OSF API
import requests
resp = requests.get("https://api.osf.io/v2/preprints/?filter[provider]=psyarxiv&filter[date_created][gte]=2024-01-01")

# Statistical analysis
import pingouin as pg  # ANOVA, correlations, power analysis
import statsmodels.api as sm
from scipy import stats
```
