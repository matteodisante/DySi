.. _tutorial_adding_fins:

Adding and Optimizing Fins
===========================

Fins are critical for rocket stability. Properly designed fins ensure your rocket flies straight and predictably. This tutorial teaches you how to add fins to your rocket configuration, understand stability margins, and optimize fin design for your specific flight requirements.

.. note::
   
   This tutorial assumes you've completed :ref:`tutorial_basic_flight` and understand basic rocket configuration. We'll focus specifically on fin design and stability analysis.

Why Fins Matter
---------------

Fins serve two primary purposes:

1. **Stability** - Create aerodynamic restoring forces that keep the rocket pointed into the airflow
2. **Control** - Provide leverage for the rocket to naturally correct deviations

**Physics principle:** Fins move the Center of Pressure (CP) aft of the Center of Mass (CoM), creating a stabilizing moment when the rocket tilts.

.. tip::
   
   **Rule of thumb:** The Center of Pressure should be at least **one caliber** (one rocket diameter) behind the Center of Mass for stable flight.

Fin Anatomy
-----------

Understanding fin terminology is essential for design:

.. code-block:: text

                    Tip Chord
                   ┌─────────┐
                   │         │
              Span │         │ Leading Edge
                   │         │
                   │         │ Trailing Edge
                   └─────────┘
                  Root Chord
    ════════════════════════════  ← Body Tube
                  ↑
              Position
           (from tail/nose)

**Key dimensions:**

.. list-table::
   :header-rows: 1
   :widths: 25 75
   
   * - Parameter
     - Description
   * - **Root Chord**
     - Length of fin at body tube attachment (typically longest)
   * - **Tip Chord**
     - Length of fin at outer edge (often shorter for tapered fins)
   * - **Span**
     - Height of fin perpendicular to body tube
   * - **Position**
     - Location along rocket body (measured to fin root leading edge)
   * - **Cant Angle**
     - Angle fins are tilted to induce spin (typically 0° for sport rockets)
   * - **Thickness**
     - Fin material thickness (affects drag and structural strength)

Common Fin Shapes
-----------------

Trapezoidal Fins (Most Common)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tapered fins provide excellent stability with minimal drag:

.. code-block:: yaml

   fins:
     count: 4
     root_chord_m: 0.15      # 150 mm at body
     tip_chord_m: 0.05       # 50 mm at tip (tapered)
     span_m: 0.10            # 100 mm height
     position_m: 0.3         # 300 mm from tail

**Advantages:**

- ✅ Good stability with less drag than rectangular
- ✅ Easier to manufacture than complex curves
- ✅ Lighter weight at tip reduces flutter
- ✅ Proven design used in most amateur rockets

**Use when:** General purpose rocketry, high-power flights, competitions

Rectangular Fins
~~~~~~~~~~~~~~~~

Simple rectangular fins (tip chord = root chord):

.. code-block:: yaml

   fins:
     count: 3
     root_chord_m: 0.12
     tip_chord_m: 0.12       # Same as root = rectangular
     span_m: 0.08
     position_m: 0.25

**Advantages:**

- ✅ Easiest to manufacture (straight cuts)
- ✅ Maximum stability for given area
- ✅ Simple aerodynamic analysis

**Disadvantages:**

- ❌ Higher drag than tapered
- ❌ More weight at tip
- ❌ Susceptible to flutter at high speeds

**Use when:** Low-speed rockets, beginner builds, model rockets

Clipped Delta
~~~~~~~~~~~~~

Highly swept fins with small tip chord:

.. code-block:: yaml

   fins:
     count: 4
     root_chord_m: 0.20      # Long root
     tip_chord_m: 0.02       # Very short tip (clipped)
     span_m: 0.12            # Taller span
     position_m: 0.2

**Advantages:**

- ✅ Excellent high-speed performance
- ✅ Reduced flutter risk
- ✅ Sleek appearance

**Disadvantages:**

- ❌ Requires more rocket length
- ❌ More complex manufacturing

**Use when:** High-speed flights (Mach 1+), minimum diameter rockets

Tutorial: Adding Fins to Your Rocket
-------------------------------------

Let's add fins to a basic rocket step-by-step.

Step 1: Start with Base Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Begin with your rocket without fins (from Tutorial 01):

