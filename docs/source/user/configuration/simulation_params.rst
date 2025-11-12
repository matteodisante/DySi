.. _config-simulation-params:

=====================================
Simulation Parameters Reference
=====================================

This reference documents all parameters in the ``simulation`` configuration section.
The simulation section defines numerical integration settings, launch rail configuration, and termination conditions.

.. contents:: On this page
   :local:
   :depth: 2

--------

Overview
========

The simulation configuration controls:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: **Launch Rail**
        :class-card: sd-shadow-sm

        - Rail length
        - Inclination angle
        - Heading direction

    .. grid-item-card:: **Integration**
        :class-card: sd-shadow-sm

        - Time step sizes
        - Numerical tolerances
        - Solver accuracy

    .. grid-item-card:: **Termination**
        :class-card: sd-shadow-sm

        - Maximum simulation time
        - Stop conditions
        - Apogee detection

    .. grid-item-card:: **Output**
        :class-card: sd-shadow-sm

        - Verbose logging
        - Diagnostic messages

--------

Launch Rail Configuration
==========================

The ``rail`` subsection defines the launch rail geometry and orientation.

.. code-block:: yaml

    simulation:
      rail:
        length_m: 5.0
        inclination_deg: 85.0
        heading_deg: 0.0

.. important::
   **Launch rail provides initial guidance** until rocket reaches sufficient velocity for aerodynamic stability.
   
   Rocket exits rail when it has traveled ``length_m`` along the rail.

rail.length_m
-------------

:Type: ``float``
:Required: No
:Default: ``5.2``
:Unit: meters (m)

**Length of launch rail** from base to end.

.. code-block:: yaml

    simulation:
      rail:
        length_m: 5.0

.. admonition:: How to Choose Rail Length
   :class: dropdown

   **Rule of thumb:** Exit rail at **≥ 20 m/s** (45 mph) for stable flight.
   
   **Method 1: Quick estimate**
   
   For typical high-power rockets:
   
   .. list-table::
      :header-rows: 1
      :widths: 40 30 30
      
      * - Rocket Mass
        - Motor Class
        - Min Rail Length
      * - < 5 kg (11 lb)
        - H - J
        - 1.5 - 2.5 m
      * - 5 - 15 kg (11-33 lb)
        - K - L
        - 3.0 - 5.0 m
      * - 15 - 30 kg (33-66 lb)
        - M - N
        - 5.0 - 8.0 m
      * - > 30 kg (> 66 lb)
        - O+
        - 8.0+ m
   
   **Method 2: Iterative simulation**
   
   1. Run simulation with current rail length
   2. Check ``rail_exit_velocity`` in results
   3. If < 20 m/s, increase rail length
   4. Repeat until exit velocity ≥ 20 m/s
   
   **Example:** 
   
   .. code-block:: python
   
       # Check rail exit velocity
       flight.rail_exit_velocity  # Should be ≥ 20 m/s
   
   If output shows ``rail_exit_velocity = 15.2 m/s``, increase rail length.

.. warning::
   **Insufficient rail length** → low exit velocity → unstable flight!
   
   - Rocket may weathercock excessively
   - Risk of instability during rail departure
   - Potential crash

.. tip::
   **Practical considerations:**
   
   - Standard high-power rails: 1.5 m, 3.0 m, 5.0 m, 8.0 m
   - Longer rail = more stable departure, but heavier/harder to transport
   - Competition rules may specify max rail length

--------

rail.inclination_deg
--------------------

:Type: ``float``
:Required: No
:Default: ``85.0``
:Unit: degrees (°)

**Rail inclination angle** from **horizontal**.

.. code-block:: yaml

    simulation:
      rail:
        inclination_deg: 85.0  # Nearly vertical (5° from vertical)

.. important::
   **Angle measured from HORIZONTAL**, not vertical!
   
   .. code-block:: text
   
       90° = Perfectly vertical (straight up)
       85° = 5° from vertical (slight tilt)
       80° = 10° from vertical
       0°  = Horizontal
   
   **NOT** "degrees from vertical" (opposite convention).

