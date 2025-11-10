# Motor State Export & Visualization Guide

This guide explains how to use the complete motor state export and visualization system in rocket-sim.

## Quick Start

### 1. Configure Your Motor

Add all motor parameters to your YAML configuration file:

```yaml
motor:
  type: "SolidMotor"
  thrust_source: "data/motors/Cesaroni_5472M2250-P.eng"
  
  # Required parameters
  dry_mass_kg: 1.815
  dry_inertia: [0.125, 0.125, 0.002]
  nozzle_radius_m: 0.033
  grain_number: 5
  grain_density_kg_m3: 1815.0
  grain_outer_radius_m: 0.033
  grain_initial_inner_radius_m: 0.015
  grain_initial_height_m: 0.120
  grain_separation_m: 0.005
  grains_center_of_mass_position_m: -0.850
  center_of_dry_mass_position_m: 0.317
  nozzle_position_m: 0.0
  throat_radius_m: 0.011
  
  # Optional advanced parameters
  interpolation_method: "linear"  # linear, spline, akima
  coordinate_system_orientation: "nozzle_to_combustion_chamber"
  reference_pressure: null  # Pa
  
  position_m: -1.373  # Position on rocket
```

### 2. Run Simulation with State Export

```python
from src.flight_simulator import FlightSimulator
from src.state_exporter import StateExporter

# Run simulation
simulator = FlightSimulator(config_path="configs/single_sim/02_complete.yaml")
flight = simulator.run()

# Export complete state with plots
exporter = StateExporter(
    motor=simulator.motor,
    rocket=simulator.rocket,
    environment=simulator.environment,
    sim_config=simulator.sim_config
)

exporter.export_complete(
    flight=flight,
    output_dir="outputs/my_flight",
    include_plots=True
)
```

### 3. Examine Output Files

```
outputs/my_flight/
├── initial_state.json                # All scalar motor parameters BEFORE sim
├── initial_state_READABLE.txt        # Human-readable format
├── final_state.json                  # Parameters + flight results AFTER sim
├── final_state_READABLE.txt          # Human-readable format
├── trajectory.csv                    # Time series data
└── curves/
    ├── motor/                        # 11 motor curve plots
    │   ├── thrust.png
    │   ├── mass_evolution.png
    │   ├── mass_flow_rate.png
    │   ├── center_of_mass.png
    │   ├── exhaust_velocity.png
    │   ├── grain_geometry.png
    │   ├── grain_volume.png
    │   ├── burn_characteristics.png
    │   ├── kn_curve.png
    │   ├── inertia_tensor.png
    │   └── propellant_inertia_tensor.png
    ├── rocket/
    │   ├── power_off_drag.png
    │   └── power_on_drag.png
    └── environment/
        ├── wind_profile.png
        └── atmospheric_profile.png
```

## Understanding the Output

### initial_state.json / final_state.json

These files contain **only scalar/static values** (numbers, strings):

#### Motor Section (35+ attributes)
- **Geometry**: nozzle_radius, throat_radius, nozzle_area, throat_area, positions
- **Grain**: grain_number, density, radii, height, volume, mass, separation
- **Mass**: dry_mass, propellant_initial_mass, structural_mass_ratio
- **Inertia**: dry_I_11, dry_I_22, dry_I_33, dry_I_12, dry_I_13, dry_I_23
- **Performance**: total_impulse, max_thrust, burn_duration, etc.
- **Config**: interpolation_method, coordinate_system_orientation, reference_pressure

**Important**: Time-dependent attributes (thrust curve, mass evolution, etc.) are **NOT** in JSON files - they are plotted in `curves/motor/`.

### Curve Plots

All time-dependent motor attributes are visualized as high-quality PNG plots:

#### 1. **thrust.png**
- Motor thrust force vs time
- Units: N (Newtons)

#### 2. **mass_evolution.png**
- Total motor mass + propellant mass (combined plot)
- Units: kg

#### 3. **mass_flow_rate.png**
- Mass flow rate vs time
- Units: kg/s

#### 4. **center_of_mass.png**
- Motor COM + Propellant COM (combined plot)
- Units: m (meters from nozzle)

#### 5. **exhaust_velocity.png**
- Effective exhaust velocity vs time
- Units: m/s

#### 6. **grain_geometry.png**
- Grain inner radius + grain height (dual y-axis)
- Units: m
- **Note**: Uses dual y-axis if values have different scales

#### 7. **grain_volume.png**
- Total grain volume vs time
- Units: m³

#### 8. **burn_characteristics.png**
- Burn area + burn rate (dual y-axis)
- Units: m² and m/s

#### 9. **kn_curve.png**
- Kn (burn area / throat area) vs time
- Dimensionless

#### 10. **inertia_tensor.png**
- Motor inertia I_11, I_22, I_33
- Units: kg·m²
- **Note**: Uses dual y-axis if I_33 << I_11/I_22 (typical)

#### 11. **propellant_inertia_tensor.png**
- Propellant inertia components
- Units: kg·m²
- **Note**: Uses dual y-axis if scales differ significantly