.. code-block:: yaml

   rocket:
     name: "Finless Rocket"
     dry_mass_kg: 8.5
     coordinate_system: "tail_to_nose"
     cg_location_m: 1.0
     
     geometry:
       caliber_m: 0.127      # 127 mm diameter
       length_m: 1.8
     
     # ... other rocket parameters ...
     
     # NO FINS YET
     fins: null

Step 2: Calculate Initial Stability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before adding fins, check if your rocket is stable:

.. code-block:: bash

   python scripts/run_single_simulation.py --config configs/my_rocket.yaml --name test_no_fins

Check the output for stability margin:

.. code-block:: text

   WARNING: Rocket is UNSTABLE
   Stability Margin: -0.5 calibers
   (Center of Pressure is AHEAD of Center of Mass)

.. warning::
   
   Negative stability margin means **unstable** - the rocket will tumble!

Step 3: Design Your Fins
~~~~~~~~~~~~~~~~~~~~~~~~~

Add a fin configuration to your YAML:

.. code-block:: yaml

   rocket:
     # ... existing parameters ...
     
     fins:
       count: 4                # Standard: 3 or 4 fins
       root_chord_m: 0.15      # 150 mm root
       tip_chord_m: 0.05       # 50 mm tip (tapered)
       span_m: 0.10            # 100 mm height
       thickness_m: 0.003      # 3 mm plywood/fiberglass
       position_m: 0.3         # 300 mm from tail
       cant_angle_deg: 0.0     # No spin
       airfoil: null           # Flat plate

**Key design decisions:**

1. **Count:** 3 fins (120° apart) or 4 fins (90° apart)
   - 3 fins: Lighter, simpler, common in competition
   - 4 fins: More stable, easier to align, more drag

2. **Root chord:** Typically 10-20% of rocket length

3. **Tip chord:** 30-50% of root chord for good taper

4. **Span:** Start with 70-100% of rocket diameter

5. **Position:** Place near tail, but leave clearance for motor

Step 4: Validate Stability
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run simulation with fins:

.. code-block:: bash

   python scripts/run_single_simulation.py --config configs/my_rocket.yaml --name test_with_fins

Check the results:

.. code-block:: text

   ✓ Rocket is STABLE
   Initial Stability Margin: 1.8 calibers
   Out-of-rail Stability Margin: 1.9 calibers

.. tip::
   
   **Target stability margins:**
   
   - **< 1.0 calibers:** Marginally stable (risky)
   - **1.0 - 2.0 calibers:** Stable (recommended)
   - **2.0 - 3.0 calibers:** Very stable (safe)
   - **> 3.0 calibers:** Over-stable (may weathercock in wind)

Understanding Stability Margins
--------------------------------

The Static Margin
~~~~~~~~~~~~~~~~~

**Definition:** Distance between Center of Pressure (CP) and Center of Mass (CoM), measured in calibers (rocket diameters).

.. math::

   \text{Static Margin} = \frac{CP_{\text{position}} - CoM_{\text{position}}}{\text{caliber}}

**Physical meaning:**

- **Positive:** CP behind CoM → Stable (restoring moment)
- **Zero:** CP at CoM → Neutrally stable (no restoring force)
- **Negative:** CP ahead of CoM → Unstable (amplifies deviation)

How Fins Affect Stability
~~~~~~~~~~~~~~~~~~~~~~~~~~

Fins move the CP aft (toward tail) by creating lift surfaces:

1. **Larger span** → CP moves more aft → More stable
2. **Larger root chord** → CP moves more aft → More stable
3. **Position closer to tail** → CP moves more aft → More stable

**But be careful:** Excessive stability can cause problems!

Over-Stability Issues
~~~~~~~~~~~~~~~~~~~~~

When stability margin is too high (> 3.0):

- **Weathercocking:** Rocket turns excessively into wind
- **Launch sensitivity:** Small rail misalignment causes large trajectory changes
- **Reduced apogee:** Drag increases as rocket fights wind

**Solution:** Reduce fin size or move CoM aft (add nose weight)

Optimizing Fin Design
----------------------

Goal-Based Optimization
~~~~~~~~~~~~~~~~~~~~~~~

**Goal 1: Maximum Altitude**

Minimize drag while maintaining stability:

.. code-block:: yaml

   fins:
     count: 3                # Fewer fins = less drag
     root_chord_m: 0.12      # Shorter chord = less wetted area
     tip_chord_m: 0.04       # Aggressive taper
     span_m: 0.08            # Just enough for stability
     thickness_m: 0.002      # Thin material
     position_m: 0.25

**Target:** Stability margin 1.2-1.5 calibers

**Goal 2: Maximum Stability (Beginner Rocket)**

Prioritize forgiving flight characteristics:

.. code-block:: yaml

   fins:
     count: 4                # More fins = more stability
     root_chord_m: 0.18      # Longer chord
     tip_chord_m: 0.08       # Moderate taper
     span_m: 0.12            # Taller span
     thickness_m: 0.004      # Thicker (stronger)
     position_m: 0.20        # Far aft

**Target:** Stability margin 2.0-2.5 calibers

**Goal 3: High-Speed Flight (Mach 1+)**

Reduce flutter and drag:

.. code-block:: yaml

   fins:
     count: 4
     root_chord_m: 0.20      # Long root (swept)
     tip_chord_m: 0.02       # Very short tip
     span_m: 0.10            # Moderate span
     thickness_m: 0.006      # Very thick (flutter resistance)
     position_m: 0.15
     airfoil: "data/airfoils/naca0012.txt"  # Streamlined

**Target:** Stability margin 1.5-2.0 calibers, thick fins to prevent flutter

Iterative Optimization Process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Start conservative:** Large fins, high stability margin
2. **Run simulation:** Check apogee and stability
3. **Reduce fin size:** Decrease span or chord by 10%
4. **Re-simulate:** Verify still stable (margin > 1.2)
5. **Repeat:** Until apogee maximized while maintaining safe stability

.. code-block:: python

   # Example optimization script
   import numpy as np
   
   for span in np.linspace(0.08, 0.14, 7):  # Test 7 different spans
       # Update config with new span
       config['rocket']['fins']['span_m'] = span
       
       # Run simulation
       result = run_simulation(config)
       
       # Check if stable and record apogee
       if result['stability_margin'] > 1.2:
           print(f"Span {span:.3f}m: Apogee {result['apogee_m']:.0f}m, "
                 f"Stability {result['stability_margin']:.2f}")

Practical Fin Sizing
--------------------

Quick Sizing Method
~~~~~~~~~~~~~~~~~~~

For preliminary design, use these ratios:

.. list-table::
   :header-rows: 1
   :widths: 30 35 35
   
   * - Parameter
     - Conservative (Beginner)
     - Optimized (Advanced)
   * - **Root Chord**
     - 15-20% of rocket length
     - 10-15% of rocket length
   * - **Tip Chord**
     - 60-80% of root chord
     - 30-50% of root chord
   * - **Span**
     - 80-120% of caliber
     - 60-90% of caliber
   * - **Position**
     - 0-15% from tail
     - 15-25% from tail

**Example:** For 1.8m rocket, 127mm diameter:

Conservative design:

.. code-block:: yaml

   fins:
     root_chord_m: 0.27      # 15% of 1.8m
     tip_chord_m: 0.19       # 70% of root
     span_m: 0.12            # 95% of caliber (0.127m)
     position_m: 0.10        # 10cm from tail

Optimized design:

.. code-block:: yaml

   fins:
     root_chord_m: 0.18      # 10% of 1.8m
     tip_chord_m: 0.07       # 40% of root
     span_m: 0.09            # 70% of caliber
     position_m: 0.30        # 30cm from tail

Fin Material Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Material affects thickness parameter:

.. list-table::
   :header-rows: 1
   :widths: 30 25 25 20
   
   * - Material
     - Thickness (mm)
     - Weight
     - Cost
   * - Balsa wood
     - 3-6
     - Very light
     - Low
   * - Plywood
     - 3-5
     - Light
     - Low
   * - Fiberglass
     - 2-4
     - Medium
     - Medium
   * - G10/FR4
     - 1.5-3
     - Medium
     - Medium
   * - Carbon fiber
     - 1-2
     - Light
     - High
   * - Aluminum
     - 1-3
     - Heavy
     - Medium

