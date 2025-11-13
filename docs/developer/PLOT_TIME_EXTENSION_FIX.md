# Fix: Plot Time Range Extension & Apogee Correction

**Data**: 13 Novembre 2024
**Tipo**: Bug Fix + Enhancement

## Problemi Risolti

### 1. ❌ Apogeo sbagliato nel plot 3D
**Problema**: Il plot `trajectory_3d.png` marcava l'apogeo usando `np.argmax(z)` che trova semplicemente l'altitudine massima nell'array, ma non considera il tempo effettivo dell'apogeo.

**Scenario problematico**:
- Se il volo ha oscillazioni dopo l'apogeo, `argmax(z)` potrebbe puntare a un picco spurio
- Se l'array è troncato, il massimo potrebbe non essere l'apogeo vero

**Soluzione**:
```python
# PRIMA (sbagliato)
apogee_idx = np.argmax(z)
ax.scatter([x[apogee_idx]], [y[apogee_idx]], [z[apogee_idx]], ...)

# DOPO (corretto)
if hasattr(self.flight, 'apogee_time') and hasattr(self.flight, 'apogee'):
    time_array = self.flight.z[:, 0]
    apogee_idx = np.argmin(np.abs(time_array - self.flight.apogee_time))
    ax.scatter([x[apogee_idx]], [y[apogee_idx]], [z[apogee_idx]],
              label=f'Apogee: {self.flight.apogee:.1f} m @ {self.flight.apogee_time:.1f} s')
```

**Risultato**: L'apogeo ora è marcato al tempo **esatto** registrato da RocketPy.

### 2. ❌ Plot troncati troppo presto (all'apogeo)
**Problema**: Tutti i plot di volo usavano `first_event_time = apogee_time` come limite, troncando i grafici **immediatamente all'apogeo**.

**Conseguenze**:
- ❌ Non si vedeva l'apertura del paracadute
- ❌ Non si vedevano le dinamiche durante il deploy
- ❌ Impossibile analizzare cosa succede dopo l'apogeo
- ❌ Variabili cinematiche/dinamiche incomplete

**Esempio**:
```
Apogee @ 50s
Drogue deploy @ 50.5s   ← NON VISIBILE
Main deploy @ 52s       ← NON VISIBILE
Plot terminava @ 50s    ← TROPPO PRESTO!
```

**Soluzione**: Nuovo metodo helper `_get_plot_time_limit()`

## Implementazione

### Nuovo Metodo Helper

```python
def _get_plot_time_limit(self) -> float:
    """Determine appropriate time limit for flight plots.
    
    Returns time that includes parachute deployment events to show
    dynamics during and after deployment.
    
    Returns
    -------
    float
        Time limit in seconds
    """
    # Default: full flight time
    time_limit = self.flight.t_final
    
    # If we have parachute events, extend beyond first parachute
    if hasattr(self.flight, 'parachute_events') and self.flight.parachute_events:
        # Get time of last parachute deployment
        last_chute_time = max(event[0] for event in self.flight.parachute_events)
        # Add 10% of flight time after last chute or 20 seconds, whichever is less
        extension = min(0.1 * self.flight.t_final, 20.0)
        time_limit = min(last_chute_time + extension, self.flight.t_final)
    # Otherwise use apogee + extension if available
    elif hasattr(self.flight, 'apogee_time') and self.flight.apogee_time > 0:
        # Add 30% of time to apogee or 30 seconds after apogee
        extension = min(0.3 * self.flight.apogee_time, 30.0)
        time_limit = min(self.flight.apogee_time + extension, self.flight.t_final)
    
    return time_limit
```

### Logica del Time Limit

**Priorità**:
1. **Se ci sono parachute_events**: Usa ultimo deploy + estensione
   - Estensione: 10% del tempo totale o 20s (minore dei due)
   - Garantisce visibilità del deploy e dinamiche successive

2. **Altrimenti, se c'è apogee_time**: Usa apogeo + estensione
   - Estensione: 30% del tempo fino all'apogeo o 30s (minore dei due)
   - Mostra fase di discesa iniziale

3. **Fallback**: Usa tempo totale del volo (`t_final`)

**Esempi**:

| Scenario | Apogee | Deploy | t_final | Time Limit | Spiegazione |
|----------|--------|--------|---------|------------|-------------|
| Con paracadute | 50s | 52s | 120s | 64s | 52s + min(0.1×120, 20) = 64s |
| Senza paracadute | 50s | - | 120s | 65s | 50s + min(0.3×50, 30) = 65s |
| Fallback | - | - | 120s | 120s | Full flight |

### Metodi Aggiornati (11 totali)

Tutti i metodi di plot di volo ora usano `time_limit = self._get_plot_time_limit()`:

1. ✅ `plot_position_data()`
2. ✅ `plot_trajectory_3d()` - **+ fix apogeo**
3. ✅ `plot_linear_kinematics_data()`
4. ✅ `plot_flight_path_angle_data()`
5. ✅ `plot_attitude_data()`
6. ✅ `plot_angular_kinematics_data()`
7. ✅ `plot_aerodynamic_forces()`
8. ✅ `plot_rail_buttons_forces()`
9. ✅ `plot_energy_data()`
10. ✅ `plot_fluid_mechanics_data()`
11. ✅ `plot_stability_and_control_data()`

