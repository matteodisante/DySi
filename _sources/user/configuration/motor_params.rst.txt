.. _config-motor-params:

=====================================
Motor Parameters Reference
=====================================

This reference documents all parameters in the ``motor`` configuration section.
The motor section defines propulsion system properties including thrust curves, grain geometry, and nozzle characteristics.

.. contents:: On this page
   :local:
   :depth: 2

--------

Overview
========

The motor configuration supports three motor types:

.. grid:: 3
    :gutter: 2

    .. grid-item-card:: **SolidMotor**
        :class-card: sd-shadow-sm

        Solid propellant grains
        
        - Thrust curve required
        - Grain geometry
        - Burn time

    .. grid-item-card:: **HybridMotor**
        :class-card: sd-shadow-sm

        Solid fuel + liquid oxidizer
        
        - Advanced modeling
        - Fuel regression
        - Oxidizer flow

    .. grid-item-card:: **LiquidMotor**
        :class-card: sd-shadow-sm

        Liquid propellants
        
        - Tank pressurization
        - Feed system
        - Complex dynamics

.. note::
   **Current support:** rocket-sim primarily supports **SolidMotor**.
   
   HybridMotor and LiquidMotor require RocketPy API for advanced configuration.

--------

Basic Properties
================

type
----

:Type: ``string``
:Required: No
:Default: ``"SolidMotor"``
:Options: ``"SolidMotor"``, ``"HybridMotor"``, ``"LiquidMotor"``

**Motor type** determines which propulsion model RocketPy uses.

.. code-block:: yaml

    motor:
      type: "SolidMotor"

.. tab-set::

    .. tab-item:: SolidMotor (Default)

        **Solid propellant motor**
        
        - Pre-cast propellant grains
        - Thrust curve from test data or simulation
        - Simple, reliable, most common
        
        .. code-block:: yaml
        
            motor:
              type: "SolidMotor"
              thrust_source: "data/motors/Cesaroni_M1670.eng"

    .. tab-item:: HybridMotor

        **Hybrid propulsion**
        
        - Solid fuel grain + liquid oxidizer
        - More complex modeling
        - Requires additional parameters
        
        .. code-block:: yaml
        
            motor:
              type: "HybridMotor"
              # Additional hybrid-specific params required

    .. tab-item:: LiquidMotor

        **Liquid bipropellant**
        
        - Liquid fuel + liquid oxidizer
        - Most complex modeling
        - Requires tank, feed system params
        
        .. code-block:: yaml
        
            motor:
              type: "LiquidMotor"
              # Additional liquid-specific params required

--------

thrust_source
-------------

:Type: ``string``
:Required: **Yes** for SolidMotor
:File formats: ``.eng``, ``.rse``, ``.csv``

**Path to thrust curve data file**.

.. code-block:: yaml

    motor:
      thrust_source: "data/motors/Cesaroni_M1670.eng"

.. admonition:: Thrust Curve File Formats
   :class: dropdown

   **RASP Engine Format (.eng) - Recommended**
   
   Standard format for commercial motors:
   
   .. code-block:: text
      :caption: data/motors/Cesaroni_M1670.eng
   
       ; Cesaroni M1670-P
       M1670-P 75 757 0 1.815 3.101 Pro75
       0.0 0
       0.1 1800
       0.5 1850
       1.5 1750
       2.8 1600
       3.5 800
       3.8 0
   
   - First line: Comment (semicolon)
   - Second line: Motor name, diameter (mm), length (mm), delays, propellant mass (kg), total mass (kg), manufacturer
   - Data: Time (s), Thrust (N)
   
   **CSV Format**
   
   Simple comma-separated values:
   
   .. code-block:: text
      :caption: data/motors/custom_motor.csv
   
       # Time (s), Thrust (N)
       0.0, 0
       0.1, 1800
       0.5, 1850
       1.5, 1750
       2.8, 1600
       3.5, 800
       3.8, 0
   
   - Lines starting with ``#`` are comments
   - First column: Time (seconds)
   - Second column: Thrust (Newtons)

