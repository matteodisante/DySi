.. _developer-module-reference:

Module Quick Reference
======================

One-page reference for all 11 core modules in the rocket simulation framework.

Module Overview
---------------

Quick lookup table showing purpose, key classes, and I/O for each module:

.. list-table::
   :header-rows: 1
   :widths: 20 25 20 15 20

   * - Module
     - Purpose
     - Key Classes/Functions
     - Inputs
     - Outputs
   * - **config_loader**
     - Load and parse YAML configurations
     - ``ConfigLoader``
     - YAML file path
     - Config dataclasses
   * - **validators**
     - Configuration validation
     - ``RocketValidator``, ``MotorValidator``, etc.
     - Config objects
     - List of warnings
   * - **motor_builder**
     - Build RocketPy motor objects
     - ``MotorBuilder``
     - ``MotorConfig``
     - ``SolidMotor``
   * - **environment_setup**
     - Build atmospheric environment
     - ``EnvironmentBuilder``
     - ``EnvironmentConfig``
     - ``Environment``
   * - **rocket_builder**
     - Assemble complete rocket
     - ``RocketBuilder``
     - ``RocketConfig``, ``Motor``
     - ``Rocket``
   * - **flight_simulator**
     - Execute flight simulation
     - ``FlightSimulator``
     - ``Rocket``, ``Environment``, rail params
     - ``Flight``
   * - **visualizer**
     - Generate flight trajectory plots
     - ``Visualizer``
     - ``Flight``
     - PNG/PDF plots
   * - **data_handler**
     - Export summary data
     - ``DataHandler``
     - ``Flight``, summary dict
     - CSV/JSON files
   * - **state_exporter**
     - Export complete simulation state
     - ``StateExporter``
     - ``Flight``, configs, objects
     - Full state JSON/CSV
   * - **curve_plotter**
     - Plot input curves (thrust, drag, etc.)
     - ``CurvePlotter``
     - Motor, Rocket, Environment
     - Curve plots PNG
   * - **weather_fetcher**
     - Fetch real-world atmospheric data
     - ``WeatherFetcher``
     - Station ID, date
     - Wyoming/GFS data URL

Dependency Levels
-----------------

Modules organized by their dependency hierarchy:

Level 0 (No dependencies)
~~~~~~~~~~~~~~~~~~~~~~~~~

- **config_loader**: Pure YAML parsing and dataclass creation

Level 1 (Depends on config_loader only)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **validators**: Validate configuration objects
- **motor_builder**: Build motors from configs
- **environment_setup**: Build environments from configs
- **weather_fetcher**: Fetch atmospheric data (can work standalone or with configs)

