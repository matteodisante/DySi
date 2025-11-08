# Module Quick Reference

One-page reference for all 13 core modules in the rocket simulation framework.

## Module Overview

| Module | Purpose | Key Classes/Functions | Inputs | Outputs |
|--------|---------|----------------------|--------|---------|
| **config_loader** | Load and parse YAML configurations | `ConfigLoader` | YAML file path | Config dataclasses |
| **motor_builder** | Build RocketPy motor objects | `MotorBuilder` | `MotorConfig` | `SolidMotor` |
| **environment_setup** | Build atmospheric environment | `EnvironmentBuilder` | `EnvironmentConfig` | `Environment` |
| **rocket_builder** | Assemble complete rocket | `RocketBuilder` | `RocketConfig`, `Motor` | `Rocket` |
| **flight_simulator** | Execute flight simulation | `FlightSimulator` | `Rocket`, `Environment`, rail params | `Flight` |
| **visualizer** | Generate plots and visualizations | `Visualizer` | `Flight` | PNG/PDF plots |
| **data_handler** | Export simulation data | `DataHandler` | `Flight`, summary dict | CSV/JSON files |
| **monte_carlo_runner** | Run ensemble simulations | `MonteCarloRunner` | Configs, param variations | List of results |
| **sensitivity_analyzer** | OAT sensitivity analysis | `OATSensitivityAnalyzer` | Configs, param list | Sensitivity indices |
| **variance_sensitivity** | Variance-based sensitivity | `VarianceBasedSensitivityAnalyzer` | MC data | Sensitivity coefficients |
| **sensitivity_utils** | Sensitivity helper functions | Various utility functions | Sensitivity data | Formatted outputs |
| **validators** | Configuration validation | `RocketValidator`, `MotorValidator`, etc. | Config objects | List of warnings |
| **air_brakes_controller** | Air brakes control logic | `AirBrakesController` | Controller config, target apogee | Deployment level |

## Dependency Levels

### Level 0 (No dependencies)
- **config_loader**: Pure YAML parsing and dataclass creation

### Level 1 (Depends on config_loader only)
- **validators**: Validate configuration objects
- **motor_builder**: Build motors from configs
- **environment_setup**: Build environments from configs

### Level 2 (Depends on Level 0-1)
- **rocket_builder**: Needs config_loader + motor_builder
- **air_brakes_controller**: Needs config_loader for controller config

### Level 3 (Depends on Level 0-2)
- **flight_simulator**: Needs rocket_builder, motor_builder, environment_setup

### Level 4 (Depends on Level 0-3)
- **visualizer**: Needs flight_simulator output
- **data_handler**: Needs flight_simulator output
- **monte_carlo_runner**: Orchestrates flight_simulator for ensemble runs

### Level 5 (Depends on Level 0-4)
- **sensitivity_analyzer**: Needs monte_carlo_runner for data
- **variance_sensitivity**: Needs monte_carlo_runner for data
- **sensitivity_utils**: Needs sensitivity analyzers

## Typical Workflows

### Single Flight Simulation

```
config_loader → motor_builder → environment_setup → rocket_builder → flight_simulator → visualizer/data_handler
```

### Monte Carlo Analysis

```
config_loader → monte_carlo_runner → (many flight_simulator runs) → statistics → visualizer/data_handler
```

### Sensitivity Analysis

```
config_loader → monte_carlo_runner → variance_sensitivity → sensitivity_utils → visualizer
```

## Module Details

### config_loader

**Purpose**: Load YAML configurations and convert to type-safe dataclasses

**Key Classes**:
- `ConfigLoader`: Main class for loading configs

**Key Methods**:
```python
loader = ConfigLoader()
loader.load_from_yaml("config.yaml")
rocket_cfg = loader.get_rocket_config()
motor_cfg = loader.get_motor_config()
env_cfg = loader.get_environment_config()
sim_cfg = loader.get_simulation_config()
```

**Dataclasses**:
- `RocketConfig`: Rocket geometry, mass, inertia, components
- `MotorConfig`: Motor type, thrust curve, grain geometry
- `EnvironmentConfig`: Location, wind, atmospheric model
- `SimulationConfig`: Integration params, rail setup

---

### motor_builder

**Purpose**: Build RocketPy `SolidMotor` objects from configuration

**Key Classes**:
- `MotorBuilder`: Builds motors with grain geometry

**Key Methods**:
```python
builder = MotorBuilder(motor_cfg)
motor = builder.build()
summary = builder.get_summary()
```

