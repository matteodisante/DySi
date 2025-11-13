# CHANGELOG

All notable changes to the Rocket Simulation Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Complete RocketPy Flight Plot Parity + Position Data**: All flight kinematics plots
  - `trajectory_3d.png` - 3D flight path with XY/XZ/YZ projections
  - `position_data.png` - Position components (X, Y, Z) vs time **(NEW)**
  - `linear_kinematics_data.png` - Velocities (Vx,Vy,Vz) and accelerations (Ax,Ay,Az)
  - `flight_path_angle_data.png` - Flight path vs attitude angle, lateral attitude
  - `attitude_data.png` - Euler angles (ψ, θ, φ) and attitude angle
  - `angular_kinematics_data.png` - Angular velocities (ω) and accelerations (α) 
  - `aerodynamic_forces.png` - Lift, drag, bending moment, spin moment
  - `rail_buttons_forces.png` - Normal and shear forces on rail buttons (if applicable)
  - `energy_data.png` - Total energy, kinetic/potential components, thrust/drag power
  - `fluid_mechanics_data.png` - Mach, Reynolds, pressures, AoA, stream velocity, sideslip
  - `stability_and_control_data.png` - Stability margin + frequency response
- **Plot Interpretation Documentation**:
  - Complete guide (`docs/source/user/technical/plot_interpretation.rst`) - **31 plot types** documented
  - Quick reference card (`docs/source/user/quick_plot_reference.rst`) - at-a-glance interpretation
  - Pre-flight approval checklist (8 items)
  - Performance validation checklist (6 items)
  - Color-coded stability zones (red/yellow/green/blue) with thresholds
- **Developer Documentation**:
  - Static margin vs stability margin technical explanation
  - Complete flight plots implementation details (11/11 methods including position_data)
  - Plot documentation update summary
- Flight data plots automatically organized in `curves/flight/` subdirectory

### Changed
- `CurvePlotter.plot_all_flight_curves()` now calls 11 flight plot methods (RocketPy + position data)
- `Visualizer` class simplified - removed duplicate methods now in `CurvePlotter`
- `Visualizer` now only provides `plot_trajectory_2d()` (ground track) and `plot_comparison()`
- Documentation navigation enhanced with new dropdown "I want to understand what's in the output plots"
- Technical documentation section restructured: plot interpretation now first topic
- User guide index updated with quick plot reference as first item

### Removed
- **Deprecated plot methods from Visualizer**:
  - `plot_trajectory_3d()` - Use `CurvePlotter.plot_trajectory_3d()` instead (better with projections)
  - `plot_altitude_vs_time()` - Replaced by `position_data.png` (Z component)
  - `plot_velocity_vs_time()` - Replaced by `linear_kinematics_data.png` (more complete)
  - `plot_acceleration_vs_time()` - Replaced by `linear_kinematics_data.png` (more complete)
  - `create_standard_plots()` - Method no longer needed

### Deprecated
- `plots/trajectory/` directory - Use `curves/flight/` for all flight analysis plots
  - Only `trajectory_2d.png` (ground track) remains in `plots/trajectory/`

### Fixed
- Clarified confusion between static margin (CP at Mach=0) and stability margin (CP at actual Mach)
- Added missing explanation for why static margin can be plotted "vs time" despite using Mach=0
- **Flight plot time range extended beyond apogee** - plots now show parachute deployment dynamics
  - All flight plots extend to last parachute deploy + 10% (or 20s max)
  - If no parachute: extends to apogee + 30% (or 30s max)
  - Enables analysis of deceleration, attitude changes, and AoA spikes during deploy
- **3D trajectory apogee marker fixed** - now uses exact `apogee_time` instead of `argmax(altitude)`
  - Label shows: `Apogee: 3245.7 m @ 50.1 s` (precise time)

### Changed
- Marked Monte Carlo analysis as "in development" - not yet production-ready
- Reorganized documentation structure for clarity

