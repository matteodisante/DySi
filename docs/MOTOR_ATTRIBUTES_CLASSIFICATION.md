# SolidMotor Attributes Classification

This document classifies all `rocketpy.SolidMotor` attributes into three categories for proper state export and visualization.

## Category A: SCALAR/STATIC ATTRIBUTES
These are exported to `initial_state.json/txt` and `final_state.json/txt`.

### Geometry Parameters
- `coordinate_system_orientation` : str - Motor coordinate system orientation
- `nozzle_radius` : float - Nozzle outlet radius (m)
- `nozzle_area` : float - Nozzle outlet area (m²) [DERIVED]
- `nozzle_position` : float - Nozzle position in motor coords (m)
- `throat_radius` : float - Nozzle throat radius (m)
- `throat_area` : float - Nozzle throat area (m²) [DERIVED]

### Grain Parameters
- `grain_number` : int - Number of solid grains
- `grains_center_of_mass_position` : float - Grains COM position (m)
- `grain_separation` : float - Distance between grains (m)
- `grain_density` : float - Grain density (kg/m³)
- `grain_outer_radius` : float - Grain outer radius (m)
- `grain_initial_inner_radius` : float - Initial inner radius (m)
- `grain_initial_height` : float - Initial grain height (m)
- `grain_initial_volume` : float - Initial grain volume (m³) [DERIVED]
- `grain_initial_mass` : float - Initial grain mass (kg) [DERIVED]
- `grain_burn_out` : float - Burn out time (s) [COMPUTED]

### Mass Properties
- `dry_mass` : float - Motor dry mass (kg)
- `propellant_initial_mass` : float - Initial propellant mass (kg) [DERIVED]
- `structural_mass_ratio` : float - Dry/total mass ratio [DERIVED]

### Dry Inertia Tensor (kg·m²)
- `dry_I_11` : float - I_11 component
- `dry_I_22` : float - I_22 component
- `dry_I_33` : float - I_33 component
- `dry_I_12` : float - I_12 component
- `dry_I_13` : float - I_13 component
- `dry_I_23` : float - I_23 component

### Center of Mass Positions
- `center_of_dry_mass_position` : float - Dry mass COM (m)

### Performance Metrics
- `total_impulse` : float - Total impulse (N·s)
- `max_thrust` : float - Maximum thrust (N)
- `max_thrust_time` : float - Time of max thrust (s)
- `average_thrust` : float - Average thrust (N)
- `burn_start_time` : float - Burn start time (s)
- `burn_out_time` : float - Burn out time (s)
- `burn_duration` : float - Burn duration (s)
- `burn_time` : tuple[float, float] - (start, end) times (s)

### Configuration Metadata
- `interpolate` : str - Interpolation method ('linear', 'spline', 'akima')
- `reference_pressure` : float - Reference atmospheric pressure (Pa)

**Total: ~35 scalar attributes**

---

## Category B: FUNCTION ATTRIBUTES (Time-dependent)
These are plotted as curves in `outputs/flight_XXX/curves/motor/`.

### Mass Evolution
- `total_mass(t)` : Function - Total motor mass (kg)
  - **Plot**: `mass_evolution.png` (combined with propellant_mass)
  
- `propellant_mass(t)` : Function - Propellant mass (kg)
  - **Plot**: `mass_evolution.png` (combined with total_mass)
  
- `total_mass_flow_rate(t)` : Function - Mass flow rate (kg/s)
  - **Plot**: `mass_flow_rate.png`

### Center of Mass
- `center_of_mass(t)` : Function - Motor COM position (m)
  - **Plot**: `center_of_mass.png` (combined with propellant COM)
  
- `center_of_propellant_mass(t)` : Function - Propellant COM position (m)
  - **Plot**: `center_of_mass.png` (combined with motor COM)

### Thrust and Exhaust
- `thrust(t)` : Function - Thrust force (N)
  - **Plot**: `thrust.png`
  
- `vacuum_thrust(t)` : Function - Vacuum thrust (N)
  - **Plot**: Can be added to `thrust.png` as secondary curve
  
- `exhaust_velocity(t)` : Function - Exhaust velocity (m/s)
  - **Plot**: `exhaust_velocity.png`

