# PROMPT: Repository Cleanup & Reorganization

## OBIETTIVO
Pulire, riorganizzare e aggiornare completamente la repository rocket-sim per:
1. Rimuovere file obsoleti/inutili
2. Aggiornare documentazione con le nuove modifiche
3. Riorganizzare struttura cartelle se necessario
4. Garantire coerenza e manutenibilità

---

## FASE 1: ANALISI E IDENTIFICAZIONE

### 1.1 Scansiona Output Directory
```bash
outputs/
```

**AZIONI**:
- [ ] Lista tutte le subdirectory in `outputs/`
- [ ] Identifica simulazioni vecchie/test
- [ ] Controlla dimensioni file (plot PNG, JSON, CSV)
- [ ] **ELIMINA**: Tutte le vecchie simulazioni tranne eventuali esempi di riferimento
- [ ] **MANTIENI**: Max 1-2 esempi completi ben documentati (rinominare con nomi chiari)

**DECISIONE**: 
- Mantenere `outputs/` vuoto o con max 1 esempio `outputs/example_complete_flight/`?
- Aggiungere `outputs/.gitignore` per evitare commit di output?

---

### 1.2 Scansiona Documentation
```bash
docs/
├── API_REFERENCE.md
├── ARCHITECTURE_QUICK.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── MODULE_REFERENCE.md
├── SENSITIVITY_ANALYSIS.md
├── TROUBLESHOOTING.md
├── WEATHER_INTEGRATION.md
├── MOTOR_ATTRIBUTES_CLASSIFICATION.md      # NUOVO
├── IMPLEMENTATION_SUMMARY.md               # NUOVO
├── MOTOR_STATE_EXPORT_GUIDE.md            # NUOVO
└── ...
```

**AZIONI PER OGNI FILE**:

#### docs/API_REFERENCE.md
- [ ] Verifica se è aggiornato con le nuove modifiche (StateExporter, CurvePlotter)
- [ ] Aggiungi sezioni per:
  - `StateExporter` (export scalari vs funzioni)
  - `CurvePlotter` (11 nuovi metodi motor)
  - `MotorConfig` (3 nuovi parametri)
- [ ] Se mancante/incompleto: **AGGIORNA**
- [ ] Se ben scritto e completo: **MANTIENI**

#### docs/ARCHITECTURE.md / ARCHITECTURE_QUICK.md
- [ ] Verifica se descrive correttamente il flusso:
  - Config → Builder → Simulation → Export → Plots
- [ ] Aggiungi diagramma per nuovo sistema export:
  ```
  Motor → StateExporter → initial_state.json (scalari)
                       → CurvePlotter → curves/motor/*.png (funzioni)
  ```
- [ ] Se obsoleto: **AGGIORNA**
- [ ] Se ridondante (ARCHITECTURE vs ARCHITECTURE_QUICK): **UNIFICA** in un solo file

#### docs/MODULE_REFERENCE.md
- [ ] Verifica se documenta tutti i moduli in `src/`:
  - config_loader.py
  - motor_builder.py
  - rocket_builder.py
  - environment_setup.py
  - flight_simulator.py
  - state_exporter.py ← **VERIFICA AGGIORNAMENTO**
  - curve_plotter.py ← **VERIFICA AGGIORNAMENTO**
  - data_handler.py
  - visualizer.py
  - ...
- [ ] Se incompleto: **AGGIORNA** con nuovi metodi
- [ ] Se ben fatto: **MANTIENI**

#### docs/CONTRIBUTING.md
- [ ] Verifica se spiega:
  - Come aggiungere nuovi parametri a Config
  - Come estendere CurvePlotter per nuovi plot
  - Come aggiornare StateExporter per nuovi attributi
- [ ] Se mancante: **AGGIUNGI** sezione "Adding New Motor Attributes"
- [ ] Se completo: **MANTIENI**

#### docs/TROUBLESHOOTING.md
- [ ] Verifica se include troubleshooting per:
  - Plot non generati
  - Attributi mancanti in JSON
  - Errori di configurazione motor
