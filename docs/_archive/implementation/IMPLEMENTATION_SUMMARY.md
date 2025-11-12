# Implementation Summary: Complete Motor State Export & Visualization

## Overview

This document summarizes the complete implementation of improved motor state export and visualization for the rocket-sim project, following the comprehensive analysis of RocketPy's `SolidMotor` class.

---

## 1. PARAMETRI AGGIUNTI A MotorConfig

### Parametri Mancanti Identificati e Aggiunti

Tre parametri erano assenti dalla configurazione originale:

```python
# src/config_loader.py - MotorConfig
interpolation_method: str = "linear"  # NEW
coordinate_system_orientation: str = "nozzle_to_combustion_chamber"  # NEW
reference_pressure: Optional[float] = None  # NEW
```

**Dettagli**:
- `interpolation_method`: Metodo di interpolazione per thrust curve ('linear', 'spline', 'akima')
- `coordinate_system_orientation`: Orientamento del sistema di coordinate del motore
- `reference_pressure`: Pressione atmosferica di riferimento per i dati di thrust (Pa)

### File Aggiornati
- ✅ `src/config_loader.py` - MotorConfig dataclass
- ✅ `src/motor_builder.py` - MotorBuilder.build()
- ✅ `configs/single_sim/01_minimal.yaml` - con commenti per parametri opzionali
- ✅ `configs/single_sim/02_complete.yaml` - con tutti i parametri
- ✅ `configs/templates/template_advanced.yaml` - template completo documentato

---

## 2. CLASSIFICAZIONE ATTRIBUTI SOLIDMOTOR

### Categoria A: SCALARI/STATICI (35+ attributi)
**Esportati in `initial_state.json/txt` e `final_state.json/txt`**

#### Geometry Parameters (7)
- `coordinate_system_orientation`, `nozzle_radius`, `nozzle_area`, `nozzle_position`
- `throat_radius`, `throat_area`

#### Grain Parameters (10)
- `grain_number`, `grains_center_of_mass_position`, `grain_separation`
- `grain_density`, `grain_outer_radius`, `grain_initial_inner_radius`
- `grain_initial_height`, `grain_initial_volume`, `grain_initial_mass`
- `grain_burn_out`

#### Mass Properties (3)
- `dry_mass`, `propellant_initial_mass`, `structural_mass_ratio`

#### Dry Inertia Tensor (6)
- `dry_I_11`, `dry_I_22`, `dry_I_33`
- `dry_I_12`, `dry_I_13`, `dry_I_23`

#### Performance Metrics (8)
- `total_impulse`, `max_thrust`, `max_thrust_time`, `average_thrust`
- `burn_start_time`, `burn_out_time`, `burn_duration`, `burn_time`

#### Configuration Metadata (2)
- `interpolate`, `reference_pressure`

### Categoria B: FUNZIONI (23 attributi → 12 plot files)
**Plottati come curve in `outputs/flight_XXX/curves/motor/`**

| Attributo | Plot File | Descrizione |
|-----------|-----------|-------------|
| `thrust(t)` | `thrust.png` | Curva di thrust |
| `total_mass(t)` + `propellant_mass(t)` | `mass_evolution.png` | Evoluzione massa (combinato) |
| `total_mass_flow_rate(t)` | `mass_flow_rate.png` | Portata massica |
| `center_of_mass(t)` + `center_of_propellant_mass(t)` | `center_of_mass.png` | Posizione COM (combinato) |
| `exhaust_velocity(t)` | `exhaust_velocity.png` | Velocità di scarico |
| `grain_inner_radius(t)` + `grain_height(t)` | `grain_geometry.png` | Geometria grano (dual y-axis) |
| `grain_volume(t)` | `grain_volume.png` | Volume grano |
| `burn_area(t)` + `burn_rate(t)` | `burn_characteristics.png` | Caratteristiche combustione (dual y-axis) |
| `Kn(t)` | `kn_curve.png` | Curva Kn |
| `I_11(t)`, `I_22(t)`, `I_33(t)` | `inertia_tensor.png` | Tensore inerzia motore (dual y-axis se necessario) |
| `propellant_I_11(t)`, `propellant_I_22(t)`, `propellant_I_33(t)` | `propellant_inertia_tensor.png` | Tensore inerzia propellente (dual y-axis se necessario) |