.. warning::
   
   **Flutter warning:** Thin fins can flutter (vibrate) at high speeds!
   
   **Flutter speed estimate:**
   
   .. math::
   
      V_{\text{flutter}} \approx 100 \sqrt{\frac{t}{c}}
   
   Where:
   - :math:`V_{\text{flutter}}` = flutter speed (m/s)
   - :math:`t` = thickness (m)
   - :math:`c` = average chord (m)
   
   For 3mm thick fin with 0.1m chord: :math:`V_{\text{flutter}} \approx 173` m/s

Advanced Features
-----------------

Canted Fins (Spin Stabilization)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cant angle induces rocket spin for gyroscopic stabilization:

.. code-block:: yaml

   fins:
     # ... other parameters ...
     cant_angle_deg: 2.0     # 2° cant (positive = clockwise from nose view)

**Effects of cant:**

- **Spin rate:** ~1-2 Hz per degree of cant (depends on thrust)
- **Drag increase:** ~5-10% additional drag
- **Trajectory:** Slight corkscrew path

**When to use:**

- ✅ Low stability margin rockets (< 1.0 caliber)
- ✅ Long, slender rockets prone to weathercocking
- ✅ Rockets with flexible airframes

**When NOT to use:**

- ❌ High-speed flights (spin increases drag)
- ❌ Precision altitude attempts
- ❌ Payload flights (spinning affects sensors)

Custom Airfoils
~~~~~~~~~~~~~~~

For high-performance rockets, use streamlined airfoils:

.. code-block:: yaml

   fins:
     # ... other parameters ...
     airfoil: "data/airfoils/naca0012.txt"  # Symmetric airfoil

**Airfoil file format** (plain text, two columns):

.. code-block:: text

   # NACA 0012 Airfoil Coordinates
   # X/C  Y/C (normalized, 0-1)
   0.0000  0.0000
   0.0050  0.0103
   0.0100  0.0144
   ...
   1.0000  0.0000

**When airfoils help:**

- High-speed flights (> Mach 0.5)
- Drag-critical altitude attempts
- Competition rockets

**When to skip:**

- Low-speed flights (< 100 m/s)
- Beginner builds (flat plate is simpler)
- Thick fins (airfoil benefit minimal)

Validation and Testing
----------------------

Pre-Flight Checklist
~~~~~~~~~~~~~~~~~~~~

Before flying with new fins:

1. ✅ **Stability margin check:** 1.0 - 3.0 calibers
2. ✅ **Rail exit velocity:** > 20 m/s (ensures fins are effective)
3. ✅ **Fin strength:** No flex when pressed firmly
4. ✅ **Alignment:** Fins parallel to rocket axis (< 1° error)
5. ✅ **Attachment:** Secure epoxy fillets, no gaps
6. ✅ **Balance point:** CoM ahead of CP when suspended

Simulation Validation
~~~~~~~~~~~~~~~~~~~~~

Run simulation and check:

.. code-block:: bash

   python scripts/run_single_simulation.py --config configs/my_rocket.yaml --name fin_test

**Review outputs:**

.. code-block:: text

   Initial Stability Margin: 1.8 calibers  ✓
   Out-of-rail Velocity: 24.5 m/s         ✓
   Out-of-rail Stability: 1.9 calibers    ✓
   Max Velocity: 245 m/s                  ✓
   Apogee: 2850 m                         ✓

Visual Inspection
~~~~~~~~~~~~~~~~~

Check the ``final_state_READABLE.txt`` file:

.. code-block:: bash

   grep -A 15 "Stability:" outputs/fin_test/final_state_READABLE.txt

Look for:

- Static margin value
- CP and CoM positions
- Stability margin throughout flight

Common Fin Problems
-------------------

Problem 1: Unstable Rocket
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Negative or very low stability margin

**Causes:**

- Fins too small
- Fins too far forward
- CoM too far aft
- Heavy nose cone

**Solutions:**

1. **Increase fin span** by 20%
2. **Move fins closer to tail**
3. **Add nose weight** to move CoM forward
4. **Increase root chord** for more fin area

Problem 2: Over-Stable Rocket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Stability margin > 3.0 calibers

**Causes:**

- Fins too large
- CoM too far forward

**Solutions:**

1. **Reduce fin span** by 15%
2. **Shorten root chord**
3. **Move fins forward** slightly
4. **Remove nose weight** if present

