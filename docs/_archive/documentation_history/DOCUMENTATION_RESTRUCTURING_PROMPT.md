# 📚 Prompt per Ristrutturazione Completa della Documentazione

> **Obiettivo**: Trasformare la documentazione attuale in una risorsa professionale, chiara, navigabile e utile, seguendo gli standard di eccellenza di RocketPy, NumPy e SciPy.

---

## 🎯 Problemi Identificati nella Documentazione Attuale

### 1. **Contenuti Obsoleti**
- [ ] Riferimenti a funzionalità "in development" mai completate
- [ ] Informazioni contraddittorie tra diversi file
- [ ] Esempi di codice non aggiornati con l'API corrente
- [ ] Documentazione Monte Carlo presente ma funzionalità non implementata

### 2. **Struttura Confusionaria**
- [ ] Troppi file Markdown sconnessi senza navigazione chiara
- [ ] Duplicazione di informazioni tra README, docs/user, docs/developer
- [ ] Mancanza di gerarchia logica dei contenuti
- [ ] Percorsi di apprendimento non chiari (da principiante a esperto)

### 3. **Difficile Consultazione**
- [ ] Nessun indice generale navigabile
- [ ] Ricerca di informazioni specifica richiede troppi click
- [ ] Mancanza di quick reference/cheat sheets
- [ ] Assenza di FAQ per problemi comuni

### 4. **Scarsa Utilità Pratica**
- [ ] Esempi limitati e non progressivi
- [ ] Mancanza di "ricette" per casi d'uso comuni
- [ ] Spiegazioni teoriche senza esempi concreti
- [ ] Tutorial insufficienti per onboarding utenti

### 5. **Aspetto Non Professionale**
- [ ] Mix di inglese e italiano in alcuni punti
- [ ] Formattazione inconsistente tra file
- [ ] Uso eccessivo di emoji che distrae
- [ ] Mancanza di standard di scrittura tecnica

---

## 📋 Modelli di Riferimento Excellence

### **RocketPy Documentation**
```
Punti di forza da emulare:
✓ Getting Started chiaro con progressione logica
✓ Esempi pratici commentati in ogni sezione
✓ API reference completa con docstring NumPy-style
✓ Tutorial progressivi (basic → intermediate → advanced)
✓ Sezioni "See Also" per cross-reference
✓ Notebook Jupyter integrati nella documentazione
```

### **NumPy Documentation**
```
Punti di forza da emulare:
✓ Quick Reference cards per funzioni comuni
✓ Suddivisione chiara: User Guide / Reference / Developer
✓ Esempi testati automaticamente (doctest)
✓ Spiegazioni matematiche chiare con LaTeX
✓ "Notes" section per dettagli implementativi
✓ Standard docstring consistenti
```

### **SciPy Documentation**
```
Punti di forza da emulare:
✓ Tutorial per ogni modulo con teoria + pratica
✓ Cookbook con soluzioni a problemi specifici
✓ Bibliografia e riferimenti scientifici
✓ Versioning chiaro della documentazione
✓ Warning boxes per edge cases importanti
✓ Performance notes
```

---

## 🏗️ Struttura Proposta della Nuova Documentazione