### Removed
- Removed sensitivity analysis modules (variance-based and OAT methods) - feature not working
- Removed Sphinx documentation setup (using Markdown documentation only)
- Removed `statsmodels` and `prettytable` dependencies (no longer needed)
- Cleaned up temporary files and build artifacts

---

## [1.0.0] - 2025-11-10

### Added

#### Motor Configuration
- Added 3 missing motor parameters to `MotorConfig`:
  - `interpolation_method` (linear, spline, akima)
  - `coordinate_system_orientation` (nozzle_to_combustion_chamber, combustion_chamber_to_nozzle)
  - `reference_pressure` (atmospheric pressure for thrust data)

#### Motor State Export
- **Complete scalar attribute export** (35+ attributes):
  - Geometry: nozzle radius/area, throat radius/area, positions
  - Grain: number, density, radii, height, volume, mass, separation
  - Mass: dry mass, propellant mass, structural mass ratio
  - Inertia: complete dry inertia tensor (6 components)
  - Performance: impulse, thrust, burn times
  - Configuration: interpolation, coordinate system, reference pressure

#### Visualization
- **11 new motor curve plots**:
  1. `thrust.png` - Thrust vs time
  2. `mass_evolution.png` - Total mass + propellant mass (combined)
  3. `mass_flow_rate.png` - Mass flow rate vs time
  4. `center_of_mass.png` - Motor COM + propellant COM (combined)
  5. `exhaust_velocity.png` - Exhaust velocity vs time
  6. `grain_geometry.png` - Inner radius + height (dual y-axis)
  7. `grain_volume.png` - Grain volume vs time
  8. `burn_characteristics.png` - Burn area + burn rate (dual y-axis)
  9. `kn_curve.png` - Kn vs time
  10. `inertia_tensor.png` - I_11, I_22, I_33 (intelligent dual y-axis)
  11. `propellant_inertia_tensor.png` - Propellant inertia (intelligent dual y-axis)

- **Smart dual y-axis**: Automatically enables when value scales differ by >10x
- **Combined plots**: Related attributes on same graph for direct comparison

#### Air Brakes Control
- PID controller implementation
- Bang-bang controller
- Model-predictive control (MPC)
- Hardware constraint modeling (servo lag, rate limiting, computation time)

#### Weather Integration
- Wyoming atmospheric soundings (radiosonde data)
- GFS (Global Forecast System) forecasts
- ERA5 reanalysis (historical data)
- Custom atmospheric profiles

#### Output Organization
```
outputs/flight_XXX/
├── initial_state.json
├── initial_state_READABLE.txt
├── final_state.json
├── final_state_READABLE.txt
└── curves/
    ├── motor/          # 11 motor plots
    ├── rocket/         # Drag curves
    └── environment/    # Wind & atmospheric profiles
```

### Changed
- Updated `MotorBuilder` to use all new motor configuration parameters
- Completely rewrote `_extract_motor_state()` in `state_exporter.py`
- Extended `curve_plotter.py` with 11+ new plotting methods
- Improved error handling and logging throughout

### Fixed
- Motor position validation
- Function object serialization in state export
- Plot scaling issues with dual y-axis

---

## [0.9.0] - 2025-11-06

### Added
- Initial project structure
- Configuration system with YAML support
- Validation framework
- Builder pattern implementations (Motor, Environment, Rocket)
- Core flight simulation engine
- Basic visualization and data export
- CLI scripts for single simulations
- Test suite with pytest
- Documentation structure

### Core Features
- Single flight simulations
- YAML configuration with type safety
- Comprehensive validation layer
- Multiple export formats (CSV, JSON, KML)
- Publication-quality plots

---

## Notes

### Version History
- **v1.0.0** - Complete motor export system, air brakes, weather integration
- **v0.9.0** - Initial release with core simulation features

### Future Plans
- Complete Monte Carlo analysis implementation
- Parallel execution framework
- Enhanced statistical analysis tools
- Additional control algorithms
- Performance optimizations