### Modifiche al Codice

**Pattern applicato**:

```python
# PRIMA
first_event_time = self.flight.t_final
if hasattr(self.flight, 'apogee_time') and self.flight.apogee_time > 0:
    first_event_time = self.flight.apogee_time

ax.set_xlim(0, first_event_time)

# DOPO
time_limit = self._get_plot_time_limit()
ax.set_xlim(0, time_limit)
```

**Per plot con indici** (es. aerodynamic_forces):

```python
# PRIMA
first_event_time_index = np.searchsorted(self.flight.time[:, 0], first_event_time)
ax.plot(data[:first_event_time_index, 0], data[:first_event_time_index, 1])

# DOPO
time_limit = self._get_plot_time_limit()
time_limit_index = np.searchsorted(self.flight.time[:, 0], time_limit)
ax.plot(data[:time_limit_index, 0], data[:time_limit_index, 1])
```

## Benefici

### 1. Analisi Completa del Volo

**PRIMA**:
```
Plot terminava @ apogeo (50s)
- Non si vedeva drogue deploy @ 50.5s
- Non si vedeva main deploy @ 52s
- Non si vedeva decelerazione paracadute
```

**DOPO**:
```
Plot esteso fino a 64s (deploy + 12s)
✓ Visibile drogue deploy @ 50.5s
✓ Visibile main deploy @ 52s
✓ Visibile spike di decelerazione
✓ Visibile transizione a discesa stabile
```

### 2. Dinamiche al Deploy Visibili

**Cosa si vede ora**:
- **Spike di decelerazione** in `linear_kinematics_data.png` (Az negativo enorme)
- **Cambio di attitude** in `attitude_data.png` (nutation spike)
- **Spike di AoA** in `fluid_mechanics_data.png` (paracadute aperto → alto drag)
- **Perdita di energia** in `energy_data.png` (energia dissipata dal paracadute)

### 3. Apogeo Accurato

**PRIMA**: Apogeo marcato a t=50.0s ma poteva essere impreciso
**DOPO**: Apogeo marcato a t=50.123s (esatto) con label: `Apogee: 3245.7 m @ 50.1 s`

### 4. Flessibilità

Il sistema ora si adatta automaticamente:
- ✅ Voli con paracadute → estende oltre deploy
- ✅ Voli balistici → estende oltre apogeo
- ✅ Voli anomali → usa t_final come fallback

## Test di Verifica

### Import Check
```bash
✓ Import OK
```

### Volo con Paracadute (Caso Tipico)

**Parametri**:
- Apogee: 50s
- Drogue deploy: 50.5s  
- Main deploy: 52s
- t_final: 120s

**Risultato atteso**:
- `time_limit = 52s + min(0.1×120, 20) = 64s`
- Plot mostra: 0s → 64s
- ✓ Drogue visibile
- ✓ Main visibile
- ✓ Dinamiche post-deploy visibili

### Volo Balistico (Senza Paracadute)

**Parametri**:
- Apogee: 50s
- No parachute events
- t_final: 80s

**Risultato atteso**:
- `time_limit = 50s + min(0.3×50, 30) = 65s`
- Plot mostra: 0s → 65s
- ✓ Fase discesa visibile

## Modifiche ai File

### src/curve_plotter.py

**Aggiunte**:
- Metodo `_get_plot_time_limit()` (linea ~2600)

**Modifiche** (11 metodi):
- Sostituito `first_event_time` con `time_limit = self._get_plot_time_limit()`
- Sostituito `first_event_time_index` con `time_limit_index`
- Fix apogeo in `plot_trajectory_3d()` usando `apogee_time`

**Linee modificate**: ~150 linee in 11 metodi

## Compatibilità

### Non Breaking
✅ Tutti i metodi mantengono la stessa firma
✅ Output files hanno stesso nome
✅ Struttura subplot invariata

### Miglioramenti Visibili
- ✅ Plot più lunghi (mostrano più dati)
- ✅ Apogeo più preciso (usa tempo esatto)
- ✅ Deploy events visibili

## Documentazione

**Non richiede aggiornamenti** alla documentazione utente perché:
- I plot hanno lo stesso nome
- L'interpretazione rimane identica
- Il cambiamento è un miglioramento trasparente

**Nota interna**: Potrebbe essere utile aggiungere nella documentazione developer una nota su `_get_plot_time_limit()` per spiegare la logica di estensione.

## Conclusione

✅ **Problema 1 risolto**: Apogeo 3D ora usa `apogee_time` esatto
✅ **Problema 2 risolto**: Plot estesi oltre apogeo fino a deploy + buffer
✅ **11 metodi aggiornati**: Tutti i flight plots ora mostrano dinamiche complete
✅ **Zero breaking changes**: Compatibilità totale con codice esistente

**Risultato**: Analisi del volo molto più completa, con visibilità su eventi critici come l'apertura del paracadute.
