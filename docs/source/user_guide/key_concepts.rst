Key Concepts
============

This page explains the core concepts and architecture of the rocket simulation framework.

Framework Architecture
----------------------

The framework is built on a modular architecture with clear separation of concerns:

.. code-block:: text

    Configuration Layer (YAML + Dataclasses)
              ↓
    Builder Layer (Progressive Construction)
              ↓
    Simulation Layer (RocketPy Integration)
              ↓
    Analysis Layer (Monte Carlo, Sensitivity)
              ↓
    Output Layer (Plots, JSON, Reports)

Configuration System
--------------------

Type-Safe YAML Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All simulations are configured using YAML files that map to Python dataclasses. This provides:

- **Type safety**: Automatic validation of parameter types
- **IDE support**: Autocomplete and type hints
- **Documentation**: Self-documenting configuration structure
- **Version control friendly**: Human-readable text format

Example structure:

.. code-block:: python

    @dataclass
    class MotorConfig:
        thrust_source: str
        burn_out_time_s: float
        dry_mass_kg: float
        position_m: float  # Required - no default!
        # ... more parameters

    @dataclass
    class RocketConfig:
        radius_m: float
        mass_kg: float
        center_of_mass_without_motor_m: float
        # ... more parameters

Configuration Validation
~~~~~~~~~~~~~~~~~~~~~~~~

The framework performs comprehensive validation:

1. **Type checking**: Ensures correct data types
2. **Required parameters**: Fails fast on missing critical parameters
3. **Physical constraints**: Validates realistic values (e.g., positive mass)
4. **File existence**: Checks data files exist before simulation

Builder Pattern
---------------

Progressive Component Construction
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The framework uses builders for complex object construction:

.. code-block:: python

    # Step 1: Build motor
    motor_builder = MotorBuilder(motor_config)
    motor = motor_builder.build()

    # Step 2: Build environment
    env_builder = EnvironmentBuilder(env_config)
    environment = env_builder.build()

    # Step 3: Build rocket (depends on motor)
    rocket_builder = RocketBuilder(
        rocket_config,
        motor=motor,
        motor_config=motor_config
    )
    rocket = rocket_builder.build()

Benefits:

- **Dependency injection**: Clear component dependencies
- **Testability**: Easy to mock components
- **Flexibility**: Can customize construction steps
- **Error handling**: Validation at each build step

RocketPy Integration
--------------------

Native API Usage
~~~~~~~~~~~~~~~~

The framework uses RocketPy's native API without modification:

.. code-block:: python

    from rocketpy import SolidMotor, Rocket, Environment, Flight

    # Create RocketPy objects using their native API
    motor = SolidMotor(...)
    rocket = Rocket(...)
    environment = Environment(...)
    flight = Flight(rocket, environment, ...)

This ensures:

- **Full RocketPy compatibility**: Access to all features
- **Upstream updates**: Automatically benefit from RocketPy improvements
- **Community support**: Use RocketPy documentation and examples
- **No vendor lock-in**: Can use RocketPy directly if needed

Monte Carlo Analysis
---------------------

Uncertainty Quantification
~~~~~~~~~~~~~~~~~~~~~~~~~~

Monte Carlo simulation quantifies uncertainty in flight predictions by:

1. **Sampling**: Draw random parameter values from distributions
2. **Simulation**: Run many independent simulations
3. **Aggregation**: Collect and analyze results
4. **Statistics**: Compute distributions, percentiles, confidence intervals

Supported distributions:

- **Normal**: ``mean`` and ``std``
- **Uniform**: ``min`` and ``max``
- **Truncated normal**: Normal with bounds

Example configuration:

.. code-block:: yaml

    parameter_variations:
      motor.thrust_source:
        type: "normal"
        mean: 1.0      # Multiplier on nominal thrust
        std: 0.033     # 3.3% uncertainty

      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

Parallel Execution
~~~~~~~~~~~~~~~~~~

Monte Carlo simulations run in parallel using Python's multiprocessing:

- Automatic CPU core detection
- Progress monitoring
- Error handling per simulation
- Result aggregation

Sensitivity Analysis
--------------------

Variance-Based Methods
~~~~~~~~~~~~~~~~~~~~~~

The framework supports sensitivity analysis to identify which parameters most affect outcomes:

**Sobol Indices**
  Global sensitivity analysis that decomposes output variance into contributions from each input parameter.

**LAE (Local Average Effect)**
  Measures the average effect of varying each parameter while marginalizing over others.

Configuration example:

.. code-block:: yaml

    sensitivity_analysis:
      method: "sobol"  # or "lae"
      n_samples: 1000
      target_variable: "apogee_m"
      parameters:
        - "motor.thrust_source"
        - "rocket.mass_kg"
        - "environment.wind_speed_mps"

Air Brakes Control
------------------

Active Control System
~~~~~~~~~~~~~~~~~~~~~

The framework includes an air brakes controller for apogee targeting:

**Control Algorithms**:

- **PID**: Proportional-Integral-Derivative control
- **Bang-Bang**: Binary on/off control
- **Model Predictive**: Predictive control with constraints

**Hardware Constraints**:

- Maximum deployment level (0.0 to 1.0)
- Deployment rate limits
- Control loop frequency
- Sensor noise filtering

**State Management**:

The controller automatically resets state between Monte Carlo runs to prevent contamination:

.. code-block:: python

    def reset_state(self):
        """Reset controller state for new simulation."""
        self._integral = 0.0
        self._prev_error = 0.0
        self._commanded_deployment = 0.0
        # Auto-called on first controller invocation

Weather Integration
-------------------

Real Weather Data
~~~~~~~~~~~~~~~~~

The framework supports multiple weather data sources:

**Wyoming Soundings**
  Atmospheric profiles from radiosonde measurements

**GFS Forecasts**
  NOAA Global Forecast System predictions

**ERA5 Reanalysis**
  High-resolution historical weather data

**Custom Profiles**
  User-defined atmospheric conditions

Wind Convention
~~~~~~~~~~~~~~~

The framework uses the meteorological convention:

- Wind direction = direction wind **comes FROM**
- 0° = North, 90° = East, 180° = South, 270° = West
- Formula: ``u = -V*sin(θ)``, ``v = -V*cos(θ)``

Example: A "North wind" (0°) blows **toward the South**.

Output Formats
--------------

The framework generates multiple output formats:

**JSON Files**
  Complete simulation data for post-processing

**Plots**
  Trajectory, velocity, acceleration, stability plots

**Summary Statistics**
  Apogee, max velocity, flight time, impact point

**Sensitivity Reports**
  Parameter importance rankings and indices

**Monte Carlo Distributions**
  Histograms, scatter plots, confidence intervals

Next Steps
----------

- :doc:`configuration` - Complete configuration reference
- :doc:`../examples/index` - Practical examples
- :doc:`../development/index` - Contributing guide
