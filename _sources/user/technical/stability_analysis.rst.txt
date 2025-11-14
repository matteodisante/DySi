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

When the rocket is perturbed from vertical flight, aerodynamic forces acting at CP create a restoring moment about CM that returns the rocket to stable flight. This requires CP to be aft of CM.

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

CP position changes with speed due to compressibility effects:

1. **Compressibility effects** at transonic speeds (Mach 0.8-1.2) alter pressure distribution
2. **Shock wave formation** changes the location of aerodynamic center
3. **Fin effectiveness** varies with Mach number due to boundary layer effects

These variations can be significant (5-15% body length) and affect stability margins.

--------

Which Metric Should You Use?
=============================

Understanding Both Metrics
---------------------------

**For comprehensive stability analysis, both metrics are important:**

Static Margin
~~~~~~~~~~~~~

Provides a **conservative baseline** using CP at Mach 0. Useful for:

- Initial design iterations
- Subsonic rockets (Mach < 0.8)
- Quick stability checks

**Limitation:** Does not capture CP variations during flight.

Stability Margin  
~~~~~~~~~~~~~~~~

Provides **accurate stability assessment** at actual flight conditions. Essential for:

- Transonic/supersonic rockets (Mach > 0.8)
- Final design validation
- Understanding stability evolution during flight

**Advantage:** Shows real stability margin throughout the flight envelope.

Interpreting Stability Margin
------------------------------

The stability margin varies during flight due to:

1. **Mach number changes** - CP shifts as rocket accelerates/decelerates
2. **Propellant depletion** - CM moves forward as motor burns
3. **Altitude effects** - Aerodynamic forces decrease with atmospheric density

**Key Analysis Approach:**

Plot stability margin vs. time and identify:

- **Minimum stability point** - Often occurs during transonic transition
- **Critical flight phases** - Motor burnout, maximum dynamic pressure
- **Margin safety factor** - Ensure minimum stays above 1.0 caliber

.. code-block:: python

   # Example: Analyzing stability margin throughout flight
   import matplotlib.pyplot as plt
   
   # Extract from RocketPy Flight object
   time = flight.time
   mach = flight.mach_number
   
   # Calculate stability margin at each time point
   stability_margins = []
   for t, M in zip(time, mach):
       margin = rocket.stability_margin(M, t)
       stability_margins.append(margin)
   
   # Plot
   plt.figure(figsize=(10, 6))
   plt.plot(time, stability_margins, 'b-', linewidth=2)
   plt.axhline(y=1.0, color='r', linestyle='--', label='Minimum Safe Margin')
   plt.xlabel('Time (s)')
   plt.ylabel('Stability Margin (calibers)')
   plt.title('Stability Margin Evolution During Flight')
   plt.grid(True, alpha=0.3)
   plt.legend()
   plt.show()

**Critical Interpretation Points:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Observation
     - Interpretation
   * - Margin decreases during acceleration
     - Normal - Mach effects shifting CP forward
   * - Sudden drop near Mach 1
     - Transonic CP shift - verify margin stays > 1.0
   * - Margin increases after burnout
     - CM moved forward, propellant depleted
   * - Margin below 1.0 at any point
     - **Unsafe** - redesign needed

Practical Recommendations
--------------------------

**Initial Design Phase:**
   Start with **Static Margin** targeting 2.0-2.5 calibers for safety buffer

**Detailed Analysis Phase:**
   Plot **Stability Margin vs Time** for complete flight:
   
   - Verify margin never drops below 1.0 caliber
   - Identify minimum margin point
   - Check margins at critical events (max Q, burnout, apogee)

**For Subsonic Rockets (Mach < 0.8):**
   Static Margin alone is typically sufficient if > 1.5 calibers

**For Transonic/Supersonic Rockets (Mach > 0.8):**
   **Must** analyze Stability Margin throughout flight envelope:
   
   - CP shifts can reduce margin by 0.5-1.0 calibers in transonic region
   - Static Margin alone is inadequate - can miss critical instabilities

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
✅ **Validated** - Based on Barrowman (1967) methodology [1]_
⚠️ **Approximation** - Complex geometries may require CFD validation

.. important::
   
   **RocketPy's CP Calculation Accounts For:**
   
   - Nose cone shape and length (von Karman, ogive, conical, etc.)
   - Fin geometry (trapezoidal, elliptical, all standard types)
   - Body tube effects and diameter changes
   - Interference between components
   - Mach number compressibility corrections

For standard rocket configurations, Barrowman's method provides accuracy within 5-10% of experimental data. Complex geometries (unconventional fins, non-axisymmetric bodies) may require CFD or wind tunnel validation.

--------

Practical Stability Analysis
=============================
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

General Stability Targets
--------------------------