**Input**: `MotorConfig` dataclass
**Output**: RocketPy `SolidMotor` object

---

### environment_setup

**Purpose**: Build RocketPy `Environment` objects with wind and atmosphere

**Key Classes**:
- `EnvironmentBuilder`: Sets up atmospheric conditions

**Key Methods**:
```python
builder = EnvironmentBuilder(env_cfg)
environment = builder.build()
summary = builder.get_summary()
```

**Input**: `EnvironmentConfig` dataclass
**Output**: RocketPy `Environment` object

---

### rocket_builder

**Purpose**: Assemble complete rocket with nose cone, fins, parachutes, air brakes

**Key Classes**:
- `RocketBuilder`: Progressive rocket assembly

**Key Methods**:
```python
builder = RocketBuilder(rocket_cfg)
rocket = builder.build(motor)
stability = builder.get_stability_info()
summary = builder.get_summary()
```

**Input**: `RocketConfig` dataclass, `Motor` object
**Output**: RocketPy `Rocket` object

**Key Info**:
- Automatically adds nose cone, fins, parachutes based on config
- Supports air brakes with controller integration
- Validates stability (static margin)

---

### flight_simulator

**Purpose**: Execute flight simulation using RocketPy's ODE solver

**Key Classes**:
- `FlightSimulator`: Run simulation and extract metrics

**Key Methods**:
```python
sim = FlightSimulator(rocket, motor, environment, rail_length_m, inclination_deg, heading_deg)
flight = sim.run()
summary = sim.get_summary()
sim.print_summary()
```

**Input**: `Rocket`, `Motor`, `Environment`, rail parameters
**Output**: RocketPy `Flight` object

**Key Metrics**:
- Apogee altitude, time, coordinates
- Max velocity, Mach number, acceleration
- Flight time, landing coordinates
- Off-rail velocity, rail angle

---

### visualizer

**Purpose**: Create publication-quality plots from flight data

**Key Classes**:
- `Visualizer`: Multi-plot generation

**Key Methods**:
```python
viz = Visualizer(flight)
viz.plot_trajectory_3d(output_path="trajectory.png")
viz.plot_altitude_vs_time(output_path="altitude.png")
viz.plot_velocity_vs_time(output_path="velocity.png")
viz.create_standard_plots(output_dir)  # All plots at once
```

**Input**: RocketPy `Flight` object
**Output**: PNG/PDF plot files

**Available Plots**:
- 3D trajectory
- Altitude vs time
- Velocity vs time
- Acceleration vs time
- Angular velocity
- Stability margin evolution

---

### data_handler

**Purpose**: Export simulation data in standard formats

**Key Classes**:
- `DataHandler`: Multi-format export

**Key Methods**:
```python
handler = DataHandler()
handler.export_trajectory_csv(flight, "trajectory.csv")
handler.export_summary_json(summary, "summary.json")
handler.export_complete_dataset(flight, summary, output_dir, formats=['csv', 'json'])
```

**Input**: `Flight` object, summary dict
**Output**: CSV, JSON, HDF5 files

**Export Formats**:
- CSV: Trajectory time series
- JSON: Flight summary and metadata
- HDF5: Full dataset for large ensembles

---

### monte_carlo_runner

**Purpose**: Run ensemble simulations with parameter variations

**Key Classes**:
- `MonteCarloRunner`: Parallel ensemble execution

**Key Methods**:
```python
runner = MonteCarloRunner(rocket_cfg, motor_cfg, env_cfg, sim_cfg, num_simulations=100)
runner.add_parameter_variation("rocket.dry_mass_kg", mean=16.0, std=0.5, distribution="normal")
results = runner.run(parallel=True, max_workers=4)
stats = runner.get_statistics()
runner.print_statistics_summary()
```

**Input**: Base configs, parameter variations
**Output**: List of result dicts with statistics

**Features**:
- Parallel execution with multiprocessing
- Automatic parameter sampling (normal, uniform, truncated normal)
- Statistical summaries (mean, std, percentiles)
- Export in RocketPy format for sensitivity analysis

---

### sensitivity_analyzer (OAT)

**Purpose**: One-At-a-Time sensitivity analysis for parameter screening

**Key Classes**:
- `OATSensitivityAnalyzer`: Traditional sensitivity indices

**Key Methods**:
```python
analyzer = OATSensitivityAnalyzer(rocket_cfg, motor_cfg, env_cfg, sim_cfg)
analyzer.add_parameter("rocket.dry_mass_kg", variation_percent=10.0)
analyzer.run(output_metric="apogee_m")
analyzer.print_summary()
analyzer.plot_tornado_diagram("tornado.png")
```