.. tip::
   **Where to find thrust curves:**
   
   - `ThrustCurve.org <https://www.thrustcurve.org/>`_ - Database of commercial motors
   - Motor manufacturer websites (Cesaroni, AeroTech, etc.)
   - RASP download: includes thousands of motor files
   - Motor test stand data (custom motors)

.. warning::
   **File path rules:**
   
   - Relative paths are from project root (where you run scripts)
   - Use forward slashes ``/`` even on Windows
   - Check file exists before running simulation

--------

Coordinate System
=================

.. _config-motor-params-coordinate-system:

coordinate_system_orientation
------------------------------

:Type: ``string``
:Required: No
:Default: ``"nozzle_to_combustion_chamber"``
:Options: ``"nozzle_to_combustion_chamber"``, ``"combustion_chamber_to_nozzle"``

**Motor internal coordinate system** for position measurements **within the motor**.

.. important::
   This is **separate** from the rocket coordinate system (``tail_to_nose`` or ``nose_to_tail``).
   
   Motor positions are defined **relative to motor**, then the complete motor is positioned in rocket frame using ``position_m``.

.. tab-set::

    .. tab-item:: nozzle_to_combustion_chamber (Default)

        **Origin at nozzle exit, positive toward combustion chamber**
        
        .. code-block:: text
        
            Combustion ←──────────→ Nozzle
            Chamber              Exit
            +0.7 m               0.0 m (origin)
        
        .. code-block:: yaml
        
            motor:
              coordinate_system_orientation: "nozzle_to_combustion_chamber"
              nozzle_position_m: 0.0                      # Always 0.0 in this system
              grains_center_of_mass_position_m: 0.317     # 0.317 m from nozzle
              center_of_dry_mass_position_m: 0.317        # 0.317 m from nozzle

    .. tab-item:: combustion_chamber_to_nozzle

        **Origin at combustion chamber forward end, positive toward nozzle**
        
        .. code-block:: text
        
            Combustion ──────────→ Nozzle
            Chamber              Exit
            0.0 m (origin)       +0.7 m
        
        .. code-block:: yaml
        
            motor:
              coordinate_system_orientation: "combustion_chamber_to_nozzle"
              nozzle_position_m: 0.7                      # 0.7 m from chamber
              grains_center_of_mass_position_m: 0.383     # 0.383 m from chamber
              center_of_dry_mass_position_m: 0.383

.. seealso::
   - :ref:`config-motor-params-position` for positioning motor in rocket frame
   - :ref:`tutorial-coordinate-systems` for complete coordinate system guide

--------

.. _config-motor-params-position:

position_m
----------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Position of motor nozzle exit** in **rocket coordinate system**.

.. code-block:: yaml

    rocket:
      coordinate_system: "tail_to_nose"
      geometry:
        length_m: 2.065
    
    motor:
      position_m: 0.0  # Nozzle at tail (0.0 m from tail)

.. important::
   ``position_m`` is measured in the **rocket coordinate system**, not the motor coordinate system.

.. tab-set::

    .. tab-item:: tail_to_nose rocket

        **Rocket origin at tail, positive toward nose**
        
        Motor nozzle typically at or near tail:
        
        .. code-block:: yaml
        
            rocket:
              coordinate_system: "tail_to_nose"
            
            motor:
              position_m: 0.0  # Nozzle flush with tail
              # OR
              position_m: 0.1  # Nozzle 0.1 m from tail (recessed)

    .. tab-item:: nose_to_tail rocket

        **Rocket origin at nose, positive toward tail**
        
        Motor nozzle position = rocket length:
        
        .. code-block:: yaml
        
            rocket:
              coordinate_system: "nose_to_tail"
              geometry:
                length_m: 2.065
            
            motor:
              position_m: 2.065  # Nozzle at tail (2.065 m from nose)

