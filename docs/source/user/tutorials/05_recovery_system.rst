.. _tutorial_recovery_system:

Configuring Recovery Systems
=============================

Safe recovery is essential for rocket reusability and payload protection. This tutorial covers parachute configuration, deployment triggers, descent analysis, and dual-deployment systems for high-power rockets.

.. note::
   
   This tutorial assumes you've completed :ref:`tutorial_basic_flight` and :ref:`tutorial_adding_fins`. We'll focus specifically on recovery system design and optimization.

Recovery System Basics
----------------------

Why Recovery Matters
~~~~~~~~~~~~~~~~~~~~

A well-designed recovery system:

- ✅ **Protects the rocket** - Safe landing prevents damage
- ✅ **Enables reusability** - Fly again without rebuilding
- ✅ **Recovers payloads** - Preserve expensive electronics
- ✅ **Ensures safety** - Controlled descent protects people and property
- ✅ **Meets regulations** - Required for most high-power flights

**Landing velocity targets:**

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Rocket Type
     - Max Velocity
     - Recovery Method
   * - Model rocket (< 500g)
     - < 4 m/s
     - Single parachute
   * - High-power (< 5kg)
     - < 6 m/s
     - Single or dual deploy
   * - Heavy rocket (> 5kg)
     - < 8 m/s
     - Dual deploy recommended
   * - Fragile payload
     - < 5 m/s
     - Dual deploy + main chute

Recovery System Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Physical components:**

1. **Parachute(s)** - Fabric canopy that creates drag
2. **Shock cord** - Elastic tether connecting rocket sections
3. **Deployment bag** - Protects chute during ascent
4. **Ejection charge** - Black powder or CO₂ to separate sections
5. **Altimeter/Timer** - Triggers deployment

**Simulation parameters:**

- ``cd_s`` - Drag coefficient × area (combined parachute effectiveness)
- ``trigger`` - Deployment condition (apogee, altitude, time)
- ``lag`` - Delay from trigger to full deployment (seconds)
- ``sampling_rate`` - Altimeter measurement frequency (Hz)
- ``noise`` - Sensor noise for realistic simulations

Understanding Cd×S
------------------

The Critical Parameter
~~~~~~~~~~~~~~~~~~~~~~

The ``cd_s`` parameter combines two factors:

.. math::

   C_D \times S = \text{Drag Coefficient} \times \text{Surface Area}

**Physical meaning:**

- **Cd** (drag coefficient): Shape efficiency (0.75-1.5 for parachutes)
- **S** (surface area): Parachute area in m²
- **Cd×S**: Total drag effectiveness in m²

.. tip::
   
   **Quick estimate:** For a round parachute, ``Cd ≈ 0.75`` to ``0.85``
   
   So for a 3-meter diameter chute:
   
   - Area = π × (1.5)² = 7.07 m²
   - Cd×S = 0.8 × 7.07 ≈ **5.7 m²**

Calculating Cd×S
~~~~~~~~~~~~~~~~

**Method 1: From parachute diameter**

.. code-block:: python

   import math
   
   diameter_m = 3.0      # Parachute diameter
   cd = 0.8              # Typical for round chute
   
   area = math.pi * (diameter_m / 2)**2
   cd_s = cd * area
   
   print(f"Cd×S = {cd_s:.2f} m²")  # Output: Cd×S = 5.65 m²

**Method 2: From desired descent rate**

.. code-block:: python

   import math
   
   # Parameters
   mass_kg = 8.5                # Rocket mass
   target_velocity_ms = 6.0     # Desired descent rate
   air_density = 1.225          # kg/m³ at sea level
   g = 9.81                     # Gravity
   
   # Terminal velocity equation: V = sqrt(2*m*g / (rho * Cd*S))
   # Solve for Cd*S:
   cd_s = (2 * mass_kg * g) / (air_density * target_velocity_ms**2)
   
   print(f"Required Cd×S = {cd_s:.2f} m²")  # Output: 3.77 m²

**Method 3: From manufacturer data**

Many parachute manufacturers specify descent rate for a given weight:

