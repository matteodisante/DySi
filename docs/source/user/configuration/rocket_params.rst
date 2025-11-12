.. _config-rocket-params:

=====================================
Rocket Parameters Reference
=====================================

This reference documents all parameters in the ``rocket`` configuration section.
The rocket section defines physical properties, geometry, mass distribution, aerodynamic surfaces, and recovery systems.

.. contents:: On this page
   :local:
   :depth: 2

--------

Overview
========

The rocket configuration is divided into these subsections:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: **Basic Properties**
        :class-card: sd-shadow-sm

        - Name and identification
        - Dry mass
        - Center of gravity location
        - Coordinate system

    .. grid-item-card:: **Geometry**
        :class-card: sd-shadow-sm

        - Caliber (diameter)
        - Total length
        - Reference areas

    .. grid-item-card:: **Inertia**
        :class-card: sd-shadow-sm

        - Moments of inertia (Ixx, Iyy, Izz)
        - About center of mass

    .. grid-item-card:: **Components**
        :class-card: sd-shadow-sm

        - Nose cone
        - Fins
        - Parachute
        - Air brakes

--------

Basic Properties
================

name
----

:Type: ``string``
:Required: Yes
:Default: ``"Rocket"``

Name or identifier for the rocket. Used in simulation outputs, plots, and logs.

.. code-block:: yaml

    rocket:
      name: "Calisto"

.. tip::
   Use descriptive names for easy identification when comparing multiple configurations:
   
   - ``"Calisto_v2.3_competition"``
   - ``"TestRocket_2024-03-15"``
   - ``"Zeus_Production_Dry_Run"``

--------

dry_mass_kg
-----------

:Type: ``float``
:Required: Yes
:Unit: kilograms (kg)

Total mass of the rocket **without motor propellant**.

Includes:

- Airframe structure (body tubes, bulkheads, centering rings)
- Nose cone
- Fins
- Recovery system (parachutes, shock cords, electronics)
- Avionics (flight computer, sensors, batteries)
- Empty motor casing

Excludes:

- Motor propellant mass
- Anything consumed during flight

.. code-block:: yaml

    rocket:
      dry_mass_kg: 15.426

.. admonition:: How to Measure
   :class: dropdown

   **Method 1: Direct weighing (most accurate)**
   
   1. Assemble complete rocket with empty motor casing
   2. Use digital scale (precision ≥ 0.1 kg)
   3. Weigh 3 times, take average
   
   **Method 2: Component-by-component**
   
   Sum masses of all components:
   
   .. code-block:: text
   
       Airframe body tubes:      2.5 kg
       Nose cone:                1.2 kg
       Fins (4×):                0.8 kg
       Motor casing (empty):     1.1 kg
       Avionics bay:             0.9 kg
       Recovery system:          0.7 kg
       Fasteners/misc:           0.3 kg
       ─────────────────────────────
       Total dry mass:           7.5 kg

.. warning::
   **Do NOT include propellant mass!** RocketPy adds motor mass automatically.
   
   If you accidentally include propellant mass, the simulation will have **double** the motor mass and produce incorrect results.

--------

coordinate_system
-----------------

:Type: ``string``
:Required: No
:Default: ``"tail_to_nose"``
:Options: ``"tail_to_nose"``, ``"nose_to_tail"``

Defines the positive direction for position measurements along the rocket axis.

.. tab-set::

    .. tab-item:: tail_to_nose (default)

        **Origin at rocket tail, positive toward nose**
        
        .. code-block:: text
        
            Nose ←─────────────────→ Tail
                 +2.0 m        0.0 m
                 
            Example positions:
            - Nose tip:           +2.0 m
            - Center of mass:     +1.2 m
            - Fin root:           +0.3 m
            - Nozzle exit:         0.0 m (origin)
        
        .. code-block:: yaml
        
            rocket:
              coordinate_system: "tail_to_nose"
              cg_location_m: 1.2       # 1.2 m from tail
              nose_cone:
                position_m: 2.0        # At rocket nose
              fins:
                position_m: 0.3        # 0.3 m from tail

    .. tab-item:: nose_to_tail

        **Origin at nose tip, positive toward tail**
        
        .. code-block:: text
        
            Nose ─────────────────→ Tail
            0.0 m           +2.0 m
                 
            Example positions:
            - Nose tip:            0.0 m (origin)
            - Center of mass:     +0.8 m
            - Fin root:           +1.7 m
            - Nozzle exit:        +2.0 m
        
        .. code-block:: yaml
        
            rocket:
              coordinate_system: "nose_to_tail"
              cg_location_m: 0.8       # 0.8 m from nose
              nose_cone:
                position_m: 0.0        # At origin
              fins:
                position_m: 1.7        # 1.7 m from nose

