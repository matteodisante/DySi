# Static Margin Plot - Spiegazione Tecnica

## Domande e Risposte

### 1. Cosa fa `plots.static_margin()` in RocketPy?

In RocketPy, il metodo `rocket.plots.static_margin()` genera un **plot del margine statico nel tempo**.

**Definizione del margine statico:**
```python
static_margin(t) = (center_of_mass(t) - cp_position(0)) / (2 * radius)
```

**Caratteristica chiave**: Il CP (Center of Pressure) è **sempre calcolato a Mach=0**, indipendentemente dal numero di Mach reale durante il volo.

### 2. Il margine statico viene usato in DySi?

**No**, DySi **non usa** `rocket.plots.static_margin()` direttamente.

Invece, DySi implementa plot più avanzati in `curve_plotter.py`:

- **`plot_static_margin_enhanced()`** - usa `rocket.stability_margin(mach, time)` che è più accurato
- **`plot_stability_margin_surface()`** - superficie 3D del margine vs Mach e tempo
- **`plot_stability_envelope()`** - margine con zone di sicurezza e eventi critici

Questi metodi usano il **margine di stabilità** (stability margin) che considera il CP al **Mach reale** del volo.

### 3. Come può il margine statico essere plottato nel tempo se è calcolato a Mach=0?

Questa è la **chiave per capire la differenza tra static margin e stability margin**.

**Plot del margine statico nel tempo:**
- L'asse X è il **tempo**
- L'asse Y è il **margine statico** = (CoM(t) - CP(Mach=0)) / (2 * radius)

**Cosa varia:**
- ✅ Il **CoM cambia nel tempo** per consumo propellente
- ❌ Il **CP rimane fisso a Mach=0** per tutta la durata

**Risultato**: Il plot mostra come il CoM si sposta nel tempo, ma il CP è **sempre quello a Mach=0**.

### Perché questo è importante?

#### Margine Statico (Static Margin)
- **Conservativo**: usa sempre CP a Mach=0
- **Utile per design iniziale**: garantisce sicurezza in tutte le condizioni
- **Semplice**: non richiede dati di volo
- **Limitazione**: NON riflette il comportamento reale in volo transonico/supersonico

#### Margine di Stabilità (Stability Margin)
- **Realistico**: usa CP al Mach reale di quel momento
- **Accurato**: riflette il comportamento reale in volo
- **Complesso**: richiede dati di volo (Mach vs tempo)
- **Vantaggio**: mostra che la stabilità può **migliorare** in regime transonico

### Esempio Pratico

```python
# ❌ SBAGLIATO - Non fare questo!
mach_range = np.linspace(0, 1.2, 50)
wrong_margins = [rocket.static_margin(5.0) for m in mach_range]
# Questo plotta lo stesso valore 50 volte!

# ✅ CORRETTO - Margine statico vs tempo
time_range = np.linspace(0, burnout_time, 100)
static_margins = [rocket.static_margin(t) for t in time_range]
plt.plot(time_range, static_margins)
plt.title("Static Margin vs Time (at Mach=0)")

# ✅✅ MIGLIORE - Margine di stabilità (CP varia con Mach)
stability_margins = []
for t in time_range:
    mach = flight.mach_number(t)
    sm = rocket.stability_margin(mach, t)
    stability_margins.append(sm)
plt.plot(time_range, stability_margins)
plt.title("Stability Margin vs Time (CP varies with Mach)")
```

## Conclusione

- **Static margin** = metrica semplificata con CP fisso a Mach=0 (conservativa)
- **Stability margin** = metrica realistica con CP al Mach reale
- **Entrambe valide** - usa static margin per design, stability margin per analisi
- **Mai plottare static margin vs Mach** - non ha senso fisico!

## Riferimenti

- `RocketPy/rocketpy/rocket/rocket.py` - metodi `evaluate_static_margin()` e `evaluate_stability_margin()`
- `DySi/docs/developer/STABILITY_MARGIN_CLARIFICATION.md` - documentazione dettagliata
- `DySi/src/curve_plotter.py` - implementazione plot avanzati

---

*Documento creato il 13 novembre 2025*
