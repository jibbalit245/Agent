# Engineering — Doctoral Knowledge Index

## Quick Lookup

| Discipline | Best Source | URL |
|------------|-------------|-----|
| Mechanical | ASME Digital Collection | https://asmedigitalcollection.asme.org/ |
| Electrical/Electronic | IEEE Xplore | https://ieeexplore.ieee.org/ |
| Civil/Structural | ASCE Library | https://ascelibrary.org/ |
| Materials properties | MatWeb | https://www.matweb.com/ |
| Engineering formulas | Engineering Toolbox | https://www.engineeringtoolbox.com/ |
| Standards | NIST | https://www.nist.gov/ |
| Aerospace/NASA | NTRS | https://ntrs.nasa.gov/ |
| Control systems | MathWorks Docs | https://www.mathworks.com/help/control/ |

## Technical Standards & Codes

### Standards Bodies (Free Access Where Noted)
- **NIST (National Institute of Standards & Technology)**
  https://www.nist.gov/
  Publications library: https://nvlpubs.nist.gov/
  Engineering Lab: https://www.nist.gov/el
  Free: FIPS, NIST SPs, technical notes

- **ISO Standards** — https://www.iso.org/standards.html
  Most require purchase. Preview available.

- **ASTM International** — https://www.astm.org/
  Material & testing standards. Subscription required.

- **ANSI** — https://www.ansi.org/
  American standards aggregator.

- **IEC (Electrical)** — https://www.iec.ch/

### Domain-Specific Codes
- **ASCE 7** (Structural loads) — through ASCE library
- **ACI 318** (Concrete) — through ACI
- **AISC** (Steel) — https://www.aisc.org/technical-resources/
- **NEC** (Electrical) — through NFPA

## Material Properties Databases

- **MatWeb** — https://www.matweb.com/
  100,000+ material datasheets. Free registration.
  Metals, plastics, ceramics, composites.

- **NIST Material Data** — https://www.nist.gov/mml
  Thermophysical properties, JANAF tables.

- **Matweb API** — https://www.matweb.com/api/ (limited free tier)

- **ASM Aerospace Specification Metals** — http://asm.matweb.com/
  Free material property tables.

- **CES EduPack / Granta** — https://www.ansys.com/products/materials/granta-edupack
  Gold standard materials database (institutional).

- **MMPDS** (Metallic Materials for Aerospace) — USAF publication

## Engineering Reference Sites

- **Engineering Toolbox** — https://www.engineeringtoolbox.com/
  Formulas, tables, unit conversions. Mechanical, thermal, fluid, electrical.

- **Engineering ToolKit** — https://www.engineeringtoolkit.com/

- **eFunda** — https://www.efunda.com/
  Formulas for mechanical, thermal, structural engineering.

- **The Engineering Index (Ei)** — via Elsevier's Compendex (institutional)

## Research Journals

### Open Access
- **Nature Engineering (Nature Portfolio)** — https://www.nature.com/subjects/engineering
- **Heliyon Engineering** — https://www.heliyon.com/ (Elsevier OA)
- **PLOS ONE** (engineering content) — https://journals.plos.org/plosone/

### High-Impact (Subscription/Institutional)
- **Nature** — ground-breaking engineering/materials
- **Science** — top-tier multidisciplinary
- **Advanced Materials** — Wiley
- **Nano Letters** — ACS
- **IEEE Transactions on...** (many subtopics) — https://ieeexplore.ieee.org/
- **ASME Journal of...** — https://asmedigitalcollection.asme.org/

### Preprints
- **arXiv Engineering** — https://arxiv.org/list/eess/recent (electrical/signal/systems)
- **SSRN** — some engineering papers
- **TechRxiv** (IEEE) — https://www.techrxiv.org/

## Simulation & CAE Tools

### FEA / FEM
- **OpenFOAM** (CFD, free) — https://openfoam.org/
- **FEniCS** (FEM, free/Python) — https://fenicsproject.org/
- **Calculix** (FEA, free) — http://www.calculix.de/
- **ANSYS Student** (free license) — https://www.ansys.com/academic/students

### CAD
- **FreeCAD** (free) — https://www.freecad.org/
- **OpenSCAD** (programmatic) — https://openscad.org/
- **CATIA/SolidWorks/NX** — industry standard, institutional

### Control Systems
- **MATLAB Control Toolbox** — https://www.mathworks.com/help/control/
- **Python-control** (free) — https://python-control.readthedocs.io/
- **Simulink** — block diagram simulation

### Electronics / EDA
- **KiCad** (free PCB design) — https://www.kicad.org/
- **LTspice** (free SPICE) — https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html
- **Qucs** (free circuit sim) — http://qucs.sourceforge.net/

## Aerospace & Government Technical Reports

- **NASA Technical Reports Server (NTRS)** — https://ntrs.nasa.gov/
  Free access to NASA research. 1 million+ documents.

- **DTIC (Defense Technical Info)** — https://www.dtic.mil/
  DoD technical reports. Some public, some restricted.

- **FAA Research** — https://www.faa.gov/data_research/research/

- **DOE Office of Scientific Information** — https://www.osti.gov/
  DOE-funded research. Much is free.

## Textbook References by Discipline

### Mechanical
- **Shigley's Mechanical Engineering Design** — machine design bible
- **White** — Fluid Mechanics
- **Cengel & Boles** — Thermodynamics: An Engineering Approach
- **Beer & Johnston** — Mechanics of Materials
- **Hibbeler** — Engineering Mechanics (Statics/Dynamics)

### Electrical/Electronics
- **Sedra & Smith** — Microelectronic Circuits
- **Razavi** — Design of Analog CMOS Integrated Circuits
- **Pozar** — Microwave Engineering
- **Griffiths** — Introduction to Electrodynamics (physics foundation)
- **Lathi** — Modern Digital and Analog Communication Systems

### Civil/Structural
- **Gere & Goodno** — Mechanics of Materials
- **Chopra** — Dynamics of Structures
- **Bowles** — Foundation Analysis and Design

### Systems/Control
- **Ogata** — Modern Control Engineering
- **Franklin, Powell & Emami-Naeini** — Feedback Control of Dynamic Systems
- **Doyle, Francis & Tannenbaum** — Feedback Control Theory (free PDF)
  https://www.cds.caltech.edu/~doyle/distributed/DFT.pdf

## Python Engineering Libraries

```python
# Control systems
import control as ct
sys = ct.tf([1], [1, 2, 1])  # Transfer function
ct.bode_plot(sys)

# Numerical methods
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from scipy.linalg import solve

# Signal processing
from scipy.signal import butter, filtfilt, freqz

# FEM (via FEniCS)
from fenics import *
mesh = UnitSquareMesh(32, 32)
V = FunctionSpace(mesh, 'P', 1)
```