**Input**: Configs, parameter list with variation percentages
**Output**: Sensitivity indices, tornado diagram

**Use Case**: Quick screening to identify most influential parameters

---

### variance_sensitivity

**Purpose**: Variance-based sensitivity analysis (RocketPy standard method)

**Key Classes**:
- `VarianceBasedSensitivityAnalyzer`: Statistical variance decomposition

**Key Methods**:
```python
analyzer = VarianceBasedSensitivityAnalyzer(parameter_names, target_names)
analyzer.set_nominal_parameters(means, stds)
analyzer.fit(parameters_df, targets_df)
analyzer.print_summary()
analyzer.plot_sensitivity_bars("sensitivity.png", target_name="apogee_m")
```

**Input**: Monte Carlo parameter samples and target values
**Output**: Sensitivity coefficients (%), Linear Approximation Error (LAE)

**Key Metrics**:
- Sensitivity coefficient: % variance contribution
- LAE: Model linearity validation (<10% = excellent)
- Effect per std: Practical impact magnitude

**Use Case**: Rigorous quantitative sensitivity analysis with statistical validation

---

### sensitivity_utils

**Purpose**: Helper functions for sensitivity analysis workflows

**Key Functions**:
- `estimate_parameter_statistics()`: Compute means and std devs
- `create_sensitivity_comparison()`: Compare OAT vs variance-based
- `filter_significant_parameters()`: Remove params with sensitivity < LAE
- `calculate_variance_reduction()`: Estimate variance reduction from control
- `export_sensitivity_to_json()`: Save results in JSON format

**Use Case**: Post-processing and interpretation of sensitivity results

---

### validators

**Purpose**: Validate configurations for physical correctness

**Key Classes**:
- `RocketValidator`: Rocket physics validation
- `MotorValidator`: Motor parameter validation
- `EnvironmentValidator`: Environment validation
- `SimulationValidator`: Simulation parameter validation

**Key Methods**:
```python
warnings = RocketValidator.validate(rocket_cfg)
for w in warnings:
    print(f"{w.level}: {w.message}")
```

**Validation Checks**:
- **Critical**: Positive masses, valid coordinates, stability
- **Warning**: Unusual values, potential design issues
- **Info**: Recommendations and suggestions

**Use Case**: Catch configuration errors before running simulations

---

### air_brakes_controller

**Purpose**: Active control system for air brakes deployment

**Key Classes**:
- `AirBrakesController`: PID/bang-bang/MPC controllers

**Key Methods**:
```python
controller = AirBrakesController(controller_config, target_apogee_m=3000.0)
deployment = controller.compute_deployment(current_state, current_time)
```

**Controller Types**:
- **PID**: Classic proportional-integral-derivative control
- **Bang-bang**: Simple on/off control
- **MPC**: Model predictive control (advanced)

**Features**:
- Realistic actuator lag and computation delay
- Safety interlocks (min altitude, min time)
- Deployment rate limiting

**Use Case**: Competition rockets with apogee targeting requirements

---

## Quick Tips

### Finding the Right Module

**Need to...**
- Parse a YAML file? → `config_loader`
- Build simulation objects? → `motor_builder`, `environment_setup`, `rocket_builder`
- Run a simulation? → `flight_simulator`
- Create plots? → `visualizer`
- Export data? → `data_handler`
- Uncertainty analysis? → `monte_carlo_runner`
- Identify critical parameters? → `sensitivity_analyzer` or `variance_sensitivity`
- Check config validity? → `validators`

### Import Patterns

All modules are in the `src/` package:

```python
from src.config_loader import ConfigLoader
from src.motor_builder import MotorBuilder
from src.flight_simulator import FlightSimulator
# etc.
```

### Error Handling

Most modules raise exceptions on critical errors:
- `ValueError`: Invalid parameter values
- `FileNotFoundError`: Missing thrust curve or config files
- `RuntimeError`: Simulation convergence failures

Use validators to catch issues early:
```python
from src.validators import validate_all_configs

warnings = validate_all_configs(rocket_cfg, motor_cfg, env_cfg, sim_cfg)
if any(w.level == "ERROR" for w in warnings):
    print("Critical errors found! Fix before running simulation")
```

## See Also

- **Full architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Config schema**: [../configs/README_CONFIGS.md](../configs/README_CONFIGS.md)
- **Troubleshooting**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Example notebooks**: [../notebooks/](../notebooks/)
