.. _technical-stability-analysis:

============================================
Rocket Stability: Theory and Best Practices
============================================

Understanding rocket stability is **critical** for safe flight. This page provides a comprehensive explanation of stability concepts, RocketPy's calculation methods, and best practices for design and analysis.

.. contents:: Table of Contents
   :local:
   :depth: 3

--------

Why Stability Matters
=====================

An **unstable rocket** will tumble uncontrollably, potentially:

❌ Veering off course and landing far from target  
❌ Experiencing excessive drag and reduced altitude  
❌ Structurally failing due to aerodynamic loads  
❌ Posing safety hazards to people and property  

**Proper stability analysis prevents these failures.**

--------

Stability Fundamentals
======================

Center of Mass (CM) and Center of Pressure (CP)
------------------------------------------------

**Center of Mass (CM)**
   The point where the rocket's weight acts. Also called **Center of Gravity (CG)**.
   
   - Changes during flight as propellant burns
   - Moves toward the nose as motor empties
   - You specify this in config as ``cg_location_m``

**Center of Pressure (CP)**
   The point where aerodynamic forces act.
   
   - **Depends on Mach number** - varies during flight!
   - Calculated by RocketPy from fin/nosecone geometry
   - **Not a single fixed value**

The Golden Rule
---------------

.. important::
   
   **For stable flight: CP must be BEHIND CM**
   
   (Toward the tail, away from the nose)

Think of it like a dart or arrow - the heavy part (CM) must be in front!

.. figure:: /_static/stability_diagram.png
   :alt: Stability diagram showing CM and CP
   
   **Stable configuration**: CP behind CM creates restoring moment

--------

RocketPy's Stability Metrics
=============================

RocketPy provides **two different stability metrics**. Understanding when to use each is crucial!

Static Margin
-------------

.. code-block:: python

   static_margin(t) = [CM(t) - CP(Mach=0)] / caliber

**Definition:**
   Distance between CM and CP at **Mach 0** (subsonic), divided by rocket diameter.

**Key Characteristics:**

✅ **Simple** - Uses single CP value (Mach 0)  
✅ **Conservative** - Good for initial design  
✅ **Time-dependent** - Accounts for CM changing as propellant burns  
⚠️ **Approximation** - Assumes CP doesn't change with speed  

**When to Use:**

- Initial design and sizing
- Quick stability checks
- Subsonic rockets (max speed < Mach 0.8)
- Rule-of-thumb evaluations

**Target Values:**

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Static Margin
     - Stability
     - Flight Characteristics
   * - < 0 calibers
     - ❌ **Unstable**
     - Will tumble immediately
   * - 0-1 calibers
     - ⚠️ **Marginally stable**
     - May weathercock, sensitive to winds
   * - 1.0-2.5 calibers
     - ✅ **Optimal**
     - Stable with good maneuverability
   * - 2.5-3.5 calibers
     - ✅ **Very stable**
     - Predictable but less maneuverable
   * - > 3.5 calibers
     - ⚠️ **Over-stable**
     - Weathercocking, high drag

Stability Margin
-----------------

.. code-block:: python

   stability_margin(Mach, t) = [CM(t) - CP(Mach)] / caliber

**Definition:**
   Distance between CM and CP **at actual flight Mach number**, divided by diameter.

**Key Characteristics:**

✅ **Accurate** - Uses actual CP(Mach) during flight  
✅ **Dynamic** - Captures real aerodynamic behavior  
✅ **Two parameters** - Function of both time AND Mach  
⚠️ **Complex** - Requires understanding flight profile  

**When to Use:**

- Final design validation
- High-speed rockets (transonic/supersonic)
- Detailed flight analysis
- Competition accuracy requirements
- Post-flight analysis

**Why It's Different:**

CP position changes with speed because:

1. **Compressibility effects** at transonic speeds (Mach 0.8-1.2)
2. **Shock wave formation** changes pressure distribution
3. **Fin effectiveness** varies with Mach number

.. admonition:: Example: CP Movement
   :class: note
   
   A rocket with trapezoidal fins might have:
   
   - CP at 1.85m from nose at Mach 0.3 (subsonic)
   - CP at 1.78m from nose at Mach 0.9 (transonic)  
   - CP at 1.82m from nose at Mach 1.5 (supersonic)
   
   Using static margin (Mach 0) would miss the **transonic instability**!

--------

Which Metric Should You Use?
=============================

Decision Flow
-------------

.. code-block:: text

   START
     ↓
   Is rocket supersonic (Mach > 1)?
     ├─ NO → Use Static Margin (simpler, sufficient)
     └─ YES
         ↓
       Does it pass through transonic region?
         ├─ NO → Static Margin OK
         └─ YES → Use Stability Margin (critical!)