.. important::
   **All positions** (CG, nose cone, fins, motor, air brakes) must use the **same coordinate system**.
   
   Be consistent throughout your configuration!

.. seealso::
   - :ref:`config-motor-params-position` for motor position in rocket frame
   - :ref:`how-to-measure-rocket-dimensions` for measuring positions

--------

cg_location_m
-------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

Location of rocket's **center of gravity (dry)** measured from the coordinate system origin.

This is the **dry CG** (without motor). RocketPy will compute the **wet CG** during flight as propellant burns.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      cg_location_m: 1.255  # 1.255 m from tail

.. admonition:: How to Measure Center of Gravity
   :class: dropdown

   **Method 1: Balance point (simple, good accuracy)**
   
   1. Assemble complete rocket with **empty motor casing**
   2. Balance rocket horizontally on a knife edge, dowel, or string
   3. Measure distance from balance point to reference (tail or nose)
   
   .. image:: /_static/images/measure_cg_balance.png
      :alt: Measuring CG with balance method
      :width: 400px
      :align: center
   
   **Method 2: Two-point weighing (more accurate)**
   
   1. Place rocket horizontally on two scales
   2. Measure distances and weights:
   
      - :math:`L` = distance between scales
      - :math:`W_1` = weight on front scale
      - :math:`W_2` = weight on rear scale
      - :math:`x_1` = distance from tail to front scale
   
   3. Calculate CG from tail:
   
   .. math::
   
       x_{CG} = x_1 + \frac{W_2 \cdot L}{W_1 + W_2}
   
   **Method 3: CAD software**
   
   Use SolidWorks, Fusion 360, or OpenRocket's built-in CG calculator.

.. warning::
   **Critical for stability!** 
   
   Wrong CG position → wrong static margin → potentially unstable rocket
   
   Accuracy target: ±5 mm for small rockets, ±10 mm for large rockets

--------

cp_location_m
-------------

:Type: ``float`` or ``null``
:Required: No
:Default: ``null`` (RocketPy computes automatically)
:Unit: meters (m)

Location of rocket's **center of pressure (CP)** measured from the coordinate system origin.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      cp_location_m: null  # Let RocketPy calculate

.. tab-set::

    .. tab-item:: Auto-calculation (Recommended)

        **Let RocketPy calculate CP** from fin geometry and nose cone shape:
        
        .. code-block:: yaml
        
            rocket:
              cp_location_m: null  # Auto-calculation
              fins:
                count: 4
                root_chord_m: 0.120
                tip_chord_m: 0.040
                span_m: 0.100
                # ... RocketPy uses Barrowman equations
        
        ✅ **Advantages:**
        
        - Automatically adjusts if you change fin size
        - Uses Barrowman method (industry standard)
        - No manual calculations needed
        
        ⚠️ **Limitations:**
        
        - Assumes standard shapes (trapezoidal fins, standard nose cones)
        - May be inaccurate for complex geometries

    .. tab-item:: Manual override

        **Manually specify CP** from wind tunnel tests, CFD, or OpenRocket:
        
        .. code-block:: yaml
        
            rocket:
              coordinate_system: "tail_to_nose"
              cp_location_m: 0.516  # From OpenRocket simulation
        
        ✅ **When to use:**
        
        - Non-standard fin shapes (clipped delta, elliptical)
        - Unusual body shapes (boat-tail, flared section)
        - CFD or wind tunnel data available
        - OpenRocket/RASAero validation
        
        ⚠️ **Remember:**
        
        - CP changes with Mach number (use subsonic value)
        - Update manually if you change fin geometry

