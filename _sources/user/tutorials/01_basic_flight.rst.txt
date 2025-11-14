Tutorial 1: Basic Flight Simulation
====================================

.. admonition:: What You'll Learn
   :class: tip

   In this tutorial, you will:
   
   * Create a complete rocket configuration from scratch
   * Understand each configuration parameter
   * Run a simulation and interpret results
   * Modify parameters to see their effects

.. admonition:: Prerequisites
   :class: note

   * Completed :doc:`/getting_started/installation`
   * Completed :doc:`/getting_started/quickstart`
   * Basic understanding of :doc:`/getting_started/key_concepts`
   
   **Time required**: ~15 minutes

Introduction
------------

In the quickstart, you ran a pre-made configuration. Now you'll build one from scratch
to understand exactly what each parameter does and why it matters.

We'll simulate a simple high-power rocket:

* **Name**: "Tutorial Rocket"
* **Motor**: AeroTech J450DM (readily available commercial motor)
* **Target altitude**: ~500 meters
* **Recovery**: Single parachute

Step 1: Create Configuration File
----------------------------------

Create a new file ``configs/tutorial_rocket.yaml``:

.. code-block:: bash

   cd /path/to/rocket-sim
   touch configs/tutorial_rocket.yaml

Open it in your preferred editor and start with the basic structure:

.. code-block:: yaml

   # Tutorial Rocket Configuration
   # A simple high-power rocket for learning
   
   rocket:
     # Rocket parameters go here
   
   motor:
     # Motor parameters go here
   
   environment:
     # Environment parameters go here
   
   simulation:
     # Simulation parameters go here

This four-section structure is mandatory. Let's fill each section.

Step 2: Configure the Rocket
-----------------------------

The rocket section defines physical properties. Add these parameters:

.. code-block:: yaml

   rocket:
     name: "Tutorial Rocket"
     
     # Mass and inertia
     mass: 5.0                    # kg (dry mass, without motor)
     radius: 0.052                # m (outer radius, ~4 inch diameter)
     inertia: [0.8, 0.8, 0.003]   # kg⋅m² [I_longitudinal, I_longitudinal, I_spin]
     center_of_mass_without_motor: 0.8  # m from nose tip
     
     # Coordinate system convention: nose tip is 0.0, tail is negative
     
     # Nose cone
     nose_cone:
       length: 0.3                # m
       kind: "vonKarman"          # Aerodynamic shape (low drag)
       position: 1.2              # m from tail (rocket is 1.2m long)
     
     # Body tube (implicitly defined by radius and rocket length)
     
     # Fins (trapezoidal)
     fins:
       number: 3                  # 3-fin configuration
       root_chord: 0.15           # m (fin length at body tube)
       tip_chord: 0.08            # m (fin length at tip)
       span: 0.12                 # m (fin height from body to tip)
       position: 0.1              # m from tail (aft of rocket)
       cant_angle: 0              # degrees (0 = no spin)
       airfoil: null              # Use flat plate (simple)
     
     # Motor position
     motor_position: -0.5         # m from nose tip (negative = toward tail)
     
     # Recovery system
     parachutes:
       - name: "Main"
         cd_s: 1.5                # Drag coefficient × area (m²)
         trigger: "apogee"        # Deploy at highest point
         sampling_rate: 105       # Hz
         lag: 1.5                 # seconds (delay after trigger)
         noise: [0, 8.3, 0.5]     # [mean, std_dev, time_correlation]
     
     # Aerodynamics (let RocketPy calculate)
     power_off_drag: null         # Auto-calculate from geometry
     power_on_drag: null          # Auto-calculate from geometry

**Understanding the Parameters:**

* ``mass``: Rocket without motor (weigh all components except motor)
* ``radius``: Outer radius of body tube (diameter / 2)
* ``inertia``: Moment of inertia (can estimate or calculate)
* ``center_of_mass_without_motor``: Balance point without motor
* ``motor_position``: Where motor is mounted (negative = toward tail from nose)

.. seealso::
   For detailed parameter explanations, see :doc:`/user/configuration/rocket_params`.