.. tab-set::

    .. tab-item:: Vertical (90°)

        **Perfectly vertical launch**
        
        .. code-block:: yaml
        
            simulation:
              rail:
                inclination_deg: 90.0
        
        ✅ **Pros:**
        
        - Maximum altitude
        - Simplest trajectory
        - Minimal drift
        
        ⚠️ **Cons:**
        
        - Sensitive to wind
        - Harder to set up precisely

    .. tab-item:: Nearly vertical (85°)

        **Standard high-power launch** (5° from vertical)
        
        .. code-block:: yaml
        
            simulation:
              rail:
                inclination_deg: 85.0
        
        ✅ **Pros:**
        
        - Reduces weathercocking
        - Easier to align
        - Still achieves high altitude
        
        Typical for competition launches.

    .. tab-item:: Angled (75-80°)

        **Intentional tilt** (10-15° from vertical)
        
        .. code-block:: yaml
        
            simulation:
              rail:
                inclination_deg: 80.0  # 10° from vertical
        
        ✅ **When to use:**
        
        - Strong crosswind (tilt into wind)
        - Landing zone constraints
        - Demonstration launches
        
        ⚠️ **Reduces apogee** significantly!

.. admonition:: Inclination vs. Altitude Loss
   :class: dropdown

   **Approximate altitude loss** from non-vertical launch:
   
   .. list-table::
      :header-rows: 1
      :widths: 40 30 30
      
      * - inclination_deg
        - Angle from vertical
        - Altitude loss
      * - 90°
        - 0° (vertical)
        - 0% (reference)
      * - 85°
        - 5°
        - ~1-2%
      * - 80°
        - 10°
      - ~3-5%
      * - 75°
        - 15°
        - ~7-10%
      * - 60°
        - 30°
        - ~25-30%
   
   For max altitude, use 85-90°.

--------

rail.heading_deg
----------------

:Type: ``float``
:Required: No
:Default: ``0.0``
:Unit: degrees (°)

**Rail azimuth heading** direction (compass bearing).

.. code-block:: yaml

    simulation:
      rail:
        heading_deg: 0.0  # Pointing North

.. important::
   **Compass convention:** 
   
   .. code-block:: text
   
       heading_deg = 0°   → North
       heading_deg = 90°  → East
       heading_deg = 180° → South
       heading_deg = 270° → West

.. image:: /_static/images/rail_heading_compass.png
   :alt: Rail heading compass rose
   :width: 300px
   :align: center

.. admonition:: Choosing Heading for Wind
   :class: dropdown

   **Strategy: Launch into the wind** to minimize drift.
   
   **Example scenario:**
   
   .. code-block:: text
   
       Wind from West (direction_deg = 270°)
       → Wind blowing toward East
       → Point rail toward West to counter drift
       
       Solution:
         rail.heading_deg = 270.0  # Toward West (into wind)
   
   **General rule:**
   
   .. code-block:: yaml
   
       # If wind from direction D:
       environment:
         wind:
           direction_deg: D  # Wind FROM this direction
       
       simulation:
         rail:
           heading_deg: D  # Point INTO wind (same angle)
   
   **Crosswind component:**
   
   If wind is oblique, you can tilt rail slightly upwind to compensate for drift.

.. tip::
   **Landing zone constraints:**
   
   - Adjust heading to aim rocket toward safe landing area
   - Account for wind drift during descent
   - Use Monte Carlo simulations to predict impact dispersion

--------

Integration Parameters
======================

max_time_s
----------

:Type: ``float``
:Required: No
:Default: ``600.0``
:Unit: seconds (s)

**Maximum simulation time** before automatic termination.

.. code-block:: yaml

    simulation:
      max_time_s: 600.0  # 10 minutes

Simulation stops when:

- Rocket lands (altitude = 0), **OR**
- Time reaches ``max_time_s``