- [ ] Se incompleto: **AGGIORNA** con FAQ comuni
- [ ] Se obsoleto: **ELIMINA** e integra in guide esistenti

#### docs/SENSITIVITY_ANALYSIS.md
- [ ] Verifica pertinenza con il progetto
- [ ] Se usato: **MANTIENI**
- [ ] Se non implementato/obsoleto: **ELIMINA** o sposta in `docs/archived/`

#### docs/WEATHER_INTEGRATION.md
- [ ] Verifica se aggiornato con ambiente attuale
- [ ] Se utile e aggiornato: **MANTIENI**
- [ ] Se obsoleto: **AGGIORNA** o **ELIMINA**

#### NUOVI FILE (creati oggi)
- [x] docs/MOTOR_ATTRIBUTES_CLASSIFICATION.md - **MANTIENI** (ben fatto)
- [x] docs/IMPLEMENTATION_SUMMARY.md - **MANTIENI** (ben fatto)
- [x] docs/MOTOR_STATE_EXPORT_GUIDE.md - **MANTIENI** (ben fatto)

**DECISIONE FINALE DOCS**:
- Organizzare in subdirectory?
  ```
  docs/
  ├── user-guides/
  │   ├── MOTOR_STATE_EXPORT_GUIDE.md
  │   └── GETTING_STARTED.md
  ├── developer/
  │   ├── ARCHITECTURE.md
  │   ├── API_REFERENCE.md
  │   ├── MOTOR_ATTRIBUTES_CLASSIFICATION.md
  │   └── CONTRIBUTING.md
  ├── implementation/
  │   └── IMPLEMENTATION_SUMMARY.md
  └── archived/
      └── (file obsoleti)
  ```

---

### 1.3 Scansiona Root Directory
```bash
/
├── CHANGELOG_MOTOR_EXPORT.md    # NUOVO - da integrare?
├── README.md
├── requirements.txt
├── requirements-docs.txt
├── setup.py
├── single_sim_log              # ???
└── ...
```

**AZIONI**:

#### CHANGELOG_MOTOR_EXPORT.md
- [ ] **INTEGRA** contenuto in `CHANGELOG.md` principale (se esiste)
- [ ] Oppure **RINOMINA** in `CHANGELOG.md` se non esiste
- [ ] **ELIMINA** dopo integrazione

#### README.md
- [ ] Verifica se documenta:
  - Quick start aggiornato
  - Nuove feature (motor export completo, 11 plot)
  - Link a docs/MOTOR_STATE_EXPORT_GUIDE.md
- [ ] **AGGIORNA** con esempio di utilizzo nuovo sistema
- [ ] Aggiungi badge/sezioni:
  ```markdown
  ## Features
  - ✅ Complete motor state export (35+ attributes)
  - ✅ 11 motor curve plots with smart dual y-axis
  - ✅ Organized output structure (motor/, rocket/, environment/)
  ```

#### single_sim_log
- [ ] Verifica contenuto
- [ ] Se è un log di test vecchio: **ELIMINA**
- [ ] Se è utile: **RINOMINA** con nome descrittivo e **SPOSTA** in `outputs/` o `logs/`

---

### 1.4 Scansiona Configs
```bash
configs/
├── README_CONFIGS.md
├── weather_example.yaml
├── monte_carlo/
├── single_sim/
│   ├── 01_minimal.yaml          # Aggiornato oggi
│   └── 02_complete.yaml         # Aggiornato oggi
└── templates/
    ├── template_advanced.yaml   # Aggiornato oggi
    └── template_basic.yaml
```

**AZIONI**:

#### README_CONFIGS.md
- [ ] Verifica se documenta:
  - Tutti i parametri motor (inclusi i 3 nuovi)
  - Differenza tra minimal/complete
  - Come usare i template
- [ ] **AGGIORNA** con tabella completa parametri motor
- [ ] Se incompleto: **ESPANDI** con esempi