.. admonition:: Measuring Motor Position
   :class: dropdown

   **Method 1: Nozzle flush with tail**
   
   Most common configuration - nozzle exit aligns with rocket tail:
   
   - ``tail_to_nose``: ``position_m = 0.0``
   - ``nose_to_tail``: ``position_m = rocket.geometry.length_m``
   
   **Method 2: Nozzle recessed (inside body tube)**
   
   Measure distance from tail/nose to nozzle exit:
   
   .. code-block:: text
   
       tail_to_nose system:
           Tail ──── 0.15 m ──── Nozzle Exit ──── rest of motor
           
           position_m = 0.15
   
   **Method 3: Nozzle extends beyond tail**
   
   If nozzle protrudes past rocket tail:
   
   .. code-block:: text
   
       tail_to_nose system:
           Nozzle Exit ──── 0.05 m ──── Tail ──── body tube
           
           position_m = -0.05  # Negative! (extends beyond tail)

--------

Mass Properties
===============

dry_mass_kg
-----------

:Type: ``float``
:Required: Yes
:Unit: kilograms (kg)

**Mass of motor casing and hardware** without propellant.

.. code-block:: yaml

    motor:
      dry_mass_kg: 1.815

Includes:

- Motor casing (aluminum, fiberglass, etc.)
- Nozzle hardware
- Bulkheads and closures
- O-rings, snap rings
- Igniter (negligible mass)

Excludes:

- Propellant (grains)

.. admonition:: How to Determine
   :class: dropdown

   **Method 1: Manufacturer specification (recommended)**
   
   Check motor data sheet:
   
   - ThrustCurve.org: "Empty Weight"
   - Motor manual: "Case Weight"
   
   **Method 2: Weigh empty motor**
   
   1. Use motor after firing (propellant burned)
   2. Clean out residue
   3. Weigh on digital scale
   
   **Method 3: From .eng file**
   
   Parse RASP .eng file header:
   
   .. code-block:: text
   
       M1670-P 75 757 0 1.815 3.101 Pro75
                          ─────  ─────
                          Prop   Total
   
   dry_mass_kg = total_mass - propellant_mass = 3.101 - 1.815 = 1.286 kg

--------

center_of_dry_mass_position_m
------------------------------

:Type: ``float``
:Required: No
:Default: Computed from geometry
:Unit: meters (m)

**Center of mass of empty motor casing** in motor coordinate system.

.. code-block:: yaml

    motor:
      coordinate_system_orientation: "nozzle_to_combustion_chamber"
      center_of_dry_mass_position_m: 0.317  # 0.317 m from nozzle

.. admonition:: How to Determine
   :class: dropdown

   **Method 1: Assume uniform casing (simplest)**
   
   For cylindrical motor casing with uniform thickness:
   
   .. math::
   
       x_{dry} = \frac{L_{motor}}{2}
   
   **Method 2: Balance empty motor**
   
   1. Use motor after burn (empty)
   2. Balance on knife edge
   3. Measure distance from nozzle exit to balance point
   
   **Method 3: CAD model**
   
   Model motor casing in CAD → read CoM

.. note::
   If omitted, RocketPy estimates from motor geometry.
   
   For accurate simulations, measure or calculate explicitly.

--------

dry_inertia
-----------

:Type: ``tuple of float`` (3 elements: Ixx, Iyy, Izz)
:Required: No
:Default: ``(0.125, 0.125, 0.002)``
:Unit: kg·m²

**Moments of inertia of empty motor** about its center of mass.

.. code-block:: yaml

    motor:
      dry_inertia: [0.125, 0.125, 0.002]  # [Ixx, Iyy, Izz]

- ``Ixx, Iyy``: Transverse inertia (perpendicular to motor axis)
- ``Izz``: Axial inertia (spin axis)

