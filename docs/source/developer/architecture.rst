.. _developer-architecture:

=======================
System Architecture
=======================

This document explains the architecture of the rocket simulation framework, from configuration loading to output generation.

.. contents:: Table of Contents
   :local:
   :depth: 3

--------

Overview
========

The framework follows a **layered architecture** with clear separation of concerns:

.. mermaid::

   flowchart TD
       A[YAML Config] --> B[ConfigLoader]
       B --> C[Validators]
       C --> D{Builders}
       D --> E[Motor]
       D --> F[Environment]
       D --> G[Rocket]
       E --> H[FlightSimulator]
       F --> H
       G --> H
       H --> I[RocketPy Flight]
       I --> J[Results Extraction]
       J --> K[Outputs]
       K --> L[CSV/JSON]
       K --> M[Plots]
       K --> N[KML]

**Design Principles:**

- ✅ **Type Safety**: Full type hints with dataclasses
- ✅ **Validation First**: Catch errors at config load, not runtime
- ✅ **Separation of Concerns**: Each module has one responsibility
- ✅ **Builder Pattern**: Progressive object construction
- ✅ **Testability**: Dependency injection throughout

--------

System Layers
=============

1. Configuration Layer
----------------------

**Purpose**: Load and validate YAML configurations into type-safe Python objects.

**Key Components**:

.. code-block:: text

   configs/single_sim/my_rocket.yaml
        ↓
   ConfigLoader.load_from_yaml()
        ↓
   Dataclass objects (RocketConfig, MotorConfig, EnvironmentConfig)
        ↓
   Validators.validate()
        ↓
   Validated configurations ready for builders

**Configuration Structure**:

.. code-block:: yaml

   rocket:
     name: "Artemis"
     dry_mass_kg: 16.4
     geometry:
       caliber_m: 0.127
       length_m: 2.0
     nose_cone:
       length_m: 0.5
       kind: "vonKarman"
     fins:
       count: 4
       root_chord_m: 0.120
       span_m: 0.100
   
   motor:
     type: "SolidMotor"
     thrust_source: "data/motors/motor.eng"
   
   environment:
     latitude_deg: 39.39
     longitude_deg: -8.29
     elevation_m: 100

**Type Safety with Dataclasses**:

.. code-block:: python

   @dataclass
   class RocketConfig:
       name: str
       dry_mass_kg: float
       geometry: GeometryConfig
       nose_cone: NoseConeConfig
       fins: FinsConfig
       # ... more fields with types

2. Validation Layer
-------------------

**Purpose**: Ensure physical plausibility and configuration consistency.

**Validation Types**:

1. **Physical Bounds**
   
   - Mass > 0 and < 1000 kg
   - Lengths > 0
   - Angles in valid ranges

2. **Consistency Checks**
   
   - Stability margin > 1.0 calibers
   - Center of pressure aft of center of gravity
   - Fin positions within rocket length

3. **File Existence**
   
   - Motor thrust curves exist
   - Custom drag curves exist (if specified)
   - Airfoil files exist (if specified)

**Example Validation**:

.. code-block:: python

   class RocketValidator:
       def validate_stability(self, config: RocketConfig) -> None:
           """Ensure rocket is statically stable."""
           cp = config.cp_location_m or self._estimate_cp(config)
           cg = config.cg_location_m
           caliber = config.geometry.caliber_m
           
           margin = (cp - cg) / caliber
           
           if margin < 1.0:
               raise ValueError(
                   f"Unstable! Static margin {margin:.2f} < 1.0 calibers"
               )

3. Builder Layer
----------------

**Purpose**: Construct RocketPy objects from validated configurations.

**Pattern**: Builder pattern with progressive construction

**Workflow**:

.. code-block:: text

   MotorConfig → MotorBuilder.build() → rocketpy.SolidMotor
   EnvConfig → EnvironmentBuilder.build() → rocketpy.Environment
   RocketConfig → RocketBuilder.build() → rocketpy.Rocket

**Motor Construction**:

.. code-block:: python

   class MotorBuilder:
       def __init__(self, config: MotorConfig):
           self.config = config
       
       def build(self) -> SolidMotor:
           motor = SolidMotor(
               thrust_source=self.config.thrust_source,
               burn_time=self.config.burn_time_s,
               dry_mass=self.config.dry_mass_kg,
               dry_inertia=self.config.dry_inertia,
               # ... more parameters
           )
           return motor

**Rocket Construction**:

.. code-block:: python

   class RocketBuilder:
       def build(self, motor: Motor) -> Rocket:
           # Create base rocket
           rocket = Rocket(
               radius=self.config.geometry.caliber_m / 2,
               mass=self.config.dry_mass_kg,
               # ... more parameters
           )
           
           # Add components progressively
           rocket.add_motor(motor, position=motor_config.position_m)
           self._add_nose_cone(rocket)
           self._add_fins(rocket)
           self._add_parachute(rocket)
           
           return rocket