.. list-table:: Stability Design Targets by Rocket Class
   :header-rows: 1
   :widths: 30 25 45

   * - Rocket Type
     - Target Margin
     - Reference
   * - **Model rocket** (< Mach 0.5)
     - 1.5-2.0 cal
     - Stine & Stine (2004) [2]_
   * - **High-power** (Mach 0.5-0.9)
     - 1.8-2.5 cal
     - NFPA 1127 (2023) [3]_
   * - **Transonic** (Mach 0.8-1.2)
     - 2.0-3.0 cal
     - Niskanen (2009) [4]_
   * - **Supersonic** (> Mach 1.2)
     - 1.5-2.5 cal
     - Box et al. (2011) [5]_
   * - **Competition** (precision)
     - 1.5-2.0 cal
     - Empirical best practice

.. note::
   
   These are **guidelines**, not absolute rules. Actual optimal margin depends on:
   
   - Specific aerodynamic configuration
   - Flight profile and mission requirements  
   - Environmental conditions (wind, altitude)
   - Motor characteristics and burn profile

Fin Design Considerations
--------------------------

**Fin Positioning:**

Fins should be located at 85-95% of body length from nose (Barrowman, 1967 [1]_). This positioning:

- Maximizes CP-CM separation
- Provides adequate structural support
- Minimizes fin-body interference effects

**Fin Span Guidelines:**

For trapezoidal fins on cylindrical body:

.. math::

   s_{fin} = (2 \text{ to } 3) \times r_{body}

Where :math:`s_{fin}` is fin semi-span and :math:`r_{body}` is body radius.

**Source:** Mandell et al. (1973), "Topics in Advanced Model Rocketry" [6]_

**Fin Geometry Starting Point:**

.. code-block:: yaml

   # Conservative initial design (4-fin configuration)
   fins:
     count: 3 or 4              # 3-fin more efficient, 4-fin more stable
     root_chord_m: L_body × 0.18  # 15-20% of total body length
     tip_chord_m: root × 0.45     # Taper ratio 0.4-0.5
     span_m: diameter × 1.5       # 2-3× body radius for adequate authority
     sweep_angle_deg: 30-45       # Reduces transonic drag

These are **starting values** - iterate based on simulation results.

Mass Distribution Strategy
---------------------------

**Forward-Heavy Configuration (Recommended):**

Per Stine & Stine (2004) [2]_, placing heavy components forward ensures stable CG position:

✅ **Electronics/avionics in nose section** - Maximizes forward mass  
✅ **Heavy nose cone material** (fiberglass, metal tip)  
✅ **Battery packs forward of motor** - Low-density propellant relative to electronics

**Configurations to Avoid:**

❌ **Heavy tail section** - Aft CG reduces stability  
❌ **Excessive motor overhang** - Shifts CG aft  
❌ **Large fin mass without forward ballast** - Unbalanced configuration  

--------

Advanced Topics
===============

Transonic Flight Considerations
--------------------------------

The **transonic region (Mach 0.8-1.2)** presents significant aerodynamic challenges:

⚠️ **CP can shift 5-15% of body length** (Box et al., 2011 [5]_)
⚠️ **Wave drag increases dramatically** - drag coefficient may double  
⚠️ **Stability margin may decrease** by 0.5-1.0 calibers  

**Mitigation Strategies:**

1. **Higher subsonic margin** - Start with 2.5-3.0 calibers minimum (Niskanen, 2009 [4]_)
2. **Boat tail design** - 5-7° convergence angle reduces base drag and CP shift
3. **Smooth geometric transitions** - Avoid sharp discontinuities that trigger early separation
4. **Validation with multiple tools** - Cross-check with OpenRocket, RASAero II, or wind tunnel data

Motor Burnout Effects
----------------------

CM shifts **forward** as propellant depletes (Stine & Stine, 2004 [2]_):

.. math::

   \text{Static Margin}_{\text{burnout}} > \text{Static Margin}_{\text{ignition}}

**Critical Check:**

Both initial (full motor) and final (empty motor) margins must be within acceptable range:

- **At ignition:** Verify margin ≥ 1.5 calibers
- **At burnout:** Verify margin ≤ 3.5 calibers (avoid over-stability)

Large solid motors can shift CG by 10-20% of body length during burn.

Weathercocking
--------------

**Definition:** Rocket aligns with resultant wind vector, causing trajectory deviation.

**Physical Cause:** 

High stability creates strong restoring moments. In crosswind, the rocket "corrects" excessively, turning into the relative wind direction (Gregorek, 1970 [7]_).

**Symptoms:**

- Apogee significantly lower than predicted (increased drag from angle of attack)
- Large horizontal drift downrange
- Curved trajectory turning into prevailing wind

**Mitigation:**

- Reduce stability margin to 1.5-2.0 calibers (balance stability and weathercock resistance)
- Launch in wind speeds < 20 mph for high-power rockets
- Use aerodynamic damping (larger diameter, shorter fins) to reduce angular response

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