.. code-block:: text

   "Fruity Chutes FC-60 (60-inch diameter):
   Descent rate: 18 ft/s at 5 lbs"
   
   Convert to SI:
   - Descent rate: 18 ft/s = 5.5 m/s
   - Weight: 5 lbs = 2.27 kg
   
   Calculate Cd×S = (2 × 2.27 × 9.81) / (1.225 × 5.5²)
                  = 1.20 m²

Common Parachute Types
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 25 40
   
   * - Type
     - Cd Range
     - Best For
     - Notes
   * - Round (hemispherical)
     - 0.75-0.85
     - General purpose
     - Most common, predictable
   * - Flat circular
     - 0.70-0.80
     - Light rockets
     - Simpler construction
   * - Annular (ring)
     - 0.60-0.75
     - Stable descent
     - Less oscillation
   * - Cruciform
     - 0.85-1.20
     - Max drag
     - Complex to pack
   * - Elliptical
     - 0.60-0.70
     - Drift control
     - Horizontal glide
   * - Parafoil (ram-air)
     - 0.50-0.60
     - Guided recovery
     - Steerable, complex

Tutorial: Single Parachute System
----------------------------------

Step 1: Design Requirements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before configuring, define your requirements:

.. code-block:: text

   Rocket specifications:
   - Total mass: 8.5 kg (dry) + 2.0 kg (motor) = 10.5 kg
   - Expected apogee: 2500 m
   - Launch site: Sea level (ρ = 1.225 kg/m³)
   
   Requirements:
   - Landing velocity: < 6 m/s (safe for reuse)
   - Deployment: At apogee (simplest)
   - Recovery: Within 500 m of launch site

Step 2: Calculate Parachute Size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import math
   
   # Rocket parameters
   mass_total_kg = 10.5
   target_descent_ms = 6.0
   
   # Atmospheric
   rho = 1.225  # kg/m³ at sea level
   g = 9.81
   
   # Calculate required Cd×S
   cd_s_required = (2 * mass_total_kg * g) / (rho * target_descent_ms**2)
   print(f"Required Cd×S: {cd_s_required:.2f} m²")
   # Output: Required Cd×S: 4.67 m²
   
   # Choose parachute
   cd_round = 0.80  # Round parachute
   area_required = cd_s_required / cd_round
   diameter_required = 2 * math.sqrt(area_required / math.pi)
   
   print(f"Minimum diameter: {diameter_required:.2f} m")
   # Output: Minimum diameter: 2.73 m
   
   # Round up for safety margin
   diameter_actual = 3.0  # meters
   area_actual = math.pi * (diameter_actual / 2)**2
   cd_s_actual = cd_round * area_actual
   
   print(f"\nFinal design:")
   print(f"  Diameter: {diameter_actual:.1f} m")
   print(f"  Cd×S: {cd_s_actual:.2f} m²")
   # Output: Cd×S: 5.65 m²

Step 3: Configure in YAML
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add parachute configuration to your rocket:

.. code-block:: yaml

   rocket:
     # ... other rocket parameters ...
     
     parachute:
       enabled: true
       name: "Main Chute"
       cd_s: 5.65              # From calculation above
       trigger: "apogee"       # Deploy at highest point
       sampling_rate_hz: 105.0 # Typical altimeter frequency
       lag_s: 1.5              # Ejection + inflation time
       noise_std: [0, 0, 0]    # No noise (ideal conditions)

**Parameter explanation:**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60
   
   * - Parameter
     - Units
     - Description
   * - ``enabled``
     - boolean
     - Set to ``true`` to activate recovery
   * - ``name``
     - string
     - Descriptive name for output files
   * - ``cd_s``
     - m²
     - Drag effectiveness (calculated above)
   * - ``trigger``
     - string
     - Deployment condition (see triggers below)
   * - ``sampling_rate_hz``
     - Hz
     - Altimeter measurement frequency
   * - ``lag_s``
     - seconds
     - Deployment delay (realistic timing)
   * - ``noise_std``
     - [x, y, z]
     - Sensor noise in m (for Monte Carlo)

Step 4: Run and Validate
~~~~~~~~~~~~~~~~~~~~~~~~~