4. Simulation Layer
-------------------

**Purpose**: Execute flight simulation using RocketPy.

**Key Class**: ``FlightSimulator``

**Execution Flow**:

.. code-block:: text

   Rocket + Environment + SimConfig
        ↓
   FlightSimulator.run()
        ↓
   rocketpy.Flight(
       rocket=rocket,
       environment=environment,
       rail_length=config.rail.length_m,
       inclination=config.rail.inclination_deg,
       heading=config.rail.heading_deg
   )
        ↓
   6-DOF Integration (RocketPy)
        ↓
   Flight object with trajectory data

**Integration Details**:

- **Solver**: scipy.integrate.solve_ivp (adaptive RK45/DOP853)
- **Time stepping**: Adaptive with rtol=1e-6, atol=1e-9
- **Phases**:
  
  1. Rail-guided launch
  2. Powered ascent (motor burning)
  3. Coasting ascent
  4. Apogee
  5. Parachute deployment
  6. Descent
  7. Ground impact

**Metrics Extraction**:

.. code-block:: python

   class FlightSimulator:
       def extract_metrics(self, flight: Flight) -> Dict[str, float]:
           return {
               'apogee_m': flight.apogee,
               'apogee_time_s': flight.apogee_time,
               'max_velocity_ms': max(flight.speed),
               'max_acceleration_ms2': max(flight.acceleration),
               'flight_time_s': flight.t_final,
               'impact_velocity_ms': flight.impact_velocity,
               'lateral_distance_m': (flight.x_impact**2 + flight.y_impact**2)**0.5,
               # ... more metrics
           }

5. Output Layer
---------------

**Purpose**: Export results in multiple formats for analysis and visualization.

**Output Structure**:

.. code-block:: text

   outputs/
   └── artemis/
       ├── final_state                      # Binary (pickle)
       ├── final_state_READABLE.txt         # Human-readable summary
       ├── artemis_log                      # Detailed log
       ├── curves/
       │   ├── motor_thrust.png
       │   └── rocket_static_margin.png
       ├── plots/
       │   ├── artemis_altitude.png
       │   ├── artemis_velocity.png
       │   ├── artemis_acceleration.png
       │   ├── artemis_trajectory_2d.png
       │   └── artemis_trajectory_3d.png
       └── trajectory/
           ├── artemis_summary.json         # Key metrics
           └── artemis_trajectory.csv       # Full time series

**JSON Summary**:

.. code-block:: json

   {
     "simulation_config": {
       "name": "artemis",
       "date": "2025-11-12T14:30:00"
     },
     "flight_results": {
       "apogee_m": 3245.7,
       "apogee_time_s": 18.3,
       "max_velocity_ms": 287.4,
       "max_acceleration_ms2": 145.2,
       "flight_time_s": 156.8,
       "impact_velocity_ms": 6.2,
       "lateral_distance_m": 234.5
     },
     "environment": {
       "latitude_deg": 39.3897,
       "longitude_deg": -8.2889,
       "elevation_m": 100.0
     }
   }

**CSV Trajectory** (sample):

.. code-block:: text

   time_s,altitude_m,x_m,y_m,vx_ms,vy_ms,vz_ms,ax_ms2,ay_ms2,az_ms2
   0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000
   0.010,0.001,0.000,0.000,0.058,0.000,0.196,11.6,0.0,39.2
   0.020,0.005,0.000,0.000,0.174,0.000,0.587,17.4,0.0,58.7
   ...

--------

Data Flow Diagrams
==================

Single Flight Simulation
-------------------------

.. code-block:: text

   ┌──────────────┐
   │ YAML Config  │
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │ ConfigLoader │ Parse YAML → Dataclasses
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │  Validators  │ Check physical plausibility
   └──────┬───────┘
          │
          ├─────────────┬─────────────┐
          ▼             ▼             ▼
   ┌────────────┐ ┌──────────┐ ┌────────────┐
   │MotorBuilder│ │EnvBuilder│ │RocketBuilder│
   └──────┬─────┘ └─────┬────┘ └──────┬─────┘
          │             │             │
          ▼             ▼             ▼
   ┌────────────┐ ┌──────────┐ ┌────────────┐
   │   Motor    │ │Environment│ │   Rocket   │
   └──────┬─────┘ └─────┬────┘ └──────┬─────┘
          │             │             │
          └──────┬──────┴──────┬──────┘
                 │             │
                 ▼             ▼
          ┌─────────────────────────┐
          │   FlightSimulator.run() │
          └───────────┬─────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │  RocketPy Flight Object │ 6-DOF Integration
          └───────────┬─────────────┘
                      │
                      ▼
          ┌─────────────────────────┐
          │   Extract Metrics       │
          └───────────┬─────────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
   ┌──────────────┐      ┌──────────────┐
   │ DataHandler  │      │  Visualizer  │
   └──────┬───────┘      └──────┬───────┘
          │                     │
          ▼                     ▼
   ┌──────────────┐      ┌──────────────┐
   │ CSV/JSON/KML │      │  PNG Plots   │
   └──────────────┘      └──────────────┘

