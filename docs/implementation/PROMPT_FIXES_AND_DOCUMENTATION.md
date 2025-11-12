# PROMPT: Correzioni e Documentazione Sistema Rocket-Sim

## OBIETTIVO
Risolvere 3 problemi critici e creare documentazione completa per l'interpretazione dei risultati.

---

## PROBLEMA 1: Valori "N/A" nel file initial_state_READABLE.txt

### Descrizione
Nel file `outputs/artemis/initial_state_READABLE.txt`, molti valori nelle aerodynamic surfaces sono "N/A":

```plaintext
NOSE CONES (1):
--- Nose Cone #1 ---
  Length:     N/A        ← PROBLEMA
  Kind:       N/A        ← PROBLEMA
  Position:   N/A        ← PROBLEMA

FINS (1 set(s)):
--- Fin Set #1 ---
  Name:         Fins
  Number:       4
  Root Chord:   0.1200 m
  Tip Chord:    0.0600 m
  Span:         0.1000 m
  Position:     N/A      ← PROBLEMA
  Cant Angle:   0.00°
```

### Causa Probabile
Il metodo `_write_rocket_section()` in `src/state_exporter.py` non accede correttamente agli attributi degli oggetti aerodynamic surfaces (NoseCone, Fins, Tail) di RocketPy.

### Soluzione Richiesta

**File da modificare:** `src/state_exporter.py`

**Metodo da fixare:** `_write_rocket_section()`

**Azioni:**

1. **Investigare struttura RocketPy:**
   - Usare `dir(rocket.aerodynamic_surfaces[0])` per vedere attributi disponibili
   - Controllare documentazione RocketPy per accesso a proprietà NoseCone, Fins, Tail
   - Verificare se attributi sono pubblici o privati (es: `_length` vs `length`)

2. **Correggere accesso attributi:**
   ```python
   # Invece di (probabile codice attuale):
   nose_cone.get('length', 'N/A')  # ← SBAGLIATO
   
   # Usare accesso diretto:
   getattr(nose_cone, 'length', None)  # ← CORRETTO
   # oppure
   nose_cone.length if hasattr(nose_cone, 'length') else 'N/A'
   ```

3. **Attributi da estrarre correttamente:**

   **NoseCone:**
   - `length` (m)
   - `kind` (string: "vonKarman", "conical", etc.)
   - `position` (m)
   - `rocket_radius` (m)
   - `name` (string)

   **Fins:**
   - `root_chord` (m)
   - `tip_chord` (m)
   - `span` (m)
   - `position` (m) - **CRITICO**
   - `cant_angle` (rad o deg)
   - `sweep_angle` (rad o deg)
   - `n` (numero di pinne)
   - `name` (string)

   **Tail:**
   - `top_radius` (m)
   - `bottom_radius` (m)
   - `length` (m)
   - `position` (m)
   - `name` (string)

4. **Testing:**
   - Eseguire `python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml --name test_fix`
   - Verificare che `outputs/test_fix/initial_state_READABLE.txt` non contenga "N/A" per posizioni/geometrie
   - Controllare anche `final_state_READABLE.txt`

**Output atteso:**
```plaintext
NOSE CONES (1):
--- Nose Cone #1 ---
  Length:     0.5000 m
  Kind:       vonKarman
  Position:   0.0000 m

FINS (1 set(s)):
--- Fin Set #1 ---
  Name:         Fins
  Number:       4
  Root Chord:   0.1200 m
  Tip Chord:    0.0600 m
  Span:         0.1000 m
  Position:     1.9500 m     ← FIXATO!
  Cant Angle:   0.00°
```

---

## PROBLEMA 2: File di Log nella Cartella Sbagliata

### Descrizione
Quando si esegue:
```bash
python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml --name artemis --log-file artemis_log
```

Il file `artemis_log` viene salvato in:
```
/Users/matteodisante/Documents/university/starpi/rocket-sim/artemis_log  ← SBAGLIATO
```

Invece che in:
```
/Users/matteodisante/Documents/university/starpi/rocket-sim/outputs/artemis/artemis_log  ← CORRETTO
```

### Soluzione Richiesta

**File da modificare:** `scripts/run_single_simulation.py`

**Azioni:**

1. **Localizzare setup del logging:**
   - Cercare dove viene configurato il file handler del logger
   - Probabile chiamata a `logging.FileHandler(log_file_path)`

