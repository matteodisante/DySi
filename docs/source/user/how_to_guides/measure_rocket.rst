How to Measure Your Rocket's Parameters
========================================

.. admonition:: Quick Answer
   :class: tip

   **Essential measurements**:
   
   * Mass: Weigh on scale (without motor)
   * Radius: Measure outer diameter, divide by 2
   * Center of Mass: Balance on edge, measure distance from nose
   * Fin dimensions: Measure with ruler/calipers
   * Motor position: Measure from nose tip to nozzle

Problem
-------

You want to simulate your actual rocket, but configuration files need specific
physical parameters. How do you measure them accurately?

This guide shows you how to measure every parameter needed for a rocket-sim configuration.

Tools You'll Need
-----------------

**Essential:**

* Digital scale (±10g accuracy)
* Measuring tape or ruler
* Calipers (optional, for precision)
* Notebook for recording measurements

**Helpful:**

* String or thin rod (for balance point)
* Calculator
* Camera (document measurements)

Step-by-Step Measurements
--------------------------

1. Overall Dimensions
~~~~~~~~~~~~~~~~~~~~~

**Rocket Length**

Measure from nose tip to tail:

.. code-block:: text

   ├─────── Length (L) ────────┤
   ●                            ●
   Nose tip                   Tail

Record: ``L = ___ m``

**Body Tube Radius**

Measure outer diameter with calipers or tape, then divide by 2:

.. code-block:: text

   Diameter (D) = ___ mm
   Radius (r) = D / 2 = ___ mm = ___ m

Record: ``rocket.radius = ___ m``

.. tip::
   Convert to meters: 100 mm = 0.1 m

2. Mass Properties
~~~~~~~~~~~~~~~~~~

**Dry Mass (Without Motor)**

1. Remove motor from rocket
2. Remove motor retention (if separate)
3. Weigh rocket on scale

.. code-block:: text

   Mass = ___ kg

Record: ``rocket.mass = ___ kg``

.. warning::
   DO NOT include:
   
   * Motor (empty or loaded)
   * Motor propellant
   
   DO include:
   
   * Airframe, fins, nose cone
   * Parachutes and recovery hardware
   * Avionics, batteries
   * Any payload

**Center of Mass (Without Motor)**

Method 1: Balance Test
^^^^^^^^^^^^^^^^^^^^^^^

1. Remove motor
2. Find balance point on thin edge or string
3. Measure distance from nose tip to balance point

.. code-block:: text

   ├── CM distance from nose ──┤
   ●                             ⚖
   Nose                     Balance point

Record: ``rocket.center_of_mass_without_motor = ___ m``

Method 2: Calculation
^^^^^^^^^^^^^^^^^^^^^

If you can't balance it, estimate from component masses:

.. math::

   x_{CM} = \frac{\sum m_i \cdot x_i}{\sum m_i}

Where:

* :math:`m_i` = mass of component i
* :math:`x_i` = distance of component i from nose

**Moment of Inertia**

For most users, use this approximation:

Longitudinal (I_xx, I_yy):

.. math::

   I_{long} \approx \frac{1}{12} m L^2

Spin (I_zz):

.. math::

   I_{spin} \approx \frac{1}{2} m r^2

Where:

* m = rocket mass (kg)
* L = rocket length (m)
* r = radius (m)

Example calculation:

.. code-block:: python

   mass = 5.0  # kg
   length = 1.2  # m
   radius = 0.052  # m
   
   I_long = (1/12) * mass * length**2
   # I_long = 0.6 kg⋅m²
   
   I_spin = (1/2) * mass * radius**2
   # I_spin = 0.00676 kg⋅m²

Record: ``rocket.inertia = [0.6, 0.6, 0.007]``

.. note::
   These are approximations. For competition, consider using CAD software
   (SolidWorks, Fusion 360) for precise inertia calculations.

3. Nose Cone
~~~~~~~~~~~~

**Length**

Measure from tip to base of nose cone:

.. code-block:: text

   ├─ Nose Length ─┤
   ●────────────────●
   Tip            Base

Record: ``nose_cone.length = ___ m``

**Shape**

Identify nose cone profile:

* **Von Karman**: Optimized for low drag (most common)
* **Ogive**: Curved profile
* **Conical**: Simple cone
* **Parabolic**: Parabolic curve
* **Power Series**: Generalized curve

If unsure, use ``"vonKarman"`` (safe default).

Record: ``nose_cone.kind = "vonKarman"``

**Position**

Measure distance from TAIL to nose cone base:

.. code-block:: text

   Tail                    Nose base  Tip
   ●────────────────────────●─────────●
   ├─ nose_cone.position ──┤