.. admonition:: Static Margin Calculation
   :class: dropdown

   RocketPy automatically computes **static margin** from CG and CP:
   
   .. math::
   
       \text{Static Margin (cal)} = \frac{CP - CG}{\text{caliber}}
   
   Where ``caliber`` is rocket diameter.
   
   **Stability criteria:**
   
   - **< 0 calibers**: Unstable ❌
   - **0-1 calibers**: Marginally stable ⚠️
   - **1-2 calibers**: Stable ✅ (competition standard)
   - **2-3 calibers**: Very stable ✅
   - **> 3 calibers**: Overstable (inefficient, excessive drag)

.. seealso::
   - :ref:`tutorial-basic-flight-stability` for static margin examples
   - :ref:`how-to-optimize-static-margin` for design iteration

--------

Geometry
========

The ``geometry`` subsection defines rocket dimensions.

.. code-block:: yaml

    rocket:
      geometry:
        caliber_m: 0.127      # Diameter in meters
        length_m: 2.000       # Total length in meters

caliber_m
---------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Outer diameter** of the main airframe body tube.

.. code-block:: yaml

    rocket:
      geometry:
        caliber_m: 0.127  # 127 mm diameter

.. tip::
   **Common calibers:**
   
   .. list-table::
      :header-rows: 1
      :widths: 30 30 40
      
      * - Description
        - Inches
        - Meters (caliber_m)
      * - Small model rocket
        - 2.6"
        - 0.066
      * - Mid-power
        - 3.0"
        - 0.076
      * - Mid-power
        - 4.0"
        - 0.102
      * - High-power
        - 5.0"
        - 0.127
      * - High-power
        - 6.0"
        - 0.152
      * - Competition
        - 6.17" (157 mm)
        - 0.157

.. admonition:: Measurement Instructions
   :class: dropdown

   1. Measure **outer diameter** with calipers at 3 locations
   2. Take average
   3. Convert to meters:
   
      - Inches → meters: multiply by 0.0254
      - Millimeters → meters: divide by 1000
   
   Example:
   
   .. code-block:: text
   
       Measurement 1:  126.8 mm
       Measurement 2:  127.1 mm
       Measurement 3:  126.9 mm
       ──────────────────────
       Average:        127.0 mm  →  0.127 m

--------

length_m
--------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Total length** of assembled rocket from nose tip to nozzle exit (or tail end).

.. code-block:: yaml

    rocket:
      geometry:
        length_m: 2.065  # Total rocket length

Includes:

- Nose cone
- All body tube sections
- Boat-tail (if present)
- Motor nozzle extending beyond airframe (if applicable)

.. admonition:: Measurement Instructions
   :class: dropdown

   **Method 1: Assembled rocket**
   
   1. Lay rocket horizontally on flat surface
   2. Measure from nose tip to nozzle exit
   3. Use measuring tape or laser distance meter
   
   **Method 2: Component sum**
   
   Add lengths of all sections:
   
   .. code-block:: text
   
       Nose cone:               0.350 m
       Upper body tube:         0.800 m
       Avionics bay:            0.215 m
       Lower body tube:         0.600 m
       Motor casing extension:  0.100 m
       ─────────────────────────────
       Total length:            2.065 m

--------

Inertia
=======

The ``inertia`` subsection defines the rocket's moments of inertia about its center of mass.

.. code-block:: yaml

    rocket:
      inertia:
        ixx_kg_m2: 6.321
        iyy_kg_m2: 6.321
        izz_kg_m2: 0.0346

These values are critical for accurate **attitude dynamics** (rotation, spin, wobble).

.. important::
   **Moments of inertia must be calculated about the dry center of mass.**
   
   RocketPy will adjust these values during flight as propellant burns and CG shifts.

ixx_kg_m2, iyy_kg_m2
--------------------

:Type: ``float``
:Required: Yes
:Unit: kg·m²

**Transverse moments of inertia** about axes perpendicular to rocket centerline.

For a rocket with **axial symmetry**, ``ixx_kg_m2`` = ``iyy_kg_m2``.

.. code-block:: yaml

    rocket:
      inertia:
        ixx_kg_m2: 6.321
        iyy_kg_m2: 6.321

