Architecture
============

This page describes the framework's architecture and design patterns.

Overview
--------

The framework follows a layered architecture:

.. code-block:: text

    ┌─────────────────────────────────────────────┐
    │         Configuration Layer                  │
    │  (YAML files + Python dataclasses)          │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────┐
    │           Builder Layer                      │
    │  (MotorBuilder, RocketBuilder, EnvBuilder)  │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────┐
    │         RocketPy Integration                 │
    │  (Native RocketPy objects)                  │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────┐
    │        Simulation Layer                      │
    │  (RocketSimulator, MonteCarloRunner)        │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────┐
    │          Analysis Layer                      │
    │  (Sensitivity, Statistics, Plotting)        │
    └─────────────────┬───────────────────────────┘
                      │
    ┌─────────────────▼───────────────────────────┐
    │           Output Layer                       │
    │  (JSON, CSV, Plots, Reports)                │
    └─────────────────────────────────────────────┘

Core Modules
------------

Configuration (src/config.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Type-safe configuration management

**Key Classes**:

- ``MotorConfig``: Motor parameters
- ``RocketConfig``: Rocket parameters
- ``EnvironmentConfig``: Environment parameters
- ``SimulationConfig``: Simulation parameters

**Pattern**: Dataclass-based configuration with YAML loading

.. code-block:: python

    @dataclass
    class MotorConfig:
        thrust_source: str
        dry_mass_kg: float
        position_m: float
        # ... more fields

Builders (src/*_builder.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Progressive construction of RocketPy objects

**Key Classes**:

- ``MotorBuilder``: Constructs ``SolidMotor``
- ``RocketBuilder``: Constructs ``Rocket``
- ``EnvironmentBuilder``: Constructs ``Environment``

**Pattern**: Builder pattern with dependency injection

.. code-block:: python

    class RocketBuilder:
        def __init__(
            self,
            config: RocketConfig,
            motor: Optional[SolidMotor] = None,
            motor_config: Optional[MotorConfig] = None
        ):
            self.config = config
            self.motor = motor
            self.motor_config = motor_config

        def build(self) -> Rocket:
            # Progressive construction
            rocket = self._create_base_rocket()
            self._add_nose_cone(rocket)
            self._add_fins(rocket)
            self._add_motor(rocket)
            self._add_parachutes(rocket)
            self._add_air_brakes(rocket)
            return rocket

Simulation (src/simulator.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Run single rocket simulations

**Key Class**: ``RocketSimulator``

**Pattern**: Facade pattern wrapping RocketPy

.. code-block:: python

    class RocketSimulator:
        def __init__(
            self,
            rocket: Rocket,
            environment: Environment,
            simulation_config: SimulationConfig
        ):
            self.rocket = rocket
            self.environment = environment
            self.config = simulation_config

        def run(self) -> Flight:
            # Run RocketPy simulation
            return Flight(
                rocket=self.rocket,
                environment=self.environment,
                rail_length=self.config.rail_length_m,
                inclination=self.config.inclination_deg,
                heading=self.config.heading_deg,
                terminate_on_apogee=self.config.terminate_on_apogee,
                verbose=self.config.verbose
            )

Monte Carlo (src/monte_carlo_runner.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Uncertainty quantification with parallel execution

**Key Class**: ``MonteCarloRunner``

**Pattern**: Parallel map-reduce

.. code-block:: python

    class MonteCarloRunner:
        def run(self) -> List[Dict]:
            # Sample parameter space
            samples = self._generate_samples()

            # Parallel execution
            with multiprocessing.Pool() as pool:
                results = pool.map(
                    self._run_single_simulation,
                    range(self.n_simulations)
                )

            # Aggregate results
            return self._aggregate_results(results)

Air Brakes (src/air_brakes_controller.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Purpose**: Active control for apogee targeting

**Key Class**: ``AirBrakesController``

**Pattern**: Control loop with state management

.. code-block:: python

    class AirBrakesController:
        def __init__(self, config: AirBrakesConfig):
            self.config = config
            self._integral = 0.0
            self._prev_error = 0.0

        def reset_state(self):
            """Reset for new simulation (Monte Carlo)."""
            self._integral = 0.0
            self._prev_error = 0.0
            # ... reset other state

        def controller_function(self, time, observed_variables):
            """RocketPy callback function."""
            if not observed_variables:
                # Auto-reset for new simulation
                self.reset_state()

            # Control logic
            error = self._compute_error(observed_variables)
            deployment = self._compute_deployment(error)
            return deployment

Design Patterns
---------------

Builder Pattern
~~~~~~~~~~~~~~~

**Where**: Motor, Rocket, Environment construction

**Why**:
- Separates configuration from construction
- Allows progressive assembly
- Encapsulates RocketPy API details

**Example**:

.. code-block:: python

    # Progressive construction
    motor = MotorBuilder(motor_config).build()
    environment = EnvironmentBuilder(env_config).build()
    rocket = RocketBuilder(rocket_config, motor=motor).build()

Dependency Injection
~~~~~~~~~~~~~~~~~~~~

**Where**: RocketBuilder needs motor and motor_config

**Why**:
- Decouples components
- Enables testing with mocks
- Makes dependencies explicit

**Example**:

.. code-block:: python

    rocket_builder = RocketBuilder(
        config=rocket_config,
        motor=motor,              # Injected dependency
        motor_config=motor_config  # Injected dependency
    )

Facade Pattern
~~~~~~~~~~~~~~

**Where**: RocketSimulator wraps RocketPy

**Why**:
- Simplifies RocketPy API usage
- Provides consistent interface
- Encapsulates complexity

**Example**:

.. code-block:: python

    simulator = RocketSimulator(rocket, environment, sim_config)
    flight = simulator.run()  # Simple interface
    summary = simulator.get_summary()  # Convenient methods

Strategy Pattern
~~~~~~~~~~~~~~~~

**Where**: Air brakes controller types (PID, bang-bang, MPC)

**Why**:
- Allows runtime algorithm selection
- Encapsulates control algorithms
- Easy to add new controllers

**Example**:

.. code-block:: python

    # Strategy selected via configuration
    controller_type = config.controller_type  # "pid" or "bang_bang"
    controller = self._create_controller(controller_type)

Key Design Decisions
--------------------

RocketPy Native API
~~~~~~~~~~~~~~~~~~~

**Decision**: Use RocketPy's API without modification

**Rationale**:
- Full access to RocketPy features
- Automatic upstream updates
- No vendor lock-in
- Community compatibility

**Trade-off**: Must adapt to RocketPy API changes

Type-Safe Configuration
~~~~~~~~~~~~~~~~~~~~~~~

**Decision**: Use Python dataclasses for configuration

**Rationale**:
- Compile-time type checking
- IDE autocomplete support
- Validation at load time
- Self-documenting

**Trade-off**: Less flexible than plain dictionaries

Parallel Monte Carlo
~~~~~~~~~~~~~~~~~~~~

**Decision**: Use multiprocessing for parallelization

**Rationale**:
- Automatic CPU core utilization
- Process isolation (prevents state contamination)
- Simple implementation

**Trade-off**: Process overhead, no shared memory

Module Organization
-------------------

.. code-block:: text

    src/
    ├── config.py                  # Configuration dataclasses
    ├── motor_builder.py           # Motor construction
    ├── rocket_builder.py          # Rocket construction
    ├── environment_setup.py       # Environment construction
    ├── simulator.py               # Single simulation
    ├── monte_carlo_runner.py      # Monte Carlo analysis
    ├── air_brakes_controller.py   # Air brakes control
    ├── sensitivity_analysis.py    # Sensitivity methods
    └── utils.py                   # Utility functions

    scripts/
    ├── run_single_simulation.py   # CLI for single sim
    ├── run_monte_carlo.py         # CLI for Monte Carlo
    └── run_sensitivity.py         # CLI for sensitivity

    tests/
    ├── test_config.py             # Configuration tests
    ├── test_builders.py           # Builder tests
    ├── test_simulator.py          # Simulation tests
    └── test_monte_carlo.py        # Monte Carlo tests

    docs/
    └── source/                    # Sphinx documentation

Data Flow
---------

Single Simulation
~~~~~~~~~~~~~~~~~

.. code-block:: text

    YAML file → load_config() → Config objects
                                      ↓
    Config → MotorBuilder → SolidMotor
                                      ↓
    Config → EnvironmentBuilder → Environment
                                      ↓
    Config + Motor → RocketBuilder → Rocket
                                      ↓
    Rocket + Environment → RocketSimulator → Flight
                                      ↓
    Flight → get_summary() → Results dict
                                      ↓
    Results → JSON/Plots → Output files

Monte Carlo Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    YAML file → load_config() → Config + Variations
                                      ↓
    MonteCarloRunner → Sample parameter space
                                      ↓
    For each sample:
        Perturb config → Build rocket → Simulate → Results
                                      ↓
    Aggregate results → Statistics
                                      ↓
    Statistics → Plots/JSON → Output files

Extension Points
----------------

Adding New Controller Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Implement controller logic in ``AirBrakesController``
2. Add configuration fields to ``AirBrakesConfig``
3. Update controller factory method
4. Add tests

Adding New Weather Sources
~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add source type to ``EnvironmentConfig``
2. Implement fetch logic in ``EnvironmentBuilder``
3. Handle data format conversion
4. Add tests

Adding New Sensitivity Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Implement method in ``sensitivity_analysis.py``
2. Add method enum to configuration
3. Update CLI script
4. Add tests

Performance Considerations
--------------------------

Bottlenecks
~~~~~~~~~~~

1. **RocketPy simulation**: ~0.1-1s per simulation
2. **Multiprocessing overhead**: Process spawning
3. **Data aggregation**: Large result sets

Optimizations
~~~~~~~~~~~~~

1. **Parallel execution**: Use all CPU cores
2. **Lazy loading**: Load data only when needed
3. **Efficient serialization**: Use JSON for results
4. **Minimize file I/O**: Batch writes

Next Steps
----------

- :doc:`contributing` - Start contributing
- :doc:`testing` - Write and run tests
- :doc:`code_style` - Follow coding standards
