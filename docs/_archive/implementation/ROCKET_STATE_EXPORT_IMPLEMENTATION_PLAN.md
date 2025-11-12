# Rocket State Export - Implementation Plan

## Overview
This document describes the complete plan for extending the state export functionality from Motor to Rocket, including all attributes, plots, and documentation.

**KEY REQUIREMENT**: Output files contain ONLY state data (numerical values). Analysis, interpretation, and reports are generated in SEPARATE documents.

## Progress Status

### ✅ Completed
1. Extended `state_exporter.py` with comprehensive Rocket state export
   - Added complete `_write_rocket_section()` with ALL rocket attributes
   - Includes: geometry, masses, CoM, inertias (without motor, dry, total), eccentricities
   - Includes: all aerodynamic surfaces (nosecones, fins, tails)
   - Includes: rail buttons, parachutes, air brakes, controllers, sensors
   - Outputs: JSON (machine-readable) + TXT (human-readable)

2. Enhanced Motor thrust curve plot in `curve_plotter.py`
   - Added `plot_thrust_curve()` with rich annotations
   - Shows: burn times, max thrust point, average thrust line, total impulse area
   - Output: `outputs/{name}/curves/motor/thrust_curve.png`

3. Implemented ALL Rocket Plots (17 plots total) in `curve_plotter.py`
   - Created `plot_all_rocket_curves()` method
   - Mass properties: 4 plots (total mass, comparison, flow rate, reduced mass)
   - Center of mass: 2 plots (evolution, CoM to CDM)
   - Inertia: 4 plots (lateral, axial, products, comparison)
   - Aerodynamics: 3 plots (drag coefficients, CP vs Mach, lift coefficient)
   - Stability: 2 plots (static margin, stability margin surface)
   - Performance: 1 plot (thrust-to-weight ratio)
   - Schematic: 1 plot (rocket.draw())

4. Implemented Technical Schematics
   - Created `save_all_schematics()` method in `curve_plotter.py`
   - Saves `rocket.draw()` → `plots/rocket_schematic.png`
   - Saves `motor.draw()` → `plots/motor_schematic.png` (if available)
   - Integrated into flight_simulator.py workflow

5. Verified and Completed `02_complete.yaml`
   - Added ALL missing parameters:
     - Motor: reference_pressure (critical for altitude correction)
     - Rocket: inertia products (I_12, I_13, I_23)
     - Rocket: eccentricities (cm_x/y, cp_x/y, thrust_x/y)
     - Rocket: tail section configuration
     - Rocket: rail_buttons configuration
     - Rocket: air_brakes with controller parameters
   - Added comprehensive inline comments for all sections

6. Integrated Exports in `flight_simulator.py`
   - State exports (initial and final) already functional
   - Curve plots automatically generated via `export_curves_plots()`
   - Added schematic generation via `save_all_schematics()`
   - Complete output structure now includes:
     - `initial_state.json` and `initial_state_READABLE.txt`
     - `final_state.json` and `final_state_READABLE.txt`
     - `curves/motor/` (11 plots)
     - `curves/rocket/` (17 plots)
     - `curves/environment/` (2 plots)
     - `plots/rocket_schematic.png`
     - `plots/motor_schematic.png`
     - `trajectory/` (CSV data and summary JSON)

7. Created Comprehensive Template: `template_complete_documented.yaml`
   - 400+ lines of fully documented configuration
   - Every parameter explained with:
     - Physical meaning and purpose
     - Units and typical values
     - Available options
     - Usage examples
   - Organized sections:
     - Rocket (mass, inertia, geometry, surfaces, recovery, control)
     - Motor (type, performance, grain config, critical parameters)
     - Environment (location, atmosphere, wind, gravity)
     - Simulation (integration, rail, termination)
     - Monte Carlo (uncertainty quantification)
   - Created companion `README.md` with:
     - Usage instructions
     - Best practices
     - Common issues and solutions
     - Tips for success

### 🔄 In Progress
None - all tasks completed!

### 📋 Future Work (Low Priority)

**8. Report Generator Module (Optional)**
   - Separate HTML/PDF report generation
   - See: `docs/implementation/REPORT_GENERATOR_SPEC.md`
   - Features:
     - Executive summary
     - Embedded plots and analysis
     - Automated safety checks
     - Performance recommendations
   - Priority: LOW (nice to have, not critical)

#### HIGH PRIORITY