.. admonition:: How to Calculate
   :class: dropdown

   **Method 1: CAD software (most accurate)**
   
   1. Create 3D model in SolidWorks/Fusion 360
   2. Assign material densities
   3. Use CAD's mass properties tool → read Ixx, Iyy
   
   **Method 2: Approximation for cylindrical rocket**
   
   For uniform density cylinder (rough estimate):
   
   .. math::
   
       I_{xx} = I_{yy} = m \left[ \frac{r^2}{4} + \frac{L^2}{12} \right]
   
   Where:
   
   - :math:`m` = dry mass (kg)
   - :math:`r` = radius (m)
   - :math:`L` = length (m)
   
   Example: ``m=15.426 kg``, ``r=0.0635 m``, ``L=2.065 m``
   
   .. math::
   
       I_{xx} = 15.426 \times \left[ \frac{0.0635^2}{4} + \frac{2.065^2}{12} \right] = 6.32\text{ kg·m}^2
   
   **Method 3: Parallel axis theorem** (component-by-component)
   
   For each component i:
   
   .. math::
   
       I_i = I_{i,cm} + m_i \cdot d_i^2
   
   Sum all components.

.. warning::
   **Approximations are acceptable for initial design**, but:
   
   - Critical for spin-stabilized rockets
   - Important for attitude control systems
   - Affects weathercocking behavior
   
   For competition rockets, use CAD-calculated values.

--------

izz_kg_m2
---------

:Type: ``float``
:Required: Yes
:Unit: kg·m²

**Axial moment of inertia** about rocket centerline (spin axis).

.. code-block:: yaml

    rocket:
      inertia:
        izz_kg_m2: 0.0346

Much smaller than Ixx/Iyy because mass is distributed close to centerline.

.. admonition:: How to Calculate
   :class: dropdown

   **Method 1: CAD software**
   
   Use CAD mass properties tool → read Izz
   
   **Method 2: Approximation for hollow cylinder**
   
   .. math::
   
       I_{zz} = \frac{m}{2} \left( r_{outer}^2 + r_{inner}^2 \right)
   
   Example: body tube with 
   
   - :math:`m = 10` kg
   - :math:`r_{outer} = 0.0635` m
   - :math:`r_{inner} = 0.061` m
   
   .. math::
   
       I_{zz} = \frac{10}{2} (0.0635^2 + 0.061^2) = 0.0387 \text{ kg·m}^2

.. tip::
   **Typical ratios for rockets:**
   
   .. math::
   
       \frac{I_{xx}}{I_{zz}} \approx 100 \text{ to } 300
   
   If your ratio is outside this range, double-check calculations.

--------

Nose Cone
=========

The ``nose_cone`` subsection defines nose cone geometry.

.. code-block:: yaml

    rocket:
      nose_cone:
        length_m: 0.55829
        kind: "vonKarman"
        position_m: 0.0

length_m
--------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Length of nose cone** from tip to base (where it meets body tube).

.. code-block:: yaml

    rocket:
      nose_cone:
        length_m: 0.558

.. admonition:: Measurement Instructions
   :class: dropdown

   1. Measure along centerline from tip to shoulder base
   2. Do NOT include shoulder length (insertion part)

--------

kind
----

:Type: ``string``
:Required: No
:Default: ``"vonKarman"``
:Options: ``"vonKarman"``, ``"conical"``, ``"ogive"``, ``"elliptical"``, ``"parabolic"``, ``"powerseries"``

Nose cone **shape profile**.

.. tab-set::

    .. tab-item:: vonKarman (Default)

        **Von Kármán profile** (Haack series, C=0)
        
        - Lowest drag coefficient for subsonic/transonic flight
        - Smooth curved profile
        - **Best for competitions** targeting max altitude
        
        .. code-block:: yaml
        
            rocket:
              nose_cone:
                kind: "vonKarman"

    .. tab-item:: ogive

        **Tangent ogive** (circular arc tangent to body)
        
        - Very common in model rocketry
        - Good drag performance
        - Easy to manufacture
        
        .. code-block:: yaml
        
            rocket:
              nose_cone:
                kind: "ogive"

    .. tab-item:: conical

        **Conical (straight taper)**
        
        - Simplest shape
        - Higher drag than curved profiles
        - Easy to make, structurally strong
        
        .. code-block:: yaml
        
            rocket:
              nose_cone:
                kind: "conical"

    .. tab-item:: elliptical

        **Elliptical profile**
        
        - Intermediate drag
        - Aesthetically pleasing
        
        .. code-block:: yaml
        
            rocket:
              nose_cone:
                kind: "elliptical"