## Motor Parameter Reference

### Required Parameters

These parameters **must** be specified in your YAML config:

```yaml
thrust_source: str           # Path to .eng or .csv file
dry_mass_kg: float          # Motor dry mass
dry_inertia: [float, float, float]  # [I_11, I_22, I_33]
nozzle_radius_m: float      # Nozzle exit radius
grain_number: int           # Number of grains
grain_density_kg_m3: float  # Grain density
grain_outer_radius_m: float
grain_initial_inner_radius_m: float
grain_initial_height_m: float
grain_separation_m: float
grains_center_of_mass_position_m: float
center_of_dry_mass_position_m: float
```

### Optional Parameters (with defaults)

```yaml
nozzle_position_m: 0.0                # Nozzle position in motor coords
burn_time_s: null                     # Auto-computed from thrust curve
throat_radius_m: 0.011                # For Kn calculation
interpolation_method: "linear"        # linear, spline, akima
coordinate_system_orientation: "nozzle_to_combustion_chamber"
reference_pressure: null              # Atmospheric pressure (Pa)
```

## Advanced Usage

### Custom Plot Generation

Generate only motor plots without full export:

```python
from src.curve_plotter import CurvePlotter

plotter = CurvePlotter(motor, rocket, environment)
motor_plots = plotter.plot_all_motor_curves("outputs/my_flight/curves")

# Returns dict: {'motor_thrust': Path(...), 'motor_mass_evolution': Path(...), ...}
```

### Export Only Initial State

Before running simulation:

```python
exporter = StateExporter(motor, rocket, environment, sim_config)
exporter.export_initial_state("outputs/my_flight/initial_state.json")
```

### Export Only Final State

After simulation:

```python
exporter.export_final_state(flight, "outputs/my_flight/final_state.json")
```

### Export with Selective Plots

```python
# Export states without generating plots
exporter.export_complete(
    flight=flight,
    output_dir="outputs/my_flight",
    include_plots=False
)

# Then generate only specific plots manually
plotter = CurvePlotter(motor, rocket, environment)
plotter.plot_thrust_curve("outputs/my_flight/curves/motor")
plotter.plot_mass_evolution("outputs/my_flight/curves/motor")
```

## Understanding Derived Values

Some motor attributes are **derived** (computed from input parameters):

### Always Derived
- `nozzle_area` = π × nozzle_radius²
- `throat_area` = π × throat_radius²
- `grain_initial_volume` = grain_height × π × (outer_radius² - inner_radius²)
- `grain_initial_mass` = grain_volume × grain_density
- `propellant_initial_mass` = grain_initial_mass × grain_number
- `structural_mass_ratio` = dry_mass / (dry_mass + propellant_initial_mass)

### Computed from Thrust Curve
- `total_impulse` = ∫ thrust(t) dt
- `max_thrust` = max(thrust(t))
- `max_thrust_time` = argmax(thrust(t))
- `average_thrust` = total_impulse / burn_duration
- `burn_start_time`, `burn_out_time`, `burn_duration`

### Computed During Simulation
- `grain_burn_out` = time when grain is fully consumed

These derived values appear in both `initial_state` and `final_state` exports.

## Troubleshooting

### Missing Plots

If some motor plots are not generated:

1. **Check motor type**: Only `SolidMotor` has grain geometry plots
2. **Check attributes**: Motor must have the corresponding Function attributes
3. **Check logs**: Look for warnings in console output
4. **Verify motor build**: Ensure MotorBuilder.build() succeeded

### JSON Too Large

If JSON files are very large:

- This shouldn't happen! Function objects are **excluded** from JSON.
- If you see large arrays in JSON, there's a bug - report it.
- Use `include_plots=False` and rely on curve plots instead.

### Dual Y-Axis Not Used

Dual y-axis is automatically enabled when value scales differ by >10x.
Example: I_33 (axial inertia) is typically much smaller than I_11/I_22 (lateral inertia).

If you want to force single-axis plots, modify `CurvePlotter.plot_inertia_tensor()`:
```python
use_dual_axis = False  # Force single axis
```

### Custom Interpolation Not Working

Ensure your YAML config specifies:
```yaml
motor:
  interpolation_method: "spline"  # or "akima"
```

And that MotorConfig has the parameter:
```python
interpolation_method: str = "linear"  # In MotorConfig dataclass
```

## Example Configurations

See:
- `configs/single_sim/01_minimal.yaml` - Minimal working configuration
- `configs/single_sim/02_complete.yaml` - All parameters specified
- `configs/templates/template_advanced.yaml` - Fully documented template

## Related Documentation

- [Motor Attributes Classification](MOTOR_ATTRIBUTES_CLASSIFICATION.md) - Complete list of all SolidMotor attributes
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - Technical details of the implementation
- [API Reference](API_REFERENCE.md) - Full API documentation
- RocketPy Documentation: https://docs.rocketpy.org/

## Support

For issues or questions:
1. Check this guide and related documentation
2. Verify your YAML configuration is complete
3. Check console logs for warnings/errors
4. Consult RocketPy documentation for motor parameters