.. admonition:: How to Calculate
   :class: dropdown

   **Method 1: Hollow cylinder approximation**
   
   For thin-walled cylindrical casing:
   
   .. math::
   
       I_{xx} = I_{yy} = m \left[ \frac{r^2}{2} + \frac{L^2}{12} \right]
   
   .. math::
   
       I_{zz} = m r^2
   
   Where:
   
   - :math:`m` = dry_mass_kg
   - :math:`r` = casing outer radius (m)
   - :math:`L` = motor length (m)
   
   **Example:** 
   
   - :math:`m = 1.5` kg
   - :math:`r = 0.0375` m (75 mm diameter)
   - :math:`L = 0.7` m
   
   .. math::
   
       I_{xx} = 1.5 \times \left[ \frac{0.0375^2}{2} + \frac{0.7^2}{12} \right] = 0.063 \text{ kg·m}^2
   
   .. math::
   
       I_{zz} = 1.5 \times 0.0375^2 = 0.002 \text{ kg·m}^2

.. note::
   Default values are reasonable estimates for 75 mm diameter motors.
   
   For high-fidelity simulations, calculate from motor geometry or use CAD.

--------

Nozzle Geometry
===============

nozzle_radius_m
---------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Outer radius of motor nozzle exit**.

.. code-block:: yaml

    motor:
      nozzle_radius_m: 0.033  # 33 mm radius, 66 mm diameter

Used for:

- Base drag calculations
- Exit pressure thrust correction

.. admonition:: How to Measure
   :class: dropdown

   1. Measure **nozzle exit diameter** with calipers
   2. Divide by 2 to get radius
   3. Convert to meters:
   
      - Millimeters → meters: divide by 1000
      - Inches → meters: multiply by 0.0254
   
   Example:
   
   .. code-block:: text
   
       Nozzle exit diameter: 66 mm
       Radius: 66 / 2 = 33 mm = 0.033 m

--------

throat_radius_m
---------------

:Type: ``float``
:Required: No
:Default: ``0.011``
:Unit: meters (m)

**Radius of nozzle throat** (smallest cross-section).

.. code-block:: yaml

    motor:
      throat_radius_m: 0.011  # 11 mm radius

Used for:

- Chamber pressure estimation
- Thrust coefficient calculations
- Advanced propulsion modeling

.. note::
   **Not required for basic simulations.**
   
   RocketPy can estimate from nozzle exit radius if omitted.

--------

nozzle_position_m
-----------------

:Type: ``float``
:Required: No
:Default: Depends on motor coordinate system
:Unit: meters (m)

**Position of nozzle exit** in **motor coordinate system**.

.. code-block:: yaml

    motor:
      coordinate_system_orientation: "nozzle_to_combustion_chamber"
      nozzle_position_m: 0.0  # Always 0.0 for this orientation

.. tab-set::

    .. tab-item:: nozzle_to_combustion_chamber

        **Nozzle at origin** (always 0.0)
        
        .. code-block:: yaml
        
            motor:
              coordinate_system_orientation: "nozzle_to_combustion_chamber"
              nozzle_position_m: 0.0  # Fixed

    .. tab-item:: combustion_chamber_to_nozzle

        **Nozzle at +L (motor length)**
        
        .. code-block:: yaml
        
            motor:
              coordinate_system_orientation: "combustion_chamber_to_nozzle"
              nozzle_position_m: 0.7  # Motor length = 0.7 m

.. tip::
   Use default (0.0) for ``nozzle_to_combustion_chamber`` orientation.

--------

Propellant Grain Geometry
==========================

For **SolidMotor** only. These parameters define the propellant grain configuration.

.. image:: /_static/images/motor_grain_geometry.png
   :alt: Solid motor grain geometry
   :width: 500px
   :align: center

grain_number
------------

:Type: ``integer``
:Required: Yes (for SolidMotor)

**Number of propellant grains** stacked in motor.

.. code-block:: yaml

    motor:
      grain_number: 5

.. tip::
   **Typical configurations:**
   
   - **1 grain**: Short impulse, simple BATES grain
   - **3-5 grains**: Medium impulse (most common)
   - **6-8 grains**: Long burn, high total impulse

--------

grain_density_kg_m3
-------------------

:Type: ``float``
:Required: Yes
:Unit: kg/m³

**Density of propellant** material.

.. code-block:: yaml

    motor:
      grain_density_kg_m3: 1815.0  # APCP propellant