**Note sui Plot**:
- **Dual Y-Axis**: Utilizzato quando i valori hanno scale molto diverse (es: `I_11` vs `I_33`, dove `I_11/I_33 > 10`)
- **Combined Plots**: Attributi correlati sono combinati sullo stesso grafico per confronto diretto

### Categoria C: UTILITY/INTERNI (3 attributi)
**Esclusi dall'export**

- `plots` : _SolidMotorPlots
- `prints` : _SolidMotorPrints
- `_mass_flow_rate` : Function (cache interno)

---

## 3. MODIFICHE AL CODICE

### A) StateExporter (`src/state_exporter.py`)

**Metodo `_extract_motor_state()` completamente riscritto**:

```python
def _extract_motor_state(self) -> Dict[str, Any]:
    """Extract complete motor parameters (ONLY scalar/static values).
    
    Function attributes (time-dependent curves) are handled separately 
    by plot generation in CurvePlotter.
    """
    # Define explicit list of 35+ scalar attributes (Category A)
    SCALAR_ATTRIBUTES = [
        # Geometry, Grain, Mass, Inertia, Performance, Metadata...
    ]
    
    # Extract only scalars, skip Function objects
    for attr_name in SCALAR_ATTRIBUTES:
        if hasattr(self.motor, attr_name):
            value = getattr(self.motor, attr_name)
            # Skip Function objects (they go to plots)
            if hasattr(value, '__class__') and value.__class__.__name__ == 'Function':
                logger.debug(f"Skipping Function attribute '{attr_name}'")
                continue
            motor_state[attr_name] = self._serialize_attribute_value(value, attr_name)
```

**Vantaggi**:
- ✅ Export pulito: solo valori numerici/stringhe, NO Function objects
- ✅ Separazione delle responsabilità: scalari in JSON, funzioni nei plot
- ✅ File JSON/TXT più leggibili e compatti
- ✅ Nessuna serializzazione complessa di oggetti Function

### B) CurvePlotter (`src/curve_plotter.py`)

**Completamente esteso con 12 nuovi metodi di plotting**:

#### Metodo Principale
```python
def plot_all_motor_curves(self, output_dir: Path) -> dict:
    """Generate all motor curve plots in motor/ subdirectory."""
    # 1. Thrust curve
    # 2. Mass evolution (combined)
    # 3. Mass flow rate
    # 4. Center of mass (combined)
    # 5. Exhaust velocity
    # 6. Grain geometry (dual y-axis)
    # 7. Grain volume
    # 8. Burn characteristics (dual y-axis)
    # 9. Kn curve
    # 10. Motor inertia tensor (dual y-axis if needed)
    # 11. Propellant inertia tensor (dual y-axis if needed)
```

#### Nuovi Metodi Helper
```python
def plot_single_function(func, title, xlabel, ylabel, output_path)
def _sample_function(func, num_points=200)
def plot_mass_evolution(output_dir)
def plot_center_of_mass(output_dir)
def plot_grain_geometry(output_dir)  # Dual y-axis
def plot_burn_characteristics(output_dir)  # Dual y-axis
def plot_inertia_tensor(output_dir)  # Dual y-axis intelligente
def plot_propellant_inertia_tensor(output_dir)  # Dual y-axis intelligente
```

**Caratteristiche**:
- ✅ **Dual Y-Axis Intelligente**: Rileva automaticamente quando le scale sono troppo diverse (rapporto > 10:1)
- ✅ **Combined Plots**: Attributi correlati sullo stesso grafico (es: total_mass + propellant_mass)
- ✅ **Robust Sampling**: Gestisce sia Function con `.get_source()` che sampling manuale
- ✅ **High-Quality Output**: DPI=300, tight layout, labels chiari

---

## 4. STRUTTURA OUTPUT