.. admonition:: How to Choose max_time_s
   :class: dropdown

   **Rule of thumb:** Set to **3-5× expected flight time**.
   
   **Typical flight times:**
   
   .. list-table::
      :header-rows: 1
      :widths: 50 50
      
      * - Rocket Type
        - Total Flight Time
      * - Small model rocket (300 m)
        - 30 - 60 s
      * - High-power L motor (1500 m)
        - 90 - 150 s
      * - Competition M motor (3000 m)
        - 150 - 300 s
      * - High-altitude O motor (10 km)
        - 300 - 600 s
   
   **Recommended max_time_s:**
   
   - Small flights: 120 s
   - Medium flights: 300 s
   - Large flights: 600 s
   - Extreme altitude: 900 s

.. warning::
   **Too low max_time_s** → simulation terminates before landing!
   
   Check results: if ``final_time ≈ max_time_s`` and rocket still airborne, increase ``max_time_s``.

--------

max_time_step_s
---------------

:Type: ``float``
:Required: No
:Default: ``inf`` (automatic)
:Unit: seconds (s)

**Maximum time step** for numerical integrator.

.. code-block:: yaml

    simulation:
      max_time_step_s: .inf  # Automatic (recommended)

.. tab-set::

    .. tab-item:: inf (Automatic - Recommended)

        **Let RocketPy choose optimal time step**
        
        .. code-block:: yaml
        
            simulation:
              max_time_step_s: .inf
        
        ✅ **Advantages:**
        
        - Adaptive step size for accuracy
        - Fast integration
        - Handles stiff dynamics
        
        Use this for **almost all simulations**.

    .. tab-item:: Manual limit

        **Force maximum time step**
        
        .. code-block:: yaml
        
            simulation:
              max_time_step_s: 0.01  # Max 10 ms steps
        
        ⚠️ **When to use:**
        
        - Debugging integration issues
        - Very high sampling rate output
        - Custom event detection
        
        Slower simulations!

.. note::
   ``max_time_step_s`` is an **upper limit**. RocketPy may use smaller steps when needed (e.g., near apogee, motor burnout, parachute deployment).

--------

min_time_step_s
---------------

:Type: ``float``
:Required: No
:Default: ``0.0``
:Unit: seconds (s)

**Minimum time step** for numerical integrator.

.. code-block:: yaml

    simulation:
      min_time_step_s: 0.0  # No lower limit

Rarely needs to be changed. Leave at default ``0.0`` for automatic behavior.

--------

rtol
----

:Type: ``float``
:Required: No
:Default: ``1e-6``

**Relative tolerance** for numerical integrator.

.. code-block:: yaml

    simulation:
      rtol: 1e-6  # 0.0001% relative error

Controls **relative error** in integrated state variables (position, velocity).

.. admonition:: Tolerance Explanation
   :class: dropdown

   **Relative tolerance (rtol):**
   
   Acceptable error relative to variable magnitude:
   
   .. math::
   
       \text{Relative Error} = \frac{|\text{Estimated Error}|}{|\text{State Variable}|} < \text{rtol}
   
   **Example:** ``rtol = 1e-6`` means:
   
   - For velocity = 100 m/s, accept error < 0.0001 m/s
   - For altitude = 1000 m, accept error < 0.001 m
   
   **Smaller rtol** → more accurate, slower simulation
   
   **Larger rtol** → less accurate, faster simulation

.. tip::
   **Recommended values:**
   
   - **``1e-6``**: Default, good for most simulations
   - **``1e-8``**: High accuracy (competition, research)
   - **``1e-4``**: Fast preliminary design

--------

atol
----

:Type: ``float``
:Required: No
:Default: ``1e-6``

**Absolute tolerance** for numerical integrator.

.. code-block:: yaml

    simulation:
      atol: 1e-6

Controls **absolute error** in integrated state variables.

.. admonition:: Absolute vs. Relative Tolerance
   :class: dropdown

   **Absolute tolerance (atol):**
   
   Acceptable error in absolute units:
   
   .. math::
   
       |\text{Estimated Error}| < \text{atol}
   
   **When it matters:**
   
   - Near zero crossings (e.g., apogee, vertical velocity = 0)
   - State variables approaching zero
   
   **Combined tolerance check:**
   
   RocketPy accepts step if:
   
   .. math::
   
       |\text{Error}| < \text{atol} + \text{rtol} \times |\text{State}|