.. seealso::
   `Nose Cone Design (Apogee Rockets) <https://www.apogeerockets.com/Tech/Rocket_Nose_Cone_Design>`_

--------

position_m
----------

:Type: ``float``
:Required: No
:Default: Depends on coordinate system
:Unit: meters (m)

**Position of nose cone tip** in rocket coordinate system.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      geometry:
        length_m: 2.065
      nose_cone:
        position_m: 2.065  # At rocket nose (tail_to_nose system)

.. tip::
   **Default position** (if omitted):
   
   - ``tail_to_nose``: ``position_m = geometry.length_m`` (at nose)
   - ``nose_to_tail``: ``position_m = 0.0`` (at origin)
   
   Usually you can omit this parameter.

--------

Fins
====

The ``fins`` subsection defines fin geometry and placement.

.. code-block:: yaml

    rocket:
      fins:
        count: 4
        root_chord_m: 0.120
        tip_chord_m: 0.040
        span_m: 0.100
        thickness_m: 0.003
        position_m: 0.373
        cant_angle_deg: 0.0
        airfoil: null

RocketPy assumes **trapezoidal fins** by default.

count
-----

:Type: ``integer``
:Required: Yes

**Number of fins** (equally spaced around body).

.. code-block:: yaml

    rocket:
      fins:
        count: 4  # 4 fins, 90° apart

.. tip::
   **Common configurations:**
   
   - **3 fins**: Minimum for stability, lighter weight
   - **4 fins**: Standard, better roll control
   - **6+ fins**: Competition rockets for max stability

--------

root_chord_m
------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Length of fin at root** (where fin attaches to body tube).

.. code-block:: yaml

    rocket:
      fins:
        root_chord_m: 0.120

.. image:: /_static/images/fin_geometry.png
   :alt: Fin geometry definition
   :width: 400px
   :align: center

--------

tip_chord_m
-----------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Length of fin at tip** (outer edge).

.. code-block:: yaml

    rocket:
      fins:
        tip_chord_m: 0.040

For **rectangular fins**, ``tip_chord_m = root_chord_m``.

--------

span_m
------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Height of fin** (perpendicular distance from body to fin tip).

.. code-block:: yaml

    rocket:
      fins:
        span_m: 0.100

.. warning::
   **Ground clearance check:**
   
   Ensure fins don't hit ground when rocket is on launch pad:
   
   .. math::
   
       \text{span} + \text{caliber}/2 < \text{rail\_height}

--------

thickness_m
-----------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Thickness of fin material**.

.. code-block:: yaml

    rocket:
      fins:
        thickness_m: 0.003  # 3 mm plywood

Used for:

- Mass calculation
- Flutter speed calculation (stiffness)

.. admonition:: Common Materials
   :class: dropdown

   .. list-table::
      :header-rows: 1
      :widths: 40 30 30
      
      * - Material
        - Typical Thickness
        - thickness_m
      * - 1/8" plywood
        - 3.2 mm
        - 0.0032
      * - 1/16" plywood
        - 1.6 mm
        - 0.0016
      * - Fiberglass (2 layers)
        - 1.0 mm
        - 0.0010
      * - Carbon fiber (2 layers)
        - 0.5 mm
        - 0.0005
      * - G10 FR4 (3 mm)
        - 3.0 mm
        - 0.0030

--------

position_m
----------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Position of fin root leading edge** in rocket coordinate system.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      fins:
        position_m: 0.373  # 0.373 m from tail

.. tip::
   **Fin placement for stability:**
   
   - Fins should be near tail (increases CP separation from CG)
   - Leave ~1-2 calibers from nozzle for exhaust flow
   
   Example: For 0.127 m caliber rocket, place fins at ≥ 0.2 m from tail

--------

cant_angle_deg
--------------

:Type: ``float``
:Required: No
:Default: ``0.0``
:Unit: degrees (°)

**Cant angle** for inducing spin stabilization.