Practical Recommendations
--------------------------

**Phase 1: Initial Design**
   Use **Static Margin** for quick iterations
   
   Target: 1.5-2.0 calibers

**Phase 2: Final Validation**
   Check **Stability Margin** across flight profile
   
   Verify: Never drops below 1.0 at any Mach

**Phase 3: Flight Analysis**
   Plot both metrics vs time
   
   Identify: Minimum stability point

Best Practices
--------------

1. **Always check both** for high-performance rockets
2. **Plot stability vs time** - see the full picture
3. **Add safety margin** - aim higher than minimum
4. **Validate with OpenRocket** or RASAero if possible
5. **Test subsonic first** before attempting transonic

--------

Center of Pressure Calculation
===============================

How RocketPy Calculates CP
---------------------------

RocketPy computes CP(Mach) using **Barrowman equations**:

.. code-block:: python

   # Simplified concept (actual code more complex)
   for each aerodynamic surface (nose, fins, tail):
       local_cp = surface.cp_position(Mach)
       local_lift = surface.lift_coefficient_derivative(Mach)
       
   # Weighted average by lift contribution
   total_cp = Σ(local_cp × local_lift) / Σ(local_lift)

**Key Points:**

✅ **Automatic** - No manual CP specification needed  
✅ **Mach-dependent** - Proper transonic/supersonic handling  
✅ **Validated** - Based on extensive rocket literature  
⚠️ **Approximation** - Complex geometries may need CFD  

Why Manual CP Specification Was Removed
----------------------------------------

Previously, the config had ``cp_location_m`` parameter. This was **removed** because:

❌ **Single value can't capture Mach dependence**  
❌ **Users would use subsonic value for supersonic flight**  
❌ **False sense of accuracy** - a guess masquerading as data  
❌ **RocketPy calculates it better anyway**  

.. important::
   
   **Trust RocketPy's CP calculation!**
   
   It accounts for:
   
   - Nose cone shape and length
   - Fin geometry (all types)
   - Body tube effects
   - Interference between components
   - Mach number effects

If you have **CFD data**, the proper approach is creating a custom aerodynamic surface, not overriding CP with a single value.

--------

Practical Stability Analysis
=============================

Step-by-Step Process
---------------------

**1. Run Initial Simulation**

.. code-block:: bash

   python scripts/run_single_simulation.py \\
       --config configs/my_rocket.yaml \\
       --name stability_check \\
       --verbose

**2. Check Static Margin**

.. code-block:: bash

   grep "Static Margin" outputs/stability_check/final_state_READABLE.txt

Expected output:

.. code-block:: text

   Initial Static Margin: 1.85 calibers ✓
   Final Static Margin: 2.12 calibers ✓

**3. Extract Stability Data**

The ``final_state.json`` contains:

.. code-block:: json

   {
     "stability": {
       "static_margin_calibers": 1.85,
       "center_of_mass_m": 1.255,
       "center_of_pressure_m": 1.485,
       "center_of_pressure_mach": 0.3
     }
   }

.. note::
   
   ``center_of_pressure_mach: 0.3`` indicates the CP value is calculated at Mach 0.3,
   which is representative for subsonic flight.

**4. Plot Stability Evolution**

Use curve plotter to visualize CP vs Mach:

.. code-block:: python

   from src.curve_plotter import CurvePlotter
   
   plotter = CurvePlotter(motor, rocket, environment)
   plotter.plot_cp_vs_mach("outputs/stability_check/curves/")

This shows how CP moves during flight!

**5. Analyze Full Flight**

Check stability margin throughout flight:

.. code-block:: python

   import json
   
   with open("outputs/stability_check/flight_data.csv") as f:
       # Plot stability_margin vs time
       # Identify minimum value and when it occurs

Common Stability Issues
-----------------------

**Symptom: Negative Static Margin**
   | **Cause:** CP ahead of CM
   | **Fix:** Move fins back OR increase fin size OR move CG forward

**Symptom: Margin drops below 1.0 during flight**
   | **Cause:** Propellant burnout shifts CM too far forward
   | **Fix:** Redesign mass distribution OR shorten motor

**Symptom: Over-stable (> 3.5 calibers)**
   | **Cause:** Fins too large or too far back
   | **Fix:** Reduce fin span OR move fins forward

**Symptom: Stable at Mach 0.3 but unstable at Mach 0.9**
   | **Cause:** Transonic CP shift
   | **Fix:** Increase subsonic margin to 2.5+ calibers for safety buffer

--------

Design Guidelines
=================

General Rules
-------------