Record: ``nose_cone.position = ___ m`` (from tail)

4. Fins
~~~~~~~

**Number**

Count fins: typically 3 or 4

Record: ``fins.number = 3``

**Root Chord**

Measure fin length at body tube attachment:

.. code-block:: text

         ┌─ Tip
         │
         │  ← Span
         │
   ──────┴────
   ← Root Chord →

Record: ``fins.root_chord = ___ m``

**Tip Chord**

Measure fin length at tip:

Record: ``fins.tip_chord = ___ m``

**Span**

Measure fin height from body tube to tip:

Record: ``fins.span = ___ m``

**Position**

Measure distance from TAIL to fin leading edge:

.. code-block:: text

   Tail     Fin
   ●─────────┴
   ├─ pos ──┤

Record: ``fins.position = ___ m`` (from tail)

**Sweep Angle (Optional)**

Measure angle of fin leading edge from vertical:

.. code-block:: text

      │ ╱
      │╱  ← Sweep angle
      ┴

If fins are perpendicular to body, ``sweep_length = 0``.

Otherwise, measure horizontal distance from root leading edge to tip leading edge.

Record: ``fins.sweep_length = ___ m``

5. Motor
~~~~~~~~

**Dry Mass**

Weigh empty motor casing:

Record: ``motor.dry_mass = ___ kg``

**Nozzle Radius**

Measure nozzle throat diameter, divide by 2:

Record: ``motor.nozzle_radius = ___ m``

**Motor Position**

Measure from NOSE TIP to motor NOZZLE EXIT:

.. code-block:: text

   Nose tip              Nozzle
   ●───────────────────────●
   ├─ motor_position ─────┤
   (negative value)

Since motor is toward tail, this is negative:

Record: ``rocket.motor_position = -___ m``

.. note::
   Motor coordinate system is separate. The ``motor_position`` parameter
   in the rocket section defines where the motor nozzle is located in rocket coordinates.

**Grain Geometry**

For commercial motors, get these from:

* Motor manufacturer datasheet
* ThrustCurve.org motor details
* Estimate from motor dimensions

If unavailable, use defaults from similar motor class.

6. Parachute
~~~~~~~~~~~~

**Drag Coefficient × Area (Cd·S)**

This is the key parameter for parachute descent.

**Option 1: Calculate from Parachute Specs**

.. math::

   C_d \cdot S = C_d \cdot \frac{\pi D^2}{4}

Where:

* :math:`C_d` = 1.5 for round parachutes (typical)
* :math:`D` = parachute diameter (m)

Example:

.. code-block:: python

   import math
   
   diameter = 1.0  # m (3 ft parachute)
   cd = 1.5        # Round parachute
   
   cd_s = cd * (math.pi * diameter**2 / 4)
   # cd_s = 1.178 m²

**Option 2: Calculate from Desired Descent Rate**

.. math::

   C_d \cdot S = \frac{2 \cdot m \cdot g}{\\rho \cdot v^2}

Where:

* m = total mass (rocket + motor) (kg)
* g = 9.81 m/s²
* ρ = air density ≈ 1.225 kg/m³ (sea level)
* v = desired descent velocity (m/s)

Target descent rate: 4-6 m/s for safe landing

Example:

.. code-block:: python

   mass = 6.0       # kg (rocket + spent motor)
   g = 9.81         # m/s²
   rho = 1.225      # kg/m³
   v_target = 5.0   # m/s (desired descent)
   
   cd_s = (2 * mass * g) / (rho * v_target**2)
   # cd_s = 3.84 m²

Record: ``parachutes[0].cd_s = ___ m²``

Measurement Checklist
---------------------

Use this checklist to ensure you have all measurements:

.. code-block:: text

   Rocket Overall:
   ☐ radius (m)
   ☐ mass (kg, without motor)
   ☐ center_of_mass_without_motor (m from nose)
   ☐ inertia [I_long, I_long, I_spin] (kg⋅m²)
   
   Nose Cone:
   ☐ length (m)
   ☐ kind (shape name)
   ☐ position (m from tail)
   
   Fins:
   ☐ number
   ☐ root_chord (m)
   ☐ tip_chord (m)
   ☐ span (m)
   ☐ position (m from tail)
   ☐ sweep_length (m, if applicable)
   
   Motor:
   ☐ thrust_source (path to .eng file)
   ☐ dry_mass (kg)
   ☐ nozzle_radius (m)
   ☐ motor_position (m from nose, negative)
   
   Parachute:
   ☐ cd_s (m²)
   ☐ trigger (e.g., "apogee")
   ☐ lag (seconds delay)