.. code-block:: yaml

    rocket:
      fins:
        cant_angle_deg: 2.0  # 2° cant for slow spin

.. tab-set::

    .. tab-item:: No cant (0°)

        **Fins aligned with airflow** (default)
        
        - No induced spin
        - Minimum drag
        - Standard for non-spinning rockets
        
        .. code-block:: yaml
        
            rocket:
              fins:
                cant_angle_deg: 0.0

    .. tab-item:: Canted fins

        **Fins angled to induce spin**
        
        - Improves gyroscopic stability
        - Reduces weathercocking
        - Increases drag
        
        .. code-block:: yaml
        
            rocket:
              fins:
                cant_angle_deg: 3.0  # Moderate spin
        
        **Typical values:**
        
        - 1-2°: Slow spin, minimal drag
        - 3-5°: Moderate spin
        - 5-10°: Fast spin, high drag penalty

.. warning::
   **Excessive cant angle:**
   
   - Causes significant drag increase
   - May cause excessive spin rate (instability, recovery issues)
   - Generally avoid cant_angle > 5° unless specifically needed

--------

airfoil
-------

:Type: ``string`` or ``null``
:Required: No
:Default: ``null`` (flat plate)

**Airfoil cross-section** for lift/drag calculations.

.. code-block:: yaml

    rocket:
      fins:
        airfoil: null  # Flat plate (default)

.. tab-set::

    .. tab-item:: null (Flat Plate)

        **Simplest model** (default)
        
        - Assumes fins are flat plates
        - Reasonable accuracy for thin fins
        
        .. code-block:: yaml
        
            rocket:
              fins:
                airfoil: null

    .. tab-item:: Custom Airfoil

        **Specify airfoil profile** for higher accuracy
        
        Provide path to airfoil data file (RocketPy format):
        
        .. code-block:: yaml
        
            rocket:
              fins:
                airfoil: "data/airfoils/NACA0012.txt"
        
        .. code-block:: text
           :caption: data/airfoils/NACA0012.txt
        
            # NACA 0012 airfoil coordinates
            # x/c    y/c
            1.0000  0.0000
            0.9500  0.0157
            0.9000  0.0222
            # ... more coordinates

.. seealso::
   - :ref:`how-to-create-airfoil-file` for custom profiles
   - `UIUC Airfoil Database <https://m-selig.ae.illinois.edu/ads/coord_database.html>`_

--------

Parachute
=========

The ``parachute`` subsection defines recovery system parameters.

.. code-block:: yaml

    rocket:
      parachute:
        enabled: true
        name: "Main"
        cd_s: 10.0
        trigger: "apogee"
        sampling_rate_hz: 105.0
        lag_s: 1.5
        noise_std: [0.0, 0.0, 0.0]

enabled
-------

:Type: ``boolean``
:Required: No
:Default: ``true``

Enable or disable parachute deployment.

.. code-block:: yaml

    rocket:
      parachute:
        enabled: true

Set to ``false`` for ballistic flights or testing without recovery.

--------

name
----

:Type: ``string``
:Required: No
:Default: ``"Main"``

Identifier for parachute (useful for dual-deployment systems).

.. code-block:: yaml

    rocket:
      parachute:
        name: "Main Chute"

--------

cd_s
----

:Type: ``float``
:Required: Yes
:Unit: m²

**Drag coefficient × reference area** for parachute.

.. code-block:: yaml

    rocket:
      parachute:
        cd_s: 10.0

.. admonition:: How to Calculate
   :class: dropdown

   **Formula:**
   
   .. math::
   
       C_D S = C_D \times \frac{\pi D^2}{4}
   
   Where:
   
   - :math:`C_D` = drag coefficient (typically 0.75-2.2 for parachutes)
   - :math:`D` = parachute diameter (m)
   
   **Example:** 1.5 m diameter parachute, :math:`C_D = 1.5`
   
   .. math::
   
       C_D S = 1.5 \times \frac{\pi \times 1.5^2}{4} = 2.65 \text{ m}^2
   
   **Typical values:**
   
   .. list-table::
      :header-rows: 1
      :widths: 40 30 30
      
      * - Parachute Type
        - Cd (typical)
        - Example cd_s
      * - Hemispherical
        - 2.2
        - 15.0
      * - Conical
        - 0.75
        - 6.0
      * - Annular (Top Flight)
        - 1.5
        - 10.0
      * - Cruciform
        - 1.0
        - 8.0