Step 3: Configure the Motor
----------------------------

We'll use an AeroTech J450DM motor. Add this to the ``motor`` section:

.. code-block:: yaml

   motor:
     # Thrust curve source
     thrust_source: "data/motors/aerotech/AeroTech_J450DM.eng"
     
     # Motor properties
     dry_mass: 0.457              # kg (empty motor casing)
     dry_inertia: [0.015, 0.015, 0.0001]  # kg⋅m² (motor tube inertia)
     
     # Nozzle
     nozzle_radius: 0.025         # m
     
     # Grain geometry (BATES grain configuration)
     grain_number: 4              # Number of propellant grains
     grain_density: 1750          # kg/m³ (APCP propellant)
     grain_outer_radius: 0.0335   # m
     grain_initial_inner_radius: 0.015  # m (core diameter)
     grain_initial_height: 0.070  # m (grain length)
     grain_separation: 0.003      # m (gap between grains)
     
     # Positions (in motor coordinate system: nozzle is 0.0)
     nozzle_position: 0.0         # m
     grains_center_of_mass_position: 0.12  # m
     center_of_dry_mass_position: 0.14     # m
     
     # Burn characteristics
     throat_radius: 0.012         # m
     interpolation_method: "linear"

**Key Points:**

* ``thrust_source``: Path to `.eng` file (RASP format)
* ``dry_mass``: Empty motor casing (not including propellant)
* Grain parameters define propellant geometry (affects burn profile)

.. note::
   Motor `.eng` files can be downloaded from `ThrustCurve.org <http://www.thrustcurve.org/>`_.
   The file includes thrust curve data that RocketPy will read automatically.

**Where to get the .eng file:**

.. code-block:: bash

   # Download from ThrustCurve.org or use included example
   mkdir -p data/motors/aerotech
   # Copy AeroTech_J450DM.eng to that directory

Step 4: Configure the Environment
----------------------------------

Define launch site atmospheric conditions:

.. code-block:: yaml

   environment:
     # Launch location
     latitude: 35.5495            # degrees North (example: Oklahoma)
     longitude: -105.0000         # degrees West
     elevation: 1500              # m above sea level
     
     # Date (optional, for solar activity)
     date: [2025, 6, 15, 12]      # [year, month, day, hour(UTC)]
     
     # Atmospheric model
     atmospheric_model_type: "StandardAtmosphere"  # ISA model
     
     # Wind (optional)
     # For now, use no wind (calm day)

**Explanation:**

* ``latitude/longitude``: Launch site coordinates
* ``elevation``: Altitude of launch site
* ``atmospheric_model_type``: 
  
  * ``"StandardAtmosphere"``: ISA 1976 model (simple, repeatable)
  * ``"Forecast"``: Real weather data (advanced)
  * ``"Reanalysis"``: Historical weather (advanced)

Step 5: Configure the Simulation
---------------------------------

Set launch parameters:

.. code-block:: yaml

   simulation:
     # Launch angle
     inclination: 85              # degrees from horizontal (85° ≈ vertical)
     heading: 90                  # degrees (0=N, 90=E, 180=S, 270=W)
     
     # Launch rail
     rail_length: 3.0             # m (guides rocket until stable)
     
     # Simulation limits (optional)
     max_time: 300                # seconds (stop simulation after 5 min)
     time_step: null              # Use adaptive step (recommended)

**Understanding Launch Angles:**

.. code-block:: text

   inclination = 85°:  Nearly vertical (5° from vertical)
   heading = 90°:      Launches toward East
   
   Typical range: 80-90° for high-power rockets

Step 6: Validate Configuration
-------------------------------

Save your ``configs/tutorial_rocket.yaml`` file. Now validate it:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config configs/tutorial_rocket.yaml \
       --name tutorial_test \
       --validate-only

This checks:

* ✅ YAML syntax is correct
* ✅ All required parameters present
* ✅ Parameters physically plausible
* ✅ Rocket is statically stable (static margin ≥ 2)

**If validation fails:**