```
docs/
├── index.rst                          # Landing page Sphinx
├── getting_started/
│   ├── installation.rst              # Setup chiaro passo-passo
│   ├── quickstart.rst                # Prima simulazione in 5 minuti
│   ├── key_concepts.rst              # Concetti base (cosa è un Flight, Motor, etc.)
│   └── next_steps.rst                # Dove andare dopo il quickstart
│
├── user_guide/                        # Guide per utenti (non sviluppatori)
│   ├── index.rst
│   ├── tutorials/
│   │   ├── 01_basic_flight.rst       # Tutorial progressivi
│   │   ├── 02_custom_motor.rst
│   │   ├── 03_weather_integration.rst
│   │   ├── 04_air_brakes.rst
│   │   └── 05_advanced_plotting.rst
│   ├── how_to_guides/                # "Ricette" per task specifici
│   │   ├── configure_rocket.rst
│   │   ├── import_motor_data.rst
│   │   ├── export_results.rst
│   │   ├── create_custom_plots.rst
│   │   └── troubleshoot_validation.rst
│   ├── configuration/
│   │   ├── overview.rst              # Struttura YAML spiegata
│   │   ├── rocket_params.rst         # Un parametro alla volta
│   │   ├── motor_params.rst
│   │   ├── environment_params.rst
│   │   └── simulation_params.rst
│   └── examples/                      # Esempi completi commentati
│       ├── minimal_flight.rst
│       ├── competition_rocket.rst
│       └── research_vehicle.rst
│
├── reference/                         # API Reference tecnica
│   ├── index.rst
│   ├── cli.rst                       # Comandi CLI documentati
│   ├── api/
│   │   ├── config_loader.rst         # Auto-generated da docstrings
│   │   ├── motor_builder.rst
│   │   ├── rocket_builder.rst
│   │   ├── flight_simulator.rst
│   │   └── ...
│   ├── configuration_schema.rst      # Schema YAML completo
│   └── outputs_reference.rst         # Tutti i file output spiegati
│
├── developer_guide/
│   ├── index.rst
│   ├── contributing.rst              # Come contribuire
│   ├── architecture.rst              # Design del sistema
│   ├── coding_standards.rst          # Convenzioni del progetto
│   ├── testing.rst                   # Come scrivere test
│   └── extending.rst                 # Come aggiungere funzionalità
│
├── background/                        # Contesto teorico
│   ├── rocket_physics.rst            # Fisica dei razzi (breve!)
│   ├── simulation_theory.rst         # Come funziona la simulazione
│   └── validation.rst                # Come vengono validati i parametri
│
└── appendices/
    ├── glossary.rst                  # Termini tecnici
    ├── faq.rst                       # Domande frequenti
    ├── changelog.rst                 # Storia delle versioni
    ├── bibliography.rst              # Riferimenti scientifici
    └── migration_guides/             # Guide per aggiornamenti breaking
```

---

## ✍️ Standard di Scrittura Tecnica

### **Tone of Voice**
```markdown
❌ EVITARE:
- "Ora proveremo a fare..." (troppo informale)
- "Questa cosa fantastica..." (soggettivo)
- "Semplicemente..." (condiscendente)
- Mix italiano/inglese

✅ USARE:
- "This tutorial demonstrates..." (chiaro, diretto)
- "The following example shows..." (professionale)
- "Note: This feature requires..." (informativo)
- Inglese tecnico consistente
```

### **Struttura dei Tutorial**
```markdown
Ogni tutorial DEVE avere:

1. **Obiettivo Chiaro**: "By the end of this tutorial, you will be able to..."
2. **Prerequisites**: "Before starting, ensure you have..."
3. **Step-by-Step Instructions**: Numerati, testati, funzionanti
4. **Complete Working Example**: Codice completo copiabile
5. **Expected Output**: Cosa aspettarsi come risultato
6. **What's Next**: Link al tutorial successivo
7. **See Also**: Cross-reference a contenuti correlati
```

### **Struttura delle How-To Guides**
```markdown
Ogni guida DEVE rispondere a:

1. **Problem Statement**: "How to configure a custom drag curve"
2. **Quick Answer**: Risposta in 2-3 righe per chi ha fretta
3. **Detailed Solution**: Step-by-step con spiegazioni
4. **Common Pitfalls**: Errori tipici da evitare
5. **Related Topics**: Link ad altre guide pertinenti
```