Configuration to Output Pipeline
---------------------------------

**Step-by-step transformation:**

1. **YAML File** → ``configs/single_sim/artemis.yaml``
   
   - User-friendly configuration format
   - Comments and documentation inline
   - Units explicitly specified in parameter names

2. **ConfigLoader** → Type-safe Python objects
   
   - Parse YAML to dictionaries
   - Create dataclass instances
   - Validate required fields exist

3. **Validators** → Physical checks
   
   - Stability margin validation
   - Mass/inertia consistency
   - File existence checks

4. **Builders** → RocketPy objects
   
   - MotorBuilder creates ``rocketpy.SolidMotor``
   - EnvironmentBuilder creates ``rocketpy.Environment``
   - RocketBuilder creates ``rocketpy.Rocket``

5. **FlightSimulator** → Trajectory computation
   
   - Initialize ``rocketpy.Flight``
   - Run 6-DOF integration
   - Extract key metrics

6. **Outputs** → Multiple export formats
   
   - **Visualizer**: Generate plots (altitude, velocity, 3D trajectory)
   - **DataHandler**: Export CSV (time series), JSON (summary), KML (Google Earth)
   - **StateExporter**: Save RocketPy state objects (pickle)

--------

Key Design Patterns
===================

Builder Pattern
---------------

**Usage**: Motor, Environment, and Rocket construction

**Benefits**:

- Separates configuration from construction
- Progressive object assembly
- Validation during construction
- Clear, readable code

**Example**:

.. code-block:: python

   # Progressive construction
   motor = MotorBuilder(motor_config).build()
   
   rocket = (RocketBuilder(rocket_config)
       .set_motor(motor)
       .add_nose_cone()
       .add_fins()
       .add_parachute()
       .build())

Factory Pattern
---------------

**Usage**: ConfigLoader creates appropriate config objects

**Benefits**:

- Centralized object creation
- Type safety enforcement
- Easy to extend with new config types

Dependency Injection
--------------------

**Usage**: Throughout (FlightSimulator, Builders)

**Benefits**:

- Testability (easy mocking)
- Loose coupling
- Clear dependencies in signatures

**Example**:

.. code-block:: python

   # Dependencies injected via constructor
   simulator = FlightSimulator(
       rocket=rocket,
       environment=environment,
       config=sim_config
   )

--------

Module Responsibilities
=======================

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Module
     - Responsibility
     - Key Classes
   * - ``config_loader.py``
     - YAML parsing, dataclass creation
     - ConfigLoader, RocketConfig, MotorConfig, etc.
   * - ``validators.py``
     - Configuration validation
     - RocketValidator, MotorValidator
   * - ``motor_builder.py``
     - Motor object construction
     - MotorBuilder
   * - ``environment_setup.py``
     - Environment construction
     - EnvironmentBuilder
   * - ``rocket_builder.py``
     - Rocket assembly
     - RocketBuilder
   * - ``flight_simulator.py``
     - Flight execution & metrics
     - FlightSimulator
   * - ``data_handler.py``
     - Data export (CSV, JSON, KML)
     - DataHandler
   * - ``visualizer.py``
     - Plotting & visualization
     - Visualizer
   * - ``state_exporter.py``
     - RocketPy state serialization
     - StateExporter

--------

Extension Points
================

Adding New Components
---------------------

To add a new rocket component (e.g., air brakes):

1. **Create Configuration**:

   .. code-block:: python
   
      @dataclass
      class AirBrakesConfig:
          enabled: bool
          drag_coefficient: float
          reference_area_m2: float
          position_m: float

2. **Update RocketConfig**:

   .. code-block:: python
   
      @dataclass
      class RocketConfig:
          # ... existing fields
          air_brakes: Optional[AirBrakesConfig] = None

3. **Add Builder Method**:

   .. code-block:: python
   
      class RocketBuilder:
          def _add_air_brakes(self, rocket: Rocket) -> None:
              if self.config.air_brakes is None:
                  return
              
              rocket.add_air_brakes(
                  drag_coefficient=self.config.air_brakes.drag_coefficient,
                  reference_area=self.config.air_brakes.reference_area_m2,
                  position=self.config.air_brakes.position_m
              )