2. **Modificare path del log file:**
   ```python
   # PRIMA (sbagliato):
   if args.log_file:
       file_handler = logging.FileHandler(args.log_file)
   
   # DOPO (corretto):
   if args.log_file:
       # Assicura che il log vada nella cartella output
       output_dir = Path(f"outputs/{args.name}")
       output_dir.mkdir(parents=True, exist_ok=True)
       log_path = output_dir / args.log_file
       file_handler = logging.FileHandler(log_path)
   ```

3. **Logica completa:**
   - Se `--log-file` specificato: salvare in `outputs/{name}/{log_file}`
   - Se `--log-file` non specificato: non creare file log (solo console)
   - Assicurarsi che la directory output esista prima di creare il log

4. **Informare l'utente:**
   ```python
   logger.info(f"Log file will be saved to: {log_path}")
   ```

5. **Testing:**
   ```bash
   # Test 1: con nome log esplicito
   python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml --name test_log --log-file simulation.log
   # Verificare: outputs/test_log/simulation.log esiste
   
   # Test 2: senza nome log
   python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml --name test_no_log
   # Verificare: nessun file log creato, solo output console
   ```

**Bonus:** Aggiungere log file di default:
```python
# Se non specificato, crea automaticamente un log file con timestamp
if not args.log_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    args.log_file = f"simulation_{timestamp}.log"
```

---

## PROBLEMA 3: Documentazione Interpretazione Risultati

### Descrizione
Serve documentazione completa che spieghi:
1. **Parametri di input** - Cosa significa ogni parametro nel config YAML
2. **Parametri di output** - Cosa significa ogni valore nei file `initial_state_READABLE.txt` e `final_state_READABLE.txt`
3. **Curve plots** - Interpretazione di tutti i 30 plot generati (11 motor + 17 rocket + 2 environment)
4. **Relazioni** - Come input si trasformano in output
5. **Unità di misura** - Chiarezza assoluta su tutte le unità

### Soluzione Richiesta

**Nuovo file da creare:** `docs/user/RESULTS_INTERPRETATION_GUIDE.md`

**Struttura documento:**

