Configuration Reference
=======================

Complete documentation of all configuration parameters for rocket-sim.

This section provides detailed reference material for every parameter you can use
in YAML configuration files. Each parameter includes:

* **Description**: What it controls
* **Type**: Data type (float, int, string, etc.)
* **Units**: SI units used
* **Required**: Whether parameter is mandatory
* **Default**: Default value if not specified
* **Valid Range**: Physically acceptable values
* **Example**: Practical usage example

Organization
------------

Configuration is divided into four main sections:

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🚀 Rocket Parameters
      :link: rocket_params
      :link-type: doc

      Physical properties, geometry, aerodynamics

   .. grid-item-card:: 🔥 Motor Parameters
      :link: motor_params
      :link-type: doc

      Thrust curve, propellant, nozzle

   .. grid-item-card:: 🌍 Environment Parameters
      :link: environment_params
      :link-type: doc

      Atmosphere, weather, location

   .. grid-item-card:: ⚙️ Simulation Parameters
      :link: simulation_params
      :link-type: doc

      Launch conditions, integration settings

Quick Reference
---------------

**Most Used Parameters:**

Rocket:
   ``mass``, ``radius``, ``inertia``, ``center_of_mass_without_motor``,
   ``motor_position``, ``nose_cone``, ``fins``, ``parachutes``

Motor:
   ``thrust_source``, ``dry_mass``, ``nozzle_radius``, ``grain_*``

Environment:
   ``latitude``, ``longitude``, ``elevation``, ``atmospheric_model_type``

Simulation:
   ``inclination``, ``heading``, ``rail_length``

Configuration Structure
-----------------------

Every configuration file follows this structure:

.. code-block:: yaml

   # Four required top-level sections
   
   rocket:
     # Rocket physical properties
     name: "..."
     mass: ...
     # ... more rocket parameters
   
   motor:
     # Motor and propulsion
     thrust_source: "..."
     dry_mass: ...
     # ... more motor parameters
   
   environment:
     # Atmospheric conditions
     latitude: ...
     longitude: ...
     # ... more environment parameters
   
   simulation:
     # Launch and simulation settings
     inclination: ...
     heading: ...
     # ... more simulation parameters

.. seealso::
   :doc:`/user/tutorials/01_basic_flight` for a complete annotated example.

Parameter Categories
--------------------

.. toctree::
   :maxdepth: 2
   :caption: Configuration Sections

   rocket_params
   motor_params
   environment_params
   simulation_params

Units Convention
----------------

All parameters use **SI units** unless explicitly stated:

.. list-table::
   :header-rows: 1
   :widths: 30 20 30 20

   * - Quantity
     - Unit
     - Symbol
     - Example
   * - Length
     - meters
     - m
     - ``radius: 0.052``
   * - Mass
     - kilograms
     - kg
     - ``mass: 5.0``
   * - Time
     - seconds
     - s
     - ``burn_time: 3.9``
   * - Velocity
     - meters/second
     - m/s
     - ``max_velocity: 287.3``
   * - Acceleration
     - meters/second²
     - m/s²
     - ``max_accel: 89.2``
   * - Force
     - newtons
     - N
     - ``thrust: 1670``
   * - Angle (config)
     - degrees
     - °
     - ``inclination: 85``
   * - Angle (internal)
     - radians
     - rad
     - (auto-converted)
   * - Pressure
     - pascals
     - Pa
     - ``pressure: 101325``
   * - Temperature
     - kelvin
     - K
     - ``temperature: 288.15``
   * - Density
     - kg/m³
     - kg/m³
     - ``grain_density: 1815``
   * - Inertia
     - kg⋅m²
     - kg⋅m²
     - ``inertia: [0.8, 0.8, 0.003]``

.. warning::
   **Angles in configuration files are in DEGREES**, but RocketPy internally
   uses radians. rocket-sim handles conversion automatically.

Coordinate Systems
------------------

Different components use different coordinate systems:

**Rocket Coordinate System**

.. code-block:: text

   Tail (-) ──────────> Nose (+)
   
   Origin: Nose tip (position 0.0)
   Positive direction: Toward tail

Example positions:

* Nose cone base: 0.95 m (from nose tip, toward tail)
* Motor nozzle: -0.60 m (negative = toward tail from nose)

**Motor Coordinate System**

.. code-block:: text

   Nozzle (0) ──────────> Combustion Chamber (+)
   
   Origin: Nozzle exit (position 0.0)
   Positive direction: Toward combustion chamber

Example positions:

* Nozzle: 0.0 m
* Grains center: 0.12 m
* Motor dry mass center: 0.14 m

**World Coordinate System**

.. code-block:: text

   X: East
   Y: North
   Z: Up (vertical)
   
   Origin: Launch point

Used for trajectory output.

Parameter Validation
--------------------

rocket-sim automatically validates all parameters for:

**Physical Plausibility**
   * Positive masses, lengths, densities
   * Reasonable ranges (e.g., fin span < rocket radius × 10)
   * Consistent dimensions

**Aerodynamic Stability**
   * Static margin ≥ 2.0 calibers
   * Center of pressure behind center of gravity
   * Fin area sufficient for stability

**Completeness**
   * All required parameters present
   * Valid file paths
   * Correct parameter types

To validate without running simulation:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config your_config.yaml \
       --validate-only

See :doc:`/user/how_to_guides/validate_design` for details.

Common Mistakes
---------------

.. dropdown:: Using wrong units
   :color: danger

   **Wrong**: ``radius: 52`` (assumes millimeters)
   
   **Correct**: ``radius: 0.052`` (meters)
   
   All lengths MUST be in meters.

.. dropdown:: Including motor in rocket mass
   :color: danger

   **Wrong**: ``mass: 6.5`` (includes motor)
   
   **Correct**: ``mass: 5.0`` (without motor)
   
   Motor mass is added automatically by RocketPy.

.. dropdown:: Confusing coordinate systems
   :color: danger

   **Wrong**: ``motor_position: 0.60`` (positive)
   
   **Correct**: ``motor_position: -0.60`` (negative, toward tail)
   
   In rocket coordinates, motor is typically negative (toward tail from nose).

.. dropdown:: Forgetting required parameters
   :color: warning

   Each section has mandatory parameters. If missing, validation will fail
   with clear error message indicating what's required.

Templates
---------

Use these templates as starting points:

**Minimal Configuration**
   See ``configs/single_sim/01_minimal.yaml``

**Complete Configuration**
   See ``configs/single_sim/02_complete.yaml``

**Documented Template**
   See ``configs/templates/template_complete_documented.yaml``

Examples
--------

Real-world rocket configurations:

* :doc:`/user/examples/calisto` - Research rocket
* :doc:`/user/examples/prometheus` - Competition vehicle
* :doc:`/user/examples/student_rocket` - University team rocket

Further Reading
---------------

* :doc:`/user/how_to_guides/create_config` - Create configuration file
* :doc:`/user/how_to_guides/measure_rocket` - Measure parameters
* :doc:`/user/tutorials/01_basic_flight` - Annotated example
* `RocketPy API <https://docs.rocketpy.org/>`_ - Underlying library documentation