.. tip::
   **Choosing cd_s for target descent rate:**
   
   .. math::
   
       v_{descent} = \sqrt{\frac{2mg}{\rho \cdot C_D S}}
   
   Solve for :math:`C_D S`:
   
   .. math::
   
       C_D S = \frac{2mg}{\rho \cdot v_{descent}^2}
   
   Example: 20 kg rocket, target 5 m/s descent, ρ=1.225 kg/m³
   
   .. math::
   
       C_D S = \frac{2 \times 20 \times 9.81}{1.225 \times 5^2} = 12.8 \text{ m}^2

--------

trigger
-------

:Type: ``string`` or ``float``
:Required: No
:Default: ``"apogee"``

**Deployment trigger condition**.

.. tab-set::

    .. tab-item:: "apogee"

        **Deploy at apogee** (highest altitude)
        
        .. code-block:: yaml
        
            rocket:
              parachute:
                trigger: "apogee"
        
        RocketPy detects apogee when vertical velocity changes sign.

    .. tab-item:: Altitude (m)

        **Deploy at specific altitude above ground**
        
        .. code-block:: yaml
        
            rocket:
              parachute:
                trigger: 800.0  # Deploy at 800 m AGL
        
        Used for dual-deployment (drogue at apogee, main at low altitude):
        
        .. code-block:: yaml
        
            rocket:
              parachute:
                - name: "Drogue"
                  cd_s: 1.5
                  trigger: "apogee"
                - name: "Main"
                  cd_s: 15.0
                  trigger: 300.0  # Main at 300 m

.. note::
   **Current limitation:** rocket-sim supports **single parachute** only.
   
   For dual-deployment, use RocketPy API directly.

--------

sampling_rate_hz
----------------

:Type: ``float``
:Required: No
:Default: ``105.0``
:Unit: hertz (Hz)

**Sampling rate** of altimeter for trigger detection.

.. code-block:: yaml

    rocket:
      parachute:
        sampling_rate_hz: 105.0

Affects simulation of realistic deployment timing (accounts for sensor update rate).

--------

lag_s
-----

:Type: ``float``
:Required: No
:Default: ``1.5``
:Unit: seconds (s)

**Deployment lag time** from trigger to full parachute inflation.

.. code-block:: yaml

    rocket:
      parachute:
        lag_s: 1.5

Accounts for:

- Ejection charge firing delay
- Parachute leaving deployment bag
- Line stretch
- Canopy inflation time

.. admonition:: Typical Values
   :class: dropdown

   .. list-table::
      :header-rows: 1
      :widths: 50 50
      
      * - System
        - lag_s
      * - Small drogue (0.3 m)
        - 0.5 - 1.0 s
      * - Main chute (1.5 m)
        - 1.0 - 2.0 s
      * - Large main (3.0 m)
        - 2.0 - 3.0 s
      * - Tender Descender / reefed chute
        - 0.5 - 1.0 s

--------

noise_std
---------

:Type: ``list of float`` (3 elements)
:Required: No
:Default: ``[0.0, 0.0, 0.0]``
:Unit: various (pressure, x, y position)

**Standard deviation of sensor noise** for Monte Carlo simulations.

.. code-block:: yaml

    rocket:
      parachute:
        noise_std: [5.0, 0.0, 0.0]  # ±5 Pa pressure noise

.. note::
   **Advanced parameter** - usually leave at default ``[0.0, 0.0, 0.0]`` unless:
   
   - Running Monte Carlo with sensor uncertainties
   - Modeling specific altimeter characteristics

--------

Air Brakes
==========

The ``air_brakes`` subsection defines active drag control for apogee targeting.

.. code-block:: yaml

    rocket:
      air_brakes:
        enabled: true
        drag_coefficient: 1.5
        reference_area_m2: 0.01
        position_m: -0.5
        deployment_level: 1.0
        controller:
          algorithm: "pid"
          target_apogee_m: 3000.0
          kp: 0.001

.. warning::
   **Advanced feature** - requires custom motor controller hardware
   
   See :ref:`how-to-implement-air-brakes` for complete setup guide.