### **Docstring Standard (NumPy Style)**
```python
def build_motor(config: MotorConfig, output_dir: Path) -> Motor:
    """
    Build a RocketPy Motor object from configuration.

    This function creates a RocketPy SolidMotor, HybridMotor, or LiquidMotor
    based on the provided configuration, handling thrust curve interpolation,
    grain geometry, and nozzle calculations.

    Parameters
    ----------
    config : MotorConfig
        Motor configuration containing thrust curve path, geometry parameters,
        and propellant properties. See :class:`MotorConfig` for details.
    output_dir : pathlib.Path
        Directory where motor state files and plots will be saved.
        Must exist and be writable.

    Returns
    -------
    rocketpy.Motor
        Configured Motor object ready for flight simulation.

    Raises
    ------
    FileNotFoundError
        If thrust curve file specified in config does not exist.
    ValueError
        If motor parameters are physically invalid (e.g., negative mass).

    See Also
    --------
    MotorConfig : Configuration dataclass for motor parameters
    validate_motor : Validation function for motor physical plausibility
    export_motor_state : Export motor attributes and curves

    Notes
    -----
    - Thrust curve is automatically interpolated to 0.1s resolution
    - Grain geometry is validated for physical consistency
    - Motor coordinate system: nozzle (0) → combustion chamber (+)

    Examples
    --------
    >>> from pathlib import Path
    >>> config = MotorConfig(
    ...     thrust_source="motors/Cesaroni_M1670.eng",
    ...     dry_mass=1.815,
    ...     dry_inertia=(0.125, 0.125, 0.002),
    ...     nozzle_radius=0.033,
    ...     grain_outer_radius=0.033,
    ...     grain_initial_inner_radius=0.015,
    ...     grain_initial_height=0.120,
    ...     grain_separation=0.005,
    ...     grain_density=1815,
    ...     grain_number=5,
    ...     nozzle_position=0.0,
    ...     center_of_dry_mass_position=0.317
    ... )
    >>> motor = build_motor(config, Path("outputs/test_motor"))
    >>> print(f"Total impulse: {motor.total_impulse:.0f} Ns")
    Total impulse: 5683 Ns

    References
    ----------
    .. [1] RocketPy Motor Documentation: https://docs.rocketpy.org/
    .. [2] Sutton, G. P., & Biblarz, O. (2016). Rocket Propulsion Elements.
    """
```

---

## 📝 Template per Ogni Tipo di Documento

### **Tutorial Template**
```rst
Tutorial: [Task Name]
=====================

.. admonition:: Learning Objectives
   :class: tip

   By the end of this tutorial, you will be able to:
   
   * [Objective 1]
   * [Objective 2]
   * [Objective 3]

Prerequisites
-------------

Before starting, ensure you have:

* Installed rocket-sim (see :doc:`/getting_started/installation`)
* Basic understanding of [concept] (see :doc:`/getting_started/key_concepts`)
* [Other requirements]

.. note::
   Estimated time: [X] minutes

Step 1: [Action]
----------------

[Explanation of what we're doing and why]

.. code-block:: python

   # Complete, working code
   from rocket_sim import ...

Expected output:

.. code-block:: text

   [What user should see]

Step 2: [Next Action]
---------------------

[Continue...]

Complete Example
----------------

Here's the complete working code:

.. literalinclude:: ../../examples/tutorial_01.py
   :language: python
   :caption: Complete example code

Download: :download:`tutorial_01.py <../../examples/tutorial_01.py>`

What You've Learned
-------------------

In this tutorial, you:

* [Summary of what was learned]
* [Key takeaways]

Next Steps
----------

Now that you understand [X], you can:

* :doc:`tutorial_02` - Learn about [next topic]
* :doc:`../how_to_guides/configure_rocket` - Apply this to custom rockets

See Also
--------

* :class:`~rocket_sim.MotorBuilder` - API reference
* :doc:`/reference/configuration_schema` - Full parameter list
```

### **How-To Guide Template**
```rst
How to [Specific Task]
======================

.. admonition:: Quick Answer
   :class: tip

   [2-3 line answer for experienced users]

Problem
-------

[Clear problem statement - what user wants to achieve]

Solution
--------

[Step-by-step solution]

1. [Step 1]

   .. code-block:: yaml

      # Configuration snippet
      parameter: value

2. [Step 2]

   .. code-block:: python

      # Python code if needed

Complete Example
----------------

[Full working example]

Common Pitfalls
---------------

.. warning::
   **[Common mistake]**: [Explanation and how to avoid]

.. note::
   **[Tip]**: [Helpful advice]

Explanation
-----------

[Deeper explanation of why this works, if needed]

Alternatives
------------

[Other approaches to solve the same problem]

See Also
--------

* :doc:`related_guide_1`
* :doc:`../tutorials/tutorial_name`
```

### **API Reference Template**
```rst
:mod:`rocket_sim.module_name`
=============================

.. automodule:: rocket_sim.module_name
   :no-members:
   :no-inherited-members:

Module description and purpose.

Classes
-------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   ClassName1
   ClassName2

Functions
---------

.. autosummary::
   :toctree: generated/
   :nosignatures:

   function_name_1
   function_name_2

Detailed API
------------

.. autoclass:: ClassName1
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

.. autofunction:: function_name_1
```

---

## 🎨 Elementi Visivi e Navigazione