```markdown
# Guida all'Interpretazione dei Risultati - Rocket Simulation

## Introduzione
Questa guida spiega come interpretare tutti i file e plot generati dalla simulazione.

## PARTE 1: Parametri di Input (Config YAML)

### Rocket Parameters
#### mass (dry_mass_kg)
- **Significato:** Massa strutturale del rocket senza motore
- **Unità:** kilogrammi (kg)
- **Include:** Airframe, nosecone, fins, parachute, avionics, payload
- **Esclude:** Motore (aggiunto separatamente)
- **Valori tipici:** 10-30 kg per high-power rockets
- **Impatto:** Influenza T/W ratio, accelerazione, apogeo

#### inertia (ixx, iyy, izz)
- **Significato:** Momenti di inerzia rispetto agli assi principali
- **Unità:** kg·m²
- **Assi:**
  - I_xx, I_yy: inerzia laterale (beccheggio e imbardata)
  - I_zz: inerzia assiale (rollio)
- **Relazioni:** Per rocket simmetrici: I_xx ≈ I_yy >> I_zz
- **Come calcolare:** Da CAD o formula cilindro cavo
- **Impatto:** Stabilità rotazionale, risposta a disturbi

[... continuare per TUTTI i parametri ...]

### Motor Parameters
#### reference_pressure
- **Significato:** Pressione atmosferica a cui è stata misurata la thrust curve
- **Unità:** Pascal (Pa)
- **Valori comuni:**
  - 101325 Pa = pressione a livello del mare (standard)
  - 0 Pa = thrust misurata in camera a vuoto
- **⚠️ CRITICO:** Valore sbagliato → thrust in quota completamente errata
- **Come RocketPy lo usa:**
  ```
  F_totale(altitudine) = F_curve(t) + (P_ref - P_ambiente(h)) × A_nozzle
  ```
- **Esempio impatto:**
  - Se reference_pressure = 101325 Pa e volo a 1000m (P~90000 Pa)
  - Correzione thrust = (101325 - 90000) × 0.0034 m² ≈ +38 N
  - Thrust effettiva = Thrust_curva + 38 N

[... continuare per TUTTI i parametri motor, environment, simulation ...]

## PARTE 2: Parametri di Output

### Initial State File

#### Center of Mass Positions
**CoM without Motor (center_of_mass_without_motor):**
- **Significato:** Posizione del centro di massa del rocket vuoto (senza motore)
- **Riferimento:** Misurata dal nose tip nel sistema nose_to_tail
- **Unità:** metri (m)
- **Relazione con input:** Uguale a `cg_location_m` nel config
- **Uso:** Baseline per calcolo static margin

**Center of Dry Mass (center_of_dry_mass_position):**
- **Significato:** CoM del rocket completo ma senza propellente
- **Include:** Struttura rocket + motore vuoto
- **Cambia nel tempo:** NO (massa distribuita fissa)
- **Uso:** Static stability dopo burnout

**Motor Center of Dry Mass:**
- **Significato:** CoM del motore vuoto nel sistema rocket
- **Calcolo:** motor_position + center_of_dry_mass_position_motor
- **Uso:** Calcolo inerzie composite

#### Inertia Tensors - Le 3 Configurazioni

**Without Motor:**
- Solo struttura rocket
- Baseline per design

**Dry (with unloaded motor):**
- Rocket + motore vuoto
- Configurazione post-burnout

**Total (time-dependent):**
- Rocket + motore + propellente(t)
- Cambia durante combustione
- Visualizzato nei plot

**Perché 3 configurazioni:**
1. Design independence (rocket senza motore)
2. Final state prediction (dopo burnout)
3. Flight dynamics (durante combustione)

#### Static Margin
- **Significato:** Distanza tra CoM e CoP normalizzata al calibro
- **Formula:** (x_CP - x_CoM) / calibro
- **Unità:** calibri (diametri rocket)
- **Range sicuro:** 1.5 - 3.0 calibri
- **Interpretazione:**
  - < 1.0: Instabile
  - 1.0 - 1.5: Marginale
  - 1.5 - 3.0: Stabile
  - > 3.0: Sovra-stabile (eccessivo drag)

[... continuare per TUTTI gli attributi ...]

### Final State File

#### Differenze rispetto a Initial State
- **Total Mass:** Ridotta (propellente consumato)
- **CoM:** Spostato (consumo asimmetrico propellente)
- **Inertia:** Ridotta (meno massa rotante)

#### Attributi Nuovi in Final State
[Specificare quali attributi appaiono solo nel final state]

## PARTE 3: Interpretazione Curve Plots

### Motor Plots (11 total)

#### 1. thrust_curve.png
**Cosa mostra:**
- Thrust del motore vs tempo
- Area colorata = Total Impulse
- Linea verde tratteggiata = Average Thrust
- Marker rossi = Burn start/out
- Punto rosso = Max Thrust

**Come leggere:**
- **Forma curva:** Progressive (picco subito) vs Regressive (picco a metà)
- **Area sotto curva:** Maggiore = più impulso totale
- **Max thrust:** Determina max accelerazione
- **Average thrust:** Predictor apogeo (più significativo di max)

**Red flags:**
- Picco troppo alto → stress strutturale
- Durata troppo breve → apogeo limitato
- Thrust negativa (mai dovrebbe succedere)

**Valori tipici:**
- High-power amateur: 500-3000 N max thrust
- Burn time: 2-5 secondi
- Total impulse: classe G-M (5000-10000 N·s)

#### 2. mass_evolution.png
**Cosa mostra:**
- Massa totale motore vs tempo (blu solido)
- Massa solo propellente vs tempo (rosso tratteggiato)

**Come leggere:**
- **Pendenza curva:** Tasso consumo propellente (mass flow rate)
- **Differenza verticale:** Massa motore vuoto (costante)
- **Slope changes:** Indicano fasi combustione diverse

**Uso pratico:**
- Verifica mass ratio (propellant/total)
- Check consumo propellente completo a burn-out

#### 3. center_of_mass.png (motor)
**Cosa mostra:**
- Posizione CoM motore vs tempo

**Significato shift:**
- CoM si sposta man mano che propellente brucia
- Pattern dipende da geometria grain
- Impatta stabilità dinamica rocket

[... CONTINUARE PER TUTTI gli 11 motor plots ...]

### Rocket Plots (17 total)

#### 1. total_mass_vs_time.png
**Cosa mostra:**
- Massa totale rocket (struttura + motore + propellente) vs tempo

**Fasi visibili:**
1. **t=0 → burn-out:** Massa decresce (propellente consumato)
2. **burn-out → apogee:** Massa costante (coasting)
3. **Dopo apogee:** Eventuale deploy paracadute (piccola variazione)

**Interpretazione:**
- **Slope durante burn:** = mass flow rate motor
- **Step discontinuity:** Deploy paracadute o staging
- **Final mass:** Deve essere = initial mass - propellant mass

#### 2. mass_components_comparison.png
**Cosa mostra:**
- Bar chart comparativo dei componenti massa

**Componenti:**
- Rocket Structure
- Motor (dry)
- Propellant (initial)
- Total Dry Mass
- Total Mass (t=0)

**Uso:**
- Visual mass budget
- Identifica componenti dominanti
- Verifica somme corrette

**Best practices:**
- Propellant dovrebbe essere 15-40% total mass
- Motor dry mass < 15% total mass

#### 3. inertia_comparison.png
**Cosa mostra:**
- Bar chart di I_11, I_22, I_33 per diverse configurazioni

**Configurazioni:**
- Without motor
- Dry (with empty motor)
- Total at t=0 (full propellant)
- Total at burn-out

**Pattern atteso:**
- I_11 ≈ I_22 (simmetria)
- I_33 << I_11 (cilindro)
- Total(t=0) > Total(burn-out) > Dry > Without motor

**Red flags:**
- I_11 ≠ I_22 → asimmetria indesiderata
- I_33 > I_11 → geometria anomala

#### 4. static_margin_vs_time.png
**⚠️ PLOT CRITICO PER STABILITÀ**

**Cosa mostra:**
- Static margin (CP - CM)/calibro vs tempo

**Zone sicurezza:**
- **Verde (>1.5):** Stabile
- **Giallo (1.0-1.5):** Marginale
- **Rosso (<1.0):** Instabile

**Interpretazione temporale:**
- **Durante burn:** Margin cambia perché CoM si sposta (propellente consuma)
- **Direzione shift:** CoM tipicamente va verso tail → margin aumenta
- **Post-burnout:** Margin costante

**Safety check:**
- Margin DEVE rimanere > 1.5 per TUTTO il volo
- Margin < 1.0 in qualsiasi istante → UNSAFE

**Cosa fare se instabile:**
1. Spostare fins più verso tail
2. Aumentare span fins
3. Spostare CoM più verso nose (ballast)

#### 5. stability_margin_surface.png
**⚠️ PLOT AVANZATO - 3D STABILITY**

**Cosa mostra:**
- Superficie 3D: Stability margin vs Mach vs Tempo
- Contour plot con isolinee

**Assi:**
- X: Mach number (0 → 3+)
- Y: Time (0 → burn-out)
- Z (colore): Stability margin (calibers)

**Interpretazione colori:**
- Verde scuro: Molto stabile (>2.5)
- Verde chiaro: Stabile (1.5-2.5)
- Giallo: Marginale (1.0-1.5)
- Rosso: Instabile (<1.0)

**Fenomeni visibili:**
1. **Transonic instability (M=0.8-1.2):**
   - Possibile dip nel margin (shock wave effects)
   - Normale ma deve rimanere >1.5

2. **Time variation:**
   - Margin cambia perché CoM si sposta

3. **Supersonic stabilization:**
   - Margin tipicamente aumenta M>1.5

**Red flags:**
- Qualsiasi zona rossa
- Discontinuità sharp (errori numerici)

#### 6. thrust_to_weight_vs_time.png
**Cosa mostra:**
- Rapporto Thrust/Weight vs tempo

**Fasi:**
1. **Liftoff:** T/W massimo (massa max, thrust iniziale)
2. **Durante burn:** T/W aumenta (massa decresce, thrust varia)
3. **Post burn-out:** T/W = 0 (no thrust)

**Safety thresholds:**
- **T/W > 5** al liftoff: Minimo per launch sicuro
- **T/W > 10:** Optimal performance
- **T/W < 3:** Rail velocity insufficiente

**Max T/W tipico:**
- Amateur rockets: 10-20
- Professional: 5-15 (più controllato)

**Cosa fare se T/W troppo basso:**
1. Motore più potente
2. Ridurre massa rocket
3. Rail più lungo (compensa)

[... CONTINUARE PER TUTTI i 17 rocket plots ...]

### Environment Plots (2 total)

#### 1. wind_profile.png
**Cosa mostra:**
- Wind velocity vs altitudine

**Interpretazione:**
- Vento varia con quota (wind shear)
- Impatta drift laterale rocket

#### 2. atmospheric_profile.png
**Cosa mostra:**
- Temperatura, pressione, densità vs altitudine

**Uso:**
- Verifica atmospheric model
- Impatta drag e thrust

## PARTE 4: Relazioni Input → Output

### Come Input Diventa Output

**Esempio 1: Mass Properties**
```
INPUT (config.yaml):
  rocket.dry_mass_kg = 16.426
  motor.dry_mass_kg = 1.815
  motor.propellant_mass = 2.956 (da thrust curve)