Level 2 (Depends on Level 0-1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **rocket_builder**: Needs config_loader + motor_builder

Level 3 (Depends on Level 0-2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **flight_simulator**: Needs rocket_builder, motor_builder, environment_setup

Level 4 (Depends on Level 0-3)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **visualizer**: Needs flight_simulator output (Flight object)
- **data_handler**: Needs flight_simulator output
- **state_exporter**: Needs Flight object + all config objects
- **curve_plotter**: Needs motor, rocket, environment objects

Typical Workflows
-----------------

Single Flight Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   config_loader → validators → motor_builder → environment_setup → 
   rocket_builder → flight_simulator → visualizer/data_handler/state_exporter

With Real Weather Data
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   config_loader → weather_fetcher → environment_setup (with real data) → 
   rocket_builder → flight_simulator → outputs

Comprehensive Analysis
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   config_loader → build objects → flight_simulator → 
   [visualizer, data_handler, state_exporter, curve_plotter] in parallel

Module Details
--------------

config_loader
~~~~~~~~~~~~~

**Purpose**: Load YAML configurations and convert to type-safe dataclasses

**Key Classes**:
   - ``ConfigLoader``: Main class for loading configs

**Key Methods**:

.. code-block:: python

   loader = ConfigLoader()
   loader.load_from_yaml("config.yaml")
   rocket_cfg = loader.get_rocket_config()
   motor_cfg = loader.get_motor_config()
   env_cfg = loader.get_environment_config()
   sim_cfg = loader.get_simulation_config()

**Dataclasses**:
   - ``RocketConfig``: Rocket geometry, mass, inertia, components
   - ``MotorConfig``: Motor type, thrust curve, grain geometry
   - ``EnvironmentConfig``: Location, wind, atmospheric model
   - ``SimulationConfig``: Integration params, rail setup

motor_builder
~~~~~~~~~~~~~

**Purpose**: Build RocketPy ``SolidMotor`` objects from configuration

**Key Classes**:
   - ``MotorBuilder``: Builds motors with grain geometry

**Key Methods**:

.. code-block:: python

   builder = MotorBuilder(motor_cfg)
   motor = builder.build()
   summary = builder.get_summary()

**Input**: ``MotorConfig`` dataclass

**Output**: RocketPy ``SolidMotor`` object

environment_setup
~~~~~~~~~~~~~~~~~

**Purpose**: Build RocketPy ``Environment`` objects with wind and atmosphere

**Key Classes**:
   - ``EnvironmentBuilder``: Sets up atmospheric conditions

**Key Methods**:

.. code-block:: python

   builder = EnvironmentBuilder(env_cfg)
   environment = builder.build()
   summary = builder.get_summary()

**Input**: ``EnvironmentConfig`` dataclass

**Output**: RocketPy ``Environment`` object

rocket_builder
~~~~~~~~~~~~~~

**Purpose**: Assemble complete rocket with nose cone, fins, parachutes, air brakes

**Key Classes**:
   - ``RocketBuilder``: Progressive rocket assembly

**Key Methods**:

.. code-block:: python

   builder = RocketBuilder(rocket_cfg)
   rocket = builder.build(motor)
   stability = builder.get_stability_info()
   summary = builder.get_summary()

**Input**: ``RocketConfig`` dataclass, ``Motor`` object

**Output**: RocketPy ``Rocket`` object

**Key Info**:
   - Automatically adds nose cone, fins, parachutes based on config
   - Supports air brakes with controller integration
   - Validates stability (static margin)

flight_simulator
~~~~~~~~~~~~~~~~

**Purpose**: Execute flight simulation using RocketPy's ODE solver

**Key Classes**:
   - ``FlightSimulator``: Run simulation and extract metrics

**Key Methods**:

.. code-block:: python

   sim = FlightSimulator(
       rocket, motor, environment, 
       rail_length_m, inclination_deg, heading_deg
   )
   flight = sim.run()
   summary = sim.get_summary()
   sim.print_summary()

**Input**: ``Rocket``, ``Motor``, ``Environment``, rail parameters

**Output**: RocketPy ``Flight`` object

**Key Metrics**:
   - Apogee altitude, time, coordinates
   - Max velocity, Mach number, acceleration
   - Flight time, landing coordinates
   - Off-rail velocity, rail angle

visualizer
~~~~~~~~~~

**Purpose**: Create publication-quality plots from flight data

**Key Classes**:
   - ``Visualizer``: Multi-plot generation

**Key Methods**:

.. code-block:: python

   viz = Visualizer(flight)
   viz.plot_trajectory_3d(output_path="trajectory.png")
   viz.plot_altitude_vs_time(output_path="altitude.png")
   viz.plot_velocity_vs_time(output_path="velocity.png")
   viz.create_standard_plots(output_dir)  # All plots at once

**Input**: RocketPy ``Flight`` object

**Output**: PNG/PDF plot files

**Available Plots**:
   - 3D trajectory
   - Altitude vs time
   - Velocity vs time
   - Acceleration vs time
   - Angular velocity
   - Stability margin evolution

data_handler
~~~~~~~~~~~~

**Purpose**: Export simulation summary data in standard formats

**Key Classes**:
   - ``DataHandler``: Multi-format export for summary data

**Key Methods**:

.. code-block:: python

   handler = DataHandler()
   handler.export_trajectory_csv(flight, "trajectory.csv")
   handler.export_summary_json(summary, "summary.json")
   handler.export_complete_dataset(
       flight, summary, output_dir, 
       formats=['csv', 'json']
   )

**Input**: ``Flight`` object, summary dict

**Output**: CSV, JSON files

**Export Formats**:
   - **CSV**: Trajectory time series (time, position, velocity, etc.)
   - **JSON**: Flight summary and metadata (apogee, max velocity, etc.)

**Note**: For comprehensive state export including all configurations and intermediate objects, use ``state_exporter`` instead.

state_exporter
~~~~~~~~~~~~~~

**Purpose**: Export complete simulation state with all configurations and objects

**Key Classes**:
   - ``StateExporter``: Comprehensive state serialization

**Key Methods**:

.. code-block:: python

   exporter = StateExporter(
       flight=flight,
       rocket_config=rocket_cfg,
       motor_config=motor_cfg,
       environment_config=env_cfg,
       simulation_config=sim_cfg,
       motor=motor,
       rocket=rocket,
       environment=environment
   )
   
   # Export everything
   exporter.export_all(output_dir="outputs/my_sim")
   
   # Or export selectively
   exporter.export_final_state_readable("final_state.txt")
   exporter.export_config_summary("config_summary.json")
   exporter.export_flight_data_csv("flight_data.csv")

**Input**: Flight, all config objects, RocketPy objects

**Output**: Multiple files including:
   - ``final_state_READABLE.txt``: Human-readable final state
   - ``config_summary.json``: All input configurations
   - ``flight_data.csv``: Complete trajectory
   - ``flight_summary.json``: Key metrics
   - KML files for Google Earth visualization

**Use Case**: Complete archival of simulation results with full reproducibility

curve_plotter
~~~~~~~~~~~~~

**Purpose**: Generate plots of simulation input curves (thrust, drag, atmospheric profiles)

**Key Classes**:
   - ``CurvePlotter``: Input curve visualization

**Key Methods**:

.. code-block:: python

   plotter = CurvePlotter(motor, rocket, environment)
   
   # Generate all curves at once
   paths = plotter.plot_all_curves(output_dir="outputs/curves")
   
   # Or plot individually
   plotter.plot_thrust_curve("thrust.png")
   plotter.plot_drag_curves("drag.png")
   plotter.plot_atmospheric_profile("atmosphere.png")
   plotter.plot_wind_profile("wind.png")

**Input**: RocketPy Motor, Rocket, Environment objects

**Output**: PNG plots showing:
   - Motor thrust curve over time
   - Drag coefficient vs Mach number
   - Atmospheric pressure/temperature/density vs altitude
   - Wind speed/direction vs altitude
   - Center of pressure evolution

**Use Case**: Visual verification of input parameters before running simulation

weather_fetcher
~~~~~~~~~~~~~~~

**Purpose**: Fetch real-world atmospheric data from online sources

**Key Classes**:
   - ``WeatherFetcher``: Interface to atmospheric data providers
   - ``WeatherConfig``: Configuration for data source

**Key Methods**:

.. code-block:: python

   from datetime import datetime
   
   config = WeatherConfig(
       source="wyoming",
       wyoming_station="72340",  # Oakland, CA
       fetch_real_time=False
   )
   
   fetcher = WeatherFetcher(config)
   
   # Fetch Wyoming radiosonde data
   sounding_url = fetcher.fetch_wyoming_sounding(
       date=datetime(2024, 6, 15, 12, 0)
   )
   
   # Use with RocketPy Environment
   environment.set_atmospheric_model(
       type='wyoming_sounding', 
       file=sounding_url
   )

**Data Sources**:
   - **Wyoming**: Real radiosonde (weather balloon) data
   - **GFS**: Global Forecast System forecasts
   - **ERA5**: Historical reanalysis data (planned)
   - **Standard Atmosphere**: ISA model fallback

**Input**: Station ID, date/time

**Output**: URL or file path for atmospheric profile

**Use Case**: High-fidelity simulations using actual atmospheric conditions

validators
~~~~~~~~~~

**Purpose**: Validate configurations for physical correctness before simulation

**Key Classes**:
   - ``RocketValidator``: Rocket physics validation
   - ``MotorValidator``: Motor parameter validation
   - ``EnvironmentValidator``: Environment validation
   - ``SimulationValidator``: Simulation parameter validation
   - ``ValidationWarning``: Warning/error data structure

**Key Methods**:

.. code-block:: python

   from src.validators import validate_all_configs
   
   # Validate all configs at once
   warnings = validate_all_configs(
       rocket_cfg, motor_cfg, env_cfg, sim_cfg
   )
   
   # Or validate individually
   from src.validators import RocketValidator
   warnings = RocketValidator.validate(rocket_cfg)
   
   # Check for critical errors
   for w in warnings:
       if w.level == "ERROR":
           print(f"CRITICAL: {w.message}")
       elif w.level == "WARNING":
           print(f"Warning: {w.message}")

**Validation Checks**:
   - **Critical**: Positive masses, valid coordinates, stability margin
   - **Warning**: Unusual values, potential design issues
   - **Info**: Recommendations and optimization suggestions

**Use Case**: Catch configuration errors before running expensive simulations

Quick Tips
----------

Finding the Right Module
~~~~~~~~~~~~~~~~~~~~~~~~~

**Need to...**

- Parse a YAML file? → ``config_loader``
- Validate configurations? → ``validators``
- Build simulation objects? → ``motor_builder``, ``environment_setup``, ``rocket_builder``
- Get real weather data? → ``weather_fetcher``
- Run a simulation? → ``flight_simulator``
- Create flight plots? → ``visualizer``
- Plot input curves (thrust, drag)? → ``curve_plotter``
- Export summary data? → ``data_handler``
- Export complete state for archival? → ``state_exporter``
- Generate KML for Google Earth? → ``state_exporter``

Import Patterns
~~~~~~~~~~~~~~~

All modules are in the ``src/`` package:

.. code-block:: python

   from src.config_loader import ConfigLoader
   from src.motor_builder import MotorBuilder
   from src.flight_simulator import FlightSimulator
   # etc.

Error Handling
~~~~~~~~~~~~~~

Most modules raise exceptions on critical errors:

- ``ValueError``: Invalid parameter values
- ``FileNotFoundError``: Missing thrust curve or config files
- ``RuntimeError``: Simulation convergence failures

Use validators to catch issues early:

.. code-block:: python

   from src.validators import validate_all_configs

   warnings = validate_all_configs(
       rocket_cfg, motor_cfg, env_cfg, sim_cfg
   )
   if any(w.level == "ERROR" for w in warnings):
       print("Critical errors found! Fix before running simulation")

See Also
--------

- :ref:`developer-architecture` - Full system architecture overview
- :doc:`/user/configuration/index` - Configuration schema reference
- :doc:`/user/how_to_guides/troubleshoot` - Troubleshooting guide
- :doc:`/user/tutorials/index` - Step-by-step tutorials