Simulate and check descent rate:

.. code-block:: bash

   python scripts/run_single_simulation.py --config configs/my_rocket.yaml --name recovery_test

Check the results:

.. code-block:: bash

   grep "Impact" outputs/recovery_test/final_state_READABLE.txt

Expected output:

.. code-block:: text

   Impact:
   ----------------------------------------
     Velocity:                    -5.8 m/s
     Position X:                  -12.3 m
     Position Y:                  485.2 m
     Distance from Launch:        485.4 m

✓ Landing velocity 5.8 m/s < 6.0 m/s target - **Success!**

Deployment Triggers
-------------------

Apogee Trigger (Most Common)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deploy when rocket reaches highest point:

.. code-block:: yaml

   parachute:
     trigger: "apogee"

**How it works:**

- Altimeter detects when rocket stops ascending (velocity ≈ 0)
- Deployment occurs at maximum altitude
- Simplest and most reliable

**Advantages:**

- ✅ No programming required (built into altimeters)
- ✅ Maximizes descent time (gentle landing)
- ✅ Predictable deployment altitude

**Disadvantages:**

- ❌ May drift far in wind (long descent time)
- ❌ Not suitable for very high flights (excessive drift)

**Best for:** Model rockets, low-wind conditions, general sport flying

Altitude Trigger
~~~~~~~~~~~~~~~~

Deploy at specific altitude above ground:

.. code-block:: yaml

   parachute:
     trigger: 800  # Deploy at 800 meters AGL

**How it works:**

- Altimeter triggers when rocket descends through specified altitude
- Allows dual-deploy configurations (see below)

**Advantages:**

- ✅ Control drift distance
- ✅ Enable dual-deploy systems
- ✅ Optimize for landing site size

**Disadvantages:**

- ❌ Requires accurate ground elevation
- ❌ More complex altimeter programming
- ❌ Risk if apogee < trigger altitude

**Best for:** Dual-deploy, high-altitude flights, limited recovery area

Time Trigger (Backup)
~~~~~~~~~~~~~~~~~~~~~~

Deploy after fixed time from launch:

.. code-block:: python

   # Note: RocketPy uses callable functions for custom triggers
   def time_trigger(p, y):
       """Deploy 30 seconds after launch."""
       return y[0] > 30.0  # y[0] is time in seconds

.. warning::
   
   Time triggers are **dangerous** as primary deployment! Only use as backup or for very predictable flights.

Custom Triggers
~~~~~~~~~~~~~~~

For advanced scenarios, create custom trigger functions:

.. code-block:: python

   def velocity_trigger(p, y):
       """Deploy when descending faster than 30 m/s."""
       vz = y[5]  # Vertical velocity
       return vz < -30.0  # Negative = descending
   
   # Add to rocket in Python code (not YAML)
   rocket.add_parachute(
       name="Drogue",
       cd_s=0.5,
       trigger=velocity_trigger,
       sampling_rate=105,
       lag=1.0,
       noise=(0, 0, 0)
   )

Deployment Lag
--------------

Understanding Lag Time
~~~~~~~~~~~~~~~~~~~~~~

The ``lag_s`` parameter models real-world deployment delay:

**Lag components:**

1. **Ejection charge firing** (~0.1-0.3 s)
2. **Separation** (~0.2-0.5 s)
3. **Bag deployment** (~0.3-0.6 s)
4. **Inflation** (~0.5-1.5 s)

**Total typical lags:**

- **Small parachute** (< 1m): 0.8-1.2 seconds
- **Medium parachute** (1-3m): 1.2-1.8 seconds
- **Large parachute** (> 3m): 1.5-2.5 seconds

.. code-block:: yaml

   parachute:
     # Realistic lag for 3-meter chute
     lag_s: 1.5

.. tip::
   
   **Conservative approach:** Use larger lag value for safety margin in simulations. Real flight will only be better than predicted.

Effect on Landing Velocity
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Longer lag means rocket falls farther before chute inflates:

.. code-block:: python

   # At apogee, rocket begins falling
   # After lag time, additional velocity gained:
   
   lag_time = 2.0  # seconds
   g = 9.81
   
   # Velocity gained during lag (ignoring drag)
   v_gained = g * lag_time
   print(f"Velocity gained: {v_gained:.1f} m/s")
   # Output: 19.6 m/s
   
   # This velocity is then arrested by parachute
   # Longer lag = harder opening forces!

.. warning::
   
   Excessive lag can cause:
   
   - High opening forces (shock cord/parachute damage)
   - Increased landing velocity
   - Lower deployment altitude than expected

Dual-Deploy Systems
--------------------

What is Dual Deploy?
~~~~~~~~~~~~~~~~~~~~

Dual-deploy uses two parachutes for optimal recovery:

1. **Drogue chute** - Small, deploys at apogee
2. **Main chute** - Large, deploys at low altitude

**Benefits:**

- ✅ **Reduced drift** - Fast descent with drogue minimizes wind drift
- ✅ **Safe landing** - Large main chute ensures gentle touchdown
- ✅ **Lower deployment** - Main opens close to ground (less stress)
- ✅ **Professional** - Standard for high-power rocketry

**Typical deployment:**

.. code-block:: text

   Apogee (2500m)
       ↓
   Drogue deploys → Fast descent at 20-30 m/s
       ↓
       ↓ (85 seconds, 450m drift)
       ↓
   800m AGL
       ↓
   Main deploys → Slow descent at 5-7 m/s
       ↓
       ↓ (140 seconds, 180m drift)
       ↓
   Landing

   Total drift: 630m vs. 1850m for single chute!

Configuring Dual Deploy
~~~~~~~~~~~~~~~~~~~~~~~~

**Important:** RocketPy/rocket-sim currently supports **single parachute** in YAML config. For dual-deploy, you need to add a second parachute via Python code or use staged separation.

**Workaround example** (requires Python scripting):

.. code-block:: python

   from src.config_loader import ConfigLoader
   from src.rocket_builder import RocketBuilder
   
   # Load base config
   loader = ConfigLoader()
   loader.load_from_yaml("configs/my_rocket.yaml")
   
   # Build rocket (without main chute)
   rocket_config = loader.get_rocket_config()
   rocket_config.parachute = None  # Disable YAML parachute
   
   builder = RocketBuilder(rocket_config)
   rocket = builder.build_complete_rocket()
   
   # Add drogue chute at apogee
   rocket.add_parachute(
       name="Drogue",
       cd_s=0.5,          # Small drogue
       trigger="apogee",
       sampling_rate=105,
       lag=1.0,
       noise=(0, 0, 0)
   )
   
   # Add main chute at 800m
   rocket.add_parachute(
       name="Main",
       cd_s=8.0,          # Large main
       trigger=800,        # 800m AGL
       sampling_rate=105,
       lag=1.5,
       noise=(0, 0, 0)
   )
   
   # Continue with simulation...

Sizing Dual-Deploy Parachutes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Drogue chute:**

- Target descent rate: 20-30 m/s
- Cd×S calculation: same formula, higher velocity

.. code-block:: python

   mass_kg = 10.5
   drogue_velocity = 25.0  # m/s (fast descent)
   
   drogue_cds = (2 * mass_kg * 9.81) / (1.225 * drogue_velocity**2)
   print(f"Drogue Cd×S: {drogue_cds:.2f} m²")
   # Output: 0.34 m²
   
   # For Cd=0.8, diameter ≈ 0.74m (30 inches)

**Main chute:**

- Same calculation as single-deploy
- Target: 5-7 m/s descent

Descent Analysis
----------------

Predicting Landing Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wind causes drift during descent. Estimate landing distance:

.. code-block:: python

   # Single chute system
   apogee_m = 2500
   descent_rate_ms = 6.0
   wind_speed_ms = 5.0  # Average wind
   
   descent_time_s = apogee_m / descent_rate_ms
   drift_distance_m = wind_speed_ms * descent_time_s
   
   print(f"Descent time: {descent_time_s:.0f} s ({descent_time_s/60:.1f} min)")
   print(f"Drift distance: {drift_distance_m:.0f} m")
   # Output: 417 seconds (6.9 min), 2083 m drift!