.. admonition:: Common Propellant Densities
   :class: dropdown

   .. list-table::
      :header-rows: 1
      :widths: 50 50
      
      * - Propellant Type
        - Density (kg/m³)
      * - APCP (Ammonium Perchlorate)
        - 1700 - 1850
      * - Black Powder
        - 1700 - 1800
      * - KNDX (Potassium Nitrate / Dextrose)
        - 1700 - 1900
      * - KNSB (Potassium Nitrate / Sorbitol)
        - 1800 - 1900
      * - HTPB (Hydroxyl-Terminated Polybutadiene)
        - 1750 - 1800

.. tip::
   Check manufacturer data sheets for exact density.
   
   For commercial motors: ThrustCurve.org often lists propellant type.

--------

grain_outer_radius_m
--------------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Outer radius of cylindrical propellant grain**.

.. code-block:: yaml

    motor:
      grain_outer_radius_m: 0.033  # 33 mm radius

Should match motor casing inner radius (minus inhibitor thickness if present).

--------

grain_initial_inner_radius_m
----------------------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Inner radius of grain bore** (hollow core) at ignition.

.. code-block:: yaml

    motor:
      grain_initial_inner_radius_m: 0.015  # 15 mm bore radius

For **BATES (cylindrical core-burning)** grains.

.. admonition:: Grain Burn Geometry
   :class: dropdown

   As motor burns, inner radius increases:
   
   .. code-block:: text
   
       t=0 (ignition):
       ╔═══════════════╗
       ║  ░░░░░░░░░░░  ║  grain_outer_radius_m = 33 mm
       ║  ░░░╔═╗░░░░  ║
       ║  ░░░║ ║░░░░  ║  grain_initial_inner_radius_m = 15 mm
       ║  ░░░╚═╝░░░░  ║
       ║  ░░░░░░░░░░░  ║
       ╚═══════════════╝
       
       t=burnout:
       ╔═══════════════╗
       ║  ╔═════════╗  ║  Inner radius → grain_outer_radius_m
       ║  ║         ║  ║  (all propellant consumed)
       ║  ║         ║  ║
       ║  ╚═════════╝  ║
       ╚═══════════════╝
   
   RocketPy models regression of burning surface.

--------

grain_initial_height_m
----------------------

:Type: ``float``
:Required: Yes
:Unit: meters (m)

**Axial length of each individual grain**.

.. code-block:: yaml

    motor:
      grain_number: 5
      grain_initial_height_m: 0.120  # Each grain is 120 mm tall
      # Total propellant length = 5 × 0.120 = 0.600 m

--------

grain_separation_m
------------------

:Type: ``float``
:Required: No
:Default: ``0.005``
:Unit: meters (m)

**Spacing between stacked grains**.

.. code-block:: yaml

    motor:
      grain_separation_m: 0.005  # 5 mm gap

Small gaps between grains affect:

- Total motor length
- Burn surface area
- Pressure distribution

.. note::
   For commercial motors, grain_separation is often negligible (0.001 - 0.005 m).

--------

grains_center_of_mass_position_m
---------------------------------

:Type: ``float``
:Required: No
:Default: Computed from grain geometry
:Unit: meters (m)

**Center of mass of all propellant grains** (combined) in motor coordinate system.

.. code-block:: yaml

    motor:
      coordinate_system_orientation: "nozzle_to_combustion_chamber"
      grains_center_of_mass_position_m: 0.317  # 0.317 m from nozzle

.. admonition:: How to Calculate
   :class: dropdown

   For symmetrically stacked grains centered in motor:
   
   .. math::
   
       x_{grains} = x_{nozzle} + \frac{L_{motor}}{2}
   
   Where :math:`L_{motor}` is the total grain stack length.
   
   **Example:** 5 grains, each 0.120 m tall, 0.005 m separation
   
   .. math::
   
       L_{grain\_stack} = 5 \times 0.120 + 4 \times 0.005 = 0.620 \text{ m}
   
   If motor coordinate system is ``nozzle_to_combustion_chamber``:
   
   .. math::
   
       x_{grains} = 0.0 + \frac{0.620}{2} = 0.310 \text{ m}

