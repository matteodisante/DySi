# Cleanup: Rimozione Plot Duplicati e Aggiunta Position Data

**Data**: 13 Novembre 2024
**Tipo**: Refactoring + Feature Addition

## Obiettivo

1. ✅ Aggiungere plot delle posizioni (x, y, z vs tempo)
2. ✅ Rimuovere plot duplicati da `visualizer.py`
3. ✅ Consolidare tutti i plot di volo in `curves/flight/`
4. ✅ Aggiornare documentazione

## Modifiche Implementate

### 1. Nuovo Plot: position_data.png

**File**: `src/curve_plotter.py`

**Metodo aggiunto**: `plot_position_data()`

**Contenuto** (3 subplot):
- **X Position (East)**: Spostamento orizzontale verso est (m)
- **Y Position (North)**: Spostamento orizzontale verso nord (m)  
- **Z Position (Altitude)**: Altitudine sopra il suolo (m) - con apogeo marcato

**Utilità**:
- Vedere drift cumulativo dovuto al vento (X, Y)
- Profilo altimetrico parabolico (Z)
- Base per calcolare velocità (derivate)

### 2. Metodi Rimossi da visualizer.py

**Prima** (5 metodi):
1. `plot_trajectory_2d()` - ✅ MANTENUTO (ground track utile)
2. `plot_trajectory_3d()` - ❌ RIMOSSO (duplicato, versione in curve_plotter è migliore)
3. `plot_altitude_vs_time()` - ❌ RIMOSSO (ora in position_data.png come subplot Z)
4. `plot_velocity_vs_time()` - ❌ RIMOSSO (ora in linear_kinematics_data.png più completo)
5. `plot_acceleration_vs_time()` - ❌ RIMOSSO (ora in linear_kinematics_data.png più completo)
6. `create_standard_plots()` - ❌ RIMOSSO (non più necessario)
7. `plot_comparison()` - ✅ MANTENUTO (utile per confronti)

**Dopo** (2 metodi):
1. `plot_trajectory_2d()` - Ground track 2D (XY projection)
2. `plot_comparison()` - Confronto tra voli multipli

**Linee di codice rimosse**: ~370 linee

### 3. Aggiornamento run_single_simulation.py

**Prima**:
```python
plot_paths = visualizer.create_standard_plots(
    trajectory_data,
    base_filename=output_name,
)
# Creava: trajectory_2d, trajectory_3d, altitude, velocity, acceleration
```

**Dopo**:
```python
plot_path = visualizer.plot_trajectory_2d(
    trajectory_data,
    filename=f"{output_name}_trajectory_2d.png",
)
# Crea solo: trajectory_2d (ground track)
```

**Ragione**: Tutti gli altri plot sono ora generati da `CurvePlotter` in `curves/flight/` con maggiore dettaglio.

### 4. Struttura Output Aggiornata

```
outputs/<simulation>/
├── plots/
│   └── trajectory/
│       └── <name>_trajectory_2d.png    ← Solo ground track (XY)
└── curves/
    ├── motor/       (11 plots)
    ├── rocket/      (2 plots)
    ├── stability/   (5 plots)
    ├── environment/ (2 plots)
    └── flight/      (11 plots) ← TUTTI I PLOT DI VOLO
        ├── trajectory_3d.png           (con proiezioni XYZ)
        ├── position_data.png           ← NUOVO
        ├── linear_kinematics_data.png  (Vx,Vy,Vz + Ax,Ay,Az)
        ├── flight_path_angle_data.png
        ├── attitude_data.png
        ├── angular_kinematics_data.png
        ├── aerodynamic_forces.png
        ├── rail_buttons_forces.png
        ├── energy_data.png
        ├── fluid_mechanics_data.png
        └── stability_and_control_data.png
```

**Totale plot di volo**: 11 (vs 10 RocketPy + 1 custom position_data)

### 5. Documentazione Aggiornata

#### plot_interpretation.rst

**Aggiunta sezione** `position_data.png`:
- Descrizione subplot (X, Y, Z)
- Interpretazione (cosa guardare)
- Relazione con altri plot (derivative → velocity)

**Totale plot documentati**: 27 → **31 plot**

#### quick_plot_reference.rst

**Aggiunta riga** nella tabella Flight Plots:
```rst
* - ``position_data.png``
  - Position components (X, Y, Z) vs time
```

#### CHANGELOG.md

**Sezioni aggiornate**:
- **Added**: `position_data.png` marcato come NEW
- **Removed**: Metodi deprecati da visualizer elencati
- **Changed**: Visualizer semplificato, solo 2 metodi

## Benefici

### 1. Chiarezza di Organizzazione
- ✅ `plots/trajectory/` - Solo ground track 2D
- ✅ `curves/flight/` - **Tutti i plot dettagliati di volo**
- ✅ Nessun duplicato

