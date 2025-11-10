# API Reference

Complete API documentation for the Rocket Simulation Framework.

## Table of Contents

1. [Configuration Module](#configuration-module)
2. [Validation Module](#validation-module)
3. [Builder Modules](#builder-modules)
4. [Simulation Module](#simulation-module)
5. [Monte Carlo Module](#monte-carlo-module)
6. [Sensitivity Analysis Modules](#sensitivity-analysis-modules)
7. [Visualization Module](#visualization-module)
8. [Data Handler Module](#data-handler-module)
9. [Utilities Module](#utilities-module)

---

## Configuration Module

**Module**: `src.config_loader`

**Purpose**: Load and manage YAML configuration files with type-safe dataclass objects.

### ConfigLoader

Main configuration loader class.

```python
class ConfigLoader:
    """Load and manage YAML configuration files."""
```

#### Methods

##### `__init__()`

```python
def __init__(self) -> None
```

Initialize ConfigLoader with empty configuration dictionaries.

**Example**:
```python
loader = ConfigLoader()
```

---

##### `load_from_yaml()`

```python
def load_from_yaml(self, config_path: Union[str, Path]) -> None
```

Load configuration from YAML file.

**Parameters**:
- `config_path` (str | Path): Path to YAML configuration file

**Raises**:
- `FileNotFoundError`: If config file does not exist
- `yaml.YAMLError`: If YAML is malformed
- `ValueError`: If configuration validation fails

**Example**:
```python
loader = ConfigLoader()
loader.load_from_yaml('configs/simple_rocket.yaml')
```

---

##### `get_rocket_config()`

```python
def get_rocket_config(self) -> RocketConfig
```

Get rocket configuration dataclass.

**Returns**:
- `RocketConfig`: Rocket configuration object

**Raises**:
- `ValueError`: If rocket configuration not loaded

**Example**:
```python
rocket_config = loader.get_rocket_config()
print(f"Rocket: {rocket_config.name}")
```

---

##### `get_motor_config()`

```python
def get_motor_config(self) -> MotorConfig
```

Get motor configuration dataclass.

**Returns**:
- `MotorConfig`: Motor configuration object

**Raises**:
- `ValueError`: If motor configuration not loaded

---

##### `get_environment_config()`

```python
def get_environment_config(self) -> EnvironmentConfig
```

Get environment configuration dataclass.

**Returns**:
- `EnvironmentConfig`: Environment configuration object

**Raises**:
- `ValueError`: If environment configuration not loaded

---

##### `get_simulation_config()`

```python
def get_simulation_config(self) -> SimulationConfig
```

Get simulation configuration dataclass.

**Returns**:
- `SimulationConfig`: Simulation configuration object with default values if not specified

---

##### `get_monte_carlo_config()`

```python
def get_monte_carlo_config(self) -> Optional[MonteCarloConfig]
```

Get Monte Carlo configuration dataclass.

**Returns**:
- `MonteCarloConfig | None`: Monte Carlo configuration if specified, else None

---

### Configuration Dataclasses

#### InertiaConfig

```python
@dataclass
class InertiaConfig:
    """Rocket inertia tensor configuration."""
    ixx_kg_m2: float  # Inertia about x-axis (kg·m²)
    iyy_kg_m2: float  # Inertia about y-axis (kg·m²)
    izz_kg_m2: float  # Inertia about z-axis (kg·m²)

    def to_tuple(self) -> Tuple[float, float, float]:
        """Return inertia as tuple for RocketPy API."""
```

**Example**:
```python
inertia = InertiaConfig(ixx_kg_m2=6.32, iyy_kg_m2=6.32, izz_kg_m2=0.034)
print(inertia.to_tuple())  # (6.32, 6.32, 0.034)
```

---

#### GeometryConfig

```python
@dataclass
class GeometryConfig:
    """Rocket geometry configuration."""
    caliber_m: float  # Rocket diameter (m)
    length_m: float   # Total length (m)
```

---

#### FinConfig

```python
@dataclass
class FinConfig:
    """Fin configuration."""
    count: int                      # Number of fins (typically 3 or 4)
    root_chord_m: float            # Root chord length (m)
    tip_chord_m: float             # Tip chord length (m)
    span_m: float                  # Fin span from body to tip (m)
    thickness_m: float             # Fin thickness (m)
    position_m: float = 0.0        # Position from nose (m)
    cant_angle_deg: float = 0.0    # Cant angle for spin (degrees)
    airfoil: Optional[str] = None  # Airfoil type (e.g., 'NACA0012')
```

**Example**:
```python
fins = FinConfig(
    count=4,
    root_chord_m=0.12,
    tip_chord_m=0.06,
    span_m=0.10,
    thickness_m=0.003,
    position_m=1.8,
)
```

---

#### NoseConeConfig

```python
@dataclass
class NoseConeConfig:
    """Nose cone configuration."""
    length_m: float              # Nose cone length (m)
    kind: str = "vonKarman"      # Shape: vonKarman, conical, ogive, elliptical
    position_m: float = 0.0      # Position from reference point (m)
```

**Valid `kind` values**:
- `"vonKarman"`: Von Kármán nose cone (lowest drag)
- `"conical"`: Conical nose cone
- `"ogive"`: Ogive nose cone
- `"elliptical"`: Elliptical nose cone

---

#### ParachuteConfig

```python
@dataclass
class ParachuteConfig:
    """Parachute configuration."""
    enabled: bool = True                              # Enable parachute
    name: str = "Main"                               # Parachute name
    cd_s: float = 10.0                               # Drag coeff × area (m²)
    trigger: Union[str, float] = "apogee"            # Trigger: "apogee" or altitude (m)
    sampling_rate_hz: float = 105.0                  # Sensor sampling rate (Hz)
    lag_s: float = 1.5                               # Deployment lag time (s)
    noise_std: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Sensor noise (x,y,z)
```

**Example**:
```python
# Apogee trigger
main_chute = ParachuteConfig(
    name="Main",
    cd_s=10.0,
    trigger="apogee",
    lag_s=1.5,
)

# Altitude trigger at 500m
drogue = ParachuteConfig(
    name="Drogue",
    cd_s=1.0,
    trigger=500.0,  # Deploy at 500m AGL
    lag_s=0.5,
)
```

---

#### RocketConfig

```python
@dataclass
class RocketConfig:
    """Complete rocket configuration."""
    name: str                                      # Rocket name
    dry_mass_kg: float                            # Dry mass without motor (kg)
    inertia: InertiaConfig                        # Inertia tensor
    geometry: GeometryConfig                      # Geometry (caliber, length)
    cg_location_m: float                          # CG from nose (m)
    cp_location_m: Optional[float] = None         # CP from nose (m), can be computed
    nose_cone: Optional[NoseConeConfig] = None    # Nose cone configuration
    fins: Optional[FinConfig] = None              # Fin configuration
    parachute: Optional[ParachuteConfig] = None   # Parachute configuration
    power_off_drag: Optional[str] = None          # Path to drag curve file
    power_on_drag: Optional[str] = None           # Path to drag curve file
    coordinate_system: str = "tail_to_nose"       # Coordinate system

    @property
    def radius_m(self) -> float:
        """Return rocket radius in meters."""

    @property
    def static_margin_calibers(self) -> Optional[float]:
        """Calculate static margin in calibers: (CP - CG) / caliber."""
```

**Example**:
```python
rocket_config = RocketConfig(
    name="Calisto",
    dry_mass_kg=15.426,
    inertia=InertiaConfig(6.32, 6.32, 0.034),
    geometry=GeometryConfig(caliber_m=0.127, length_m=2.0),
    cg_location_m=1.267,
    cp_location_m=1.456,
    nose_cone=nose_cone_config,
    fins=fins_config,
    parachute=parachute_config,
)

print(f"Static margin: {rocket_config.static_margin_calibers:.2f} calibers")
```

---

#### MotorConfig

```python
@dataclass
class MotorConfig:
    """Motor configuration."""
    type: str = "SolidMotor"                           # Motor type
    thrust_source: str = ""                            # Path to .eng file
    dry_mass_kg: float = 1.5                          # Dry motor mass (kg)
    dry_inertia: Tuple[float, float, float] = (...)   # Dry inertia tensor
    nozzle_radius_m: float = 0.033                    # Nozzle exit radius (m)
    grain_number: int = 5                              # Number of grains
    grain_density_kg_m3: float = 1815.0               # Propellant density (kg/m³)
    grain_outer_radius_m: float = 0.033               # Grain outer radius (m)
    grain_initial_inner_radius_m: float = 0.015       # Initial bore radius (m)
    grain_initial_height_m: float = 0.120             # Grain height (m)
    grain_separation_m: float = 0.005                 # Gap between grains (m)
    grains_center_of_mass_position_m: float = -0.85  # Grains CG position (m)
    center_of_dry_mass_position_m: float = 0.317     # Dry motor CG (m)
    nozzle_position_m: float = 0.0                    # Nozzle position (m)
    burn_time_s: Optional[float] = None               # Burn time (s), computed if None
    throat_radius_m: float = 0.011                    # Nozzle throat radius (m)
    position_m: float = -1.373                        # Motor position on rocket (m)
```

**Example**:
```python
motor_config = MotorConfig(
    type="SolidMotor",
    thrust_source="data/motors/Cesaroni_M1670.eng",
    dry_mass_kg=1.815,
    grain_number=5,
    position_m=-1.373,
)
```

---

#### WindConfig

```python
@dataclass
class WindConfig:
    """Wind configuration."""
    model: str = "constant"       # Model: constant, function, custom
    velocity_ms: float = 0.0      # Wind speed (m/s)
    direction_deg: float = 0.0    # Direction (meteorological: 0=N, 90=E)
```

**Wind direction convention**:
- 0° = North (wind from north)
- 90° = East (wind from east)
- 180° = South (wind from south)
- 270° = West (wind from west)

---

#### EnvironmentConfig

```python
@dataclass
class EnvironmentConfig:
    """Environment configuration."""
    latitude_deg: float                                # Latitude (degrees)
    longitude_deg: float                               # Longitude (degrees)
    elevation_m: float = 0.0                          # Launch site elevation (m)
    atmospheric_model: str = "standard_atmosphere"     # Atmosphere model
    atmospheric_model_file: Optional[str] = None      # Custom atmosphere file
    date: Optional[Tuple[int, int, int, int]] = None  # (year, month, day, hour_UTC)
    wind: WindConfig = field(default_factory=WindConfig)  # Wind configuration
    gravity_ms2: float = 9.80665                      # Gravity (m/s²)
    max_expected_height_m: float = 10000.0            # Max altitude (m)
```

**Valid `atmospheric_model` values**:
- `"standard_atmosphere"`: ISA standard atmosphere
- `"custom"`: Custom atmospheric profile from file

**Example**:
```python
env_config = EnvironmentConfig(
    latitude_deg=39.3897,
    longitude_deg=-8.2889,
    elevation_m=100.0,
    date=(2024, 6, 15, 12),  # June 15, 2024, 12:00 UTC
    wind=WindConfig(velocity_ms=5.0, direction_deg=90.0),
)
```

---

#### RailConfig

```python
@dataclass
class RailConfig:
    """Launch rail configuration."""
    length_m: float = 5.0           # Rail length (m)
    inclination_deg: float = 85.0   # Inclination from horizontal (degrees)
    heading_deg: float = 0.0        # Azimuth heading (0=N, 90=E)
```

---

#### SimulationConfig

```python
@dataclass
class SimulationConfig:
    """Simulation parameters."""
    rail: RailConfig = field(default_factory=RailConfig)  # Rail configuration
    terminate_on_apogee: bool = False      # Stop simulation at apogee
    max_time_s: float = 600.0              # Maximum simulation time (s)
    max_time_step_s: float = 1.0           # Max ODE solver time step (s)
    min_time_step_s: float = 0.01          # Min ODE solver time step (s)
    rtol: float = 1e-6                     # Relative tolerance for ODE solver
    atol: float = 1e-9                     # Absolute tolerance for ODE solver
    verbose: bool = False                  # Enable verbose RocketPy output
```

**Integration parameters**:
- `rtol`: Relative tolerance (1e-6 = 0.0001% accuracy)
- `atol`: Absolute tolerance (1e-9 for high precision)
- Lower tolerances = higher accuracy but slower simulation

---

#### MonteCarloConfig

```python
@dataclass
class MonteCarloConfig:
    """Monte Carlo analysis configuration."""
    num_simulations: int = 100         # Number of simulations
    seed: Optional[int] = None         # Random seed for reproducibility
    variations: Dict[str, float] = field(default_factory=dict)  # Parameter variations
```

**Example**:
```python
mc_config = MonteCarloConfig(
    num_simulations=500,
    seed=42,  # For reproducible results
    variations={
        'motor_thrust_std_pct': 5.0,      # ±5% thrust variation
        'dry_mass_std_kg': 0.5,           # ±0.5 kg mass variation
        'wind_speed_std_ms': 2.0,         # ±2 m/s wind variation
        'cg_location_std_m': 0.05,        # ±5 cm CG variation
    }
)
```

---

## Validation Module

**Module**: `src.validators`

**Purpose**: Validate configuration objects for physical plausibility and consistency.

### RocketValidator

```python
class RocketValidator:
    """Validator for rocket configurations."""
```

#### Methods

##### `validate()`

```python
@staticmethod
def validate(config: RocketConfig) -> None
```

Validate rocket configuration.

**Parameters**:
- `config` (RocketConfig): Rocket configuration to validate

**Raises**:
- `ValueError`: If configuration is invalid with detailed error message

**Checks**:
- Positive mass and inertia
- Reasonable geometry (caliber 0.05-0.5 m, length 0.5-10 m)
- Static margin > 0 (stable rocket)
- CG and CP within rocket length
- Fin geometry consistency

**Example**:
```python
from src.validators import RocketValidator

try:
    RocketValidator.validate(rocket_config)
    print("✓ Rocket configuration valid")
except ValueError as e:
    print(f"✗ Validation failed: {e}")
```

---

### MotorValidator

```python
class MotorValidator:
    """Validator for motor configurations."""
```

##### `validate()`

```python
@staticmethod
def validate(config: MotorConfig) -> None
```

Validate motor configuration.

**Parameters**:
- `config` (MotorConfig): Motor configuration to validate

**Raises**:
- `ValueError`: If configuration is invalid

**Checks**:
- Thrust source file exists
- Positive masses and dimensions
- Grain geometry consistency (inner < outer radius)
- Reasonable propellant density (1000-2500 kg/m³)
- Nozzle throat < exit radius

---

### EnvironmentValidator

```python
class EnvironmentValidator:
    """Validator for environment configurations."""
```

##### `validate()`

```python
@staticmethod
def validate(config: EnvironmentConfig) -> None
```

Validate environment configuration.

**Parameters**:
- `config` (EnvironmentConfig): Environment configuration to validate

**Raises**:
- `ValueError`: If configuration is invalid

**Checks**:
- Valid latitude (-90 to 90°) and longitude (-180 to 180°)
- Reasonable elevation (-500 to 10000 m)
- Positive wind speed
- Valid wind direction (0-360°)
- Date format (if specified)
- Atmospheric model file exists (if custom)

---

### SimulationValidator

```python
class SimulationValidator:
    """Validator for simulation configurations."""
```

##### `validate()`

```python
@staticmethod
def validate(config: SimulationConfig) -> None
```

Validate simulation configuration.

**Parameters**:
- `config` (SimulationConfig): Simulation configuration to validate

**Raises**:
- `ValueError`: If configuration is invalid

**Checks**:
- Positive rail length
- Valid inclination (0-90°)
- Valid heading (0-360°)
- Positive time limits
- max_time_step > min_time_step
- Reasonable tolerances (rtol, atol > 0)

---

## Builder Modules

### MotorBuilder

**Module**: `src.motor_builder`

```python
class MotorBuilder:
    """Builder for RocketPy SolidMotor instances."""
```

#### Methods

##### `__init__()`

```python
def __init__(self, config: MotorConfig) -> None
```

Initialize MotorBuilder.

**Parameters**:
- `config` (MotorConfig): Motor configuration

**Raises**:
- `ImportError`: If RocketPy is not installed

---

##### `build()`

```python
def build(self) -> SolidMotor
```

Build and return SolidMotor instance.

**Returns**:
- `SolidMotor`: Configured RocketPy SolidMotor object

**Raises**:
- `FileNotFoundError`: If thrust curve file does not exist
- `ValueError`: If motor type is not supported

**Example**:
```python
from src.motor_builder import MotorBuilder

motor_config = MotorConfig(
    thrust_source="data/motors/Cesaroni_M1670.eng",
    dry_mass_kg=1.815,
)

builder = MotorBuilder(motor_config)
motor = builder.build()

print(f"Total impulse: {motor.total_impulse:.0f} N·s")
print(f"Burn time: {motor.burn_time:.1f} s")
```

---

### EnvironmentBuilder

**Module**: `src.environment_setup`

```python
class EnvironmentBuilder:
    """Builder for RocketPy Environment instances."""
```

#### Methods

##### `__init__()`

```python
def __init__(self, config: EnvironmentConfig) -> None
```

Initialize EnvironmentBuilder.

**Parameters**:
- `config` (EnvironmentConfig): Environment configuration

---

##### `build()`

```python
def build(self) -> Environment
```

Build and return Environment instance.

**Returns**:
- `Environment`: Configured RocketPy Environment object

**Raises**:
- `FileNotFoundError`: If atmospheric model file does not exist
- `ValueError`: If configuration is invalid

**Example**:
```python
from src.environment_setup import EnvironmentBuilder

env_config = EnvironmentConfig(
    latitude_deg=39.3897,
    longitude_deg=-8.2889,
    elevation_m=100.0,
    wind=WindConfig(velocity_ms=5.0, direction_deg=90.0),
)

builder = EnvironmentBuilder(env_config)
environment = builder.build()

print(f"Location: ({environment.latitude}°, {environment.longitude}°)")
print(f"Elevation: {environment.elevation} m")
```

---

### RocketBuilder

**Module**: `src.rocket_builder`

```python
class RocketBuilder:
    """Builder for RocketPy Rocket instances."""
```

#### Methods

##### `__init__()`

```python
def __init__(self, config: RocketConfig, motor: Optional[SolidMotor] = None) -> None
```

Initialize RocketBuilder.

**Parameters**:
- `config` (RocketConfig): Rocket configuration
- `motor` (SolidMotor, optional): Motor instance to add during build

---

##### `build()`

```python
def build(self) -> Rocket
```

Build and return Rocket instance with all components.

**Returns**:
- `Rocket`: Configured RocketPy Rocket object

**Raises**:
- `FileNotFoundError`: If drag curve files do not exist

**Example**:
```python
from src.rocket_builder import RocketBuilder

rocket_config = RocketConfig(
    name="Calisto",
    dry_mass_kg=15.426,
    inertia=InertiaConfig(6.32, 6.32, 0.034),
    geometry=GeometryConfig(0.127, 2.0),
    cg_location_m=1.267,
    nose_cone=nose_cone_config,
    fins=fins_config,
    parachute=parachute_config,
)

builder = RocketBuilder(rocket_config)
rocket = builder.build(motor)

print(f"Total mass: {rocket.mass:.2f} kg")
print(f"Static margin: {rocket.static_margin(0):.2f} calibers")
```

---

##### `add_motor()`

```python
def add_motor(self, motor: SolidMotor) -> 'RocketBuilder'
```

Add motor to rocket at configured position.

**Parameters**:
- `motor` (SolidMotor): Motor instance

**Returns**:
- `RocketBuilder`: Self for method chaining

---

##### `add_nose_cone()`

```python
def add_nose_cone(self) -> 'RocketBuilder'
```

Add nose cone to rocket.

**Returns**:
- `RocketBuilder`: Self for method chaining

**Uses**: `self.config.nose_cone` configuration

---

##### `add_fins()`

```python
def add_fins(self) -> 'RocketBuilder'
```

Add trapezoidal fins to rocket.

**Returns**:
- `RocketBuilder`: Self for method chaining

**Uses**: `self.config.fins` configuration

---

##### `add_parachute()`

```python
def add_parachute(self) -> 'RocketBuilder'
```

Add parachute to rocket with trigger logic.

**Returns**:
- `RocketBuilder`: Self for method chaining

**Uses**: `self.config.parachute` configuration

---

## Simulation Module

**Module**: `src.flight_simulator`

### FlightSimulator

```python
class FlightSimulator:
    """Simulator for rocket flight trajectories."""
```

#### Methods

##### `__init__()`

```python
def __init__(
    self,
    rocket: Rocket,
    environment: Environment,
    config: SimulationConfig,
) -> None
```

Initialize FlightSimulator.

**Parameters**:
- `rocket` (Rocket): Configured rocket instance
- `environment` (Environment): Configured environment instance
- `config` (SimulationConfig): Simulation parameters

---

##### `run()`

```python
def run(self) -> Flight
```

Execute flight simulation.

**Returns**:
- `Flight`: RocketPy Flight instance with simulation results

**Raises**:
- `RuntimeError`: If simulation fails

**Example**:
```python
from src.flight_simulator import FlightSimulator

simulator = FlightSimulator(rocket, environment, sim_config)
flight = simulator.run()

print(f"Apogee: {flight.apogee:.0f} m")
print(f"Max velocity: {flight.max_speed:.0f} m/s")
print(f"Flight time: {flight.t_final:.1f} s")
```

---

##### `get_summary()`

```python
def get_summary(self) -> Dict[str, Any]
```

Get comprehensive flight summary.

**Returns**:
- `dict`: Flight metrics dictionary

**Raises**:
- `RuntimeError`: If simulation has not been run yet

**Returned Metrics**:
```python
{
    'apogee_m': float,              # Maximum altitude (m)
    'apogee_time_s': float,         # Time to apogee (s)
    'impact_time_s': float,         # Total flight time (s)
    'impact_velocity_ms': float,    # Impact speed (m/s)
    'max_velocity_ms': float,       # Peak velocity (m/s)
    'max_acceleration_ms2': float,  # Peak acceleration (m/s²)
    'max_acceleration_g': float,    # Peak acceleration (g)
    'lateral_drift_m': float,       # Horizontal displacement (m)
    'off_rail_velocity_ms': float,  # Velocity leaving rail (m/s)
    'off_rail_time_s': float,       # Time on rail (s)
    'burn_out_time_s': float,       # Motor burnout time (s)
    'burn_out_altitude_m': float,   # Altitude at burnout (m)
}
```

**Example**:
```python
summary = simulator.get_summary()
print(f"Apogee: {summary['apogee_m']:.0f} m")
print(f"Max G-force: {summary['max_acceleration_g']:.1f} g")
print(f"Lateral drift: {summary['lateral_drift_m']:.1f} m")
```

---

##### `export_trajectory()`

```python
def export_trajectory(self, output_path: Union[str, Path]) -> None
```

Export trajectory data to CSV file.

**Parameters**:
- `output_path` (str | Path): Output CSV file path

**CSV Columns**:
- `time_s`: Time since liftoff (s)
- `altitude_m`: Altitude AGL (m)
- `velocity_ms`: Velocity magnitude (m/s)
- `acceleration_ms2`: Acceleration magnitude (m/s²)
- `x_m`, `y_m`, `z_m`: Position (m)
- `vx_ms`, `vy_ms`, `vz_ms`: Velocity components (m/s)

**Example**:
```python
simulator.export_trajectory('outputs/trajectory.csv')
```

---

## Monte Carlo Module

**Module**: `src.monte_carlo_runner`

### MonteCarloRunner

```python
class MonteCarloRunner:
    """Monte Carlo uncertainty quantification."""
```

#### Methods

##### `__init__()`

```python
def __init__(
    self,
    base_config_path: Union[str, Path],
    mc_config: MonteCarloConfig,
    output_dir: Optional[Union[str, Path]] = None,
) -> None
```

Initialize MonteCarloRunner.

**Parameters**:
- `base_config_path` (str | Path): Path to base YAML configuration
- `mc_config` (MonteCarloConfig): Monte Carlo configuration
- `output_dir` (str | Path, optional): Output directory for results

**Example**:
```python
from src.monte_carlo_runner import MonteCarloRunner
from src.config_loader import MonteCarloConfig

mc_config = MonteCarloConfig(
    num_simulations=100,
    variations={
        'motor_thrust_std_pct': 5.0,
        'dry_mass_std_kg': 0.5,
        'wind_speed_std_ms': 2.0,
    }
)

runner = MonteCarloRunner(
    base_config_path='configs/rocket.yaml',
    mc_config=mc_config,
    output_dir='outputs/monte_carlo',
)
```

---

##### `run()`

```python
def run(self, num_workers: Optional[int] = None) -> Dict[str, Any]
```

Execute Monte Carlo simulations in parallel.

**Parameters**:
- `num_workers` (int, optional): Number of parallel workers (default: CPU count)

**Returns**:
- `dict`: Statistical results dictionary

**Example**:
```python
results = runner.run(num_workers=8)

print(f"Mean apogee: {results['apogee_m']['mean']:.0f} m")
print(f"Std dev: {results['apogee_m']['std']:.0f} m")
print(f"95th percentile: {results['apogee_m']['p95']:.0f} m")
```

**Results Structure**:
```python
{
    'apogee_m': {
        'mean': float,
        'std': float,
        'min': float,
        'max': float,
        'median': float,
        'p5': float,   # 5th percentile
        'p25': float,  # 25th percentile
        'p75': float,  # 75th percentile
        'p95': float,  # 95th percentile
    },
    'max_velocity_ms': { ... },
    'lateral_drift_m': { ... },
    # ... other metrics
}
```

---

##### `export_for_sensitivity()`

```python
def export_for_sensitivity(
    self,
    parameter_names: List[str],
    target_names: List[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]
```

Export Monte Carlo results for sensitivity analysis.

**Parameters**:
- `parameter_names` (list[str]): Parameter names to export
- `target_names` (list[str]): Target metric names to export

**Returns**:
- `tuple[DataFrame, DataFrame]`: (parameters_df, targets_df)

**Example**:
```python
params_df, targets_df = runner.export_for_sensitivity(
    parameter_names=['motor_thrust', 'dry_mass', 'wind_speed'],
    target_names=['apogee_m', 'max_velocity_ms', 'lateral_drift_m'],
)

print(params_df.head())
print(targets_df.head())
```

---

##### `save_rocketpy_format()`

```python
def save_rocketpy_format(
    self,
    output_dir: Union[str, Path],
    filename_prefix: str = "monte_carlo",
) -> Tuple[Path, Path]
```

Save results in RocketPy-compatible format.

**Parameters**:
- `output_dir` (str | Path): Output directory
- `filename_prefix` (str): Prefix for output files

**Returns**:
- `tuple[Path, Path]`: Paths to (.inputs.txt, .outputs.txt)

**Example**:
```python
inputs_file, outputs_file = runner.save_rocketpy_format(
    output_dir='outputs/',
    filename_prefix='mc_results',
)
# Creates: mc_results.inputs.txt, mc_results.outputs.txt
```

---

## Sensitivity Analysis Modules

### Variance-Based Sensitivity

**Module**: `src.variance_sensitivity`

#### VarianceBasedSensitivityAnalyzer

```python
class VarianceBasedSensitivityAnalyzer:
    """Variance-based sensitivity analysis using multiple linear regression."""
```

##### Methods

###### `__init__()`

```python
def __init__(self) -> None
```

Initialize analyzer.

---

###### `fit()`

```python
def fit(
    self,
    parameters: Union[pd.DataFrame, np.ndarray],
    targets: Union[pd.DataFrame, np.ndarray],
) -> None
```

Fit regression models and calculate sensitivity coefficients.

**Parameters**:
- `parameters` (DataFrame | ndarray): Parameter matrix (N × P)
- `targets` (DataFrame | ndarray): Target matrix (N × T)

**Example**:
```python
from src.variance_sensitivity import VarianceBasedSensitivityAnalyzer

# Load Monte Carlo data
params_df, targets_df = runner.export_for_sensitivity(
    parameter_names=['motor_thrust', 'dry_mass', 'wind_speed'],
    target_names=['apogee_m', 'max_velocity_ms'],
)

# Fit sensitivity model
analyzer = VarianceBasedSensitivityAnalyzer()
analyzer.fit(params_df, targets_df)
```

---

###### `get_sensitivity_coefficients()`

```python
def get_sensitivity_coefficients(self) -> Dict[str, Dict[str, float]]
```

Get sensitivity coefficients for all parameters and targets.

**Returns**:
- `dict`: Nested dictionary `{param_name: {target_name: sensitivity_%}}`

**Example**:
```python
sensitivities = analyzer.get_sensitivity_coefficients()

# Access specific sensitivity
motor_thrust_apogee = sensitivities['motor_thrust']['apogee_m']
print(f"Motor thrust → Apogee: {motor_thrust_apogee:.1f}%")

# Print all sensitivities for apogee
for param, targets in sensitivities.items():
    print(f"{param}: {targets['apogee_m']:.1f}%")
```

---

###### `get_linear_approximation_error()`

```python
def get_linear_approximation_error(self) -> Dict[str, float]
```

Get Linear Approximation Error (LAE) for each target.

**Returns**:
- `dict`: `{target_name: LAE_%}`

**Interpretation**:
- LAE < 5%: Excellent linear approximation
- LAE < 10%: Good linear approximation
- LAE > 20%: Poor linear approximation (use cautiously)

**Example**:
```python
lae = analyzer.get_linear_approximation_error()

for target, error in lae.items():
    if error < 10:
        print(f"✓ {target}: LAE = {error:.2f}% (good)")
    else:
        print(f"⚠ {target}: LAE = {error:.2f}% (poor linear model)")
```

---

###### `get_significant_parameters()`

```python
def get_significant_parameters(
    self,
    target: str,
    threshold: Optional[float] = None,
) -> List[Tuple[str, float]]
```

Get parameters with sensitivity > LAE (significant contributors).

**Parameters**:
- `target` (str): Target metric name
- `threshold` (float, optional): Custom threshold (default: LAE)

**Returns**:
- `list[tuple[str, float]]`: List of (param_name, sensitivity_%) sorted descending

**Example**:
```python
sig_params = analyzer.get_significant_parameters('apogee_m')

print(f"Significant parameters for apogee:")
for param, sensitivity in sig_params:
    print(f"  {param}: {sensitivity:.1f}%")
```

---

###### `predict()`

```python
def predict(
    self,
    parameters: Union[pd.DataFrame, np.ndarray],
    target: str,
) -> np.ndarray
```

Predict target values using fitted regression model.

**Parameters**:
- `parameters` (DataFrame | ndarray): Parameter values
- `target` (str): Target metric name

**Returns**:
- `ndarray`: Predicted target values

**Example**:
```python
# Predict apogee for new parameter combinations
new_params = pd.DataFrame({
    'motor_thrust': [1600, 1700, 1800],
    'dry_mass': [15.0, 15.5, 16.0],
    'wind_speed': [3.0, 5.0, 7.0],
})

predicted_apogee = analyzer.predict(new_params, 'apogee_m')
print(f"Predicted apogees: {predicted_apogee}")
```

---

###### `get_prediction_interval()`

```python
def get_prediction_interval(
    self,
    parameters: Union[pd.DataFrame, np.ndarray],
    target: str,
    confidence: float = 0.95,
) -> Tuple[np.ndarray, np.ndarray]
```

Get prediction intervals for target values.

**Parameters**:
- `parameters` (DataFrame | ndarray): Parameter values
- `target` (str): Target metric name
- `confidence` (float): Confidence level (default: 0.95 for 95%)

**Returns**:
- `tuple[ndarray, ndarray]`: (lower_bound, upper_bound)

**Example**:
```python
lower, upper = analyzer.get_prediction_interval(new_params, 'apogee_m')

for i, (l, u) in enumerate(zip(lower, upper)):
    print(f"Sim {i+1}: 95% CI = [{l:.0f}, {u:.0f}] m")
```

---

###### `plot_sensitivity_bar_chart()`

```python
def plot_sensitivity_bar_chart(
    self,
    target: str,
    top_n: Optional[int] = None,
    save_path: Optional[Union[str, Path]] = None,
) -> None
```

Plot ranked sensitivity bar chart with LAE threshold.

**Parameters**:
- `target` (str): Target metric name
- `top_n` (int, optional): Show only top N parameters (default: all)
- `save_path` (str | Path, optional): Save figure to file

**Example**:
```python
# Plot all parameters
analyzer.plot_sensitivity_bar_chart('apogee_m')

# Plot top 5 parameters and save
analyzer.plot_sensitivity_bar_chart(
    'apogee_m',
    top_n=5,
    save_path='outputs/sensitivity_apogee.png',
)
```

---

### OAT Sensitivity

**Module**: `src.sensitivity_analyzer`

#### OATSensitivityAnalyzer

```python
class OATSensitivityAnalyzer:
    """One-At-a-Time (OAT) sensitivity analysis."""
```

##### Methods

###### `__init__()`

```python
def __init__(
    self,
    base_config_path: Union[str, Path],
    parameters: Dict[str, float],
    perturbation_pct: float = 10.0,
) -> None
```

Initialize OAT sensitivity analyzer.

**Parameters**:
- `base_config_path` (str | Path): Path to base YAML configuration
- `parameters` (dict): Parameters to vary `{param_name: nominal_value}`
- `perturbation_pct` (float): Perturbation percentage (default: 10%)

**Example**:
```python
from src.sensitivity_analyzer import OATSensitivityAnalyzer

analyzer = OATSensitivityAnalyzer(
    base_config_path='configs/rocket.yaml',
    parameters={
        'motor_thrust': 1670.0,
        'dry_mass': 15.426,
        'wind_speed': 5.0,
        'cg_location': 1.267,
    },
    perturbation_pct=5.0,  # ±5% variations
)
```

---

###### `run()`

```python
def run(self) -> Dict[str, Dict[str, float]]
```

Execute OAT sensitivity analysis (2N+1 simulations).

**Returns**:
- `dict`: Local derivatives `{param_name: {target_name: ∂target/∂param}}`

**Example**:
```python
sensitivities = analyzer.run()

# Access sensitivity
d_apogee_d_thrust = sensitivities['motor_thrust']['apogee_m']
print(f"∂(apogee)/∂(thrust) = {d_apogee_d_thrust:.2f} m/N")
```

---

###### `plot_tornado_diagram()`

```python
def plot_tornado_diagram(
    self,
    target: str,
    save_path: Optional[Union[str, Path]] = None,
) -> None
```

Plot tornado diagram (ranked parameter effects).

**Parameters**:
- `target` (str): Target metric name
- `save_path` (str | Path, optional): Save figure to file

**Example**:
```python
analyzer.plot_tornado_diagram('apogee_m', save_path='outputs/tornado.png')
```

---

## Visualization Module

**Module**: `src.visualizer`

### Visualizer

```python
class Visualizer:
    """Publication-quality plotting for simulation results."""
```

#### Methods

##### `plot_trajectory_3d()`

```python
def plot_trajectory_3d(
    self,
    x: np.ndarray,
    y: np.ndarray,
    z: np.ndarray,
    title: str = "3D Trajectory",
) -> None
```

Plot 3D flight trajectory.

**Parameters**:
- `x` (ndarray): East coordinates (m)
- `y` (ndarray): North coordinates (m)
- `z` (ndarray): Altitude AGL (m)
- `title` (str): Plot title

**Example**:
```python
from src.visualizer import Visualizer

viz = Visualizer()
viz.plot_trajectory_3d(flight.x, flight.y, flight.z)
```

---

##### `plot_altitude()`

```python
def plot_altitude(
    self,
    time: np.ndarray,
    altitude: np.ndarray,
    title: str = "Altitude Profile",
) -> None
```

Plot altitude vs. time with apogee marker.

---

##### `plot_velocity()`

```python
def plot_velocity(
    self,
    time: np.ndarray,
    velocity: np.ndarray,
    title: str = "Velocity Profile",
) -> None
```

Plot velocity magnitude vs. time.

---

##### `plot_acceleration()`

```python
def plot_acceleration(
    self,
    time: np.ndarray,
    acceleration: np.ndarray,
    title: str = "Acceleration Profile",
) -> None
```

Plot acceleration vs. time with max-g marker.

---

##### `save_figure()`

```python
def save_figure(
    self,
    output_path: Union[str, Path],
    dpi: int = 300,
) -> None
```

Save current figure to file.

**Parameters**:
- `output_path` (str | Path): Output file path (.png, .pdf, .svg)
- `dpi` (int): Resolution (default: 300)

**Example**:
```python
viz.plot_altitude(flight.time, flight.z)
viz.save_figure('outputs/altitude.png', dpi=600)
```

---

## Data Handler Module

**Module**: `src.data_handler`

### Key Functions

#### `export_to_csv()`

```python
def export_to_csv(
    flight: Flight,
    output_path: Union[str, Path],
) -> None
```

Export flight trajectory to CSV.

**Parameters**:
- `flight` (Flight): RocketPy Flight instance
- `output_path` (str | Path): Output CSV file path

---

#### `export_to_json()`

```python
def export_to_json(
    summary: Dict[str, Any],
    output_path: Union[str, Path],
) -> None
```

Export flight summary to JSON.

**Parameters**:
- `summary` (dict): Flight summary dictionary
- `output_path` (str | Path): Output JSON file path

---

#### `export_to_kml()`

```python
def export_to_kml(
    flight: Flight,
    output_path: Union[str, Path],
    name: str = "Rocket Flight",
) -> None
```

Export flight trajectory to KML for Google Earth.

**Parameters**:
- `flight` (Flight): RocketPy Flight instance
- `output_path` (str | Path): Output KML file path
- `name` (str): Flight name in Google Earth

---

## Utilities Module

**Module**: `src.utils`

### Key Functions

#### `setup_logging()`

```python
def setup_logging(
    level: str = "INFO",
    log_file: Optional[Union[str, Path]] = None,
) -> None
```

Configure logging for the framework.

**Parameters**:
- `level` (str): Logging level (DEBUG, INFO, WARNING, ERROR)
- `log_file` (str | Path, optional): Log file path (default: console only)

**Example**:
```python
from src.utils import setup_logging

setup_logging(level="DEBUG", log_file="simulation.log")
```

---

#### `get_project_root()`

```python
def get_project_root() -> Path
```

Get project root directory.

**Returns**:
- `Path`: Project root path

---

## Type Annotations

All modules use comprehensive type hints for better IDE support and static analysis:

```python
from typing import Union, Optional, List, Dict, Tuple, Any
from pathlib import Path
import numpy as np
import pandas as pd
```

---

## Error Handling

### Exception Hierarchy

```
Exception
├── ValueError: Configuration validation errors
├── FileNotFoundError: Missing data files
├── ImportError: Missing dependencies
└── RuntimeError: Simulation failures
```

### Example Error Handling

```python
from src.config_loader import ConfigLoader
from src.validators import RocketValidator

try:
    loader = ConfigLoader()
    loader.load_from_yaml('configs/rocket.yaml')
    config = loader.get_rocket_config()
    RocketValidator.validate(config)
except FileNotFoundError as e:
    print(f"Config file not found: {e}")
except ValueError as e:
    print(f"Invalid configuration: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Complete Example Workflow

```python
from pathlib import Path
from src.config_loader import ConfigLoader
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator
from src.visualizer import Visualizer

# 1. Load configuration
loader = ConfigLoader()
loader.load_from_yaml('configs/simple_rocket.yaml')

# 2. Build components
motor = MotorBuilder(loader.get_motor_config()).build()
environment = EnvironmentBuilder(loader.get_environment_config()).build()
rocket = RocketBuilder(loader.get_rocket_config()).build(motor)

# 3. Run simulation
simulator = FlightSimulator(rocket, environment, loader.get_simulation_config())
flight = simulator.run()

# 4. Get results
summary = simulator.get_summary()
print(f"Apogee: {summary['apogee_m']:.0f} m")
print(f"Max velocity: {summary['max_velocity_ms']:.0f} m/s")

# 5. Visualize
viz = Visualizer()
viz.plot_altitude(flight.time, flight.z)
viz.save_figure('outputs/altitude.png')

# 6. Export data
simulator.export_trajectory('outputs/trajectory.csv')
```

---

## Version Information

- **Framework Version**: 1.1.0 (Phase 5 Complete)
- **RocketPy Version**: 1.2.0+
- **Python Version**: 3.8+
- **API Stability**: Stable (breaking changes will follow semantic versioning)

---

## Additional Resources

- **Architecture Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Sensitivity Analysis Theory**: [SENSITIVITY_ANALYSIS.md](SENSITIVITY_ANALYSIS.md)
- **Contribution Guidelines**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Main README**: [../README.md](../README.md)
- **Jupyter Notebooks**: [../notebooks/](../notebooks/)