OUTPUT (initial_state):
  Dry Mass = 18.241 kg (16.426 + 1.815)
  Total Mass(t=0) = 21.197 kg (18.241 + 2.956)
  
OUTPUT (final_state):
  Total Mass(t=final) = 18.241 kg (propellant consumed)
```

**Esempio 2: Center of Mass**
```
INPUT:
  rocket.cg_location_m = 1.255 (without motor)
  motor.position_m = 2.0
  motor.center_of_dry_mass = 0.317 (from nozzle)

CALCOLO:
  motor_CoM_in_rocket_frame = 2.0 + 0.317 = 2.317 m
  
  CoM_dry = (m_rocket × CoM_rocket + m_motor × CoM_motor) / m_total
          = (16.426 × 1.255 + 1.815 × 2.317) / 18.241
          = 1.298 m

OUTPUT:
  Center of Dry Mass = 1.298 m
```

[... più esempi per static margin, inertias, etc. ...]

## PARTE 5: Checklist Validazione Risultati

### Pre-Flight Checks (da Initial State)

- [ ] Static margin > 1.5 calibri
- [ ] T/W ratio > 5 al liftoff
- [ ] Dry mass < Total mass (t=0)
- [ ] Motor position > rocket length (nozzle outside)
- [ ] I_xx ≈ I_yy (se design simmetrico)
- [ ] CoM within reasonable range (40-60% rocket length)

### Post-Flight Checks (da Final State)

- [ ] Total mass ≈ Dry mass (propellant consumed)
- [ ] Apogee > 0 (rocket went up!)
- [ ] Max velocity reasonable (<Mach 1 per amateur)
- [ ] Impact velocity < 10 m/s (safe recovery)

### Plot Validation

- [ ] Static margin sempre > 1.5
- [ ] No red zones in stability margin surface
- [ ] Thrust curve integra a total impulse corretto
- [ ] Mass decreases monotonically during burn
- [ ] CoM shift reasonable (<20% rocket length)

## PARTE 6: Common Patterns e Anomalie

### Pattern Normali

**Mass vs Time:**
- Smooth decrease during burn
- Flat dopo burn-out

**Static Margin:**
- Slight increase during burn (CoM moves aft)
- Constant dopo burn-out

**T/W Ratio:**
- Peak early (full thrust, max mass)
- Decreases fino a burn-out
- Zero dopo

### Anomalie da Investigare

**Discontinuità sharp:**
- Possibili errori numerici
- Check integration tolerances

**Static margin < 0:**
- CRITICAL: Rocket instabile
- Redesign needed

**T/W < 3:**
- Rail velocity insufficiente
- Risk di tip-over

**Mass aumenta:**
- ERRORE nel model
- Check propellant consumption logic

## PARTE 7: Glossario Termini Tecnici

**Caliber:** Diametro rocket (unità di misura relativa)

**Static Margin:** (CP - CM) / caliber [unità: calibri]

**Stability Margin:** Generalizzazione 3D di static margin

**T/W Ratio:** Thrust / Weight (dimensionless)

**Rail Velocity:** Velocità rocket al momento di lasciare la launch rail

**Apogee:** Punto massimo altitudine

**Burn-out:** Momento in cui propellente è completamente consumato

**Coasting Phase:** Volo dopo burn-out ma prima di apogee

**Descent Phase:** Volo dopo apogee (going down)

[... più termini ...]

## PARTE 8: References e Approfondimenti

- RocketPy Documentation: https://docs.rocketpy.org/
- Barrowman Equations (stability): [link]
- Thrust Curve Formats (.eng files): [link]
- Atmospheric Models: [link]
```