4. **Update YAML Schema**:

   .. code-block:: yaml
   
      rocket:
        air_brakes:
          enabled: true
          drag_coefficient: 1.5
          reference_area_m2: 0.01
          position_m: 1.0

Adding New Output Formats
--------------------------

To add a new export format (e.g., Excel):

1. **Extend DataHandler**:

   .. code-block:: python
   
      class DataHandler:
          def export_to_excel(self, flight: Flight, output_path: str):
              """Export trajectory to Excel with multiple sheets."""
              import pandas as pd
              
              with pd.ExcelWriter(output_path) as writer:
                  # Trajectory sheet
                  trajectory_df = self._create_trajectory_df(flight)
                  trajectory_df.to_excel(writer, sheet_name='Trajectory')
                  
                  # Summary sheet
                  summary_df = self._create_summary_df(flight)
                  summary_df.to_excel(writer, sheet_name='Summary')

2. **Update CLI Interface**:

   .. code-block:: python
   
      parser.add_argument('--export-excel', action='store_true',
                         help='Export results to Excel format')

--------

Performance Considerations
==========================

Computational Complexity
------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Operation
     - Complexity
     - Typical Time
   * - Config Loading
     - O(1)
     - <0.1 seconds
   * - Validation
     - O(1)
     - <0.1 seconds
   * - Object Building
     - O(1)
     - <0.1 seconds
   * - Single Flight
     - O(N_timesteps)
     - 0.5-2 seconds
   * - Plotting
     - O(N_points)
     - 0.2-0.5 seconds
   * - CSV Export
     - O(N_points)
     - 0.1-0.3 seconds

Optimization Strategies
-----------------------

1. **Lazy Evaluation**: Only compute requested outputs
2. **Efficient Data Structures**: NumPy arrays for trajectories
3. **Minimal Object Copies**: Pass by reference where safe
4. **Caching**: Reuse atmospheric calculations (via RocketPy)

--------

Error Handling Strategy
=======================

Fail-Fast Principle
-------------------

**Errors caught at configuration load time**, not during simulation:

.. code-block:: text

   ❌ BAD: Error during flight simulation
   ✅ GOOD: Error when loading configuration
   
   Why? Fail early to save computation time and provide clear feedback.

Error Categories
----------------

1. **Configuration Errors** (``ValueError``)
   
   - Missing required fields
   - Invalid parameter values
   - File not found

2. **Validation Errors** (``ValueError``)
   
   - Physical inconsistencies
   - Stability issues
   - Out-of-range parameters

3. **Runtime Errors** (``RuntimeError``)
   
   - Integration failures
   - Numerical instabilities

**Error Message Quality**:

.. code-block:: python

   # ❌ BAD
   raise ValueError("Invalid mass")
   
   # ✅ GOOD
   raise ValueError(
       f"Rocket mass {mass:.2f} kg is outside valid range [0.1, 1000] kg. "
       f"Check 'dry_mass_kg' in configuration."
   )

--------

Testing Architecture
====================

Test Categories
---------------

1. **Unit Tests**: Individual function/class testing
   
   - ``test_config_loader.py``
   - ``test_validators.py``
   - ``test_builders.py``

2. **Integration Tests**: End-to-end workflows
   
   - ``test_single_flight_pipeline.py``
   - ``test_output_generation.py``

3. **Validation Tests**: Physical plausibility
   
   - ``test_stability_calculations.py``
   - ``test_known_flights.py`` (regression tests)

Test Coverage: ~90%

--------

Future Architecture Plans
==========================

Planned Enhancements
--------------------

1. **Web API**: FastAPI REST interface for remote simulations
2. **Database Backend**: Store simulations in PostgreSQL/SQLite
3. **Real-time Monitoring**: WebSocket-based live trajectory updates
4. **Plugin System**: Third-party component extensions
5. **Optimization Framework**: Automated design optimization

Scalability Considerations
---------------------------

- **Horizontal Scaling**: Distribute Monte Carlo across machines
- **Caching Layer**: Redis for atmospheric/motor data
- **Async Operations**: Background task queue (Celery)

--------

See Also
========

.. seealso::

   **Related Documentation:**
   
   - :ref:`user-configuration` - Configuration file reference
   - :ref:`user-tutorials` - Step-by-step tutorials
   - :ref:`api-reference` - Complete API documentation
   
   **External Resources:**
   
   - `RocketPy Documentation <https://docs.rocketpy.org/>`_
   - `Clean Architecture Principles <https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html>`_
   - `Design Patterns <https://refactoring.guru/design-patterns>`_