Read the error message carefully - it will tell you exactly what's wrong and suggest fixes.

Common issues:

* Typo in parameter name
* Missing required parameter
* Value out of physical range (e.g., negative mass)
* Static margin < 2 (unstable rocket)

Step 7: Run the Simulation
---------------------------

Once validation passes, run the full simulation:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config configs/tutorial_rocket.yaml \
       --name tutorial_rocket \
       --plots \
       --verbose

**Expected Output:**

.. code-block:: text

   ════════════════════════════════════════════════════════════════
                    ROCKET SIMULATION FRAMEWORK
   ════════════════════════════════════════════════════════════════
   
   [CONFIG] Loading configuration: configs/tutorial_rocket.yaml
   [VALID] Configuration validation: PASSED
   [BUILD] Building Motor... OK
   [BUILD] Building Environment... OK
   [BUILD] Building Rocket... OK
   [SIM] Running flight simulation...
   [SIM] Simulation completed in 1.8s
   
   ┌─────────────────────────────────────────────────────────────┐
   │                    FLIGHT SUMMARY                           │
   ├─────────────────────────────────────────────────────────────┤
   │ Apogee Altitude:        524.8 m                             │
   │ Apogee Time:            8.2 s                               │
   │ Max Velocity:           142.3 m/s                           │
   │ Max Acceleration:       201.5 m/s²                          │
   │ Impact Velocity:        4.8 m/s                             │
   │ Flight Time:            58.4 s                              │
   └─────────────────────────────────────────────────────────────┘
   
   ✓ Simulation completed successfully!

Step 8: Examine the Results
----------------------------

Navigate to the output directory:

.. code-block:: bash

   cd outputs/tutorial_rocket/
   ls -la

You'll find:

.. code-block:: text

   tutorial_rocket/
   ├── plots/
   │   ├── trajectory_3d.png           # 3D flight path
   │   ├── altitude_vs_time.png        # Altitude profile
   │   ├── velocity_vs_time.png        # Velocity over time
   │   └── acceleration_vs_time.png    # Acceleration (g-forces)
   ├── trajectory/
   │   ├── trajectory.csv              # Time-series data
   │   └── trajectory.kml              # Google Earth format
   ├── motor/
   │   ├── motor_attributes.txt        # Motor properties
   │   └── curves/                     # Thrust, mass, inertia curves
   └── final_state                     # End state of simulation

**Key Files to Check:**

1. **plots/altitude_vs_time.png**: Shows flight profile

   * Powered ascent (steep climb)
   * Coasting phase (curve flattens)
   * Apogee (peak)
   * Parachute descent (gentle slope down)

2. **trajectory/trajectory.csv**: Full data for analysis

   Open in Excel/Python to analyze:
   
   * Peak altitude vs time
   * Maximum velocity
   * G-forces during boost

Step 9: Understand What Happened
---------------------------------

Let's interpret the flight:

**Phase 1: Launch (0-0.5s)**
   Rocket accelerates on rail, fins not yet effective

**Phase 2: Powered Ascent (0.5-2.5s)**
   Motor burning, thrust > drag + gravity, rocket accelerates upward
   
   * Check ``velocity_vs_time.png``: velocity increasing
   * Check ``acceleration_vs_time.png``: high acceleration

**Phase 3: Coasting (2.5-8.2s)**
   Motor burnout, rocket continues upward on momentum
   
   * Velocity decreases due to drag and gravity
   * Still climbing but slowing down