enabled
-------

:Type: ``boolean``
:Required: No
:Default: ``false``

Enable or disable air brakes system.

.. code-block:: yaml

    rocket:
      air_brakes:
        enabled: true

--------

drag_coefficient
----------------

:Type: ``float``
:Required: No (required if ``drag_coefficient_curve`` not provided)
:Default: ``1.5``

**Drag coefficient** of fully deployed air brakes.

.. code-block:: yaml

    rocket:
      air_brakes:
        drag_coefficient: 1.5

.. tip::
   **Typical values:**
   
   - Flat plate perpendicular to flow: 1.28
   - Air brake flaps (30-45° deployment): 1.0 - 2.0

--------

reference_area_m2
-----------------

:Type: ``float``
:Required: Yes
:Unit: m²

**Reference area** of deployed air brake surface.

.. code-block:: yaml

    rocket:
      air_brakes:
        reference_area_m2: 0.01  # 100 cm²

--------

position_m
----------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Position of air brake** in rocket coordinate system.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      air_brakes:
        position_m: 1.5  # 1.5 m from tail

--------

controller
----------

:Type: ``dict``
:Required: No

**Control algorithm parameters** for air brake deployment.

.. code-block:: yaml

    rocket:
      air_brakes:
        controller:
          algorithm: "pid"
          target_apogee_m: 3000.0
          kp: 0.001
          ki: 0.0001
          kd: 0.01
          sampling_rate_hz: 20.0

See :ref:`config-airbrakes-controller` for detailed parameter reference.

--------

Drag Curves
===========

Custom drag curves can be specified for power-off and power-on flight phases.

power_off_drag
--------------

:Type: ``string`` or ``null``
:Required: No
:Default: ``null`` (RocketPy computes from geometry)

**Path to power-off drag curve** CSV file.

.. code-block:: yaml

    rocket:
      power_off_drag: "data/drag_curves/calisto_power_off.csv"

.. admonition:: Drag Curve File Format
   :class: dropdown

   CSV file with Mach number and drag coefficient:
   
   .. code-block:: text
      :caption: data/drag_curves/calisto_power_off.csv
   
       # Mach, Cd
       0.0, 0.45
       0.3, 0.46
       0.6, 0.48
       0.9, 0.52
       1.0, 0.65
       1.2, 0.58
       1.5, 0.52
   
   - First column: Mach number
   - Second column: Drag coefficient (dimensionless)
   - Lines starting with ``#`` are comments

.. seealso::
   - :ref:`how-to-generate-drag-curve` from CFD or wind tunnel
   - :ref:`example-rasaero-to-rocketpy` for importing RASAero data

power_on_drag
-------------

:Type: ``string`` or ``null``
:Required: No
:Default: ``null`` (same as power_off_drag)

**Path to power-on drag curve** CSV file (during motor burn).

.. code-block:: yaml

    rocket:
      power_on_drag: "data/drag_curves/calisto_power_on.csv"

Usually slightly different from power-off due to exhaust plume effects.

--------

Complete Example
================

.. literalinclude:: ../../../../configs/single_sim/02_complete.yaml
   :language: yaml
   :lines: 1-50
   :caption: Complete rocket configuration example
   :emphasize-lines: 2,3,9-11,28-32

--------

See Also
========

.. seealso::

   **Configuration References:**
   
   - :ref:`config-motor-params` - Motor parameters and thrust curves
   - :ref:`config-environment-params` - Launch site and atmospheric conditions
   - :ref:`config-simulation-params` - Simulation settings
   
   **Tutorials:**
   
   - :ref:`tutorial-basic-flight` - Step-by-step first simulation
   - :ref:`tutorial-stability-analysis` - Static margin calculation
   
   **How-To Guides:**
   
   - :ref:`how-to-measure-rocket` - Physical parameter measurement techniques
   - :ref:`how-to-optimize-static-margin` - Iterative design for stability
   - :ref:`how-to-dual-deployment` - Setting up drogue + main parachute
   
   **Examples:**
   
   - :ref:`example-competition-rocket` - Full competition rocket config
   - :ref:`example-high-power-rocket` - Level 2/3 certification rocket
