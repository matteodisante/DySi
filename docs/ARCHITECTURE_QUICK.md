# Architecture Quick Start (5 minutes)

Fast overview of the rocket simulation framework architecture - read this before diving into the code.

## 30-Second Summary

This framework wraps [RocketPy](https://github.com/RocketPy-Team/RocketPy) with:
1. **Type-safe YAML configurations** instead of imperative Python code
2. **Builder pattern** for progressive object construction
3. **Monte Carlo runner** for uncertainty quantification with parallel execution
4. **Variance-based sensitivity analysis** following RocketPy standards
5. **Visualization and export utilities** for production workflows

**Core principle**: Configuration-driven simulations with statistical rigor.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                      │
│  • Jupyter Notebooks     • Python Scripts    • CLI Tools    │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                   Application Layer                          │
│                                                              │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │ Single Flight│  │ Monte Carlo   │  │ Sensitivity     │  │
│  │ Simulator    │  │ Runner        │  │ Analysis        │  │
│  └──────┬───────┘  └───────┬───────┘  └────────┬────────┘  │
│         │                  │                    │           │
└─────────┼──────────────────┼────────────────────┼───────────┘
          │                  │                    │
┌─────────▼──────────────────▼────────────────────▼───────────┐
│                      Core Layer                              │
│                                                              │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐          │
│  │ Config     │   │ Builders   │   │ Validators │          │
│  │ Loader     │──▶│ (Motor,    │──▶│ (Safety    │          │
│  │ (YAML)     │   │  Env,      │   │  Checks)   │          │
│  └────────────┘   │  Rocket)   │   └────────────┘          │
│                   └──────┬─────┘                            │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   RocketPy Library                           │
│  • ODE Solver    • Aerodynamics    • 6-DOF Dynamics         │
└──────────────────────────────────────────────────────────────┘
```

---

## Module Organization (13 Modules, 5 Dependency Levels)

### Level 0: Foundation
**config_loader** - Parse YAML → Type-safe dataclasses

### Level 1: Object Construction
**motor_builder** - MotorConfig → RocketPy Motor
**environment_setup** - EnvironmentConfig → RocketPy Environment
**validators** - Config validation with warnings

### Level 2: Rocket Assembly
**rocket_builder** - RocketConfig + Motor → RocketPy Rocket
**air_brakes_controller** - PID/MPC control for active systems

### Level 3: Simulation Execution
**flight_simulator** - Rocket + Environment → Flight trajectory

### Level 4: Analysis & Output
**monte_carlo_runner** - Parallel ensemble simulations
**visualizer** - Flight data → Publication plots
**data_handler** - Export CSV/JSON/HDF5

### Level 5: Advanced Analysis
**sensitivity_analyzer** - OAT sensitivity indices
**variance_sensitivity** - Variance-based analysis with LAE
**sensitivity_utils** - Helper functions

---

## Data Flow: Single Simulation

```
config.yaml
    │
    ▼
ConfigLoader
    │
    ├──▶ RocketConfig ──▶ RocketBuilder ──┐
    ├──▶ MotorConfig ──▶ MotorBuilder ───┤
    ├──▶ EnvironmentConfig ──▶ EnvBuilder─┤
    └──▶ SimulationConfig ────────────────┤
                                          │
                                          ▼
                                   FlightSimulator
                                          │
                                          ▼
                                   Flight Object
                                          │
                     ┌────────────────────┼────────────────────┐
                     ▼                    ▼                    ▼
                Visualizer          DataHandler         Summary Stats
                     │                    │
                     ▼                    ▼
               plots/*.png          data/*.csv
```

**Execution Time**: ~1-5 seconds per simulation

---

## Data Flow: Monte Carlo Analysis

```
config.yaml
    │
    ▼
ConfigLoader
    │
    ▼
MonteCarloRunner
    │
    ├─▶ Parameter Variations (Normal/Uniform distributions)
    │
    ├─▶ Sample Generation (N sets of parameters)
    │
    └─▶ Parallel Execution
         │
         ├──▶ Worker 1: Simulation 1-25
         ├──▶ Worker 2: Simulation 26-50
         ├──▶ Worker 3: Simulation 51-75
         └──▶ Worker 4: Simulation 76-100
                │
                ▼
         Result Aggregation
                │
                ├──▶ Statistics (mean, std, percentiles)
                ├──▶ Landing dispersion ellipse
                └──▶ Export for sensitivity analysis
```

**Execution Time**: ~2-10 minutes for 100 simulations (4 cores)

---

## Data Flow: Sensitivity Analysis

```
Monte Carlo Results
    │
    ├──▶ parameters.csv (input samples)
    └──▶ outputs.csv (target variables)
         │
         ▼
VarianceBasedSensitivityAnalyzer
         │
         ├──▶ Fit linear regression: y = β₀ + Σ(β_j × x_j)
         │
         ├──▶ Variance decomposition: S(j) = β_j² × σ_j² / Var(y)
         │
         └──▶ Validation: LAE (Linear Approximation Error)
              │
              ▼
         Sensitivity Coefficients
              │
              ├──▶ Ranking by importance
              ├──▶ Filter significant (sensitivity > LAE)
              └──▶ Visualizations (bar plots, tornado diagrams)
```

**Interpretation**: S(j) = 60% means "if parameter j were known perfectly, output variance would drop by 60%"

---

## Design Patterns

### 1. Builder Pattern

**Why**: Progressive object construction with validation at each step

**Example**:
```python
# Without builder (RocketPy native - verbose)
motor = SolidMotor(...)
motor.add_grain(...)
motor.add_nozzle(...)

# With builder (this framework - clean)
motor = MotorBuilder(motor_cfg).build()
```

### 2. Dataclass Configurations

**Why**: Type safety, IDE autocomplete, validation

**Example**:
```python
@dataclass
class RocketConfig:
    name: str
    dry_mass_kg: float
    inertia: InertiaConfig
    # ... typed fields with defaults
```

### 3. Facade Pattern

**Why**: Simplify RocketPy's complex API

**Example**:
```python
# RocketPy: 50+ lines of imperative code
# This framework: 3 lines
loader = ConfigLoader()
rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config("config.yaml")
flight = FlightSimulator(rocket, motor, env, ...).run()
```

---

## Key Abstractions

### Configuration Dataclasses

**Purpose**: Type-safe, validated parameter containers

**Key Classes**:
- `RocketConfig`: Geometry, mass properties, components
- `MotorConfig`: Thrust curve, grain geometry
- `EnvironmentConfig`: Location, wind, atmosphere
- `SimulationConfig`: Integration params, rail setup

**Why**: Catch errors at load time, not runtime

---

### Builder Classes

**Purpose**: Convert configs → RocketPy objects with validation

**Key Classes**:
- `MotorBuilder`: Config → SolidMotor
- `EnvironmentBuilder`: Config → Environment
- `RocketBuilder`: Config + Motor → Rocket

**Why**: Separate configuration from construction logic

---

### Simulation Orchestrators

**Purpose**: High-level workflows

**Key Classes**:
- `FlightSimulator`: Single simulation with summary extraction
- `MonteCarloRunner`: Parallel ensemble with statistics
- `OATSensitivityAnalyzer`: Parameter screening
- `VarianceBasedSensitivityAnalyzer`: Rigorous sensitivity

**Why**: Reusable workflows instead of one-off scripts

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Physics Engine** | RocketPy | 6-DOF dynamics, aerodynamics, ODE solver |
| **Numerical Computing** | NumPy, SciPy | Array operations, statistics |
| **Data Handling** | Pandas | Tabular data, CSV I/O |
| **Visualization** | Matplotlib | Publication-quality plots |
| **Parallel Execution** | multiprocessing | CPU-bound Monte Carlo |
| **Configuration** | PyYAML | Human-readable configs |
| **Type Safety** | dataclasses, typing | Static analysis, validation |

---

## Performance Characteristics

### Single Simulation
- **Time**: 1-5 seconds (typical rocket)
- **Memory**: ~50 MB
- **CPU**: Single-threaded (RocketPy ODE solver)

### Monte Carlo (100 simulations)
- **Time**: 2-10 minutes (4 cores, parallel)
- **Memory**: ~500 MB (100 Flight objects)
- **CPU**: Embarrassingly parallel (4-8 cores recommended)

### Sensitivity Analysis
- **Time**: <1 second (reuses MC data)
- **Memory**: ~100 MB (regression on MC results)
- **CPU**: Single-threaded (linear regression)

**Bottleneck**: ODE integration in single simulations (cannot be parallelized)

---

## Configuration Philosophy

### YAML-First Design

**Traditional approach** (RocketPy native):
```python
# 100+ lines of imperative Python code
motor = SolidMotor(...)
motor.add_grain(...)
env = Environment(...)
env.set_atmospheric_model(...)
rocket = Rocket(...)
rocket.add_motor(...)
rocket.add_nose(...)
rocket.add_fins(...)
# ... many more lines
```

**This framework**:
```yaml
# config.yaml - Declarative, version-controlled
rocket:
  dry_mass_kg: 16.0
  fins:
    count: 4
motor:
  thrust_source: "data/motors/motor.eng"
environment:
  latitude_deg: 40.0
```

```python
# Python - Just workflow logic
loader = ConfigLoader()
configs = loader.load_complete_config("config.yaml")
flight = FlightSimulator(...).run()
```

**Benefits**:
- Non-programmers can modify configs
- Git-friendly diffs
- Easy A/B testing (swap YAML files)
- Separation of "what" (config) from "how" (code)

---

## Extension Points

### Adding New Components

1. **New configuration field**: Modify dataclass in `config_loader.py`
2. **New builder logic**: Update builder in `rocket_builder.py`
3. **New controller type**: Extend `air_brakes_controller.py`
4. **New sensitivity method**: Inherit from `VarianceBasedSensitivityAnalyzer`

### Adding New Workflows

1. **New analysis type**: Create module in `src/`, import in notebooks
2. **New plot type**: Add method to `Visualizer` class
3. **New export format**: Add method to `DataHandler` class

---

## Comparison to RocketPy Native

| Feature | RocketPy Native | This Framework |
|---------|----------------|----------------|
| **Configuration** | Imperative Python | Declarative YAML |
| **Type Safety** | Runtime errors | Load-time validation |
| **Monte Carlo** | Manual loop | Parallel runner with stats |
| **Sensitivity** | Manual implementation | Built-in variance-based |
| **Plotting** | Custom matplotlib | Standardized visualizer |
| **Learning Curve** | Steep (API docs) | Gentle (YAML examples) |
| **Flexibility** | Maximum | High (via YAML schema) |

**When to use RocketPy directly**: Custom physics models, research on aerodynamics

**When to use this framework**: Production workflows, competitions, parameter studies

---

## Next Steps

### Quick Start
1. Read [MODULE_REFERENCE.md](MODULE_REFERENCE.md) - 1-page module guide
2. Run [00_getting_started.ipynb](../notebooks/00_getting_started.ipynb) - 5-min example
3. Copy `configs/templates/template_basic.yaml` - Start your config

### Deep Dive
1. Full architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
2. Config schema: [../configs/README_CONFIGS.md](../configs/README_CONFIGS.md)
3. Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Common Workflows
- **Single flight**: Notebook [01_single_flight_simulation.ipynb](../notebooks/01_single_flight_simulation.ipynb)
- **Monte Carlo**: Notebook [02_monte_carlo_ensemble.ipynb](../notebooks/02_monte_carlo_ensemble.ipynb)
- **Sensitivity**: Notebook [03_sensitivity_analysis.ipynb](../notebooks/03_sensitivity_analysis.ipynb)

---

## Architecture Principles

1. **Configuration over code**: YAML files drive simulations
2. **Type safety**: Dataclasses catch errors early
3. **Separation of concerns**: Config → Build → Simulate → Analyze
4. **Reusability**: Builders and runners are generic
5. **Validation first**: Check before expensive computation
6. **Statistical rigor**: Variance-based methods with LAE validation
7. **Performance**: Parallel execution where possible

---

**Time to first simulation**: ~5 minutes
**Time to production workflow**: ~1 hour
**Lines of code for typical simulation**: ~10 (vs 100+ in native RocketPy)