#### weather_example.yaml
- [ ] Verifica se utilizzato
- [ ] Se obsoleto/non usato: **ELIMINA** o sposta in examples/

#### templates/template_basic.yaml
- [ ] Verifica se aggiornato con nuovi parametri
- [ ] **AGGIORNA** se necessario
- [ ] Mantieni differenza chiara basic vs advanced

---

### 1.5 Scansiona Scripts
```bash
scripts/
├── run_single_simulation.py
├── run_monte_carlo.py
├── run_sensitivity.py
└── ...
```

**AZIONI**:
- [ ] Verifica che tutti gli script siano funzionanti
- [ ] Controlla che usino StateExporter e CurvePlotter aggiornati
- [ ] **AGGIORNA** docstring/commenti se necessario
- [ ] Se script obsoleti: **ELIMINA** o sposta in `scripts/archived/`

---

### 1.6 Scansiona Notebooks
```bash
notebooks/
├── 00_getting_started.ipynb
├── 01_single_flight_simulation.ipynb
├── 02_monte_carlo_ensemble.ipynb
├── 03_sensitivity_analysis.ipynb
├── notebooks_outputs/
└── outputs/
```

**AZIONI**:
- [ ] Verifica se notebook sono aggiornati con:
  - Nuovi parametri motor (interpolation_method, etc.)
  - Nuovo sistema export (StateExporter)
  - Nuovi plot (CurvePlotter)
- [ ] **ESEGUI** ogni notebook e verifica che funzioni
- [ ] **AGGIORNA** celle con nuove API
- [ ] **PULISCI** outputs (notebooks_outputs/, outputs/)
- [ ] Aggiungi nuovo notebook: `04_motor_state_export.ipynb`?

---

### 1.7 Scansiona Data/Examples
```bash
data/
├── drag_curves/
└── motors/

examples/
├── 01_basic_simulation.py
├── 02_monte_carlo_simple.py
└── 03_sensitivity_analysis.py
```

**AZIONI**:

#### data/
- [ ] Verifica che tutti i file siano utilizzati
- [ ] Se drag curves/motors obsoleti: **ELIMINA**
- [ ] **MANTIENI** solo quelli referenziati nei config di esempio

#### examples/
- [ ] Verifica che tutti gli script funzionino
- [ ] **AGGIORNA** con nuove API (StateExporter, CurvePlotter)
- [ ] Aggiungi `04_motor_export_visualization.py`?
- [ ] **ESEGUI** e testa ogni esempio

---

### 1.8 Scansiona Test
```bash
tests/
├── __init__.py
├── conftest.py
├── test_builders.py
├── test_config_loader.py
├── test_validators.py
└── test_variance_sensitivity.py
```

**AZIONI**:
- [ ] Verifica se esistono test per:
  - MotorConfig (con 3 nuovi parametri)
  - StateExporter (_extract_motor_state)
  - CurvePlotter (nuovi metodi)
- [ ] **AGGIUNGI** test mancanti:
  - `test_motor_config_new_parameters.py`
  - `test_state_exporter_scalar_extraction.py`
  - `test_curve_plotter_motor_plots.py`
- [ ] **ESEGUI** `pytest` e verifica che tutto passi
- [ ] Se test obsoleti: **AGGIORNA** o **ELIMINA**

---

## FASE 2: RIORGANIZZAZIONE STRUTTURA

### 2.1 Proposta Nuova Struttura

**PRIMA**:
```
rocket-sim/
├── docs/ (12+ file disorganizzati)
├── outputs/ (molte sim vecchie)
├── notebooks/outputs/ (ridondante)
├── notebooks/notebooks_outputs/ (ridondante)
├── CHANGELOG_MOTOR_EXPORT.md (da integrare)
└── single_sim_log (???)
```

