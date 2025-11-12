# CHANGELOG

All notable changes to the Rocket Simulation Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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
