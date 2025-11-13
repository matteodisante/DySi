Key Concepts
============

This guide introduces the core concepts of rocket-sim and how they relate to rocket flight simulation.

.. admonition:: What You'll Learn
   :class: tip

   * The four main components: Motor, Environment, Rocket, Flight
   * How rocket-sim extends RocketPy
   * The simulation workflow
   * Coordinate systems and conventions

Overview
--------

rocket-sim simulates rocket trajectories using a **6-degree-of-freedom (6-DOF) model**,
which tracks both:

* **3 translational degrees**: movement in x, y, z directions
* **3 rotational degrees**: pitch, yaw, roll angles

The simulation is built on four core components:

.. code-block:: text

   Motor ──────┐
              │
   Environment ┼──> Flight ──> Results
              │
   Rocket ─────┘

1. The Motor Component
----------------------

The **Motor** represents your rocket's propulsion system.

What It Defines
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property
     - Description
   * - **Thrust Curve**
     - Force produced over time (from ``.eng`` file)
   * - **Propellant Mass**
     - How much propellant is burned
   * - **Burn Time**
     - Duration of powered flight
   * - **Center of Mass**
     - Changes as propellant burns
   * - **Inertia**
     - Moment of inertia (affects rotation)

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   motor:
     thrust_source: "data/motors/Cesaroni_M1670.eng"
     dry_mass: 1.815              # kg (motor casing empty)
     dry_inertia: [0.125, 0.125, 0.002]  # [I_x, I_y, I_z] kg⋅m²
     nozzle_radius: 0.033         # m
     grain_number: 5              # number of propellant grains
     grain_density: 1815          # kg/m³
     # ... more parameters

Key Concepts
~~~~~~~~~~~~

**Coordinate System**: Motor uses **nozzle-to-combustion-chamber** direction

.. code-block:: text

   Nozzle (0.0) ←──────── Combustion Chamber (+)
                ←── Motor axis

**Thrust Curve**: Read from industry-standard RASP ``.eng`` files:

.. code-block:: text

   ; Cesaroni M1670-BS
   M1670-BS 54 757 0 1.815 1.840 Cesaroni
   0.00 0.0
   0.05 1250.0
   0.10 1680.0
   ...
   3.51 0.0

**See Also**: :class:`~rocketpy.Motor`, :doc:`/user/configuration/motor_params` (TODO)

2. The Environment Component
-----------------------------

The **Environment** defines atmospheric and gravitational conditions.

What It Defines
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property
     - Description
   * - **Location**
     - Latitude, longitude, elevation
   * - **Atmosphere**
     - Pressure, temperature, density vs altitude
   * - **Wind**
     - Wind speed and direction vs altitude
   * - **Gravity**
     - Gravitational acceleration (varies with latitude)
   * - **Launch Date**
     - For solar activity, magnetic field (advanced)

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   environment:
     latitude: 39.3897      # degrees North
     longitude: -8.2889     # degrees West
     elevation: 1400        # meters above sea level
     
     # Optional: Use real weather data
     atmospheric_model_type: "Forecast"
     atmospheric_model_file: "GFS"
     date: [2024, 6, 21, 12]  # June 21, 2024, 12:00 UTC

Key Concepts
~~~~~~~~~~~~

**Atmospheric Models**:

* ``"StandardAtmosphere"``: ISA 1976 standard atmosphere (default)
* ``"Forecast"``: Real-time weather forecasts (GFS, NAM)
* ``"Reanalysis"``: Historical weather data (ERA5)
* ``"Custom"``: Your own atmospheric profile

**Wind Profile**: Can vary with altitude

.. code-block:: text

   Altitude (m)  |  Wind Speed (m/s)  |  Direction (°)
   ─────────────────────────────────────────────────
      0          |       5.0          |    90 (East)
    1000         |       8.0          |    95
    2000         |      12.0          |   100
    3000         |      15.0          |   105

**See Also**: :class:`~rocketpy.Environment`, :doc:`/user/how_to_guides/weather` (TODO)

3. The Rocket Component
------------------------

The **Rocket** defines your vehicle's physical structure and aerodynamics.