**DOPO**:
```
rocket-sim/
├── README.md (aggiornato)
├── CHANGELOG.md (integrato)
├── setup.py
├── requirements.txt
├── requirements-docs.txt
├── .gitignore (aggiornato)
│
├── configs/
│   ├── README.md (aggiornato)
│   ├── single_sim/
│   ├── monte_carlo/
│   └── templates/
│
├── data/
│   ├── drag_curves/ (solo file usati)
│   └── motors/ (solo file usati)
│
├── docs/
│   ├── README.md (indice)
│   ├── user/
│   │   ├── getting-started.md
│   │   ├── motor-state-export-guide.md
│   │   └── troubleshooting.md
│   ├── developer/
│   │   ├── architecture.md
│   │   ├── api-reference.md
│   │   ├── contributing.md
│   │   └── motor-attributes-classification.md
│   └── implementation/
│       └── motor-export-implementation.md
│
├── examples/
│   ├── 01_basic_simulation.py (aggiornato)
│   ├── 02_monte_carlo_simple.py (aggiornato)
│   ├── 03_sensitivity_analysis.py (aggiornato)
│   └── 04_motor_export_visualization.py (NUOVO)
│
├── notebooks/
│   ├── 00_getting_started.ipynb (aggiornato)
│   ├── 01_single_flight_simulation.ipynb (aggiornato)
│   ├── 02_monte_carlo_ensemble.ipynb (aggiornato)
│   ├── 03_sensitivity_analysis.ipynb (aggiornato)
│   └── 04_motor_state_export.ipynb (NUOVO)
│
├── outputs/ (vuoto, con .gitignore)
│
├── scripts/
│   ├── run_single_simulation.py
│   ├── run_monte_carlo.py
│   └── run_sensitivity.py
│
├── src/
│   ├── __init__.py
│   ├── config_loader.py (aggiornato)
│   ├── motor_builder.py (aggiornato)
│   ├── state_exporter.py (aggiornato)
│   ├── curve_plotter.py (aggiornato)
│   └── ...
│
└── tests/
    ├── test_config_loader.py (aggiornato)
    ├── test_state_exporter.py (NUOVO)
    ├── test_curve_plotter.py (NUOVO)
    └── ...
```

---

## FASE 3: CREAZIONE/AGGIORNAMENTO FILE

### 3.1 .gitignore Aggiornato
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Jupyter
.ipynb_checkpoints/
notebooks/outputs/
notebooks/notebooks_outputs/

# Outputs (generated during simulations)
outputs/
!outputs/.gitkeep
!outputs/example_complete_flight/

# Logs
*.log
single_sim_log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docs build
docs/_build/
docs/.doctrees/

# Distribution
dist/
build/
*.egg-info/
```

### 3.2 outputs/.gitkeep
```
# This directory is used for simulation outputs
# Outputs are ignored by git (see .gitignore)
# Add example outputs in outputs/example_complete_flight/ if needed
```

### 3.3 docs/README.md (Indice)
```markdown
# Documentation Index

## User Guides
- [Getting Started](user/getting-started.md)
- [Motor State Export Guide](user/motor-state-export-guide.md)
- [Troubleshooting](user/troubleshooting.md)

## Developer Documentation
- [Architecture](developer/architecture.md)
- [API Reference](developer/api-reference.md)
- [Motor Attributes Classification](developer/motor-attributes-classification.md)
- [Contributing](developer/contributing.md)

## Implementation Details
- [Motor Export Implementation](implementation/motor-export-implementation.md)

## Quick Links
- [Main README](../README.md)
- [CHANGELOG](../CHANGELOG.md)
- [Examples](../examples/)
- [Notebooks](../notebooks/)
```

### 3.4 CHANGELOG.md (Integrato)
```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added - 2025-11-10
- Complete motor state export system with 35+ scalar attributes
- 11 new motor curve plots with intelligent dual y-axis
- 3 new motor configuration parameters (interpolation_method, coordinate_system_orientation, reference_pressure)
- Comprehensive documentation (30+ pages)
- Smart dual y-axis detection for plots with different scales

### Changed
- StateExporter now exports only scalar attributes to JSON (Functions → plots)
- CurvePlotter extended with 11 new motor plotting methods
- Output directory reorganized (motor/, rocket/, environment/ subdirectories)

