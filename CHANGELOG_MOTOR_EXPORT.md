# CHANGELOG - Motor State Export Enhancement

## 2025-11-10 - Complete Motor State Export & Visualization

### ✨ New Features

#### Motor Configuration
- **Added 3 missing motor parameters** to `MotorConfig`:
  - `interpolation_method` (linear, spline, akima)
  - `coordinate_system_orientation` (nozzle_to_combustion_chamber, combustion_chamber_to_nozzle)
  - `reference_pressure` (atmospheric pressure for thrust data)

#### State Export
- **Complete scalar attribute export** (35+ attributes):
  - Geometry: nozzle radius/area, throat radius/area, positions
  - Grain: number, density, radii, height, volume, mass, separation
  - Mass: dry mass, propellant mass, structural mass ratio
  - Inertia: complete dry inertia tensor (6 components)
  - Performance: impulse, thrust, burn times
  - Configuration: interpolation, coordinate system, reference pressure

- **Improved export structure**:
  - Scalars only in JSON/TXT (no Function objects)
  - Time-dependent attributes moved to curve plots
  - Cleaner, more readable output files
  - Better separation of concerns

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

- **Smart dual y-axis**:
  - Automatically enables when value scales differ by >10x
  - Prevents small values from being obscured by large ones
  - Applied to: grain geometry, burn characteristics, inertia tensors

- **Combined plots**:
  - Related attributes on same graph for direct comparison
  - Mass evolution: total + propellant mass
  - Center of mass: motor + propellant COM

#### Directory Organization
```
outputs/flight_XXX/
├── initial_state.json
├── initial_state_READABLE.txt
├── final_state.json
├── final_state_READABLE.txt
└── curves/
    ├── motor/          # NEW: 11 motor plots
    ├── rocket/         # Drag curves
    └── environment/    # Wind & atmospheric profiles
```

### 🔧 Modified Files

#### Core Code
1. `src/config_loader.py`
   - Added 3 parameters to `MotorConfig`
   - Updated docstrings

2. `src/motor_builder.py`
   - Updated `build()` to pass new parameters to `SolidMotor()`
   - Now uses all available configuration options

3. `src/state_exporter.py`
   - **Completely rewrote** `_extract_motor_state()`
   - Explicit list of 35+ scalar attributes (Category A)
   - Skips Function objects (Category B - go to plots)
   - Excludes utility objects (Category C)
   - Cleaner, more maintainable code

4. `src/curve_plotter.py`
   - **Major extension**: Added 11+ new plotting methods
   - `plot_all_motor_curves()` - Main entry point
   - `plot_single_function()` - Generic plotter
   - `_sample_function()` - Robust function sampling
   - `plot_mass_evolution()` - Combined mass plot
   - `plot_center_of_mass()` - Combined COM plot
   - `plot_grain_geometry()` - Dual y-axis plot
   - `plot_burn_characteristics()` - Dual y-axis plot
   - `plot_inertia_tensor()` - Intelligent dual y-axis
   - `plot_propellant_inertia_tensor()` - Intelligent dual y-axis
   - Better error handling and logging
   - High-quality output (DPI=300, tight layout)

#### Configuration Files
5. `configs/single_sim/01_minimal.yaml`
   - Added comments for optional advanced parameters

6. `configs/single_sim/02_complete.yaml`
   - Added all 3 new motor parameters
   - Complete example configuration

7. `configs/templates/template_advanced.yaml`
   - Fully documented motor section
   - All parameters with descriptions and options

#### Documentation
8. `docs/MOTOR_ATTRIBUTES_CLASSIFICATION.md` - **NEW**
   - Complete classification of all 61 SolidMotor attributes
   - Category A: 35+ scalar attributes (exported to JSON)
   - Category B: 23 function attributes (plotted)
   - Category C: 3 utility objects (excluded)
   - Plot organization and mapping

9. `docs/IMPLEMENTATION_SUMMARY.md` - **NEW**
   - Comprehensive implementation overview
   - Detailed explanation of changes
   - Benefits and rationale
   - Usage examples
   - Testing checklist

10. `docs/MOTOR_STATE_EXPORT_GUIDE.md` - **NEW**
    - User-friendly guide for using the export system
    - Quick start tutorial
    - Parameter reference
    - Advanced usage examples
    - Troubleshooting section

### 📊 Statistics

- **Lines of code added**: ~800+
- **New methods**: 11 plotting methods
- **New attributes exported**: 35+ scalar motor attributes
- **New plot types**: 11 motor curve plots
- **Configuration parameters added**: 3
- **Documentation files created**: 3 (25+ pages)

### ✅ Verification Checklist

- [x] All required SolidMotor.__init__ parameters in MotorConfig
- [x] All 35+ scalar attributes exported to JSON
- [x] No Function objects in JSON (only in plots)
- [x] All 11 motor plots generated correctly
- [x] Dual y-axis works for different scales
- [x] Combined plots show multiple curves
- [x] YAML configs updated with new parameters
- [x] Comprehensive documentation created
- [x] Code follows project guidelines (snake_case, PEP 8, docstrings)

### 🎯 Benefits

#### For Analysis
- Complete motor state capture (35+ attributes)
- All time-dependent functions visualized
- Initial vs final state comparison
- Derived values visible (areas, volumes, masses)

#### For Documentation
- Human-readable TXT format with units
- Organized plot directory structure
- Metadata (timestamp, RocketPy version)
- Clear separation of input/output

#### For Development
- Type-safe configuration (all required params)
- Clear attribute classification (A/B/C)
- Maintainable code structure
- Comprehensive documentation

### 🔮 Future Work

Potential enhancements:
- [ ] Support for LiquidMotor and HybridMotor
- [ ] Interactive plots (Plotly) option
- [ ] HDF5 export for large datasets
- [ ] State diff tool (initial vs final)
- [ ] Automated YAML validation

### 📚 References

- RocketPy SolidMotor: `rocketpy/motors/solid_motor.py`
- RocketPy Motor base: `rocketpy/motors/motor.py`
- Project guidelines: `.github/copilot-instructions.md`

---

**Version**: 1.0.0  
**Date**: 2025-11-10  
**Impact**: Major feature addition  
**Breaking Changes**: None (backward compatible)