What It Defines
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Property
     - Description
   * - **Mass Properties**
     - Dry mass, center of mass, inertia
   * - **Geometry**
     - Radius (reference area for drag)
   * - **Nose Cone**
     - Shape, length, mass
   * - **Fins**
     - Number, shape, position
   * - **Parachutes**
     - Size, deployment conditions
   * - **Aerodynamics**
     - Drag coefficients (power-on, power-off)

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   rocket:
     name: "Calisto"
     mass: 14.426               # kg (dry mass without motor)
     radius: 0.0635             # m (outer radius)
     inertia: [6.321, 6.321, 0.0346]  # [I_x, I_y, I_z] kg⋅m²
     center_of_mass_without_motor: 0.0  # m from nose tip
     
     # Nose cone
     nose_cone:
       length: 0.55             # m
       kind: "vonKarman"        # aerodynamic shape
       position: 1.134          # m from tail
     
     # Fins
     fins:
       number: 4                # trapezoidal fins
       root_chord: 0.120        # m
       tip_chord: 0.040         # m
       span: 0.100              # m
       position: -1.04956       # m from nose tip
     
     # Recovery system
     parachutes:
       - name: "Main"
         cd_s: 10.0             # Drag coefficient × area
         trigger: "apogee"      # Deploy at apogee

Key Concepts
~~~~~~~~~~~~

**Coordinate System**: Rocket uses **tail-to-nose** convention

.. code-block:: text

   Tail (-) ──────────> Nose (+)
            Rocket axis
   
   Position 0.0 = Nose tip
   Negative values = toward tail

All position parameters (center of mass, center of pressure, component locations) 
follow this convention.

**Aerodynamic Stability**

For safe flight, the rocket must be statically stable. This requires the 
**Center of Pressure (CP)** to be aft of the **Center of Gravity (CG)**.

Static margin quantifies stability:

.. math::

   \text{Static Margin (calibers)} = \frac{CP - CG}{D_{rocket}}

**Stability criteria:**

- Static Margin < 1.0: Unstable or marginally stable
- Static Margin 1.5-2.5: Recommended range for most rockets
- Static Margin > 3.5: Over-stable (excessive weathercocking)

RocketPy calculates CP automatically from rocket geometry using Barrowman equations.
The CP position varies with Mach number during flight.

.. seealso::
   
   :ref:`technical-stability-analysis` provides comprehensive stability theory,
   including Static Margin vs Stability Margin, transonic considerations, and
   design guidelines with academic references.

**Drag Coefficients**

Drag can be specified as custom curves (from CFD/wind tunnel) or auto-calculated

.. code-block:: yaml

   # Option 1: Use custom drag curve
   rocket:
     power_off_drag: "data/drag_curves/my_rocket_poweroff.csv"
     power_on_drag: "data/drag_curves/my_rocket_poweron.csv"
   
   # Option 2: Let RocketPy calculate (based on geometry)
   rocket:
     power_off_drag: null  # Auto-calculated
     power_on_drag: null   # Auto-calculated

**See Also**: :class:`~rocketpy.Rocket`, :doc:`/user/tutorials/rocket_design` (TODO)

4. The Flight Component
------------------------

The **Flight** is the actual simulation that combines Motor + Environment + Rocket.

What It Computes
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Output
     - Description
   * - **Trajectory**
     - Position (x, y, z) over time
   * - **Velocity**
     - Speed and direction over time
   * - **Acceleration**
     - Including gravity, thrust, drag
   * - **Orientation**
     - Pitch, yaw, roll angles
   * - **Apogee**
     - Maximum altitude reached
   * - **Landing Point**
     - Impact coordinates and velocity
   * - **Flight Events**
     - Motor burnout, apogee, parachute deployment

Configuration Example
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   simulation:
     inclination: 85         # degrees from horizontal (85° = nearly vertical)
     heading: 90             # degrees (0=N, 90=E, 180=S, 270=W)
     rail_length: 5.2        # m (launch rail guides rocket initially)
     
     # Optional: Advanced features
     max_time: 600           # s (maximum simulation time)
     time_step: 0.01         # s (integration step)

Key Concepts
~~~~~~~~~~~~

**Launch Angle Convention**:

* **Inclination**: 0° = horizontal, 90° = vertical
* **Heading**: 0° = North, 90° = East, 180° = South, 270° = West

.. code-block:: text

   Inclination = 85°        Heading = 90°
   
        ↑ 90° (vertical)         North (0°)
        |                           ↑
        |                           |
   ────85°─────→ 0° (horizontal)    └──→ East (90°)

**Rail Launch**: Rocket is constrained to launch rail until velocity is high enough
for fins to stabilize the rocket.

**Flight Phases**:

1. **Rail Phase**: Constrained to launch rail direction
2. **Powered Ascent**: Motor burning, thrust > drag
3. **Coasting**: Motor burnout, still ascending
4. **Apogee**: Peak altitude, velocity = 0
5. **Descent**: Falling (with or without parachute)
6. **Impact**: Ground hit

**See Also**: :class:`~rocketpy.Flight`

The Simulation Workflow
------------------------

Understanding how the pieces fit together:

.. code-block:: text

   1. CONFIGURATION LOADING
      ├─ Load YAML file
      ├─ Parse into dataclasses (RocketConfig, MotorConfig, etc.)
      └─ Validate parameters (physical plausibility, stability)
   
   2. OBJECT BUILDING
      ├─ Build Motor (load thrust curve, compute properties)
      ├─ Build Environment (atmosphere model, wind profile)
      └─ Build Rocket (geometry, aerodynamics, add motor)
   
   3. FLIGHT SIMULATION
      ├─ Initialize state (position, velocity, orientation)
      ├─ Numerical integration (RK45 adaptive step)
      │  ├─ Compute forces (thrust, drag, gravity)
      │  ├─ Compute moments (aerodynamic, gyroscopic)
      │  └─ Update state (position, velocity, attitude)
      └─ Detect events (burnout, apogee, parachute, impact)
   
   4. RESULTS EXPORT
      ├─ Extract trajectory data (CSV, JSON, KML)
      ├─ Generate plots (altitude, velocity, 3D trajectory)
      └─ Export state files (motor curves, rocket properties)

Coordinate Systems Summary
---------------------------

rocket-sim uses **three coordinate systems** - it's important to know which is which:

.. list-table::
   :header-rows: 1
   :widths: 25 50 25

   * - System
     - Description
     - Origin
   * - **Motor**
     - Nozzle → Combustion Chamber
     - Nozzle exit (0.0)
   * - **Rocket**
     - Tail → Nose
     - Nose tip (0.0)
   * - **World**
     - East (x), North (y), Up (z)
     - Launch point (0, 0, elevation)

**Example**: Motor positioned in rocket

.. code-block:: yaml

   motor:
     nozzle_position: 0.0               # Motor coordinates (at nozzle)
     center_of_dry_mass_position: 0.317 # Motor coordinates
   
   rocket:
     motor_position: -1.255             # Rocket coordinates (nozzle at -1.255m from nose)

Physical Units Convention
--------------------------

All parameters use **SI units** unless otherwise specified:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Quantity
     - Unit
     - Example
   * - Length
     - meters (m)
     - ``radius: 0.0635``
   * - Mass
     - kilograms (kg)
     - ``mass: 14.426``
   * - Time
     - seconds (s)
     - ``burn_time: 3.9``
   * - Velocity
     - meters/second (m/s)
     - ``max_velocity: 287.3``
   * - Acceleration
     - meters/second² (m/s²)
     - ``max_acceleration: 89.2``
   * - Force
     - newtons (N)
     - ``thrust: 1670.0``
   * - Angle
     - degrees (°)
     - ``inclination: 85``
   * - Coordinates
     - degrees
     - ``latitude: 39.3897``
   * - Pressure
     - pascals (Pa)
     - ``pressure: 81060.0``
   * - Temperature
     - kelvin (K)
     - ``temperature: 288.15``

.. warning::
   **Angles are in DEGREES** for configuration, but RocketPy internally uses **radians**.
   rocket-sim handles the conversion automatically.

What You've Learned
-------------------

You now understand:

✅ The four core components: Motor, Environment, Rocket, Flight

✅ What each component defines and controls

✅ The simulation workflow from config to results

✅ Coordinate systems and unit conventions

Next Steps
----------

Now you can:

* **Deep dive into configuration** → :doc:`/user/configuration/index` (TODO)
  
  Learn every parameter in detail

* **Build your rocket** → :doc:`/user/tutorials/custom_rocket` (TODO)
  
  Simulate your own rocket design

* **Explore advanced features** → :doc:`next_steps`
  
  Weather data, air brakes, Monte Carlo analysis

.. seealso::

   * `RocketPy Theory <https://docs.rocketpy.org/en/latest/user/index.html>`_ - Mathematical background
   * :doc:`/background/rocket_physics` (TODO) - Physics primer
   * :doc:`/background/simulation_theory` (TODO) - Numerical methods

Common Misconceptions
---------------------

.. dropdown:: "Motor mass" means total motor mass
   :color: warning

   **No!** Motor ``dry_mass`` is the **empty motor casing** (without propellant).
   RocketPy adds propellant mass automatically based on the thrust curve.

.. dropdown:: Position 0.0 is always at the tail
   :color: warning

   **No!** Depends on component:
   
   * **Rocket**: 0.0 = nose tip
   * **Motor**: 0.0 = nozzle exit
   
   Always check which coordinate system you're working in!

.. dropdown:: Static margin < 2 is always unstable
   :color: warning

   **Not exactly.** Static margin < 2 calibers is generally considered **risky**,
   but small rockets can sometimes fly with SM ≈ 1.5. However, rocket-sim enforces
   SM ≥ 2 for safety.

.. dropdown:: I can use any atmospheric model anywhere
   :color: warning

   **No!** Forecast/Reanalysis data is location and time specific. Using wrong
   coordinates or dates gives unrealistic atmosphere.