### **Admonitions da Usare**
```rst
.. note::
   Informazione generale utile

.. tip::
   Suggerimento pratico per migliorare workflow

.. warning::
   Attenzione a potenziali problemi

.. danger::
   Azione che può causare errori gravi

.. seealso::
   Riferimenti correlati

.. versionadded:: 1.2.0
   Descrizione nuova funzionalità

.. deprecated:: 1.3.0
   Usa :func:`new_function` invece
```

### **Cross-References**
```rst
# Riferimento a documento
:doc:`/getting_started/installation`

# Riferimento a sezione
:ref:`section-label`

# Riferimento a classe
:class:`~rocket_sim.MotorBuilder`

# Riferimento a funzione
:func:`~rocket_sim.build_motor`

# Riferimento a parametro
:attr:`MotorConfig.thrust_source`

# Download file
:download:`example.yaml <../../configs/example.yaml>`
```

### **Indici e Navigazione**
```rst
# Ogni pagina principale deve avere TOC
.. toctree::
   :maxdepth: 2
   :caption: Contenuti:

   section1/index
   section2/index

# Glossario globale
.. glossary::

   apogee
      The highest point in a rocket's trajectory.

   burn time
      Duration of motor thrust phase.

# Usare glossario
The rocket reaches its :term:`apogee` after burnout.
```

---

## 🧪 Esempi e Notebooks

### **Esempi da Creare**
```
examples/
├── basic/
│   ├── 01_minimal_flight.py          # Assoluto minimo per volare
│   ├── 02_adding_fins.py             # Aggiungere superfici aerodinamiche
│   └── 03_custom_plots.py            # Personalizzare output
├── intermediate/
│   ├── 01_weather_integration.py     # Usare dati atmosferici reali
│   ├── 02_motor_comparison.py        # Confrontare più motori
│   └── 03_air_brakes_basic.py        # Air brakes semplici
├── advanced/
│   ├── 01_custom_drag_curve.py       # Curve di drag personalizzate
│   ├── 02_pid_tuning.py              # Tuning controller PID
│   └── 03_batch_simulations.py       # Simulazioni multiple
└── complete_rockets/
    ├── calisto_recreation.py          # Replicare razzi famosi
    ├── competition_rocket.py          # Setup per competizioni
    └── research_vehicle.py            # Veicolo da ricerca
```

### **Notebooks da Creare**
```
notebooks/
├── 00_installation_check.ipynb        # Verifica setup
├── 01_first_flight.ipynb              # Prima simulazione guidata
├── 02_understanding_outputs.ipynb     # Esplorare i risultati
├── 03_parameter_sensitivity.ipynb     # Effetto dei parametri
├── 04_real_world_weather.ipynb        # Dati atmosferici reali
└── 05_visualization_guide.ipynb       # Creare plot professionali
```

**Requisiti per ogni notebook:**
- Celle eseguibili dall'inizio alla fine senza errori
- Output salvati per visualizzazione su GitHub
- Spiegazioni markdown tra celle di codice
- "What you'll learn" all'inizio
- "Next steps" alla fine

---

## ✅ Checklist Pre-Pubblicazione

### **Per Ogni Pagina di Documentazione**
- [ ] Lingua inglese consistente (no mix italiano)
- [ ] Formattazione RST corretta (build Sphinx senza warning)
- [ ] Cross-reference funzionanti
- [ ] Codice testato ed eseguibile
- [ ] Esempi con output attesi
- [ ] Glossario per termini tecnici
- [ ] Link "See Also" pertinenti
- [ ] Versioning chiaro se applicabile

### **Per Ogni Esempio/Tutorial**
- [ ] Codice completo e funzionante
- [ ] Commenti chiari ed esplicativi
- [ ] Output salvato e verificato
- [ ] Requisiti/prerequisiti elencati
- [ ] Download disponibile
- [ ] Integrato nella navigazione docs

### **Per API Reference**
- [ ] Docstring NumPy-style per tutte le funzioni pubbliche
- [ ] Type hints corretti
- [ ] Esempi nella docstring (testabili con doctest)
- [ ] Parameters/Returns/Raises documentati
- [ ] See Also section con cross-ref
- [ ] Auto-generated con Sphinx autodoc

### **Build e Deploy**
- [ ] `make html` senza warning
- [ ] `make linkcheck` passa
- [ ] `make doctest` passa (esempi testati)
- [ ] Navigazione funzionante
- [ ] Ricerca funzionante
- [ ] Mobile-responsive
- [ ] Deploy su Read the Docs / GitHub Pages