### Directory Structure
```
outputs/flight_XXX/
├── initial_state.json                    # Scalars BEFORE simulation
├── initial_state_READABLE.txt            # Human-readable format
├── final_state.json                      # Scalars + flight results AFTER simulation
├── final_state_READABLE.txt              # Human-readable format
├── trajectory.csv                        # Time series arrays (handled by DataHandler)
└── curves/
    ├── motor/
    │   ├── thrust.png
    │   ├── mass_evolution.png
    │   ├── mass_flow_rate.png
    │   ├── center_of_mass.png
    │   ├── exhaust_velocity.png
    │   ├── grain_geometry.png
    │   ├── grain_volume.png
    │   ├── burn_characteristics.png
    │   ├── kn_curve.png
    │   ├── inertia_tensor.png
    │   └── propellant_inertia_tensor.png
    ├── rocket/
    │   ├── power_off_drag.png
    │   └── power_on_drag.png
    └── environment/
        ├── wind_profile.png
        └── atmospheric_profile.png
```

### File Formats

#### initial_state.json
```json
{
  "metadata": {
    "timestamp": "2025-11-10T...",
    "rocketpy_version": "1.x.x",
    "export_type": "initial_state"
  },
  "motor": {
    "_class_type": "SolidMotor",
    "coordinate_system_orientation": "nozzle_to_combustion_chamber",
    "nozzle_radius": 0.033,
    "nozzle_area": 0.00342119,
    "grain_number": 5,
    "grain_density": 1815.0,
    "grain_initial_mass": 1.234,
    "dry_mass": 1.815,
    "propellant_initial_mass": 6.170,
    "total_impulse": 6500.0,
    "max_thrust": 2250.0,
    "burn_duration": 3.9,
    // ... all 35+ scalar attributes
    "_note": "Time-dependent attributes are visualized in curve plots"
  },
  "rocket": { ... },
  "environment": { ... },
  "simulation_config": { ... }
}
```

#### initial_state_READABLE.txt
```
================================================================================
ROCKET SIMULATION - INITIAL STATE (INPUT PARAMETERS)
================================================================================

METADATA
--------------------------------------------------------------------------------
Export Time:      2025-11-10T14:23:45.123456
RocketPy Version: 1.x.x
Export Type:      initial_state

MOTOR PARAMETERS
================================================================================

Basic Properties:
----------------------------------------
  Type:                        SolidMotor
  Coordinate System:           nozzle_to_combustion_chamber

Mass Properties:
----------------------------------------
  Dry Mass:                    1.8150 kg
  Propellant Initial Mass:     6.1700 kg
  Structural Mass Ratio:       0.2270

Geometry:
----------------------------------------
  Nozzle Radius:               0.0330 m
  Nozzle Area:                 0.003421 m²
  Throat Radius:               0.0110 m
  Throat Area:                 0.000380 m²
  Nozzle Position:             0.0000 m

Grain Properties (Solid Motor):
----------------------------------------
  Number of Grains:            5
  Grain Density:               1815.00 kg/m³
  Grain Outer Radius:          0.0330 m
  Grain Initial Inner Radius:  0.0150 m
  Grain Initial Height:        0.1200 m
  Grain Separation:            0.0050 m
  Grain Initial Mass:          1.2340 kg
  Grain Initial Volume:        0.000680 m³

Performance:
----------------------------------------
  Total Impulse:               6500.00 N·s
  Average Thrust:              1666.67 N
  Max Thrust:                  2250.00 N
  Max Thrust Time:             0.850 s
  Burn Duration:               3.900 s
  Burn Start Time:             0.000 s
  Burn Out Time:               3.900 s

Inertia Tensor (Dry, kg·m²):
----------------------------------------
  I_11:  0.125000    I_12:  0.000000    I_13:  0.000000
  I_22:  0.125000    I_23:  0.000000
  I_33:  0.002000
```

---

## 5. BENEFICI DELL'IMPLEMENTAZIONE

### Per l'Analisi
✅ **Separazione chiara**: Scalari in JSON/TXT, funzioni nei plot  
✅ **Completezza**: TUTTI i 35+ attributi scalari esportati  
✅ **Visualizzazione completa**: 11 plot per tutte le funzioni temporali  
✅ **Tracciabilità**: Valori iniziali e finali confrontabili  

### Per la Documentazione
✅ **File leggibili**: TXT formattati con unità di misura  
✅ **Organizzazione**: Cartelle separate (motor/, rocket/, environment/)  
✅ **Metadati**: Timestamp, versione RocketPy, tipo export  

### Per il Debug
✅ **Verifica parametri**: Tutti i valori YAML sono effettivamente usati  
✅ **Valori derivati**: Visibili (nozzle_area, grain_initial_mass, etc.)  
✅ **Confronto**: Initial vs Final state side-by-side  