.. list-table:: Stability Design Targets
   :header-rows: 1
   :widths: 30 25 45

   * - Rocket Type
     - Target Margin
     - Rationale
   * - **Model rocket** (< Mach 0.5)
     - 1.5-2.0 cal
     - Simple, predictable flight
   * - **High-power** (Mach 0.5-0.9)
     - 1.8-2.5 cal
     - Buffer for transonic effects
   * - **Transonic** (Mach 0.8-1.2)
     - 2.0-3.0 cal
     - Large CP shifts possible
   * - **Supersonic** (> Mach 1.2)
     - 1.5-2.5 cal
     - Stable beyond transonic
   * - **Competition** (precision)
     - 1.5-2.0 cal
     - Balance stability/maneuverability

Fin Sizing Rules of Thumb
--------------------------

.. code-block:: yaml

   # Conservative starting point for 4 fins
   fins:
     count: 4
     root_chord_m: 0.25  # ~15-20% of body length
     tip_chord_m: 0.10   # 40-50% of root chord
     span_m: 0.15        # ~2-3× body radius
     position_m: X       # 85-95% down body length

**Iterative Process:**

1. Start with these values
2. Run simulation
3. Adjust span if margin too low/high
4. Re-run until 1.5-2.5 caliber range

Mass Distribution Strategy
---------------------------

**Forward-Heavy Design (Recommended)**

✅ Electronics/batteries in nose  
✅ Heavy nose cone material  
✅ Avionics bay forward of CG  

**Avoid:**

❌ Heavy tail section  
❌ Excess motor overhang  
❌ Large fin mass  

--------

Advanced Topics
===============

Transonic Flight Considerations
--------------------------------

The **transonic region (Mach 0.8-1.2)** is treacherous:

⚠️ **CP can shift unpredictably**  
⚠️ **Drag increases dramatically** (wave drag)  
⚠️ **Stability margin may decrease**  

**Mitigation strategies:**

1. **Higher subsonic margin** - Start with 2.5+ calibers
2. **Boat tail** - Reduces transonic drag and CP shift
3. **Smooth transitions** - Avoid sharp discontinuities
4. **Validate with tools** - OpenRocket, RASAero, or wind tunnel

Motor Burnout Effects
----------------------

CM moves **forward** as propellant burns:

.. math::

   \\text{Static Margin}_{\\text{burnout}} > \\text{Static Margin}_{\\text{launch}}

**Check both:**

- Initial margin (full motor)
- Final margin (empty motor)

Both should be in acceptable range!

Weathercocking
--------------

**Definition:** Rocket turns into the wind

**Cause:** High stability + crosswind → excessive correction

**Symptoms:**

- Apogee lower than expected
- Large drift downrange
- Trajectory curves into wind

**Solutions:**

- Reduce stability margin to 1.5-2.0
- Use smaller fins
- Launch in lower winds

--------

RocketPy Implementation Details
================================

Stability Functions in RocketPy
--------------------------------

RocketPy's ``Rocket`` class provides:

.. code-block:: python

   rocket.static_margin(time)           # Static margin at time t
   rocket.stability_margin(mach, time)   # Stability margin at (Mach, t)
   rocket.cp_position(mach)              # CP position at Mach number
   rocket.center_of_mass(time)           # CM position at time t

**Usage Example:**

.. code-block:: python

   # Check stability at launch
   launch_margin = rocket.static_margin(0)
   print(f"Launch static margin: {launch_margin:.2f} cal")
   
   # Check stability at burnout
   burnout_time = rocket.motor.burn_out_time
   burnout_margin = rocket.static_margin(burnout_time)
   print(f"Burnout static margin: {burnout_margin:.2f} cal")
   
   # Check CP at different Mach numbers
   cp_subsonic = rocket.cp_position(0.3)
   cp_transonic = rocket.cp_position(0.9)
   cp_supersonic = rocket.cp_position(1.5)
   
   print(f"CP shift: {abs(cp_transonic - cp_subsonic):.3f} m")

Accessing Stability in Output Files
------------------------------------

**1. final_state_READABLE.txt**

.. code-block:: text

   ====== STABILITY ======
   Center of Mass: 1.255 m
   Center of Pressure (Mach 0.3): 1.485 m
   
   Initial Static Margin: 1.81 calibers
   Out-of-rail Static Margin: 1.83 calibers

**2. flight_summary.json**

.. code-block:: json

   {
     "stability": {
       "initial_stability_margin_calibers": 1.81,
       "out_of_rail_stability_margin_calibers": 1.83,
       "center_of_mass_m": 1.255,
       "center_of_pressure_m": 1.485,
       "center_of_pressure_mach": 0.3
     }
   }