**Phase 4: Apogee (8.2s)**
   Velocity = 0, highest point reached (~525m)
   
   * Parachute deployment triggered
   * Rocket orientation becomes unstable (doesn't matter, parachute is out)

**Phase 5: Descent (8.2-58.4s)**
   Parachute open, slow descent
   
   * Terminal velocity ~5 m/s (safe landing)
   * Drifts with wind (if any)

**Phase 6: Impact (58.4s)**
   Rocket hits ground at 4.8 m/s (acceptable)

Step 10: Experiment with Parameters
------------------------------------

Now modify parameters to see effects. Try these experiments:

**Experiment 1: Heavier Rocket**

Change ``rocket.mass`` from 5.0 to 7.0 kg:

.. code-block:: yaml

   rocket:
     mass: 7.0  # Was 5.0

Run simulation again with ``--name tutorial_heavy``.

**Question**: Did apogee increase or decrease? Why?

**Answer**: Decreased (heavier rocket fights gravity more, same motor power)

**Experiment 2: Larger Parachute**

Change ``cd_s`` from 1.5 to 3.0:

.. code-block:: yaml

   parachutes:
     - name: "Main"
       cd_s: 3.0  # Was 1.5

**Question**: How does landing velocity change?

**Answer**: Slower descent, gentler landing

**Experiment 3: Launch Angle**

Change ``inclination`` from 85 to 80 degrees:

.. code-block:: yaml

   simulation:
     inclination: 80  # Was 85

**Question**: What happens to trajectory shape?

**Answer**: More horizontal travel, apogee farther from launch site

Step 11: Common Issues and Solutions
-------------------------------------

.. dropdown:: "Static margin less than 2 calibers"
   :color: danger

   **Problem**: Rocket is aerodynamically unstable.
   
   **Solution**: 
   
   * Move fins farther from nose (increase ``fins.position``)
   * Make fins larger (increase ``fins.span`` or ``fins.root_chord``)
   * Move center of mass forward (reduce ``center_of_mass_without_motor``)

.. dropdown:: "Motor thrust curve file not found"
   :color: warning

   **Problem**: Path to ``.eng`` file is wrong.
   
   **Solution**:
   
   * Check file exists: ``ls data/motors/aerotech/AeroTech_J450DM.eng``
   * Use absolute path or correct relative path
   * Download motor file from ThrustCurve.org if missing

.. dropdown:: "Parachute never deploys"
   :color: warning

   **Problem**: Trigger condition not met or wrong configuration.
   
   **Solution**:
   
   * Check ``trigger: "apogee"`` is correct
   * Verify rocket reaches apogee (doesn't crash during ascent)
   * Check for typos in parachute configuration

.. dropdown:: "Simulation takes too long"
   :color: info

   **Problem**: Simulation running for unrealistic time.
   
   **Solution**:
   
   * Set ``max_time: 300`` to limit simulation
   * Check rocket actually lands (impact detected)
   * Verify environment makes physical sense

What You've Learned
-------------------

Congratulations! You've now:

✅ Created a complete rocket configuration from scratch

✅ Understood the four main sections (rocket, motor, environment, simulation)

✅ Run a simulation and interpreted the results

✅ Explored how parameter changes affect flight

✅ Debugged common configuration issues

Next Steps
----------

Now you're ready for more advanced topics:

* :doc:`02_understanding_outputs` - Deep dive into data analysis
* :doc:`03_custom_motor` - Import your own motor data
* :doc:`04_adding_fins` - Advanced fin configurations
* :doc:`/user/how_to_guides/measure_rocket` - Measure real rocket parameters

Complete Example File
---------------------

Here's the complete ``tutorial_rocket.yaml`` configuration:

.. literalinclude:: /../../configs/templates/tutorial_rocket.yaml
   :language: yaml
   :caption: configs/tutorial_rocket.yaml

.. note::
   This file is available in the rocket-sim repository at
   ``configs/tutorial_rocket.yaml``. You can use it as a template for your own rockets.

Further Reading
---------------

* :doc:`/user/configuration/rocket_params` - Every rocket parameter explained
* :doc:`/user/configuration/motor_params` - Motor parameter details
* :doc:`/getting_started/key_concepts` - Review core concepts
* `RocketPy Documentation <https://docs.rocketpy.org/>`_ - Underlying library

.. seealso::

   **Related How-To Guides:**
   
   * :doc:`/user/how_to_guides/create_config` - Configuration best practices
   * :doc:`/user/how_to_guides/validate_design` - Stability validation
   * :doc:`/user/how_to_guides/troubleshooting_validation` - Fix validation errors