### 2. Completezza dell'Analisi
- ✅ Position data (x, y, z)
- ✅ Linear kinematics (v, a)
- ✅ Angular kinematics (ω, α)
- ✅ Forces, energy, stability
- ✅ Trajectory 3D con proiezioni

### 3. Riduzione Codice
- ✅ ~370 linee rimosse da visualizer.py
- ✅ Metodo `create_standard_plots()` eliminato
- ✅ Meno manutenzione

### 4. Migliore User Experience
- ✅ Tutti i plot dettagliati in `curves/flight/`
- ✅ Documentazione completa per interpretare ogni plot
- ✅ Quick reference per consultazione rapida

## Migrazione per Utenti

### Comportamenti Deprecati

**PRIMA** (codice vecchio):
```python
# ❌ Questi metodi NON esistono più
visualizer.plot_trajectory_3d(data)
visualizer.plot_altitude_vs_time(data)
visualizer.plot_velocity_vs_time(data)
visualizer.plot_acceleration_vs_time(data)
visualizer.create_standard_plots(data)
```

**DOPO** (codice nuovo):
```python
# ✅ Usa CurvePlotter per plot dettagliati
from src.curve_plotter import CurvePlotter

plotter = CurvePlotter(rocket, flight, env, motor)
plotter.plot_all_flight_curves(output_dir)

# ✅ Usa Visualizer solo per ground track
from src.visualizer import Visualizer

visualizer = Visualizer()
visualizer.plot_trajectory_2d(data, "trajectory_2d.png")
```

### File Generati

**PRIMA**:
```
plots/trajectory/
├── flight_trajectory_2d.png
├── flight_trajectory_3d.png  ← Duplicato
├── flight_altitude.png        ← Duplicato
├── flight_velocity.png        ← Duplicato
└── flight_acceleration.png    ← Duplicato
```

**DOPO**:
```
plots/trajectory/
└── flight_trajectory_2d.png   ← Solo ground track

curves/flight/
├── trajectory_3d.png          ← Versione migliore (con proiezioni)
├── position_data.png          ← Rimpiazza altitude (+ x, y)
├── linear_kinematics_data.png ← Rimpiazza velocity + acceleration
└── ... (altri 8 plot)
```

## Test di Verifica

### Import Check
```bash
✓ CurvePlotter import OK
✓ Visualizer import OK
```

### Metodi Verificati
```python
# CurvePlotter
✓ plot_position_data()           # NUOVO
✓ plot_trajectory_3d()           # Con proiezioni
✓ plot_linear_kinematics_data()  # Vx,Vy,Vz + Ax,Ay,Az
✓ plot_all_flight_curves()       # Chiama tutti 11 metodi

# Visualizer (ridotto)
✓ plot_trajectory_2d()           # Ground track
✓ plot_comparison()              # Multi-flight
```

## Compatibilità

### Breaking Changes
- ❌ `visualizer.create_standard_plots()` - Metodo rimosso
- ❌ `visualizer.plot_trajectory_3d()` - Metodo rimosso
- ❌ `visualizer.plot_altitude_vs_time()` - Metodo rimosso
- ❌ `visualizer.plot_velocity_vs_time()` - Metodo rimosso
- ❌ `visualizer.plot_acceleration_vs_time()` - Metodo rimosso

### Metodi Mantenuti
- ✅ `visualizer.plot_trajectory_2d()` - Invariato
- ✅ `visualizer.plot_comparison()` - Invariato

### Nuove Funzionalità
- ✅ `curve_plotter.plot_position_data()` - NUOVO
- ✅ 11 flight plots in `curves/flight/` invece di 5 in `plots/trajectory/`

## Statistiche

| Metrica | Prima | Dopo | Diff |
|---------|-------|------|------|
| Metodi Visualizer | 7 | 2 | -5 |
| Metodi CurvePlotter flight | 10 | 11 | +1 |
| Plot in plots/trajectory/ | 5 | 1 | -4 |
| Plot in curves/flight/ | 10 | 11 | +1 |
| Linee visualizer.py | ~550 | ~180 | -370 |
| Plot documentati | 30 | 31 | +1 |

## Conclusione

✅ **Obiettivi raggiunti al 100%**

1. ✅ Aggiunto `position_data.png` con x, y, z vs tempo
2. ✅ Rimossi 5 metodi duplicati da `visualizer.py`
3. ✅ Consolidati tutti i plot di volo in `curves/flight/` (11 totali)
4. ✅ Documentazione aggiornata (31 plot documentati)
5. ✅ Codebase più pulito (-370 linee)

**Risultato**: Sistema di plotting più organizzato, meno duplicazione, analisi più completa.