.. tip::
   **Typical pairing:**
   
   .. code-block:: yaml
   
       simulation:
         rtol: 1e-6
         atol: 1e-6  # Same order of magnitude

--------

Termination Conditions
======================

terminate_on_apogee
-------------------

:Type: ``boolean``
:Required: No
:Default: ``false``

**Stop simulation at apogee** instead of simulating full descent.

.. code-block:: yaml

    simulation:
      terminate_on_apogee: false  # Simulate full flight

.. tab-set::

    .. tab-item:: false (Default)

        **Simulate complete flight** (ascent + descent + landing)
        
        .. code-block:: yaml
        
            simulation:
              terminate_on_apogee: false
        
        ✅ **Advantages:**
        
        - Full trajectory data
        - Descent rate analysis
        - Landing location prediction
        - Recovery system validation
        
        Use for **complete flight analysis**.

    .. tab-item:: true

        **Terminate at apogee**
        
        .. code-block:: yaml
        
            simulation:
              terminate_on_apogee: true
        
        ✅ **When to use:**
        
        - Only care about max altitude
        - Faster simulations (50% time savings)
        - Apogee optimization studies
        
        ⚠️ **Limitations:**
        
        - No descent data
        - No landing location
        - Cannot validate parachute sizing

.. tip::
   For **design iterations** (optimizing fins, motor selection): use ``terminate_on_apogee: true`` for speed.
   
   For **flight validation**: use ``terminate_on_apogee: false`` for complete analysis.

--------

Output Control
==============

verbose
-------

:Type: ``boolean``
:Required: No
:Default: ``false``

**Enable verbose logging** during simulation.

.. code-block:: yaml

    simulation:
      verbose: false

.. tab-set::

    .. tab-item:: false (Default)

        **Minimal output** (quiet mode)
        
        .. code-block:: yaml
        
            simulation:
              verbose: false
        
        Only critical messages and errors printed.

    .. tab-item:: true

        **Detailed diagnostic output**
        
        .. code-block:: yaml
        
            simulation:
              verbose: true
        
        Prints:
        
        - Integration step information
        - Event detection (rail exit, apogee, parachute deployment)
        - Convergence details
        - Performance metrics
        
        ✅ **When to use:**
        
        - Debugging simulation issues
        - Understanding solver behavior
        - Diagnosing slow convergence

.. warning::
   **verbose = true** produces **extensive output** (hundreds of lines)!
   
   - Slows down simulation slightly
   - Clutters logs in batch runs
   
   Use only when debugging.

--------

Complete Examples
=================

Standard High-Power Launch
---------------------------

.. code-block:: yaml

    simulation:
      # Standard 5 m rail, nearly vertical
      rail:
        length_m: 5.0
        inclination_deg: 85.0
        heading_deg: 0.0  # North
      
      # Default integration settings
      max_time_s: 300.0
      max_time_step_s: .inf
      min_time_step_s: 0.0
      rtol: 1e-6
      atol: 1e-6
      
      # Full flight simulation
      terminate_on_apogee: false
      verbose: false

High-Accuracy Competition Simulation
-------------------------------------

.. code-block:: yaml

    simulation:
      # Long rail for stable departure
      rail:
        length_m: 8.0
        inclination_deg: 87.0  # 3° from vertical
        heading_deg: 270.0  # Launching into westerly wind
      
      # Tight tolerances for accuracy
      max_time_s: 600.0
      rtol: 1e-8  # Higher accuracy
      atol: 1e-8
      
      # Complete flight analysis
      terminate_on_apogee: false
      verbose: false

Fast Design Iteration
---------------------

.. code-block:: yaml

    simulation:
      # Minimal rail for quick sim
      rail:
        length_m: 3.0
        inclination_deg: 90.0  # Vertical
        heading_deg: 0.0
      
      # Relaxed tolerances for speed
      max_time_s: 200.0
      rtol: 1e-4  # Faster, less accurate
      atol: 1e-4
      
      # Stop at apogee (skip descent)
      terminate_on_apogee: true
      verbose: false

Debugging Simulation
--------------------