**3. Implement ALL Rocket Plots (17 plots total)**
   - Location: `src/curve_plotter.py` - add new methods
   - Create `plot_all_rocket_curves(output_dir)` method
   - Output directory: `outputs/{name}/curves/rocket/`
   
   Plots needed:
   ```python
   # Mass Properties (4 plots)
   - total_mass_vs_time.png
   - mass_components_comparison.png  # bar chart
   - mass_flow_rate_vs_time.png
   - reduced_mass_vs_time.png
   
   # Center of Mass (2 plots)
   - center_of_mass_evolution.png  # all CoM positions on same plot
   - com_to_cdm_vs_time.png
   
   # Inertia (4 plots)
   - inertia_lateral_vs_time.png  # I_11, I_22
   - inertia_axial_vs_time.png    # I_33
   - inertia_products_vs_time.png  # I_12, I_13, I_23 if non-zero
   - inertia_comparison.png  # without_motor vs dry vs total(t0) vs total(tf)
   
   # Aerodynamics (3 plots)
   - drag_coefficients_vs_mach.png  # power_on and power_off
   - cp_position_vs_mach.png
   - lift_coefficient_derivative_vs_mach.png
   
   # Stability (2 plots)
   - static_margin_vs_time.png
   - stability_margin_surface.png  # 3D or contour: Mach vs Time
   
   # Performance (1 plot)
   - thrust_to_weight_vs_time.png
   
   # Schematic (1 plot)
   - rocket_schematic.png  # using rocket.draw()
   ```

**4. Implement Technical Drawings**
   - Use `rocket.draw()` → save to `outputs/{name}/plots/rocket_schematic.png`
   - Check if `motor.draw()` exists in RocketPy → save to `outputs/{name}/plots/motor_schematic.png`
   - Add error handling if `.draw()` method not available

**5. Complete Configuration File `02_complete.yaml`**
   - Verify ALL parameters are present
   - Add inline comments explaining each parameter
   - Include units, physical meaning, valid options
   - Ensure reference_pressure is included for motor

#### MEDIUM PRIORITY

**6. Integrate Exports in `flight_simulator.py`**
   - Call `export_motor_state()` and `export_rocket_state()` for initial state
   - Call again for final state after flight simulation
   - Generate all plots and drawings
   - Update workflow to call new plot generation methods

**7. Create Documented Template**
   - File: `configs/templates/template_complete_documented.yaml`
   - Every parameter has inline comment
   - Grouped by logical sections
   - Include examples and best practices

#### LOW PRIORITY

**8. Implement Separate Report Generator**
   - NEW module: `src/report_generator.py`
   - Generates HTML/PDF report with:
     * Executive summary
     * All plots embedded
     * Analysis and interpretation
     * Performance metrics comparison
     * Recommendations
   - Output: `outputs/{name}/report.html` and `outputs/{name}/report.pdf`
   - **IMPORTANT**: Report is SEPARATE from state files

## File Structure (Final)

```
outputs/{rocket_name}/
├── initial_state.json              # Machine-readable initial state
├── initial_state_READABLE.txt      # Human-readable initial state
├── final_state.json                # Machine-readable final state
├── final_state_READABLE.txt        # Human-readable final state
│
├── curves/
│   ├── motor/
│   │   ├── thrust_curve.png ✅ (NEW - with annotations)
│   │   ├── mass_evolution.png
│   │   ├── mass_flow_rate.png
│   │   ├── center_of_mass.png
│   │   ├── exhaust_velocity.png
│   │   ├── grain_geometry.png
│   │   ├── grain_volume.png
│   │   ├── burn_characteristics.png
│   │   ├── kn_curve.png
│   │   ├── inertia_tensor.png
│   │   └── propellant_inertia_tensor.png
│   │
│   ├── rocket/ (NEW DIRECTORY - 17 plots)
│   │   ├── total_mass_vs_time.png
│   │   ├── mass_components_comparison.png
│   │   ├── mass_flow_rate_vs_time.png
│   │   ├── reduced_mass_vs_time.png
│   │   ├── center_of_mass_evolution.png
│   │   ├── com_to_cdm_vs_time.png
│   │   ├── inertia_lateral_vs_time.png
│   │   ├── inertia_axial_vs_time.png
│   │   ├── inertia_products_vs_time.png
│   │   ├── inertia_comparison.png
│   │   ├── drag_coefficients_vs_mach.png
│   │   ├── cp_position_vs_mach.png
│   │   ├── lift_coefficient_derivative_vs_mach.png
│   │   ├── static_margin_vs_time.png
│   │   ├── stability_margin_surface.png
│   │   ├── thrust_to_weight_vs_time.png
│   │   └── rocket_schematic.png
│   │
│   └── environment/
│       ├── wind_profile.png
│       └── atmospheric_profile.png
│
├── plots/ (NEW DIRECTORY - technical drawings)
│   ├── rocket_schematic.png (NEW - using rocket.draw())
│   └── motor_schematic.png (NEW - if available)
│
├── trajectory/
│   ├── {name}_trajectory.csv
│   └── {name}_summary.json
│
└── report/ (NEW - SEPARATE from state files)
    ├── report.html
    └── report.pdf
```

## Complete Rocket Attributes Classification

### Scalar Attributes (in .txt file)

#### Geometry
- radius, area
- coordinate_system_orientation