---

## 🚀 Piano di Implementazione

### **Fase 1: Fondamenta (Settimana 1-2)**
1. Ristrutturare albero directory documentazione
2. Setup Sphinx con tema professionale (sphinx-rtd-theme o sphinx-book-theme)
3. Configurare autodoc per API reference
4. Creare template base per ogni tipo di documento
5. Implementare Getting Started completo

### **Fase 2: Contenuti Core (Settimana 3-4)**
1. Scrivere tutorial progressivi (basic → advanced)
2. Creare how-to guides per task comuni
3. Documentare tutti i parametri di configurazione
4. Aggiornare/testare tutti gli esempi esistenti
5. Creare nuovi esempi mancanti

### **Fase 3: Reference e Dettagli (Settimana 5-6)**
1. Completare API reference con docstring
2. Documentare tutti i file di output
3. Creare schema di validazione completo
4. Scrivere FAQ da problemi comuni
5. Aggiungere glossario e bibliografia

### **Fase 4: Polish e Test (Settimana 7)**
1. Revisione completa coerenza e qualità
2. Testing di tutti gli esempi
3. Link checking e validazione
4. Feedback da utenti beta
5. Correzioni finali

### **Fase 5: Deploy (Settimana 8)**
1. Setup Read the Docs / GitHub Pages
2. Configurare build automatiche
3. Versioning della documentazione
4. Annuncio e comunicazione

---

## 📊 Metriche di Successo

La documentazione sarà considerata di successo se:

- ✅ Un nuovo utente può fare la prima simulazione in < 10 minuti
- ✅ Ogni parametro di configurazione ha spiegazione + esempio
- ✅ Zero domande ricorrenti senza risposta in FAQ
- ✅ Sphinx build senza warning
- ✅ Tutti gli esempi eseguibili e testati
- ✅ Feedback utenti: "chiaro e utile" > 90%
- ✅ Tempo medio per trovare informazione < 2 minuti
- ✅ Mobile navigation funzionante

---

## 🎓 Risorse e Riferimenti

### **Guide di Stile**
- [Google Developer Documentation Style Guide](https://developers.google.com/style)
- [Write the Docs - Documentation Guide](https://www.writethedocs.org/guide/)
- [Diátaxis Framework](https://diataxis.fr/) - Tutorial/How-To/Reference/Explanation

### **Esempi Excellence**
- [RocketPy Docs](https://docs.rocketpy.org/)
- [NumPy User Guide](https://numpy.org/doc/stable/user/)
- [SciPy Tutorial](https://docs.scipy.org/doc/scipy/tutorial/)
- [Django Documentation](https://docs.djangoproject.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### **Tools**
- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/) - Markdown in Sphinx
- [sphinx-autobuild](https://github.com/executablebooks/sphinx-autobuild) - Live reload
- [sphinx-copybutton](https://sphinx-copybutton.readthedocs.io/) - Copy code blocks

---

## 💡 Principi Guida Finali

1. **User First**: Ogni pagina deve rispondere a "perché l'utente ha bisogno di questo?"
2. **Show, Don't Tell**: Esempi concreti > descrizioni astratte
3. **Progressive Disclosure**: Base → Intermedio → Avanzato
4. **Consistency**: Stesso stile, formato, terminologia ovunque
5. **Testability**: Ogni esempio deve essere verificabile
6. **Maintainability**: Documentazione facile da aggiornare
7. **Searchability**: Ottimizzata per trovare informazioni rapidamente
8. **Accessibility**: Navigabile da tutti gli utenti

---

## ✨ Obiettivo Finale

> "La documentazione deve essere così chiara che un utente senza esperienza precedente possa simulare il suo primo razzo in 10 minuti, e un utente esperto possa trovare qualsiasi informazione tecnica in meno di 2 minuti."

**Target Audience:**
- Studenti universitari (ingegneria aerospaziale, fisica)
- Team di rocketry studenteschi
- Ricercatori in propulsione
- Hobbisti high-power rocketry

**Tone:** Professionale, preciso, educativo, accessibile

**Outcome:** Documentazione che diventa **riferimento** per simulazioni razzo in Python, benchmark di qualità nel settore.

---

*Questo prompt è la guida completa per trasformare la documentazione attuale in un asset professionale di eccellenza.*
