# Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Module Reference](#module-reference)
7. [Extension Points](#extension-points)
8. [Configuration System](#configuration-system)
9. [Testing Architecture](#testing-architecture)

---

## System Overview

The Rocket Simulation Framework is a **layered, modular architecture** built on top of [RocketPy](https://github.com/RocketPy-Team/RocketPy). It follows **clean architecture principles** with clear separation of concerns:

- **Configuration Layer**: YAML-based configuration with type-safe dataclasses
- **Builder Layer**: Builder pattern for constructing RocketPy objects
- **Simulation Layer**: Flight simulation execution and orchestration
- **Analysis Layer**: Monte Carlo and sensitivity analysis pipelines
- **Visualization Layer**: Publication-quality plotting and data export

### Key Design Principles

1. **Type Safety**: Full type hints and dataclass-based configuration
2. **Immutability**: Configuration objects are immutable (dataclasses)
3. **Separation of Concerns**: Each module has a single, well-defined responsibility
4. **Testability**: Dependency injection and mocking-friendly design
5. **Extensibility**: Builder pattern allows easy addition of new components
6. **Fail-Fast**: Validation at configuration load time, not runtime

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                            │
├─────────────────────────────────────────────────────────────────────────┤
│  CLI Scripts        │  Jupyter Notebooks    │  Python API               │
│  • run_single.py    │  • 00_getting_started │  • Direct module imports  │
│  • run_monte_carlo  │  • 01_single_flight   │  • Programmatic usage     │
│  • run_sensitivity  │  • 02_monte_carlo     │                           │
│                     │  • 03_sensitivity     │                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       CONFIGURATION LAYER                               │
├─────────────────────────────────────────────────────────────────────────┤
│  ConfigLoader (config_loader.py)                                        │
│  ┌────────────────┬─────────────────┬──────────────────────────────┐   │
│  │ RocketConfig   │ MotorConfig     │ EnvironmentConfig            │   │
│  │ MotorConfig    │ SimulationConfig│ MonteCarloConfig             │   │
│  └────────────────┴─────────────────┴──────────────────────────────┘   │
│                                                                          │
│  Validators (validators.py)                                             │
│  • Physical plausibility checks    • Stability analysis                 │
│  • Range validation                • Units verification                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BUILDER LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  MotorBuilder          EnvironmentBuilder        RocketBuilder          │
│  (motor_builder.py)    (environment_setup.py)    (rocket_builder.py)   │
│  ┌───────────────┐     ┌─────────────────────┐  ┌──────────────────┐  │
│  │ SolidMotor    │     │ Environment         │  │ Rocket           │  │
│  │ • Thrust curve│     │ • Atmosphere model  │  │ • Nose cone      │  │
│  │ • Grain geom. │     │ • Wind profile      │  │ • Fins           │  │
│  │ • Inertia     │     │ • Location/date     │  │ • Parachute      │  │
│  └───────────────┘     └─────────────────────┘  │ • Drag curves    │  │
│                                                  └──────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       SIMULATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  FlightSimulator (flight_simulator.py)                                  │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ • Run RocketPy Flight simulation                               │    │
│  │ • Extract metrics (apogee, velocity, acceleration, etc.)       │    │
│  │ • Export trajectory data                                       │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                          │
│  MonteCarloRunner (monte_carlo_runner.py)                               │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ • Parallel execution (ProcessPoolExecutor)                     │    │
│  │ • Parameter variation sampling                                 │    │
│  │ • Statistical aggregation                                      │    │
│  │ • Export for sensitivity analysis                              │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANALYSIS LAYER                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Variance-Based Sensitivity     │  OAT Sensitivity                      │
│  (variance_sensitivity.py)      │  (sensitivity_analyzer.py)            │
│  ┌───────────────────────────┐  │  ┌──────────────────────────────┐   │
│  │ • Multiple linear regress.│  │  │ • Local sensitivity (2N+1)   │   │
│  │ • Sensitivity coefficients│  │  │ • Tornado diagrams           │   │
│  │ • LAE validation          │  │  │ • Quick parameter screening  │   │
│  │ • Prediction intervals    │  │  └──────────────────────────────┘   │
│  └───────────────────────────┘  │                                       │
│                                                                          │
│  Sensitivity Utilities (sensitivity_utils.py)                           │
│  • Load/save RocketPy formats  • Jacobian calculation                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    VISUALIZATION & EXPORT LAYER                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Visualizer (visualizer.py)    │  DataHandler (data_handler.py)        │
│  ┌──────────────────────────┐  │  ┌────────────────────────────────┐  │
│  │ • 3D trajectory          │  │  │ • CSV export                   │  │
│  │ • Altitude profile       │  │  │ • JSON export                  │  │
│  │ • Velocity/accel plots   │  │  │ • KML export (Google Earth)    │  │
│  │ • Monte Carlo dispersion │  │  │ • RocketPy .txt formats        │  │
│  │ • Sensitivity bar charts │  │  └────────────────────────────────┘  │
│  └──────────────────────────┘  │                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          ┌──────────────────┐
                          │   RocketPy Core  │
                          │  (External Lib)  │
                          └──────────────────┘
```

---

## Core Components

### 1. Configuration System (`config_loader.py`)

**Purpose**: Load and validate YAML configuration files into type-safe dataclass objects.

**Key Classes**:
- `ConfigLoader`: Main configuration loader with YAML parsing
- `RocketConfig`: Rocket geometry, mass, inertia, components
- `MotorConfig`: Motor specifications and thrust curves
- `EnvironmentConfig`: Atmospheric model, location, wind
- `SimulationConfig`: Integration parameters, rail configuration
- `MonteCarloConfig`: Uncertainty distributions, simulation count

**Design Pattern**: **Factory** - Converts YAML dictionaries into typed objects

**Example**:
```python
loader = ConfigLoader()
loader.load_from_yaml('configs/rocket.yaml')
rocket_config = loader.get_rocket_config()
```

### 2. Validation Layer (`validators.py`)

**Purpose**: Ensure physical plausibility and consistency of configurations.

**Key Classes**:
- `RocketValidator`: Stability margin, mass distribution, geometry
- `MotorValidator`: Thrust curve sanity, grain geometry, mass consistency
- `EnvironmentValidator`: Atmospheric model, location bounds
- `SimulationValidator`: Integration parameters, rail configuration

**Validation Types**:
- **Physical Bounds**: Parameters within realistic ranges (e.g., 0 < mass < 1000 kg)
- **Consistency Checks**: Related parameters are compatible (e.g., CG < CP for stability)
- **Completeness**: Required files exist (thrust curves, atmospheric data)
- **Stability Analysis**: Static margin > 1.5 calibers (configurable threshold)

**Error Handling**:
- Raises `ValueError` with detailed messages for validation failures
- Warnings logged for non-critical issues (e.g., low stability margin)

### 3. Builder Pattern (`motor_builder.py`, `environment_setup.py`, `rocket_builder.py`)

**Purpose**: Construct RocketPy objects from configuration dataclasses.

#### MotorBuilder
- **Input**: `MotorConfig`
- **Output**: `rocketpy.SolidMotor`
- **Responsibilities**:
  - Load thrust curve from `.eng` or `.csv` files
  - Configure grain geometry (cylindrical grains)
  - Set dry mass and inertia tensor
  - Position motor on rocket centerline

#### EnvironmentBuilder
- **Input**: `EnvironmentConfig`
- **Output**: `rocketpy.Environment`
- **Responsibilities**:
  - Set geographic location (lat/lon/elevation)
  - Configure atmospheric model (standard atmosphere or custom file)
  - Set wind profile (constant, function-based, or custom)
  - Configure date/time for atmospheric conditions

#### RocketBuilder
- **Input**: `RocketConfig`, `Motor`
- **Output**: `rocketpy.Rocket`
- **Responsibilities**:
  - Create base rocket structure (mass, inertia, geometry)
  - Add motor at specified position
  - Add nose cone (vonKarman, conical, ogive, elliptical)
  - Add trapezoidal fins
  - Add parachute with trigger logic
  - Load custom drag curves (power-off, power-on)

**Design Pattern**: **Builder** - Progressive construction with method chaining

**Example**:
```python
motor = MotorBuilder(motor_config).build()
environment = EnvironmentBuilder(env_config).build()
rocket = RocketBuilder(rocket_config).build(motor)
```

### 4. Flight Simulation (`flight_simulator.py`)

**Purpose**: Execute single flight simulations and extract key metrics.

**Key Class**: `FlightSimulator`

**Workflow**:
1. **Initialize**: Accept `Rocket`, `Environment`, `SimulationConfig`
2. **Run Simulation**: Create `rocketpy.Flight` instance
   - 6-DOF trajectory integration
   - Rail-guided launch phase
   - Atmospheric flight with drag/thrust
   - Parachute deployment
   - Descent and impact
3. **Extract Metrics**: Parse flight object for key outputs
4. **Export Data**: Save trajectory data to CSV/JSON/KML

**Key Metrics Extracted**:
- **Apogee**: Maximum altitude (m)
- **Max Velocity**: Peak velocity magnitude (m/s)
- **Max Acceleration**: Peak acceleration (m/s²)
- **Flight Time**: Total time from liftoff to impact (s)
- **Impact Velocity**: Touchdown speed (m/s)
- **Lateral Drift**: Horizontal displacement from launch site (m)
- **Stability Margin**: Minimum static margin during flight (calibers)

**Integration Parameters**:
- `rtol`: Relative tolerance for ODE solver (default: 1e-6)
- `atol`: Absolute tolerance for ODE solver (default: 1e-9)
- Adaptive time stepping with `min_time_step` and `max_time_step`

### 5. Monte Carlo Analysis (`monte_carlo_runner.py`)

**Purpose**: Uncertainty quantification through parallel ensemble simulations.

**Key Class**: `MonteCarloRunner`

**Workflow**:
1. **Parameter Sampling**: Generate N parameter sets from uncertainty distributions
   - Normal distributions: `mean ± std`
   - Uniform distributions: `[min, max]`
   - Correlated parameters (if specified)
2. **Parallel Execution**: Run simulations using `ProcessPoolExecutor`
   - Multi-core parallelism (default: all available cores)
   - Progress tracking with `tqdm`
3. **Statistical Aggregation**:
   - Mean, median, std for each output metric
   - Percentiles (5th, 25th, 75th, 95th)
   - Min/max values
4. **Export**:
   - Save results as CSV/JSON
   - Export parameter/target matrices for sensitivity analysis
   - RocketPy-compatible `.inputs.txt` and `.outputs.txt` formats

**Parameter Variations**:
- Motor thrust variation (±thrust_std%)
- Mass uncertainties (dry mass, motor mass)
- Aerodynamic uncertainties (drag coefficient)
- Environmental uncertainties (wind, atmospheric density)
- Parachute deployment uncertainties (timing, Cd)

**Performance**:
- Typical: 100 simulations in ~30-60 seconds (8-core CPU)
- Scalable to 1000+ simulations for high-fidelity analysis

**Integration with Sensitivity Analysis**:
```python
# Export Monte Carlo results for sensitivity
params_df, targets_df = runner.export_for_sensitivity(
    parameter_names=['motor_thrust', 'dry_mass', 'wind_speed'],
    target_names=['apogee_m', 'max_velocity_ms', 'lateral_drift_m']
)

# Use in variance-based sensitivity
analyzer = VarianceBasedSensitivityAnalyzer()
analyzer.fit(params_df, targets_df)
```

### 6. Sensitivity Analysis

#### 6.1 Variance-Based Sensitivity (`variance_sensitivity.py`)

**Purpose**: Statistical sensitivity analysis using multiple linear regression.

**Key Class**: `VarianceBasedSensitivityAnalyzer`

**Mathematical Foundation**:

The sensitivity coefficient for parameter `j` on target `y` is:

```
S_j = 100 * (β_j² * σ_j²) / (σ_ε² + Σ_k(σ_k² * β_k²))
```

Where:
- `β_j`: Standardized regression coefficient for parameter `j`
- `σ_j`: Standard deviation of parameter `j`
- `σ_ε`: Residual standard error (model error)

**Linear Approximation Error (LAE)**:

```
LAE = 100 * σ_ε² / (σ_ε² + Σ_k(σ_k² * β_k²))
```

- LAE < 5%: Excellent linear approximation
- LAE < 10%: Good linear approximation
- LAE > 20%: Poor linear approximation (use cautiously)

**Workflow**:
1. **Fit Regression Model**: OLS regression using `statsmodels`
2. **Calculate Sensitivities**: Variance decomposition
3. **Validate**: Check LAE to ensure linear model adequacy
4. **Filter**: Identify parameters with sensitivity > LAE (significant parameters)
5. **Visualize**: Bar charts with LAE threshold line

**Interpretation**:
- **S_j = 50%**: Parameter `j` contributes 50% of output variance
- **Σ S_j ≈ 100% - LAE**: Sum of sensitivities approaches 100% for good models
- **S_j < LAE**: Parameter is not significant (noise-level contribution)

**Example**:
```python
analyzer = VarianceBasedSensitivityAnalyzer()
analyzer.fit(parameters_df, targets_df)

# Get sensitivity coefficients
sensitivities = analyzer.get_sensitivity_coefficients()
print(f"Motor thrust → Apogee: {sensitivities['motor_thrust']['apogee_m']:.1f}%")

# Validate linear approximation
lae = analyzer.get_linear_approximation_error()
if lae['apogee_m'] < 10:
    print("✓ Linear model is adequate")

# Filter significant parameters
sig_params = analyzer.get_significant_parameters(target='apogee_m')
```

#### 6.2 OAT Sensitivity (`sensitivity_analyzer.py`)

**Purpose**: Local sensitivity screening using One-At-a-Time (OAT) method.

**Key Class**: `OATSensitivityAnalyzer`

**Method**:
- Evaluate `2N+1` simulations (N = number of parameters)
- Baseline simulation + 2 variations per parameter (±δ)
- Calculate local derivatives: `∂y/∂x ≈ (y(x+δ) - y(x-δ)) / (2δ)`

**Use Cases**:
- Quick parameter screening before full Monte Carlo
- Identify most influential parameters for detailed study
- Validate variance-based results
- Design of experiments (DOE) for parameter range selection

**Comparison with Variance-Based**:

| Aspect                | OAT                  | Variance-Based        |
|-----------------------|----------------------|-----------------------|
| Simulations Required  | 2N+1                 | 100-1000+             |
| Sensitivity Type      | Local (derivatives)  | Global (variance)     |
| Interaction Effects   | Not captured         | Captured implicitly   |
| Computational Cost    | Low                  | High                  |
| Best For              | Quick screening      | Comprehensive analysis|

**Recommendation**: Use OAT for initial exploration, then variance-based for final analysis.

### 7. Visualization (`visualizer.py`)

**Purpose**: Generate publication-quality plots for simulation results.

**Key Class**: `Visualizer`

**Plot Types**:
1. **3D Trajectory**: Flight path in 3D space (East-North-Altitude)
2. **Altitude Profile**: Altitude vs. time with apogee marker
3. **Velocity Profile**: Velocity components vs. time
4. **Acceleration Profile**: Acceleration vs. time (with max-g marker)
5. **Monte Carlo Dispersion**: Scatter plots of landing ellipses
6. **Sensitivity Bar Charts**: Ranked parameter sensitivities with LAE line

**Customization**:
- Figure size, DPI, color schemes
- Grid styles, axis labels, legends
- Export formats: PNG, PDF, SVG

**Example**:
```python
visualizer = Visualizer()
visualizer.plot_trajectory_3d(flight.x, flight.y, flight.z)
visualizer.plot_altitude(flight.time, flight.z)
visualizer.save_figure('outputs/altitude_profile.png', dpi=300)
```

### 8. Data Export (`data_handler.py`)

**Purpose**: Export simulation results in multiple formats.

**Supported Formats**:
- **CSV**: Trajectory time series, summary statistics
- **JSON**: Structured data with metadata
- **KML**: Google Earth visualization (3D flight paths)
- **RocketPy .txt**: Compatible with RocketPy's MonteCarlo class
  - `.inputs.txt`: Parameter matrix
  - `.outputs.txt`: Target matrix

**Key Functions**:
- `export_to_csv()`: Save trajectory data
- `export_to_json()`: Save flight summary with config
- `export_to_kml()`: Generate Google Earth file
- `save_monte_carlo_data()`: RocketPy-compatible format

---

## Data Flow

### Single Flight Simulation

```
YAML Config → ConfigLoader → Dataclasses
                ↓
        Validators (check plausibility)
                ↓
    ┌───────────┼───────────┐
    ▼           ▼           ▼
MotorBuilder  EnvBuilder  RocketBuilder
    │           │           │
    ▼           ▼           ▼
  Motor    Environment   Rocket
    └───────────┼───────────┘
                ▼
        FlightSimulator.run()
                ↓
          RocketPy Flight
                ↓
          Extract Metrics
                ↓
      ┌─────────┴─────────┐
      ▼                   ▼
 Visualizer          DataHandler
      │                   │
      ▼                   ▼
   Plots               CSV/JSON/KML
```

### Monte Carlo Pipeline

```
Base Config + Uncertainties → MonteCarloRunner
                ↓
    Generate N parameter sets (sampling)
                ↓
    Parallel execution (ProcessPoolExecutor)
        ┌───────┼───────┐
        ▼       ▼       ▼
     Flight  Flight  Flight ... (N simulations)
        └───────┼───────┘
                ▼
    Aggregate results (mean, std, percentiles)
                ↓
      ┌─────────┴─────────┐
      ▼                   ▼
Export Dispersion    Export for Sensitivity
  (CSV/JSON)         (.inputs.txt, .outputs.txt)
                            ↓
                  VarianceBasedSensitivityAnalyzer
                            ↓
                  Sensitivity Coefficients + LAE
                            ↓
                      Bar Charts + Reports
```

### Sensitivity Analysis Pipeline

```
Monte Carlo Results → Load data (sensitivity_utils.py)
                ↓
    Parameters DataFrame + Targets DataFrame
                ↓
    VarianceBasedSensitivityAnalyzer.fit()
                ↓
        Multiple Linear Regression (OLS)
                ↓
    Extract β coefficients and σ values
                ↓
    Calculate Sensitivity Coefficients (S_j)
                ↓
    Calculate Linear Approximation Error (LAE)
                ↓
        Validate: LAE < 10%?
                ↓
    Filter significant parameters (S_j > LAE)
                ↓
      ┌─────────┴─────────┐
      ▼                   ▼
  Bar Charts          Predictions + Intervals
```

---

## Design Patterns

### 1. Builder Pattern

**Usage**: `MotorBuilder`, `EnvironmentBuilder`, `RocketBuilder`

**Purpose**: Progressive construction of complex RocketPy objects

**Benefits**:
- Separates configuration from construction logic
- Enables method chaining for fluent API
- Encapsulates RocketPy API details
- Allows validation at build time

**Example**:
```python
rocket = (RocketBuilder(config)
    .add_motor(motor)
    .add_nose_cone()
    .add_fins()
    .add_parachute()
    .build())
```

### 2. Factory Pattern

**Usage**: `ConfigLoader`

**Purpose**: Create configuration objects from YAML files

**Benefits**:
- Centralized object creation
- Type safety with dataclasses
- Validation at creation time
- Decouples file format from object structure

### 3. Strategy Pattern

**Usage**: Sensitivity analysis methods (OAT vs. Variance-Based)

**Purpose**: Interchangeable algorithms for sensitivity analysis

**Benefits**:
- Easy to add new methods (e.g., Sobol indices, Morris screening)
- Client code agnostic to analysis method
- Consistent interface across methods

### 4. Dependency Injection

**Usage**: Throughout (e.g., `FlightSimulator(rocket, environment, config)`)

**Purpose**: Loose coupling between components

**Benefits**:
- Testability (easy to mock dependencies)
- Flexibility (swap implementations)
- Clear dependencies in constructor signatures

### 5. Facade Pattern

**Usage**: `MonteCarloRunner` wraps parallel execution complexity

**Purpose**: Simplify complex subsystem (parallel execution, sampling, aggregation)

**Benefits**:
- Simple API for users
- Hides parallelization details
- Manages shared state safely

---

## Module Reference

### Core Modules

| Module | Purpose | Key Classes | LOC |
|--------|---------|-------------|-----|
| `config_loader.py` | Configuration loading | ConfigLoader, 11 dataclasses | 500 |
| `validators.py` | Validation logic | RocketValidator, MotorValidator | 650 |
| `motor_builder.py` | Motor construction | MotorBuilder | 310 |
| `environment_setup.py` | Environment construction | EnvironmentBuilder | 390 |
| `rocket_builder.py` | Rocket construction | RocketBuilder | 450 |
| `flight_simulator.py` | Flight execution | FlightSimulator | 420 |
| `monte_carlo_runner.py` | Monte Carlo analysis | MonteCarloRunner | 690 |
| `variance_sensitivity.py` | Variance-based sensitivity | VarianceBasedSensitivityAnalyzer | 820 |
| `sensitivity_analyzer.py` | OAT sensitivity | OATSensitivityAnalyzer | 455 |
| `sensitivity_utils.py` | Sensitivity utilities | Helper functions | 475 |
| `visualizer.py` | Plotting | Visualizer | 490 |
| `data_handler.py` | Data export | DataHandler | 455 |
| `utils.py` | General utilities | Helper functions | 230 |

### Support Files

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `configs/` | Configuration files | YAML configurations for rockets, environments |
| `data/motors/` | Motor data | .eng thrust curve files |
| `data/atmospheric/` | Atmospheric data | Custom atmospheric profiles |
| `scripts/` | CLI scripts | run_single.py, run_monte_carlo.py, run_sensitivity.py |
| `tests/` | Unit & integration tests | 150+ test cases |
| `notebooks/` | Jupyter tutorials | 4 comprehensive tutorials |
| `outputs/` | Simulation results | Generated plots, CSV, JSON, KML |

---

## Extension Points

### Adding New Motor Types

1. **Create Configuration**: Add `HybridMotorConfig` or `LiquidMotorConfig` dataclass
2. **Extend Builder**: Add `HybridMotorBuilder` class
3. **Update Validator**: Add `HybridMotorValidator` for type-specific checks
4. **Update ConfigLoader**: Handle new motor type in `get_motor_config()`

**Example**:
```python
@dataclass
class LiquidMotorConfig:
    type: str = "LiquidMotor"
    oxidizer_tank: TankConfig
    fuel_tank: TankConfig
    injector: InjectorConfig
    # ... liquid-specific parameters

class LiquidMotorBuilder:
    def build(self) -> LiquidMotor:
        motor = LiquidMotor(...)
        motor.add_tank(oxidizer_tank)
        motor.add_tank(fuel_tank)
        # ...
        return motor
```

### Adding New Components (e.g., Air Brakes, Rail Buttons)

1. **Configuration**: Add `AirBrakesConfig` dataclass
2. **Validator**: Add validation rules (e.g., position, size constraints)
3. **Builder Integration**: Add `RocketBuilder.add_air_brakes()` method
4. **Tests**: Add unit tests for new component

**Example**:
```python
@dataclass
class AirBrakesConfig:
    enabled: bool = True
    drag_coefficient: float = 1.5
    reference_area_m2: float = 0.01
    position_m: float = -0.5
    controller: Optional[ControllerConfig] = None

class RocketBuilder:
    def add_air_brakes(self) -> 'RocketBuilder':
        if self.config.air_brakes is None:
            return self

        self.rocket.add_air_brakes(
            drag_coefficient=self.config.air_brakes.drag_coefficient,
            reference_area=self.config.air_brakes.reference_area_m2,
            position=self.config.air_brakes.position_m,
        )
        return self
```

### Adding New Sensitivity Methods (e.g., Sobol Indices)

1. **Create Analyzer**: Implement `SobolSensitivityAnalyzer` class
2. **Interface Consistency**: Match `fit()`, `get_sensitivity_coefficients()` API
3. **Utilities**: Add Sobol-specific utilities to `sensitivity_utils.py`
4. **CLI Integration**: Add `--method sobol` to `run_sensitivity.py`

**Example**:
```python
class SobolSensitivityAnalyzer:
    def fit(self, parameters: pd.DataFrame, targets: pd.DataFrame):
        """Compute Sobol indices using saltelli sampling."""
        # Generate Saltelli sample matrices
        # Compute first-order and total-order indices
        # Store results
        pass

    def get_first_order_indices(self) -> Dict[str, Dict[str, float]]:
        """Return S_i (first-order Sobol indices)."""
        pass

    def get_total_order_indices(self) -> Dict[str, Dict[str, float]]:
        """Return S_Ti (total-order indices)."""
        pass
```

### Adding New Visualization Types

1. **Extend Visualizer**: Add new plotting methods
2. **Styling**: Use existing color schemes and layout conventions
3. **Export**: Support PNG, PDF, SVG formats

**Example**:
```python
class Visualizer:
    def plot_energy_diagram(self, flight: Flight) -> None:
        """Plot kinetic and potential energy over time."""
        time = flight.time
        ke = 0.5 * flight.rocket.mass * flight.speed**2
        pe = flight.rocket.mass * 9.81 * flight.z

        plt.figure(figsize=(10, 6))
        plt.plot(time, ke, label='Kinetic Energy')
        plt.plot(time, pe, label='Potential Energy')
        plt.plot(time, ke + pe, label='Total Energy', linestyle='--')
        plt.xlabel('Time (s)')
        plt.ylabel('Energy (J)')
        plt.legend()
        plt.grid(True)
```

---

## Configuration System

### YAML Structure

```yaml
rocket:
  name: "MyRocket"
  dry_mass_kg: 15.0
  inertia:
    ixx_kg_m2: 6.32
    iyy_kg_m2: 6.32
    izz_kg_m2: 0.034
  geometry:
    caliber_m: 0.127
    length_m: 2.0
  cg_location_m: 1.2
  # ... more rocket parameters

motor:
  type: "SolidMotor"
  thrust_source: "data/motors/Cesaroni_M1670.eng"
  # ... more motor parameters

environment:
  latitude_deg: 39.3897
  longitude_deg: -8.2889
  elevation_m: 100.0
  wind:
    velocity_ms: 5.0
    direction_deg: 90.0

simulation:
  rail:
    length_m: 5.0
    inclination_deg: 85.0
    heading_deg: 0.0
  rtol: 1.0e-6
  atol: 1.0e-9

monte_carlo:
  num_simulations: 100
  variations:
    motor_thrust_std_pct: 5.0
    dry_mass_std_kg: 0.5
    wind_speed_std_ms: 2.0
```

### Configuration Flow

```
YAML File → yaml.load() → Dict
    ↓
ConfigLoader._create_*_config() → Dataclass instances
    ↓
Validators.validate() → Raise ValueError if invalid
    ↓
Builders.build() → RocketPy objects
```

### Type Safety Guarantees

- All configurations are **dataclasses** with type hints
- **mypy** static type checking passes with zero errors
- **Runtime validation** at configuration load time
- **IDE autocomplete** for all configuration attributes

---

## Testing Architecture

### Test Structure

```
tests/
├── test_config_loader.py         # Configuration loading & validation
├── test_motor_builder.py         # Motor construction
├── test_environment_setup.py     # Environment construction
├── test_rocket_builder.py        # Rocket construction
├── test_flight_simulator.py      # Flight simulation
├── test_monte_carlo_runner.py    # Monte Carlo analysis
├── test_variance_sensitivity.py  # Variance-based sensitivity
├── test_sensitivity_analyzer.py  # OAT sensitivity
├── test_visualizer.py            # Plotting functions
├── test_data_handler.py          # Data export
└── test_validators.py            # Validation logic
```

### Test Coverage

- **Unit Tests**: 120+ tests (individual module functions)
- **Integration Tests**: 30+ tests (end-to-end workflows)
- **Total Coverage**: ~90% code coverage
- **Test Execution**: ~10 seconds for full suite

### Testing Patterns

1. **Fixture-Based Setup**: `@pytest.fixture` for reusable configurations
2. **Parameterized Tests**: `@pytest.mark.parametrize` for multiple scenarios
3. **Mock External Dependencies**: Mock RocketPy objects for isolated testing
4. **Regression Tests**: Verify consistent outputs for known inputs
5. **Property-Based Testing**: Use `hypothesis` for edge cases (planned)

**Example**:
```python
@pytest.fixture
def simple_rocket_config():
    return RocketConfig(
        name="TestRocket",
        dry_mass_kg=15.0,
        inertia=InertiaConfig(6.32, 6.32, 0.034),
        geometry=GeometryConfig(0.127, 2.0),
        cg_location_m=1.2,
    )

def test_rocket_builder_creates_valid_rocket(simple_rocket_config, motor):
    builder = RocketBuilder(simple_rocket_config)
    rocket = builder.build(motor)

    assert rocket is not None
    assert rocket.mass > 0
    assert rocket.radius == simple_rocket_config.radius_m
```

### Continuous Integration

**Planned**:
- GitHub Actions for automated testing on push
- Codecov for coverage reporting
- Pre-commit hooks for linting (black, flake8, mypy)

---

## Performance Considerations

### Computational Complexity

| Operation | Complexity | Typical Time |
|-----------|------------|--------------|
| Single Flight | O(N_timesteps) | 0.5-1 second |
| Monte Carlo (N=100) | O(N × N_timesteps) | 30-60 seconds |
| Variance Sensitivity | O(N × P + P²) | <1 second (post-MC) |
| OAT Sensitivity | O(2P × N_timesteps) | 10-30 seconds |

Where:
- `N_timesteps`: Typically 1000-10000 (adaptive)
- `N`: Number of Monte Carlo simulations
- `P`: Number of varied parameters

### Optimization Strategies

1. **Parallel Execution**: Monte Carlo uses all CPU cores
2. **Efficient Sampling**: NumPy vectorized operations
3. **Lazy Evaluation**: Only compute requested metrics
4. **Caching**: Reuse atmospheric model calculations (via RocketPy)

### Scalability

- **Single Flight**: Scales with integration complexity (O(N_timesteps))
- **Monte Carlo**: Scales linearly with cores (near-perfect parallelization)
- **Sensitivity Analysis**: Scales with parameter count (O(P²) for regression)

**Benchmark** (8-core Intel i7, 16GB RAM):
- 100 MC simulations: ~40 seconds
- 1000 MC simulations: ~6 minutes
- Variance sensitivity (100 sims, 10 params): <1 second

---

## Security Considerations

### Input Validation

- **YAML Safety**: Use `yaml.safe_load()` to prevent arbitrary code execution
- **Path Validation**: Sanitize file paths to prevent directory traversal
- **Numeric Ranges**: Validate all parameters are within physical bounds
- **File Existence**: Check data files exist before simulation

### Dependency Management

- **Pinned Versions**: `requirements.txt` specifies exact versions
- **Known Vulnerabilities**: Regularly check with `pip-audit`
- **Minimal Dependencies**: Only essential libraries included

### Data Privacy

- **No External Calls**: No network requests or telemetry
- **Local Execution**: All computations run locally
- **No PII**: Configuration files contain no personal information

---

## Future Architecture Enhancements

### Planned Additions

1. **Plugin System**: Allow third-party extensions via entry points
2. **Event System**: Publish-subscribe for simulation events (e.g., apogee detected)
3. **Optimization Framework**: Integrate with `scipy.optimize` for design optimization
4. **Web API**: FastAPI-based REST API for remote simulations
5. **Database Backend**: Store simulation results in SQLite/PostgreSQL
6. **Distributed Computing**: Celery for distributed Monte Carlo across machines

### Refactoring Opportunities

1. **Abstract Factory**: Generalize motor/environment builders for all types
2. **Observer Pattern**: Real-time simulation monitoring and callbacks
3. **Command Pattern**: Undo/redo for configuration changes
4. **Memento Pattern**: Save/restore simulation state for restarts

---

## References

- **RocketPy Documentation**: https://docs.rocketpy.org/
- **Clean Architecture**: Martin, Robert C. "Clean Architecture." Prentice Hall, 2017.
- **Design Patterns**: Gamma et al. "Design Patterns: Elements of Reusable Object-Oriented Software." Addison-Wesley, 1994.
- **Variance-Based Sensitivity**: Saltelli et al. "Global Sensitivity Analysis: The Primer." Wiley, 2008.
