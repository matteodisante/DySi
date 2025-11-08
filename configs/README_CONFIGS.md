# Configuration Files Guide

This directory contains YAML configuration files for rocket simulations. Configuration files allow you to define rocket, motor, environment, and simulation parameters in a structured, readable format.

## Directory Structure

Configuration files are organized by use case:

```
configs/
├── single_sim/         # Single flight simulations
│   ├── 01_minimal.yaml      # Minimal configuration with essential parameters only
│   └── 02_complete.yaml     # Complete configuration with all available options
├── monte_carlo/        # Monte Carlo uncertainty quantification
│   ├── 01_basic_mc.yaml     # Basic Monte Carlo with 3-4 parameter variations
│   └── 02_competition_mc.yaml  # Advanced Monte Carlo with air brakes control
├── templates/          # Template files for creating new configurations
│   ├── template_basic.yaml     # Copy this for simple rockets
│   └── template_advanced.yaml  # Copy this for competition rockets
└── weather_example.yaml # Weather data configuration example
```

### When to Use Each Directory

- **single_sim/**: Use these for:
  - Initial design validation
  - Single flight trajectory analysis
  - Testing specific configurations
  - Apogee and stability predictions

- **monte_carlo/**: Use these for:
  - Uncertainty quantification (e.g., "What's the apogee spread?")
  - Robustness analysis (e.g., "How sensitive to wind?")
  - Competition preparation (statistical landing predictions)
  - Parameter optimization studies

- **templates/**: Start here when:
  - Creating a new rocket configuration
  - You need a clean starting point
  - You want to ensure all required fields are included

## Configuration File Structure

A complete configuration file has four main sections:

1. **rocket**: Rocket physical properties and components
2. **motor**: Motor/propulsion system parameters
3. **environment**: Launch site and atmospheric conditions
4. **simulation**: Simulation parameters and settings

## Example Configurations

### Single Simulations

- **`single_sim/01_minimal.yaml`**: Minimal configuration with only essential parameters
- **`single_sim/02_complete.yaml`**: Comprehensive example with all available options and detailed comments

### Monte Carlo Simulations

- **`monte_carlo/01_basic_mc.yaml`**: Basic Monte Carlo with 3 parameter variations (50 runs)
- **`monte_carlo/02_competition_mc.yaml`**: Advanced Monte Carlo with air brakes and 5 parameter variations (100 runs)

## Configuration Schema

### Rocket Section

```yaml
rocket:
  name: string                    # Rocket name/identifier
  dry_mass_kg: float              # Dry mass without motor (kg)

  inertia:                        # Moment of inertia tensor (kg·m²)
    ixx_kg_m2: float
    iyy_kg_m2: float
    izz_kg_m2: float

  geometry:
    caliber_m: float              # Maximum diameter (m)
    length_m: float               # Total rocket length (m)

  cg_location_m: float            # Center of gravity from nose (m)
  cp_location_m: float            # Center of pressure from nose (m) [optional]

  coordinate_system: string       # "tail_to_nose" or "nose_to_tail"

  nose_cone:                      # [optional]
    length_m: float
    kind: string                  # vonKarman, conical, ogive, elliptical
    position_m: float

  fins:                           # [optional]
    count: int                    # Number of fins (typically 3-4)
    root_chord_m: float           # Root chord length (m)
    tip_chord_m: float            # Tip chord length (m)
    span_m: float                 # Fin span/height (m)
    thickness_m: float            # Fin thickness (m)
    position_m: float             # Position along rocket (m)
    cant_angle_deg: float         # Cant angle for spin (degrees) [default: 0]
    airfoil: string               # Path to airfoil file [optional]

  parachute:                      # [optional]
    enabled: bool
    name: string
    cd_s: float                   # Drag coefficient × area (m²)
    trigger: string/float         # "apogee" or altitude (m)
    sampling_rate_hz: float       # Sampling rate (Hz) [default: 105]
    lag_s: float                  # Deployment lag (s) [default: 1.5]
    noise_std: [float, float, float]  # [x, y, z] noise std dev [default: [0,0,0]]

  power_off_drag: string          # Path to drag curve file [optional]
  power_on_drag: string           # Path to drag curve file [optional]
```

### Motor Section

```yaml
motor:
  type: string                    # SolidMotor, LiquidMotor, HybridMotor
  thrust_source: string           # Path to thrust curve file (.eng, .csv)

  dry_mass_kg: float              # Motor dry mass (kg)
  dry_inertia: [float, float, float]  # [Ixx, Iyy, Izz] (kg·m²)

  nozzle_radius_m: float          # Nozzle exit radius (m)
  throat_radius_m: float          # Nozzle throat radius (m)

  # Solid motor grain parameters:
  grain_number: int               # Number of propellant grains
  grain_density_kg_m3: float      # Grain density (kg/m³)
  grain_outer_radius_m: float     # Grain outer radius (m)
  grain_initial_inner_radius_m: float  # Initial bore radius (m)
  grain_initial_height_m: float   # Grain height (m)
  grain_separation_m: float       # Gap between grains (m)

  grains_center_of_mass_position_m: float  # Grains CoM position (m)
  center_of_dry_mass_position_m: float     # Dry mass CoM position (m)
  nozzle_position_m: float        # Nozzle position (m)

  burn_time_s: float              # Total burn time (s) [optional, computed from curve]
  position_m: float               # Motor position on rocket (m)
```

### Environment Section

```yaml
environment:
  latitude_deg: float             # Launch site latitude (-90 to 90)
  longitude_deg: float            # Launch site longitude (-180 to 180)
  elevation_m: float              # Launch site elevation ASL (m)

  atmospheric_model: string       # standard_atmosphere, custom_atmosphere, etc.
  atmospheric_model_file: string  # Path to atmosphere data [optional]

  date: [int, int, int, int]      # [year, month, day, hour_utc] [optional]

  wind:
    model: string                 # constant, function, custom
    velocity_ms: float            # Wind speed (m/s)
    direction_deg: float          # Wind direction (0=North, 90=East)

  gravity_ms2: float              # Gravitational acceleration (m/s²) [default: 9.80665]
  max_expected_height_m: float    # Maximum expected altitude (m) [default: 10000]
```

### Simulation Section

```yaml
simulation:
  max_time_s: float               # Maximum simulation time (s)
  max_time_step_s: float          # Max integration time step (s) [.inf for auto]
  min_time_step_s: float          # Min integration time step (s)
  rtol: float                     # Relative tolerance [default: 1e-6]
  atol: float                     # Absolute tolerance [default: 1e-6]
  terminate_on_apogee: bool       # Stop simulation at apogee [default: false]
  verbose: bool                   # Print simulation progress [default: false]

  rail:
    length_m: float               # Launch rail length (m)
    inclination_deg: float        # Rail angle from vertical (0-90 degrees)
    heading_deg: float            # Launch direction from North (0-360 degrees)
```

## Units Convention

All values must be specified in **SI units**:

- **Length**: meters (m)
- **Mass**: kilograms (kg)
- **Time**: seconds (s)
- **Angle**: degrees (deg)
- **Force**: Newtons (N)
- **Velocity**: meters per second (m/s)
- **Acceleration**: meters per second squared (m/s²)

## Coordinate Systems

### Rocket Coordinate System

Two options are available via `coordinate_system`:

1. **`tail_to_nose`** (default): Origin at tail, +x points toward nose
2. **`nose_to_tail`**: Origin at nose, +x points toward tail

All component positions (`cg_location_m`, `cp_location_m`, `fins.position_m`, etc.) are specified relative to the chosen coordinate system origin.

### Wind Direction Convention

Wind direction follows **meteorological convention**:
- 0° = Wind from North
- 90° = Wind from East
- 180° = Wind from South
- 270° = Wind from West

### Launch Rail Angles

- **Inclination**: Angle from vertical
  - 0° = Horizontal launch
  - 90° = Vertical launch
  - Typical value: 85° (5° from vertical)

- **Heading**: Launch azimuth angle from North
  - 0° = Launch toward North
  - 90° = Launch toward East
  - 180° = Launch toward South
  - 270° = Launch toward West

## Validation

All configuration files are automatically validated when loaded. The validation system checks:

### Critical Errors (simulation will not run):
- Positive mass, inertia, and geometric values
- Valid coordinate ranges (latitude, longitude)
- Physical constraints (e.g., CP behind CG for stability)
- Required fields are present

### Warnings (simulation will run with caution):
- Unusual parameter values (e.g., very high/low mass)
- Stability concerns (e.g., low static margin)
- Out-of-range values that may indicate mistakes

## Loading Configurations

### From Python Script

```python
from src.config_loader import ConfigLoader

# Load single simulation configuration
loader = ConfigLoader()
rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(
    "configs/single_sim/02_complete.yaml"
)

# Load Monte Carlo configuration
loader.load_from_yaml("configs/monte_carlo/01_basic_mc.yaml")
rocket_cfg = loader.get_rocket_config()
mc_cfg = loader.get_monte_carlo_config()
```

### From Jupyter Notebooks

```python
from pathlib import Path
from src.config_loader import ConfigLoader

# Single simulation
config_path = Path("../configs/single_sim/01_minimal.yaml")
loader = ConfigLoader()
rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(config_path)

# Monte Carlo simulation
config_path = Path("../configs/monte_carlo/01_basic_mc.yaml")
loader.load_from_yaml(config_path)
```

### From Command Line

```bash
# Single simulation
python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml

# Monte Carlo simulation
python scripts/run_monte_carlo.py --config configs/monte_carlo/01_basic_mc.yaml
```

## Creating Custom Configurations

1. **Start with a template**: Copy from `templates/` directory
   ```bash
   # For a simple rocket
   cp configs/templates/template_basic.yaml configs/single_sim/my_rocket.yaml

   # For a competition rocket
   cp configs/templates/template_advanced.yaml configs/single_sim/my_competition_rocket.yaml
   ```

2. **Modify parameters**: Edit values to match your rocket design

3. **Validate**: Run validation to check for errors:
   ```python
   from src.validators import validate_all_configs
   warnings = validate_all_configs(rocket_cfg, motor_cfg, env_cfg, sim_cfg)
   ```

4. **Test with single simulation**: Run a single simulation before Monte Carlo analysis
   ```python
   # Test your configuration
   python scripts/run_single_simulation.py --config configs/single_sim/my_rocket.yaml
   ```

5. **Add Monte Carlo section** (if needed): Copy the `monte_carlo:` section from `monte_carlo/01_basic_mc.yaml` and adjust parameter variations

## Motor Thrust Curve Files

Motor thrust curves should be provided as:

- **`.eng` files**: RASP engine format (standard for hobby rocketry)
- **`.csv` files**: Two columns (time_s, thrust_N) with header

Example `.eng` file location:
```
data/motors/Cesaroni_M1670.eng
```

Popular motor databases:
- [ThrustCurve.org](https://www.thrustcurve.org/)
- RASP motor files
- Manufacturer data sheets

## Tips for Configuration

### Stability
- Ensure static margin ≥ 1 caliber (preferably 1.5-2.5 calibers)
- CP should be behind CG by at least one rocket diameter
- Use `cp_location_m: null` to let RocketPy compute CP automatically

### Performance
- Longer rail → higher off-rail velocity → better stability
- Lower rail inclination → higher altitude but more drift
- Parachute `cd_s` affects descent rate and landing dispersion

### Accuracy
- Tighter tolerances (`rtol`, `atol`) → slower but more accurate
- Use `verbose: true` for debugging
- Set `max_expected_height_m` to 2x estimated apogee for better atmospheric data

### Common Issues

**Static margin too low**:
- Move fins further back
- Increase fin span
- Move CG forward (add nose weight)

**High landing velocity**:
- Increase parachute `cd_s`
- Deploy parachute at higher altitude
- Add drogue + main chute system

**Simulation fails to converge**:
- Reduce tolerance (`rtol`, `atol`)
- Reduce `max_time_step_s`
- Check for invalid geometry (e.g., negative values)

## Additional Resources

- **RocketPy Documentation**: https://docs.rocketpy.org/
- **Example notebooks**: `notebooks/` directory
- **Architecture overview**: `docs/ARCHITECTURE.md`
- **API reference**: `docs/API_REFERENCE.md`

## Support

For issues or questions:
1. Check validation warnings for configuration errors
2. Review example configurations
3. Consult RocketPy documentation
4. Open an issue on GitHub repository