#### Mass
- mass (without motor)
- dry_mass (with unloaded motor)
- structural_mass_ratio

#### Positions
- center_of_mass_without_motor
- center_of_dry_mass_position
- motor_center_of_dry_mass_position
- motor_position, nozzle_position, nozzle_to_cdm

#### Inertia - Without Motor
- I_11_without_motor, I_22_without_motor, I_33_without_motor
- I_12_without_motor, I_13_without_motor, I_23_without_motor

#### Inertia - Dry (with unloaded motor)
- dry_I_11, dry_I_22, dry_I_33
- dry_I_12, dry_I_13, dry_I_23

#### Eccentricities
- cm_eccentricity_x, cm_eccentricity_y
- cp_eccentricity_x, cp_eccentricity_y
- thrust_eccentricity_x, thrust_eccentricity_y

#### Components (Lists/Nested Objects)
- aerodynamic_surfaces (nosecones, fins, tails)
- rail_buttons
- parachutes
- air_brakes
- _controllers
- sensors

### Function Attributes (plotted, NOT in .txt)

#### Mass Functions
- total_mass(t)
- propellant_mass(t)
- reduced_mass(t)
- total_mass_flow_rate(t)

#### Center of Mass Functions
- center_of_mass(t)
- motor_center_of_mass_position(t)
- center_of_propellant_position(t)
- com_to_cdm_function(t)

#### Inertia Functions
- I_11(t), I_22(t), I_33(t)
- I_12(t), I_13(t), I_23(t)

#### Aerodynamics Functions
- power_off_drag(Mach)
- power_on_drag(Mach)
- cp_position(Mach)
- total_lift_coeff_der(Mach)

#### Stability Functions
- static_margin(t)
- stability_margin(Mach, t)

#### Performance Functions
- thrust_to_weight(t)

## Configuration Parameters Checklist

### Motor Section
- ✅ thrust_source
- ✅ dry_mass, dry_inertia
- ✅ nozzle_radius, throat_radius
- ✅ grain parameters (for SolidMotor)
- ✅ coordinate_system_orientation
- ⚠️ **reference_pressure** - MUST ADD! (for pressure correction)

### Rocket Section
- ✅ radius
- ✅ mass (without motor)
- ✅ inertia (complete tensor)
- ✅ center_of_mass_without_motor
- ✅ coordinate_system_orientation
- ✅ power_off_drag, power_on_drag
- ⚠️ eccentricities (optional but should be documented)

### Aerodynamic Surfaces
- ✅ NoseCone: length, kind, position
- ✅ Fins: number, root_chord, tip_chord, span, position, cant_angle
- ✅ Tail: top_radius, bottom_radius, length, position
- ✅ RailButtons: upper_button_position, lower_button_position

### Recovery Systems
- ✅ Parachutes: name, cd_s, trigger, sampling_rate, lag
- ⚠️ AirBrakes: reference_area, drag_coefficient, controller (if present)

## Implementation Notes

### Key Design Decisions
1. **Separation of Concerns**: State files contain ONLY data, reports are separate
2. **Complete Coverage**: Export EVERY attribute, even if zero/None
3. **Human-Readable**: TXT files are well-formatted with units and sections
4. **Plot Quality**: High DPI (300), professional styling, clear annotations
5. **Error Handling**: Graceful degradation if attributes missing

### Code Patterns
- Use `try/except` for accessing potentially missing attributes
- Always include units in labels and annotations
- Consistent color schemes across related plots
- Save all plots as PNG with 300 DPI
- Use meaningful filenames

### Testing Checklist
- [ ] Run with minimal configuration (only required parameters)
- [ ] Run with complete configuration (all optional parameters)
- [ ] Verify all plots generate without errors
- [ ] Check READABLE.txt format and completeness
- [ ] Validate JSON structure
- [ ] Test with different motor types (Solid, Liquid, Hybrid)
- [ ] Test with/without air brakes
- [ ] Test with multiple parachutes

## Next Steps

1. **Implement Rocket Plots** (Priority HIGH)
   - Start with mass properties plots (easiest)
   - Then CoM plots
   - Then inertia plots
   - Finally aerodynamics and stability

2. **Add rocket.draw()** integration
   - Check RocketPy documentation
   - Implement fallback if not available

3. **Update 02_complete.yaml**
   - Add reference_pressure
   - Add comments for every parameter

4. **Integrate in flight_simulator.py**
   - Call new export functions
   - Generate all plots

5. **Create documented template**
   - Based on 02_complete.yaml
   - Add extensive comments

6. **Implement report generator** (Low priority)
   - Separate module
   - HTML/PDF output
   - Analysis and interpretation

## References
- RocketPy Documentation: https://docs.rocketpy.org/
- Copilot Instructions: `.github/copilot-instructions.md`
- Existing Implementation: `src/state_exporter.py`, `src/curve_plotter.py`