Common Pitfalls
---------------

.. warning::
   **Coordinate System Confusion**
   
   * Rocket: nose tip is 0.0, tail is positive
   * Motor: nozzle is 0.0, combustion chamber is positive
   * ``motor_position`` in rocket config: negative value (toward tail from nose)

.. warning::
   **Including Motor Mass**
   
   ``rocket.mass`` should NOT include motor. RocketPy adds motor automatically.

.. warning::
   **Wrong Center of Mass**
   
   Measure WITHOUT motor. Motor position and mass are added separately.

.. warning::
   **Units**
   
   All measurements MUST be in SI units (meters, kilograms). Convert:
   
   * Inches → meters: multiply by 0.0254
   * Feet → meters: multiply by 0.3048
   * Pounds → kg: multiply by 0.4536

Example Measurement Session
----------------------------

Here's a complete measurement session for a 4-inch rocket:

.. code-block:: text

   Rocket: "My HPR"
   Date: 2025-11-12
   
   === Overall ===
   Length: 1250 mm = 1.25 m
   Outer Diameter: 104 mm
   Radius: 52 mm = 0.052 m
   
   === Mass ===
   Rocket (no motor): 4850 g = 4.85 kg
   Balance point from nose: 780 mm = 0.78 m
   
   Inertia (calculated):
   I_long = (1/12) × 4.85 × 1.25² = 0.633 kg⋅m²
   I_spin = (1/2) × 4.85 × 0.052² = 0.00655 kg⋅m²
   
   === Nose Cone ===
   Type: Von Karman
   Length: 300 mm = 0.30 m
   Position from tail: 1250 - 300 = 950 mm = 0.95 m
   
   === Fins (3x) ===
   Root chord: 150 mm = 0.15 m
   Tip chord: 75 mm = 0.075 m
   Span: 120 mm = 0.12 m
   Position from tail: 50 mm = 0.05 m
   Sweep: 0 m (perpendicular)
   
   === Motor ===
   Motor: AeroTech J450DM
   Empty mass: 457 g = 0.457 kg
   Nozzle radius: 25 mm = 0.025 m
   Nozzle position from nose: -600 mm = -0.60 m
   
   === Parachute ===
   Diameter: 36" = 0.914 m
   Cd×S = 1.5 × π × 0.914² / 4 = 0.984 m²

This translates to YAML:

.. code-block:: yaml

   rocket:
     name: "My HPR"
     mass: 4.85
     radius: 0.052
     inertia: [0.633, 0.633, 0.007]
     center_of_mass_without_motor: 0.78
     
     nose_cone:
       length: 0.30
       kind: "vonKarman"
       position: 0.95
     
     fins:
       number: 3
       root_chord: 0.15
       tip_chord: 0.075
       span: 0.12
       position: 0.05
     
     motor_position: -0.60
     
     parachutes:
       - name: "Main"
         cd_s: 0.984
         trigger: "apogee"
         lag: 1.5
   
   motor:
     thrust_source: "data/motors/aerotech/AeroTech_J450DM.eng"
     dry_mass: 0.457
     nozzle_radius: 0.025
     # ... other motor params from datasheet

Validation
----------

After creating configuration, validate measurements:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config configs/my_rocket.yaml \
       --name validation_test \
       --validate-only

Check validation output for:

* ✅ Static margin ≥ 2.0 (stable)
* ✅ Center of pressure behind center of gravity
* ✅ All masses positive
* ✅ Reasonable dimensions

If validation fails, re-check measurements.

See Also
--------

* :doc:`create_config` - Create configuration from measurements
* :doc:`validate_design` - Validate rocket design
* :doc:`/user/configuration/rocket_params` - Parameter reference
* :doc:`/user/tutorials/01_basic_flight` - Basic simulation tutorial

Advanced: CAD-Based Measurements
---------------------------------

For precision (recommended for competitions):

1. **Model rocket in CAD** (SolidWorks, Fusion 360, OpenRocket)
2. **Export mass properties**:
   
   * Total mass
   * Center of mass (X, Y, Z)
   * Moments of inertia (Ixx, Iyy, Izz)

3. **Use CAD values directly** in configuration

CAD provides:

* Exact inertia tensors (not approximations)
* Automatic updates when design changes
* Component-level mass breakdown
* Aerodynamic analysis (OpenRocket, RASAero)

Tools:

* **OpenRocket**: Free, rocket-specific, exports mass properties
* **Fusion 360**: Free for students, full CAD with mass properties
* **SolidWorks**: Industry standard (if you have access)