Problem 3: Excessive Drag
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Low apogee compared to expected

**Causes:**

- Fins too large
- Rectangular fins (not tapered)
- Too many fins
- Thick fins

**Solutions:**

1. **Taper fins** (reduce tip chord to 40% of root)
2. **Reduce fin count** (4 → 3 if stability allows)
3. **Thin fin material** while maintaining strength
4. **Optimize span** for minimum drag

Problem 4: Flutter
~~~~~~~~~~~~~~~~~~

**Symptom:** Fins vibrate or fail at high speed

**Causes:**

- Fins too thin for chord length
- Flexible material
- Poor attachment

**Solutions:**

1. **Increase thickness** (e.g., 3mm → 6mm)
2. **Stiffen material** (plywood → G10)
3. **Add tip weight** (not recommended for amateur rockets)
4. **Reduce chord length** if possible

Comparison Example
------------------

Let's compare three fin designs for the same rocket:

**Rocket:** 1.8m length, 127mm diameter, 8.5kg dry mass, CoM at 1.0m

Design A: Conservative (Beginner)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   fins:
     count: 4
     root_chord_m: 0.18
     tip_chord_m: 0.12
     span_m: 0.12
     position_m: 0.20

**Results:**

- Stability margin: 2.4 calibers ✓
- Apogee: 2650 m
- Max velocity: 235 m/s
- Assessment: Very stable, forgiving, good for first flight

Design B: Optimized (Experienced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   fins:
     count: 3
     root_chord_m: 0.15
     tip_chord_m: 0.05
     span_m: 0.10
     position_m: 0.30

**Results:**

- Stability margin: 1.6 calibers ✓
- Apogee: 2890 m (+9%)
- Max velocity: 248 m/s
- Assessment: Stable, optimized drag, better performance

Design C: Aggressive (Expert)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   fins:
     count: 3
     root_chord_m: 0.12
     tip_chord_m: 0.03
     span_m: 0.08
     position_m: 0.35

**Results:**

- Stability margin: 1.2 calibers ⚠️
- Apogee: 3020 m (+14%)
- Max velocity: 256 m/s
- Assessment: Marginally stable, maximum performance, risky

.. tip::
   
   **Recommendation:** Start with Design A for your first flight, then progressively optimize toward Design B as you gain experience. Design C is only for expert flyers with validated simulations.

Next Steps
----------

Now that you understand fin design:

1. **Add recovery** - See :ref:`tutorial_recovery_system` to ensure safe landing
2. **Optimize for wind** - Learn :ref:`tutorial_weather_integration` for realistic conditions
3. **Parameter study** - Vary fin sizes and compare apogee vs. stability
4. **Build and test** - Validate your simulation with real flights!

.. seealso::
   
   - :ref:`configuration_rocket_params` - Complete fin parameter reference
   - :ref:`howto_measure_rocket` - Measuring CoM and fin positions
   - `OpenRocket <http://openrocket.info/>`_ - Free fin design tool with 3D visualization
   - `RocketPy Aerodynamics Docs <https://docs.rocketpy.org/en/latest/user/aerodynamics.html>`_ - Deep dive into stability

Resources
---------

Fin Design Tools
~~~~~~~~~~~~~~~~

- **OpenRocket** - Free rocket design software with automatic CP calculation
- **RASAero II** - Free aerodynamic analysis tool
- **MATLAB/Python** - Custom optimization scripts
- **CFD (Advanced)** - Computational Fluid Dynamics for complex geometries

Further Reading
~~~~~~~~~~~~~~~

- **Stine & Stine** - "Handbook of Model Rocketry" (Chapter on Stability)
- **Barrowman Equations** - Classic method for CP calculation
- **Niskanen** - "OpenRocket Technical Documentation"
- **NASA SP-8007** - "Transonic Aerodynamic Characteristics of Blunt Bodies"

Summary
-------

**Key takeaways:**

✅ Stability margin should be 1.0-3.0 calibers

✅ Larger fins increase stability but also drag

✅ Tapered fins are more efficient than rectangular

✅ Position fins near tail for maximum effect

✅ Validate stability before flying

✅ Start conservative, optimize gradually

**Fin design is iterative** - simulate, analyze, adjust, repeat until you find the optimal balance between stability and performance for your mission!