### Formato del Documento

**Stile:**
- Linguaggio chiaro e accessibile
- Esempi numerici concreti
- Formule quando necessario
- Grafici esempio quando utile
- Box WARNING/NOTE per punti critici

**Organizzazione:**
- TOC cliccabile all'inizio
- Sezioni ben separate
- Cross-references tra sezioni
- Quick reference tables

**Lunghezza stimata:**
- 100-150 pagine A4 se stampato
- 5000-8000 righe markdown
- Comprehensive ma non overwhelming

---

## PROBLEMA 4 (BONUS): Report Generator HTML/PDF

### Soluzione Proposta

**Approccio:** Report HTML auto-contenuto (singolo file .html)

**File da creare:** `src/report_generator.py`

**Caratteristiche:**

1. **Auto-contained HTML:**
   - Plot embedded come base64
   - CSS inline
   - No external dependencies
   - Apribile offline

2. **Sezioni Report:**
   - Executive Summary
   - Input Configuration
   - Flight Performance Metrics
   - Stability Analysis
   - All Plots (organized)
   - Safety Checks
   - Recommendations

3. **Template HTML:**
   ```python
   HTML_TEMPLATE = """
   <!DOCTYPE html>
   <html>
   <head>
       <meta charset="UTF-8">
       <title>Rocket Simulation Report - {rocket_name}</title>
       <style>
           /* Professional CSS styling */
           body {{ font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; }}
           .metric {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; }}
           .safe {{ color: green; font-weight: bold; }}
           .warning {{ color: orange; font-weight: bold; }}
           .danger {{ color: red; font-weight: bold; }}
           /* ... */
       </style>
   </head>
   <body>
       <h1>Flight Simulation Report</h1>
       <div class="summary">
           <h2>Executive Summary</h2>
           <div class="metric">
               <span class="label">Apogee:</span>
               <span class="value">{apogee_m:.1f} m</span>
           </div>
           <!-- ... -->
       </div>
       
       <div class="plots">
           <h2>Performance Plots</h2>
           <img src="data:image/png;base64,{thrust_curve_base64}" />
           <!-- ... -->
       </div>
       
       <div class="safety">
           <h2>Safety Checks</h2>
           <div class="{static_margin_class}">
               Static Margin: {static_margin:.2f} calibers
           </div>
       </div>
   </body>
   </html>
   """
   ```