### Grain Geometry Evolution
- `grain_inner_radius(t)` : Function - Inner radius (m)
  - **Plot**: `grain_geometry.png` (dual y-axis with height)
  
- `grain_height(t)` : Function - Grain height (m)
  - **Plot**: `grain_geometry.png` (dual y-axis with inner radius)
  
- `grain_volume(t)` : Function - Grain volume (m³)
  - **Plot**: `grain_volume.png`

### Burn Characteristics
- `burn_area(t)` : Function - Total burn area (m²)
  - **Plot**: `burn_characteristics.png` (dual y-axis with burn_rate)
  
- `burn_rate(t)` : Function - Burn rate (m/s)
  - **Plot**: `burn_characteristics.png` (dual y-axis with burn_area)
  
- `Kn(t)` : Function - Motor Kn (dimensionless)
  - **Plot**: `kn_curve.png`

### Motor Inertia Tensor Evolution (kg·m²)
- `I_11(t)` : Function - I_11 component
- `I_22(t)` : Function - I_22 component (== I_11 by symmetry)
- `I_33(t)` : Function - I_33 component
- `I_12(t)` : Function - I_12 component (== 0)
- `I_13(t)` : Function - I_13 component (== 0)
- `I_23(t)` : Function - I_23 component (== 0)
  - **Plot**: `inertia_tensor.png` (I_11, I_22, I_33 on same plot with dual y-axis if needed)

### Propellant Inertia Tensor Evolution (kg·m²)
- `propellant_I_11(t)` : Function - Propellant I_11
- `propellant_I_22(t)` : Function - Propellant I_22 (== propellant_I_11)
- `propellant_I_33(t)` : Function - Propellant I_33
- `propellant_I_12(t)` : Function - Propellant I_12 (== 0)
- `propellant_I_13(t)` : Function - Propellant I_13 (== 0)
- `propellant_I_23(t)` : Function - Propellant I_23 (== 0)
  - **Plot**: `propellant_inertia_tensor.png` (similar to motor inertia)

**Total: ~23 function attributes → ~12 plot files**

---

## Category C: UTILITY/INTERNAL ATTRIBUTES
These are excluded from export.

- `plots` : _SolidMotorPlots - Plotting utility object
- `prints` : _SolidMotorPrints - Printing utility object
- `_mass_flow_rate` : Function - Internal cache for mass flow rate

**Total: ~3 attributes to exclude**

---

## Plot Organization

```
outputs/flight_XXX/
├── initial_state.json
├── initial_state_READABLE.txt
├── final_state.json
├── final_state_READABLE.txt
├── trajectory.csv
└── curves/
    ├── motor/
    │   ├── thrust.png                    # thrust(t)
    │   ├── mass_evolution.png            # total_mass(t) + propellant_mass(t)
    │   ├── mass_flow_rate.png            # total_mass_flow_rate(t)
    │   ├── center_of_mass.png            # center_of_mass(t) + center_of_propellant_mass(t)
    │   ├── exhaust_velocity.png          # exhaust_velocity(t)
    │   ├── grain_geometry.png            # grain_inner_radius(t) + grain_height(t)
    │   ├── grain_volume.png              # grain_volume(t)
    │   ├── burn_characteristics.png      # burn_area(t) + burn_rate(t)
    │   ├── kn_curve.png                  # Kn(t)
    │   ├── inertia_tensor.png            # I_11(t), I_22(t), I_33(t)
    │   └── propellant_inertia_tensor.png # propellant_I_11(t), I_22(t), I_33(t)
    ├── rocket/
    │   ├── power_off_drag.png
    │   └── power_on_drag.png
    └── environment/
        ├── wind_profile.png
        └── atmospheric_profile.png
```

---

## Export Strategy

### initial_state.json/txt
- All Category A attributes (input + derived values)
- Values captured BEFORE simulation

### final_state.json/txt
- All Category A attributes (same as initial)
- Flight results summary (apogee, max speed, etc.)
- Values captured AFTER simulation

### curves/motor/*.png
- All Category B functions plotted
- Time series from t=0 to burn_out_time
- Combined plots where appropriate (mass, COM, geometry, burn)
- Dual y-axes for plots with different scales

### NOT exported
- Category C utility objects
- Function objects themselves (only their plots)