**3. flight_data.csv**

Time-series data including:

- ``time`` - Simulation time (s)
- ``stability_margin`` - Stability margin evolution
- ``center_of_mass`` - CM position vs time
- ``mach_number`` - Flight Mach number

--------

Validation and Testing
======================

Cross-Check with Other Tools
-----------------------------

**OpenRocket:**

1. Export your config to OpenRocket format
2. Compare static margin values
3. Should agree within 5-10%

**RASAero:**

1. Model rocket geometry
2. Compare CP location at Mach 0.3
3. Validate transonic CP shift

**Hand Calculations:**

For simple geometries, use Barrowman equations to verify RocketPy's CP.

Experimental Validation
-----------------------

**Wind Tunnel Testing (Advanced):**

- Measure CP location experimentally
- Compare with RocketPy predictions
- Validate Mach dependence

**Swing Tests (Simple):**

1. Attach rocket to string at estimated CP
2. Swing rocket in arc
3. If stable, hangs nose-first (CP behind CM confirmed)

--------

Troubleshooting Guide
=====================

Unexpected Stability Results
-----------------------------

**Q: Why is my stability margin negative even though OpenRocket shows it's stable?**

A: Check coordinate systems!

- RocketPy may use ``tail_to_nose``
- OpenRocket uses ``nose_to_tail``
- Verify your ``cg_location_m`` is in correct system

**Q: CP position seems wrong compared to manual calculation**

A: RocketPy includes:

- Nose cone contribution
- Fin-body interference
- Transition effects
- All generally more accurate than hand calcs

**Q: Stability changes unexpectedly during flight**

A: Normal! Check:

- Propellant mass depletion (CM moves forward)
- Mach number effects (CP shifts)
- Both are physical and expected

--------

References and Further Reading
===============================

Essential Resources
-------------------

**Barrowman's Thesis (1967)**
   Original development of CP calculation methods
   
   "The Practical Calculation of the Aerodynamic Characteristics of Slender Finned Vehicles"

**NFPA 1127 (High Power Rocketry Safety Code)**
   Safety requirements including stability margins

**Stine & Stine (2004)**
   "Handbook of Model Rocketry" - Practical stability guide

**RocketPy Documentation**
   https://docs.rocketpy.org/ - Official API reference

Academic Papers
---------------

- **Niskanen (2009)**: "Development of an Open Source Model Rocket Simulation Software"
- **Box et al. (2011)**: "Transonic Aerodynamics of Finned Bodies"
- **Blake (1963)**: "Missile DATCOM" - Comprehensive aerodynamic methods

Online Calculators
------------------

- **OpenRocket**: Open-source rocket simulator
- **RASAero**: NASA-developed aerodynamic analysis
- **Rocksim**: Commercial rocket design software

--------

Summary and Checklist
======================

Key Takeaways
-------------

✅ **CP must be behind CM** for stability  
✅ **Use Static Margin** for initial design  
✅ **Use Stability Margin** for transonic/supersonic  
✅ **Target 1.5-2.5 calibers** for most rockets  
✅ **Check both launch and burnout** conditions  
✅ **Trust RocketPy's CP calculation** - it's Mach-dependent  
✅ **Plot stability vs time** for full picture  

Pre-Flight Stability Checklist
-------------------------------

.. code-block:: text

   □ Static margin > 1.5 calibers at launch
   □ Static margin > 1.0 calibers at burnout
   □ CP behind CM in config coordinate system
   □ Fin span sufficient (2-3× body radius)
   □ Fins positioned at 85-95% body length
   □ (If supersonic) Stability margin checked across Mach range
   □ (If transonic) Extra margin added (2.5+ calibers)
   □ Mass distribution forward-heavy
   □ CG verified with physical weighing
   □ Validated with second tool (OpenRocket/RASAero)

--------

Questions and Support
=====================

If you encounter stability issues:

1. **Check this documentation** - Most answers are here
2. **Review** :doc:`/user/how_to_guides/validate_design` - Practical troubleshooting
3. **See** :doc:`/user/tutorials/04_adding_fins` - Step-by-step fin design
4. **Consult** :doc:`/user/configuration/rocket_params` - Parameter reference

**For bugs or feature requests**: Open an issue on GitHub

**For design assistance**: RocketPy community forums or rocket clubs

--------

.. admonition:: Remember
   :class: important
   
   **Stability is safety.**
   
   Never fly a rocket with questionable stability. When in doubt:
   
   - Add more fin area
   - Increase static margin to 2.5+ calibers
   - Test with smaller motor first
   - Validate with multiple tools
   
   An unstable rocket is a **missile**, not a rocket.