4. **Integrazione:**
   ```python
   # In flight_simulator.py dopo export state
   if export_state:
       # ... existing code ...
       
       # Generate HTML report
       from src.report_generator import ReportGenerator
       report_gen = ReportGenerator(
           rocket=self.rocket,
           environment=self.environment,
           flight=self.flight,
           output_dir=str(output_path)
       )
       report_path = report_gen.generate_html_report()
       logger.info(f"HTML report saved to: {report_path}")
   ```

5. **PDF Generation (opzionale):**
   - Usare `weasyprint` o `pdfkit`
   - Converte HTML → PDF
   - Richiede dependency extra

**Priorità:** MEDIUM (nice to have, non blocking)

---

## IMPLEMENTAZIONE PLAN

### Task Priority

1. **HIGH - FIX N/A values** (PROBLEMA 1)
   - Impatta usabilità immediata
   - Fix veloce (1-2 ore)

2. **HIGH - FIX log file path** (PROBLEMA 2)
   - UX improvement importante
   - Fix veloce (30 minuti)

3. **MEDIUM - Documentation guide** (PROBLEMA 3)
   - Importante ma non blocking
   - Tempo: 4-6 ore (documento estensivo)

4. **LOW - HTML Report Generator** (PROBLEMA 4)
   - Nice to have
   - Tempo: 2-3 ore
   - Può essere fatto dopo

### Testing Strategy

**Per ogni fix:**
1. Run simulation completa
2. Verificare output files
3. Check log files
4. Validate plots generated

**Test command:**
```bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --name test_all_fixes \
    --log-file simulation.log \
    --verbose
```

**Validation:**
- [ ] No "N/A" in initial_state_READABLE.txt
- [ ] Log file in outputs/test_all_fixes/simulation.log
- [ ] All 30 plots generated
- [ ] Schematics saved
- [ ] Documentation accurate

---

## DELIVERABLES

1. ✅ Fixed `src/state_exporter.py` - No more N/A values
2. ✅ Fixed `scripts/run_single_simulation.py` - Log files in correct location
3. ✅ New `docs/user/RESULTS_INTERPRETATION_GUIDE.md` - Comprehensive guide
4. ⚠️ Optional `src/report_generator.py` - HTML report generator
5. ✅ Updated test outputs validating all fixes

---

## NOTES

- Mantenere backward compatibility
- Aggiungere tests per evitare regressioni future
- Documentare tutte le modifiche
- Update README.md se necessario