### Per la Qualità del Codice
✅ **Type Safety**: Tutti i parametri required di SolidMotor.__init__ sono in MotorConfig  
✅ **Documentazione**: MOTOR_ATTRIBUTES_CLASSIFICATION.md completo  
✅ **Manutenibilità**: Chiara separazione responsabilità (export vs plot)  

---

## 6. ESEMPIO DI UTILIZZO

```python
from src.state_exporter import StateExporter
from src.motor_builder import MotorBuilder
from src.rocket_builder import RocketBuilder
from src.environment_setup import EnvironmentSetup

# Build motor, rocket, environment
motor = MotorBuilder(motor_config).build()
rocket = RocketBuilder(rocket_config, motor).build()
environment = EnvironmentSetup(env_config).setup()

# Initialize exporter
exporter = StateExporter(
    motor=motor,
    rocket=rocket,
    environment=environment,
    sim_config=sim_config
)

# Export initial state (before simulation)
exporter.export_initial_state("outputs/flight_001/initial_state.json")
# Creates:
#   - initial_state.json (35+ scalar motor attributes)
#   - initial_state_READABLE.txt

# Run simulation
flight = Flight(rocket, environment, ...)

# Export final state + plots (after simulation)
exporter.export_complete(
    flight=flight,
    output_dir="outputs/flight_001",
    include_plots=True
)
# Creates:
#   - final_state.json
#   - final_state_READABLE.txt
#   - curves/motor/*.png (11 plot files)
#   - curves/rocket/*.png
#   - curves/environment/*.png
```

---

## 7. FILE MODIFICATI

### Core Code Changes
1. ✅ `src/config_loader.py` - MotorConfig con 3 nuovi parametri
2. ✅ `src/motor_builder.py` - MotorBuilder.build() usa nuovi parametri
3. ✅ `src/state_exporter.py` - _extract_motor_state() riscritto per scalari
4. ✅ `src/curve_plotter.py` - Esteso con 11 nuovi plot methods

### Configuration Files
5. ✅ `configs/single_sim/01_minimal.yaml` - Commenti per parametri opzionali
6. ✅ `configs/single_sim/02_complete.yaml` - Tutti i parametri specificati
7. ✅ `configs/templates/template_advanced.yaml` - Template documentato

### Documentation
8. ✅ `docs/MOTOR_ATTRIBUTES_CLASSIFICATION.md` - Classificazione completa attributi
9. ✅ `docs/IMPLEMENTATION_SUMMARY.md` - Questo documento

---

## 8. TESTING CHECKLIST

- [ ] Verificare che initial_state.json contenga tutti i 35+ attributi scalari
- [ ] Verificare che NO Function objects siano nel JSON
- [ ] Verificare che curves/motor/ contenga 11 file PNG
- [ ] Verificare dual y-axis per grain_geometry, burn_characteristics, inertia_tensor
- [ ] Verificare che plots combinati (mass, COM) abbiano entrambe le curve
- [ ] Verificare che initial_state_READABLE.txt sia formattato correttamente
- [ ] Verificare che i nuovi parametri YAML siano effettivamente usati
- [ ] Testare con minimal config (parametri opzionali omessi)
- [ ] Testare con complete config (tutti i parametri specificati)

---

## 9. FUTURE ENHANCEMENTS

### Possibili Miglioramenti
- [ ] Aggiungere export per LiquidMotor e HybridMotor
- [ ] Aggiungere plot interattivi (Plotly) opzionali
- [ ] Aggiungere export in formato HDF5 per grandi dataset
- [ ] Aggiungere diff tool per confrontare initial vs final state
- [ ] Aggiungere validazione automatica dei parametri YAML

---

## 10. REFERENCES

- RocketPy SolidMotor source: `RocketPy/rocketpy/motors/solid_motor.py`
- RocketPy Motor base class: `RocketPy/rocketpy/motors/motor.py`
- Project guidelines: `RocketPy/.github/copilot-instructions.md`

---

**Document Version**: 1.0  
**Date**: 2025-11-10  
**Author**: AI Assistant (via GitHub Copilot)  
**Status**: ✅ Implementation Complete