.. [1] **Barrowman, J. S. (1967).** "The Practical Calculation of the Aerodynamic Characteristics of Slender Finned Vehicles." M.S. Thesis, Catholic University of America, Washington, D.C.
   
   *Foundational work on CP calculation methodology used by RocketPy and most rocket simulation software.*

.. [2] **Stine, G. H., & Stine, B. (2004).** "Handbook of Model Rocketry," 7th Edition. Wiley.
   
   *Comprehensive practical guide to rocket stability, design guidelines, and safety practices.*

.. [3] **NFPA 1127 (2023).** "Code for High Power Rocketry." National Fire Protection Association.
   
   *Official safety code including stability margin requirements for high-power rocketry.*

.. [4] **Niskanen, S. (2009).** "Development and validation of a computerized model rocket simulation software." M.S. Thesis, Helsinki University of Technology.
   
   *Theoretical foundation of OpenRocket, discusses transonic stability challenges.*

.. [5] **Box, S., Bishop, C. M., & Hunt, H. (2011).** "Transonic Aerodynamic Characteristics of Slender Bodies with Cruciform Surfaces." Journal of Spacecraft and Rockets, 48(6), 1028-1034.
   
   *Experimental data on CP shifts in transonic region for finned bodies.*

.. [6] **Mandell, G., Caporaso, G., & Bengen, W. (1973).** "Topics in Advanced Model Rocketry." MIT Press.
   
   *Advanced design techniques including fin sizing and aerodynamic optimization.*

.. [7] **Gregorek, G. M. (1970).** "An Experimental Investigation of the Effects of Wind on Rocket Flight Paths." Technical Report, Ohio State University.
   
   *Analysis of weathercocking phenomenon and stability-wind interaction.*

Additional Resources
--------------------

**Software Tools:**

- **OpenRocket** - Open-source rocket design and simulation (https://openrocket.info/)
- **RASAero II** - NASA-developed aerodynamic analysis tool
- **RocketPy Documentation** - https://docs.rocketpy.org/

**Standards and Guidelines:**

- **Tripoli Rocketry Association** - High-power rocketry certification guidelines
- **National Association of Rocketry** - Model rocket safety code
- **FAA Part 101** - Regulations for unmanned rockets

**Academic References:**

- **Missile DATCOM (1997)** - Comprehensive aerodynamic prediction methods
- **Fleeman, E. L. (2012)** - "Tactical Missile Design," 2nd Edition, AIAA
- **Sutton, G. P. (2001)** - "Rocket Propulsion Elements," 7th Edition

--------

Summary and Checklist
======================

Key Principles
--------------

✅ **CP must be aft of CM** for aerodynamic stability  
✅ **Static Margin** for initial design and subsonic rockets  
✅ **Stability Margin** essential for transonic/supersonic analysis  
✅ **Target 1.5-2.5 calibers** for most applications  
✅ **Verify both launch and burnout** configurations  
✅ **Plot stability margin vs time** to identify minimum margin point
✅ **RocketPy calculates CP(Mach)** automatically using Barrowman equations

Pre-Flight Stability Checklist
-------------------------------

**Required Checks:**

.. code-block:: text

   □ Static margin ≥ 1.5 calibers at ignition (full motor)
   □ Static margin ≥ 1.0 calibers at burnout (empty motor)  
   □ Static margin ≤ 3.5 calibers (avoid over-stability)
   □ CP position behind CM in configured coordinate system
   □ Fin semi-span = 2-3× body radius
   □ Fins positioned at 85-95% of body length from nose
   
**Additional Checks for High-Performance Rockets:**

.. code-block:: text

   □ (Transonic/Supersonic) Stability margin plotted throughout flight
   □ (Transonic) Minimum margin ≥ 1.0 caliber during Mach 0.8-1.2
   □ (Transonic) Initial static margin ≥ 2.5 calibers for safety buffer
   □ (All) Mass distribution forward-heavy verified
   □ (All) CG measured experimentally (weighing/balancing)
   □ (All) Cross-validated with independent tool (OpenRocket, RASAero II)

--------

Questions and Support
=====================

**Documentation Resources:**

- **Practical troubleshooting:** :doc:`/user/how_to_guides/validate_design`
- **Fin design tutorial:** :doc:`/user/tutorials/04_adding_fins`  
- **Configuration parameters:** :doc:`/user/configuration/rocket_params`

**Community Support:**

- GitHub Issues: Bug reports and feature requests
- RocketPy Forums: Design assistance and community discussion
- Local rocket clubs: Hands-on validation and mentorship

--------

.. admonition:: Safety First
   :class: important
   
   **Stability is not optional—it is a safety requirement.**
   
   Never launch a rocket with uncertain stability. If margins are borderline:
   
   - Increase fin area to boost CP aft
   - Add nose weight to move CM forward
   - Test with lower-impulse motor first
   - Obtain validation from experienced rocketeers
   
   An unstable rocket is uncontrollable and poses significant safety hazards.