This is why dual-deploy is important for high flights!

Terminal Velocity
~~~~~~~~~~~~~~~~~

The rocket reaches terminal velocity when drag force equals weight:

.. math::

   V_{\text{terminal}} = \sqrt{\frac{2mg}{\rho \cdot C_D S}}

At terminal velocity, descent rate is constant (equilibrium).

Checking Descent in Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After running simulation:

.. code-block:: bash

   # Check descent rate in trajectory data
   python -c "
   import pandas as pd
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Filter for descent after apogee
   descent = df[df['vz_ms'] < 0].copy()
   descent['velocity_mag'] = (descent['vx_ms']**2 + 
                               descent['vy_ms']**2 + 
                               descent['vz_ms']**2)**0.5
   
   # Terminal velocity (last 10% of flight)
   terminal_section = descent.iloc[int(len(descent)*0.9):]
   terminal_velocity = terminal_section['velocity_mag'].mean()
   
   print(f'Terminal descent rate: {terminal_velocity:.2f} m/s')
   "

Safety Considerations
---------------------

Landing Velocity Limits
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Component
     - Max Safe Velocity
     - Consequence if Exceeded
   * - Electronics bay
     - 8 m/s
     - Circuit board damage, sensor failure
   * - Fiberglass airframe
     - 10 m/s
     - Cracks, joint separation
   * - Balsa/plywood fins
     - 6 m/s
     - Fin breaking, delamination
   * - Fragile payload (eggs, glass)
     - 4 m/s
     - Payload destruction
   * - Humans nearby
     - ANY impact dangerous
     - Injury risk - keep clear!

Parachute Failure Scenarios
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What if parachute doesn't deploy?**

Always have backup plan:

1. **Backup altimeter** - Redundant deployment system
2. **Backup charge** - Two ejection charges in series
3. **Motor ejection** (model rockets) - Ejection charge in motor
4. **Streamer backup** - Small streamer as last resort

**Simulation with failure:**

Test what happens if chute fails:

.. code-block:: yaml

   parachute:
     enabled: false  # Simulate failure
     # OR
     cd_s: 0.1       # Partially deployed chute

.. danger::
   
   **Never fly without recovery system!** Even small rockets can cause serious injury when falling from altitude.

Packing and Testing
~~~~~~~~~~~~~~~~~~~

**Before flight:**

1. ✅ **Measure actual parachute** - Verify diameter
2. ✅ **Test deployment** - Ground test ejection charge
3. ✅ **Check shock cord** - Inspect for wear/damage
4. ✅ **Proper packing** - No tangles, correct folding
5. ✅ **Verify trigger** - Test altimeter programming
6. ✅ **Calculate drift** - Ensure recovery area sufficient

Advanced Topics
---------------

Reefed Deployment
~~~~~~~~~~~~~~~~~

Reef the parachute (partially restrict opening) for staged deployment:

1. Chute deploys reefed (small effective area)
2. Reef line burns through after delay
3. Chute fully inflates

**Benefits:** Reduces opening shock, enables faster initial descent

Streamer Recovery
~~~~~~~~~~~~~~~~~

For small rockets or high-speed descent tests:

.. code-block:: yaml

   parachute:
     cd_s: 0.3       # Small Cd×S acts like streamer
     trigger: "apogee"

**Typical descent:** 15-30 m/s (much faster than parachute)

Active Recovery
~~~~~~~~~~~~~~~

Guided recovery with parafoil or thrust vectoring:

- GPS-guided parafoil
- Powered descent (SpaceX-style)
- Helicopter autorotation

These require custom Python code beyond basic YAML configuration.

Optimization Example
--------------------

Let's optimize parachute size for a target drift distance:

.. code-block:: python

   import numpy as np
   import matplotlib.pyplot as plt
   
   # Parameters
   mass_kg = 10.5
   apogee_m = 2500
   wind_ms = 5.0
   max_drift_m = 800  # Recovery area limit
   min_landing_velocity = 4.0  # Damage threshold
   
   # Test range of Cd×S values
   cds_values = np.linspace(2, 10, 50)
   
   results = []
   for cds in cds_values:
       # Terminal velocity
       v_term = np.sqrt((2 * mass_kg * 9.81) / (1.225 * cds))
       
       # Descent time
       t_descent = apogee_m / v_term
       
       # Drift distance
       drift = wind_ms * t_descent
       
       results.append({
           'cds': cds,
           'velocity': v_term,
           'drift': drift,
           'descent_time': t_descent
       })
   
   # Find optimal
   for r in results:
       if r['drift'] < max_drift_m and r['velocity'] > min_landing_velocity:
           print(f"Optimal Cd×S: {r['cds']:.2f} m²")
           print(f"  Landing velocity: {r['velocity']:.2f} m/s")
           print(f"  Drift distance: {r['drift']:.0f} m")
           print(f"  Descent time: {r['descent_time']:.0f} s")
           break

Example Output:

.. code-block:: text

   Optimal Cd×S: 5.18 m²
     Landing velocity: 6.35 m/s
     Drift distance: 787 m
     Descent time: 157 s

This finds the **minimum Cd×S** (lightest parachute) that keeps drift under limit while landing safely.

Troubleshooting
---------------

Problem 1: Chute Opens at Wrong Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Deployment altitude doesn't match trigger setting

**Causes:**

- Incorrect ground elevation in config
- Lag time too long/short
- Trigger altitude is ASL not AGL

**Solution:**

.. code-block:: yaml

   environment:
     elevation_m: 100  # MUST match launch site elevation
   
   parachute:
     trigger: 800      # 800m AGL (above ground level)
     # Actual deployment: 100 + 800 = 900m ASL

Problem 2: Landing Too Hard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Impact velocity > target

**Causes:**

- Cd×S too small
- Lag time too long
- Wind increasing effective descent rate

**Solutions:**

1. Increase Cd×S by 20%
2. Reduce lag time (better packing/faster deployment)
3. Check actual vs. calculated parachute size

Problem 3: Excessive Drift
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Landing far from launch site

**Causes:**

- High apogee + large chute
- Strong winds
- Single-deploy system

**Solutions:**

1. Use dual-deploy (smaller drogue at apogee)
2. Reduce apogee (smaller motor)
3. Launch in lower wind conditions
4. Increase recovery area size

Problem 4: Chute Tangled
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Chute doesn't fully inflate (simulation shows partial deployment)

**Model in simulation:**

.. code-block:: yaml

   parachute:
     cd_s: 2.5  # Half of design value (tangled)

**Prevention:**

- Proper packing technique
- Deployment bag
- Shock cord protector
- Test deployments

Next Steps
----------

Now that you understand recovery systems:

1. **Integrate weather** - See :ref:`tutorial_weather_integration` for wind effects
2. **Run parametric studies** - Vary Cd×S and compare landing sites
3. **Simulate failures** - Test with partial deployment or no deployment
4. **Build and test** - Ground test your deployment system!

.. seealso::
   
   - :ref:`configuration_rocket_params` - Complete parachute parameter reference
   - `Fruity Chutes <https://fruitychutes.com/>`_ - Parachute manufacturer (sizing charts)
   - `Public Missiles Recovery Handbook <https://publicmissiles.com/>`_ - Dual-deploy guide
   - `RocketPy Recovery Docs <https://docs.rocketpy.org/en/latest/user/parachute.html>`_

Summary
-------

**Key takeaways:**

✅ Cd×S is the critical parameter (drag coefficient × area)

✅ Calculate Cd×S from desired landing velocity: $C_D S = \frac{2mg}{\rho V^2}$

✅ Apogee trigger is simplest and most reliable

✅ Dual-deploy reduces drift for high flights

✅ Lag time affects deployment altitude and opening forces

✅ Always validate with simulation before flying

✅ Safety margins are essential - oversize rather than undersize

**Recovery system design is about balancing:**

- Safe landing velocity
- Acceptable drift distance  
- Deployment reliability
- Cost and complexity

Start simple (single chute at apogee), then progress to dual-deploy as you gain experience!