.. code-block:: yaml

    simulation:
      rail:
        length_m: 5.0
        inclination_deg: 85.0
        heading_deg: 0.0
      
      # Force small time steps for detailed output
      max_time_s: 300.0
      max_time_step_s: 0.01  # 10 ms max steps
      rtol: 1e-6
      atol: 1e-6
      
      # Full diagnostics
      terminate_on_apogee: false
      verbose: true  # Enable detailed logging

--------

Rail Length Calculator
======================

Use this formula to estimate minimum rail length:

.. math::

   L_{rail} = \frac{v_{exit}^2 \cdot m}{2 \cdot F_{avg}}

Where:

- :math:`v_{exit}` = target exit velocity (≥ 20 m/s)
- :math:`m` = rocket mass (kg)
- :math:`F_{avg}` = average motor thrust (N)

**Example:**

.. code-block:: python

    # Target: 20 m/s exit velocity
    v_exit = 20.0  # m/s
    mass = 15.0    # kg
    thrust_avg = 1500.0  # N (from motor data)
    
    L_rail = (v_exit**2 * mass) / (2 * thrust_avg)
    print(f"Minimum rail length: {L_rail:.2f} m")
    # Output: Minimum rail length: 2.00 m

Add 20-30% safety margin:

.. code-block:: python

    L_rail_safe = L_rail * 1.25
    print(f"Recommended rail length: {L_rail_safe:.2f} m")
    # Output: Recommended rail length: 2.50 m

--------

Common Issues
=============

Rail Exit Velocity Too Low
---------------------------

**Problem:** ``rail_exit_velocity < 20 m/s`` → unstable flight

**Solutions:**

1. **Increase rail length**:

   .. code-block:: yaml
   
       simulation:
         rail:
           length_m: 6.0  # Increased from 4.0 m

2. **Use higher-thrust motor** (faster acceleration)

3. **Reduce rocket mass** (faster acceleration)

Simulation Fails to Converge
-----------------------------

**Problem:** "Integration tolerance error" or very slow simulation

**Solutions:**

1. **Tighten tolerances**:

   .. code-block:: yaml
   
       simulation:
         rtol: 1e-8  # From 1e-6
         atol: 1e-8

2. **Limit max time step**:

   .. code-block:: yaml
   
       simulation:
         max_time_step_s: 0.01  # Force smaller steps

3. **Enable verbose output** to diagnose issue:

   .. code-block:: yaml
   
       simulation:
         verbose: true

Rocket Doesn't Land
-------------------

**Problem:** Simulation ends before rocket lands

**Solution:**

Increase ``max_time_s``:

.. code-block:: yaml

    simulation:
      max_time_s: 900.0  # Increased from 300 s

--------

See Also
========

.. seealso::

   **Configuration References:**
   
   - :ref:`config-rocket-params` - Rocket physical properties
   - :ref:`config-motor-params` - Motor configuration
   - :ref:`config-environment-params` - Launch site and weather
   
   **Tutorials:**
   
   - :ref:`tutorial-basic-flight` - First complete simulation
   - :ref:`tutorial-rail-optimization` - Choosing rail length
   
   **How-To Guides:**
   
   - :ref:`how-to-calculate-rail-length` - Rail length estimation
   - :ref:`how-to-launch-heading` - Optimizing launch direction for wind
   - :ref:`how-to-integration-accuracy` - Balancing speed vs. accuracy
   
   **Examples:**
   
   - :ref:`example-rail-sensitivity` - Impact of rail length on stability
   - :ref:`example-heading-optimization` - Wind drift minimization

--------

**Configuration Reference Complete**

You now have complete documentation for all four configuration sections:

1. :ref:`config-rocket-params` - Rocket geometry, mass, components
2. :ref:`config-motor-params` - Motor and propulsion system
3. :ref:`config-environment-params` - Launch site, atmosphere, wind
4. :ref:`config-simulation-params` - Integration and rail settings

**Next steps:**

- :ref:`tutorial-basic-flight` - Put it all together in your first simulation
- :ref:`how-to-guides` - Practical guides for common tasks
- :ref:`examples` - Real-world configuration examples
