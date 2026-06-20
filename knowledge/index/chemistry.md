# Chemistry — Doctoral Knowledge Index

## Quick Lookup

| Subtopic | Best Source | URL |
|----------|-------------|-----|
| Chemical properties & data | NIST WebBook | https://webbook.nist.gov/ |
| Compound search | PubChem | https://pubchem.ncbi.nlm.nih.gov/ |
| Spectral data | SDBS | https://sdbs.db.aist.go.jp/ |
| Organic reactions | Organic Chemistry Portal | https://www.organic-chemistry.org/ |
| Reaction mechanisms | ChemTube3D | https://www.chemtube3d.com/ |
| Chemical literature | ACS Publications | https://pubs.acs.org/ |
| Preprints | ChemRxiv | https://chemrxiv.org/ |
| Crystallography | CCDC | https://www.ccdc.cam.ac.uk/ |

## Chemical Databases (Free Access)

### Property & Structure Databases
- **NIST Chemistry WebBook** — https://webbook.nist.gov/
  Thermochemical (ΔHf°, S°, Cp), IR/MS/UV spectra, phase change, reaction data.
  API: https://webbook.nist.gov/chemistry/name-ser/ (name lookup)

- **PubChem** — https://pubchem.ncbi.nlm.nih.gov/
  100M+ compounds. Structure, properties, bioactivity, literature links.
  API: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest

- **ChemSpider** — https://www.chemspider.com/
  RSC structure database. 100M+ structures. InChI/SMILES search.

- **ChEBI** (Biological molecules) — https://www.ebi.ac.uk/chebi/
  Curated chemical database for biological and medicinal chemistry.

- **ChemBL** (Drug-like molecules) — https://www.ebi.ac.uk/chembl/
  Drug discovery data. Target-compound bioactivity.

- **CCDC** (Crystal structures) — https://www.ccdc.cam.ac.uk/
  Cambridge Structural Database. 1M+ crystal structures. Some free access.

### Spectral Databases
- **SDBS** (Japan AIST) — https://sdbs.db.aist.go.jp/
  Free: NMR (1H, 13C), IR, MS, ESR spectra. 35,000+ compounds.

- **NIST WebBook Spectra** — https://webbook.nist.gov/chemistry/name-ser/
  IR, MS, UV/Vis, NMR reference spectra.

- **MassBank** (EU) — https://massbank.eu/MassBank/
  High-resolution MS spectra. Open access.

- **NMR Predict** — https://www.nmrdb.org/
  Predict 1H/13C NMR spectra from structure.

## Reaction Databases & Synthesis Tools

- **Organic Chemistry Portal** — https://www.organic-chemistry.org/
  Named reactions, reagents, protective groups. Doctoral-level reference.

- **NameRXN** (IUPAC reaction names) — https://www.namedrxns.com/

- **Reaxys** — https://www.reaxys.com/ (subscription)
  200M+ reactions. Best commercial reaction database.

- **SciFinder-n** — https://scifinder-n.cas.org/ (subscription via institution)
  Literature, reactions, substances. CAS registry.

- **Pistachio** (NextMove) — https://www.nextmovesoftware.com/ (commercial)
  Extracted reactions from patent literature.

- **ChemTube3D** — https://www.chemtube3d.com/
  Interactive 3D mechanisms. Pericyclic, organometallic, enzyme reactions.

- **CCCBDB** (NIST Computational) — https://cccbdb.nist.gov/
  Computed and experimental molecular properties. Benchmark data.

## Peer-Reviewed Journals

### Open Access
- **ACS Central Science** — https://pubs.acs.org/journal/acscii (fully OA)
- **Chemical Science** (RSC) — https://pubs.rsc.org/en/journals/journalissues/sc
- **Nature Chemistry** — https://www.nature.com/nchem/
- **ChemRxiv** (preprints) — https://chemrxiv.org/
- **PLOS Chemistry** — new OA journal from PLOS

### Subscription (available via institutional access)
- **Journal of the American Chemical Society (JACS)** — https://pubs.acs.org/journal/jacsat
- **Angewandte Chemie** — https://onlinelibrary.wiley.com/journal/15213773
- **Journal of Organic Chemistry** — https://pubs.acs.org/journal/joceah
- **Journal of Physical Chemistry A/B/C** — https://pubs.acs.org/loi/jpcafh
- **Accounts of Chemical Research** — https://pubs.acs.org/journal/achre4

## Computational Chemistry Tools

- **Gaussian** — https://gaussian.com/ (commercial QM)
- **ORCA** — https://www.orcasoftware.de/ (free for academics, powerful DFT)
- **Psi4** — https://psicode.org/ (free, Python API)
- **RDKit** — https://www.rdkit.org/ (free, cheminformatics in Python)
- **DeepChem** — https://deepchem.io/ (ML for chemistry)
- **OpenBabel** — https://openbabel.org/ (file format conversion, descriptors)
- **ASE** (Atomic Simulation Environment) — https://wiki.fysik.dtu.dk/ase/

## Reference Textbooks

### Organic Chemistry
- **March's Advanced Organic Chemistry** (7th ed) — Gold standard reference
- **Clayden** — Organic Chemistry (best mechanistic treatment)
- **Kürti & Czakó** — Strategic Applications of Named Reactions (750 reactions)

### Physical Chemistry
- **Atkins & de Paula** — Physical Chemistry (9th/10th ed)
- **McQuarrie** — Physical Chemistry: A Molecular Approach
- **Levine** — Physical Chemistry

### Inorganic Chemistry
- **Housecroft & Sharpe** — Inorganic Chemistry
- **Miessler, Fischer & Tarr** — Inorganic Chemistry (symmetry/group theory focus)
- **Greenwood & Earnshaw** — Chemistry of the Elements (encyclopedic)

### Analytical Chemistry
- **Skoog, West, Holler & Crouch** — Principles of Instrumental Analysis
- **Harris** — Quantitative Chemical Analysis

## Cheminformatics & APIs

```python
# PubChem REST API
import requests
cid = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/cids/JSON").json()
props = requests.get(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,IUPACName/JSON").json()

# RDKit (python)
from rdkit import Chem
from rdkit.Chem import Descriptors
mol = Chem.MolFromSmiles('c1ccccc1')
mw = Descriptors.ExactMolWt(mol)
```