### Fixed
- Missing motor parameters in configuration
- Function objects serialization in JSON export

[... previous changelog entries ...]
```

---

## FASE 4: TESTING & VALIDAZIONE

### 4.1 Checklist Post-Cleanup

#### File Structure
- [ ] Tutti i file obsoleti rimossi
- [ ] Documentazione organizzata in `docs/user/`, `docs/developer/`, `docs/implementation/`
- [ ] Output directory pulito (solo `.gitkeep` o 1 esempio)
- [ ] `.gitignore` aggiornato

#### Documentation
- [ ] `README.md` aggiornato con nuove feature
- [ ] `CHANGELOG.md` integrato e aggiornato
- [ ] `docs/README.md` indice creato
- [ ] Tutti i file docs referenziano correttamente i nuovi moduli
- [ ] Nessun link rotto

#### Code
- [ ] Tutti gli script in `scripts/` funzionanti
- [ ] Tutti gli esempi in `examples/` funzionanti
- [ ] Tutti i notebook in `notebooks/` eseguibili
- [ ] Config in `configs/` validati

#### Tests
- [ ] Nuovi test aggiunti per StateExporter, CurvePlotter, MotorConfig
- [ ] `pytest` passa al 100%
- [ ] Coverage accettabile (>80%)

#### Final Check
- [ ] `git status` pulito (nessun file tracked indesiderato)
- [ ] Build documentazione (se presente) funziona
- [ ] Simulazione di test completa funziona end-to-end

---

## FASE 5: ESECUZIONE

### 5.1 Backup
```bash
# Prima di qualsiasi modifica
cd /Users/matteodisante/Documents/university/starpi
cp -r rocket-sim rocket-sim-backup-$(date +%Y%m%d)
```

### 5.2 Ordine Operazioni

1. **Backup** (vedi sopra)
2. **Elimina file obsoleti** (outputs vecchi, logs, etc.)
3. **Riorganizza docs** (crea subdirectory, sposta file)
4. **Aggiorna documentazione** (README, CHANGELOG, docs/*)
5. **Aggiorna config** (.gitignore, setup.py se necessario)
6. **Testa codice** (run examples, scripts, notebooks)
7. **Aggiungi test mancanti**
8. **Commit incrementale** (non tutto insieme!)
9. **Validazione finale**

### 5.3 Git Strategy

Commits separati per:
1. `chore: Remove obsolete output files and logs`
2. `docs: Reorganize documentation structure`
3. `docs: Update README and CHANGELOG with motor export feature`
4. `docs: Update API reference and architecture docs`
5. `chore: Update .gitignore and add outputs/.gitkeep`
6. `test: Add tests for StateExporter and CurvePlotter`
7. `examples: Update examples with new motor export API`
8. `notebooks: Update notebooks with new features`

---

## DELIVERABLES

Al termine della cleanup:

1. **Repository Structure Report**:
   - Before/after tree structure
   - Files removed (count & size)
   - Files moved/renamed
   - Files updated

2. **Documentation Update Summary**:
   - List of updated docs with changes
   - New docs created
   - Deprecated docs archived

3. **Code Quality Report**:
   - Test coverage %
   - All examples working? (Y/N)
   - All notebooks working? (Y/N)
   - All scripts working? (Y/N)

4. **Final Checklist**:
   - [ ] Repository size reduced
   - [ ] Documentation well-organized
   - [ ] No broken links
   - [ ] All code functional
   - [ ] Git history clean
   - [ ] Ready for next development phase

---

## NOTES

- **NON eliminare** file senza prima verificare dipendenze
- **Testare** dopo ogni modifica significativa
- **Committare** incrementalmente
- **Documentare** ogni decisione importante
- Se in dubbio su un file: **ARCHIVIARE** invece di eliminare

---

**Estimated Time**: 2-3 ore
**Risk Level**: Medium (backup obbligatorio)
**Priority**: High (manutenibilità del progetto)
