# Nuovi Plot di Volo Implementati in DySi

Questo documento descrive i nuovi plot di dati di volo implementati nel modulo `curve_plotter.py`, 
basati sui metodi disponibili in RocketPy come mostrato in "First Simulation with RocketPy".

## Organizzazione

Tutti i plot di volo sono organizzati nella sottocartella `curves/flight/` per mantenere una struttura pulita e coerente con gli altri plot già esistenti:

- `curves/motor/` - Plot relativi al motore
- `curves/rocket/` - Plot relativi al razzo
- `curves/stability/` - Plot di stabilità
- `curves/environment/` - Plot ambientali
- **`curves/flight/`** - **Plot di dati di volo (NUOVI)**

## Nuovi Metodi Implementati

### 1. `plot_all_flight_curves()`

Metodo principale che genera tutti i plot di volo. Viene automaticamente chiamato da `plot_all_curves()` se esiste un oggetto `Flight`.

**Output**: Dictionary con nomi plot → percorsi file

### 2. `plot_attitude_data()`

**File**: `curves/flight/attitude_data.png`

Plotta gli angoli di Eulero del razzo:
- **Attitude Angle**: Angolo complessivo di assetto
- **Psi (ψ)**: Angolo di precessione
- **Theta (θ)**: Angolo di nutazione
- **Phi (φ)**: Angolo di spin

**Basato su**: `flight_plots.attitude_data()` di RocketPy

### 3. `plot_angular_kinematics_data()`

**File**: `curves/flight/angular_kinematics_data.png`

Plotta velocità e accelerazioni angolari su 3 subplot con assi doppi:
- **ω₁ e α₁**: Velocità e accelerazione angolare asse 1
- **ω₂ e α₂**: Velocità e accelerazione angolare asse 2
- **ω₃ e α₃**: Velocità e accelerazione angolare asse 3

**Caratteristiche**:
- Assi Y doppi (velocità a sinistra, accelerazione a destra)
- Colori differenziati (#ff7f0e per ω, #1f77b4 per α)

**Basato su**: `flight_plots.angular_kinematics_data()` di RocketPy

### 4. `plot_aerodynamic_forces()`

**File**: `curves/flight/aerodynamic_forces.png`

Plotta le forze e momenti aerodinamici:
- **Lift Force**: Forza di portanza (risultante + componenti R1, R2)
- **Drag Force**: Forza di resistenza
- **Bending Moment**: Momento flettente (risultante + componenti M1, M2)
- **Spin Moment**: Momento di spin

**Basato su**: `flight_plots.aerodynamic_forces()` di RocketPy

### 5. `plot_rail_buttons_forces()`

**File**: `curves/flight/rail_buttons_forces.png` (se applicabile)

Plotta le forze sui rail buttons durante la fase di rampa:
- **Normal Force**: Forza normale su upper/lower button
- **Shear Force**: Forza di taglio su upper/lower button

**Note**: 
- Viene generato solo se il razzo ha rail buttons definiti
- Mostra solo la fase di rampa (fino a `out_of_rail_time`)

**Basato su**: `flight_plots.rail_buttons_forces()` di RocketPy

### 6. `plot_energy_data()`

**File**: `curves/flight/energy_data.png`

Plotta componenti energetiche e potenze:
- **Total Energy**: Energia meccanica totale
- **Kinetic + Potential**: Componenti cinetiche e potenziali
- **Thrust Power**: Potenza di spinta (durante burnout)
- **Drag Power**: Potenza dissipata per resistenza

**Caratteristiche**:
- Notazione scientifica per valori grandi
- Xlim fino all'apogeo per energia
- Xlim fino a burnout per thrust power

**Basato su**: `flight_plots.energy_data()` di RocketPy

### 7. `plot_fluid_mechanics_data()`

**File**: `curves/flight/fluid_mechanics_data.png`

Plotta parametri di fluidodinamica (6 subplot):
- **Mach Number**: Numero di Mach vs tempo
- **Reynolds Number**: Numero di Reynolds vs tempo
- **Pressures**: Dinamica, totale, statica
- **Angle of Attack**: Angolo di attacco
- **Stream Velocity**: Componenti X, Y, Z della velocità del flusso
- **Angle of Sideslip**: Angolo di derapata

**Caratteristiche**:
- AoA e sideslip limitati a `out_of_rail_time → first_event_time`
- Notazione scientifica per numeri grandi

**Basato su**: `flight_plots.fluid_mechanics_data()` di RocketPy

### 8. `plot_stability_and_control_data()`

**File**: `curves/flight/stability_and_control_data.png`

Plotta stabilità e controllo:
- **Stability Margin**: Margine di stabilità nel tempo (con CP variabile)
  - Markers per eventi critici: out of rail, burnout, apogee
- **Frequency Response**: Risposta in frequenza normalizzata
  - Attitude angle
  - Omega 1, 2, 3

**Note**: Questo plot usa `flight.stability_margin` che considera il CP al Mach reale, diversamente da `rocket.static_margin` che usa CP a Mach=0.

**Basato su**: `flight_plots.stability_and_control_data()` di RocketPy

## Differenze da RocketPy

Le implementazioni seguono fedelmente RocketPy con alcune migliorie:

1. **Salvataggio automatico**: Tutti i plot vengono salvati come PNG ad alta risoluzione (300 DPI)
2. **Gestione errori**: Try-except robusti con logging
3. **Organizzazione**: Sottocartella dedicata `flight/` per mantenere ordine
4. **Integrazione**: Chiamata automatica da `plot_all_curves()` se `flight` è disponibile

## Utilizzo

```python
from src.curve_plotter import CurvePlotter

# Dopo aver eseguito una simulazione
plotter = CurvePlotter(
    motor=motor,
    rocket=rocket,
    environment=env,
    max_mach=flight.max_mach_number,
    flight=flight  # ← IMPORTANTE: passare l'oggetto Flight
)

# Genera tutti i plot (inclusi quelli di volo)
paths = plotter.plot_all_curves("outputs/my_simulation/curves")

# Oppure genera solo i plot di volo
flight_paths = plotter.plot_all_flight_curves("outputs/my_simulation/curves")
```

## Output Esempio

```
outputs/my_simulation/curves/flight/
├── attitude_data.png
├── angular_kinematics_data.png
├── aerodynamic_forces.png
├── rail_buttons_forces.png  (se applicabile)
├── energy_data.png
├── fluid_mechanics_data.png
└── stability_and_control_data.png
```

## Compatibilità

- ✅ Compatibile con tutte le simulazioni esistenti
- ✅ Generazione condizionale (solo se `flight` è disponibile)
- ✅ Gestione graceful di dati mancanti (rail buttons, etc.)
- ✅ Logging chiaro per debug

## Riferimenti

- **RocketPy**: `rocketpy/plots/flight_plots.py` - implementazione originale
- **DySi**: `src/curve_plotter.py` - implementazione integrata
- **Documentazione RocketPy**: "First Simulation with RocketPy" notebook

---

*Implementato il 13 novembre 2025*