.. note::
   RocketPy computes this automatically from grain geometry if omitted.

--------

Burn Characteristics
====================

burn_time_s
-----------

:Type: ``float`` or ``null``
:Required: No
:Default: ``null`` (computed from thrust curve)
:Unit: seconds (s)

**Total burn time** of motor.

.. code-block:: yaml

    motor:
      burn_time_s: null  # Auto-detect from thrust curve

.. tab-set::

    .. tab-item:: Auto-detection (Recommended)

        **Let RocketPy determine burn time** from thrust curve:
        
        .. code-block:: yaml
        
            motor:
              burn_time_s: null
        
        RocketPy finds when thrust drops to near-zero.

    .. tab-item:: Manual override

        **Specify burn time explicitly**:
        
        .. code-block:: yaml
        
            motor:
              burn_time_s: 3.8
        
        Useful for:
        
        - Truncating thrust curve
        - Matching manufacturer specification
        - Custom burn profiles

--------

Advanced Parameters
===================

interpolation_method
--------------------

:Type: ``string``
:Required: No
:Default: ``"linear"``
:Options: ``"linear"``, ``"spline"``, ``"akima"``

**Interpolation method** for thrust curve between data points.

.. code-block:: yaml

    motor:
      interpolation_method: "spline"

.. tab-set::

    .. tab-item:: linear (Default)

        **Linear interpolation**
        
        - Straight lines between points
        - Fast, simple
        - May introduce discontinuities in derivatives
        
        .. code-block:: yaml
        
            motor:
              interpolation_method: "linear"

    .. tab-item:: spline

        **Cubic spline interpolation**
        
        - Smooth curves between points
        - Continuous first and second derivatives
        - Better for integration
        
        .. code-block:: yaml
        
            motor:
              interpolation_method: "spline"

    .. tab-item:: akima

        **Akima spline**
        
        - Avoids overshooting between points
        - Good for non-smooth data
        
        .. code-block:: yaml
        
            motor:
              interpolation_method: "akima"

.. tip::
   Use ``"spline"`` for smoother simulations, especially with sparse thrust data.

--------

reference_pressure
------------------

:Type: ``float`` or ``null``
:Required: No
:Default: ``null`` (no correction)
:Unit: pascals (Pa)

**Atmospheric pressure at which thrust curve was measured**.

.. code-block:: yaml

    motor:
      reference_pressure: 101325  # Sea level standard atmosphere

RocketPy corrects thrust for altitude:

.. math::

   F_{total}(h) = F_{curve} + (P_{ref} - P_{ambient}(h)) \times A_{nozzle}

Where:

- :math:`F_{curve}` = thrust from thrust curve
- :math:`P_{ref}` = reference pressure (from config)
- :math:`P_{ambient}(h)` = ambient pressure at altitude h
- :math:`A_{nozzle}` = nozzle exit area

.. admonition:: When to Use
   :class: dropdown

   **Set reference_pressure if:**
   
   - Thrust curve from motor test stand (usually sea level = 101325 Pa)
   - Flying at significantly different altitude (mountain launch sites)
   - High-altitude flights (>3000 m)
   
   **Omit (null) if:**
   
   - Using manufacturer thrust curves (already altitude-corrected)
   - Launch site near sea level
   - Uncertainty in test conditions

.. warning::
   **Incorrect reference_pressure** can introduce 5-10% thrust error at high altitude!
   
   Check motor test report for atmospheric conditions during testing.

--------

Complete Example
================

.. literalinclude:: ../../../../configs/single_sim/02_complete.yaml
   :language: yaml
   :lines: 52-99
   :caption: Complete motor configuration example
   :emphasize-lines: 2,3,8,16-22

--------

Motor Thrust Curve Files
=========================

Thrust curve files define motor thrust vs. time.

RASP .eng Format
----------------

Standard format for commercial motors:

.. code-block:: text
   :caption: data/motors/Cesaroni_M1670.eng

    ; Cesaroni M1670-P
    ; 75mm diameter, 757mm length
    M1670-P 75 757 0 1.815 3.101 Pro75
    0.0 0
    0.05 1200
    0.1 1800
    0.5 1850
    1.0 1820
    1.5 1750
    2.0 1680
    2.5 1620
    2.8 1600
    3.2 1200
    3.5 800
    3.7 200
    3.8 0

**Header line format:**

.. code-block:: text

    MotorName Dia(mm) Len(mm) Delays Prop(kg) Total(kg) Manufacturer

**Data format:**

.. code-block:: text

    Time(s) Thrust(N)

CSV Format
----------

Simple comma/space-separated values:

.. code-block:: text
   :caption: data/motors/custom_motor.csv

    # Custom Motor Thrust Curve
    # Time (s), Thrust (N)
    0.0, 0
    0.1, 1800
    0.5, 1850
    1.5, 1750
    2.8, 1600
    3.5, 800
    3.8, 0

--------

Common Motor Examples
=====================

Small High-Power (H-J Class)
-----------------------------

.. code-block:: yaml

    motor:
      type: "SolidMotor"
      thrust_source: "data/motors/AeroTech_J450.eng"
      dry_mass_kg: 0.285
      dry_inertia: [0.01, 0.01, 0.0002]
      nozzle_radius_m: 0.017
      grain_number: 1
      grain_density_kg_m3: 1750.0
      grain_outer_radius_m: 0.027
      grain_initial_inner_radius_m: 0.012
      grain_initial_height_m: 0.140
      position_m: 0.0  # tail_to_nose rocket

Medium High-Power (K-L Class)
------------------------------

.. code-block:: yaml

    motor:
      type: "SolidMotor"
      thrust_source: "data/motors/Cesaroni_L935.eng"
      dry_mass_kg: 0.658
      dry_inertia: [0.045, 0.045, 0.0008]
      nozzle_radius_m: 0.021
      grain_number: 4
      grain_density_kg_m3: 1815.0
      grain_outer_radius_m: 0.027
      grain_initial_inner_radius_m: 0.015
      grain_initial_height_m: 0.120
      grain_separation_m: 0.005
      position_m: 0.0

Competition Motor (M-N Class)
------------------------------

.. code-block:: yaml

    motor:
      type: "SolidMotor"
      thrust_source: "data/motors/Cesaroni_M1670.eng"
      dry_mass_kg: 1.286
      dry_inertia: [0.125, 0.125, 0.002]
      nozzle_radius_m: 0.033
      throat_radius_m: 0.011
      grain_number: 5
      grain_density_kg_m3: 1815.0
      grain_outer_radius_m: 0.033
      grain_initial_inner_radius_m: 0.015
      grain_initial_height_m: 0.120
      grain_separation_m: 0.005
      grains_center_of_mass_position_m: 0.317
      center_of_dry_mass_position_m: 0.317
      coordinate_system_orientation: "nozzle_to_combustion_chamber"
      reference_pressure: 101325
      interpolation_method: "spline"
      position_m: 0.0

--------

See Also
========

.. seealso::

   **Configuration References:**
   
   - :ref:`config-rocket-params` - Rocket geometry and components
   - :ref:`config-environment-params` - Launch site conditions
   - :ref:`config-simulation-params` - Simulation settings
   
   **Tutorials:**
   
   - :ref:`tutorial-basic-flight` - Complete first simulation
   - :ref:`tutorial-motor-selection` - Choosing the right motor
   
   **How-To Guides:**
   
   - :ref:`how-to-import-thrustcurve` - Downloading from ThrustCurve.org
   - :ref:`how-to-custom-thrust-curve` - Creating custom motor data
   - :ref:`how-to-motor-coordinates` - Understanding motor positioning
   
   **Examples:**
   
   - :ref:`example-motor-comparison` - Comparing different motors
   - :ref:`example-custom-motor` - Amateur motor design simulation

--------

**Next:** :ref:`config-environment-params`
