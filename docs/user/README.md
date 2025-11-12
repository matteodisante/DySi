# User Documentation

Welcome to the rocket-sim user documentation! This directory contains comprehensive guides for using the rocket flight simulation package.

## 📚 Documentation Files

### Quick Start
- **[Getting Started](../../README.md)** - Installation and basic usage
- **[Examples](../../examples/)** - Working code examples

### Configuration
- **[CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md)** - Complete parameter reference
  - All YAML configuration parameters explained
  - Based on RocketPy official documentation
  - Includes typical values, units, and best practices
  - AI-generated additions marked with 🤖

### Results Interpretation
- **[PLOTS_AND_OUTPUT_REFERENCE.md](PLOTS_AND_OUTPUT_REFERENCE.md)** - Complete plots and output guide
  - All 30+ plots explained (motor, rocket, environment, trajectory)
  - State files reference (initial_state, final_state)
  - Trajectory data reference (CSV, JSON)
  - How to interpret and validate results
  - Based on RocketPy official plot documentation
  - AI-generated practical guidance marked with 🤖

### Motor Export Guide
- **[MOTOR_STATE_EXPORT_GUIDE.md](MOTOR_STATE_EXPORT_GUIDE.md)** - Motor state export feature
  - How motor state is exported
  - Parameter classifications and organization

### Troubleshooting
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## 🎯 Quick Reference

### Running a Simulation

```bash
# Single flight simulation
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --name my_simulation \
    --log-file simulation.log

# Monte Carlo simulation
python scripts/run_monte_carlo.py \
    --config configs/monte_carlo/01_basic_mc.yaml \
    --name my_monte_carlo
```

### Output Structure

After running a simulation, you'll find:

```
outputs/{simulation_name}/
├── simulation_YYYYMMDD_HHMMSS.log    # Execution log
├── initial_state.json                 # Initial conditions (JSON)
├── initial_state_READABLE.txt         # Initial conditions (human-readable)
├── final_state.json                   # Final state (JSON)
├── final_state_READABLE.txt           # Final state (human-readable)
├── curves/                            # Characteristic curves
│   ├── motor/       (11 plots)       # Motor performance curves
│   ├── rocket/      (14-17 plots)    # Rocket characteristics
│   └── environment/ (2 plots)        # Atmospheric conditions
├── trajectory/                        # Flight data
│   ├── {name}_trajectory.csv          # Time-series data
│   └── {name}_summary.json            # Key metrics
└── plots/                             # Trajectory visualizations
    ├── {name}_trajectory_2d.png       # Ground track
    ├── {name}_trajectory_3d.png       # 3D flight path
    ├── {name}_altitude.png            # Altitude vs time
    ├── {name}_velocity.png            # Velocity vs time
    └── {name}_acceleration.png        # Acceleration vs time
```

## 📖 Documentation Philosophy

This documentation follows these principles:

1. **RocketPy Foundation**: All technical content based on official RocketPy documentation
2. **Clear Attribution**: AI-generated additions clearly marked with 🤖
3. **Practical Guidance**: Real-world values, examples, and best practices
4. **Complete Coverage**: Every parameter, plot, and output file documented
5. **Validation Focus**: Emphasis on checking and interpreting results

## 🔍 Finding What You Need

### "I want to configure a simulation"
→ See [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md)
- Search for parameter name (e.g., "inertia_i", "root_chord")
- Check typical values and units
- Understand physical meaning and impact

### "I want to understand my results"
→ See [PLOTS_AND_OUTPUT_REFERENCE.md](PLOTS_AND_OUTPUT_REFERENCE.md)
- Check console summary interpretation
- Understand each plot (what it shows, what to look for)
- Validate results (common issues, quality checks)

### "Something went wrong"
→ See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Common error messages
- Validation failures
- Result anomalies

### "I want to learn by example"
→ See [examples/](../../examples/) and [notebooks/](../../notebooks/)
- Working code samples
- Step-by-step tutorials

## 📝 Documentation Coverage

### Configuration Parameters (CONFIGURATION_REFERENCE.md)
- ✅ Rocket: name, mass, radius, inertia, center_of_mass
- ✅ Nosecones: kind, length, position, base_radius
- ✅ Fins: n, root_chord, tip_chord, span, position, cant_angle, sweep
- ✅ Tails: top_radius, bottom_radius, length, position
- ✅ Parachutes: cd_s, trigger, lag, deploy_altitude
- ✅ Rail buttons: positions, angular_position
- ✅ Drag curves: power_on, power_off
- ✅ Motor: thrust_source, nozzle_radius, dry_mass, position
- ✅ Environment: latitude, longitude, elevation, atmospheric model
- ✅ Simulation: rail_length, inclination, heading, initial_solution

### Plots Reference (PLOTS_AND_OUTPUT_REFERENCE.md)

**Motor Plots (11):**
1. ✅ Thrust curve
2. ✅ Mass evolution
3. ✅ Center of mass evolution
4. ✅ Mass flow rate
5. ✅ Exhaust velocity
6. ✅ Inertia tensor
7. ✅ Grain geometry
8. ✅ Grain volume
9. ✅ Propellant inertia tensor
10. ✅ Kn curve
11. ✅ Burn characteristics

**Rocket Plots (14-17):**
1. ✅ Total mass vs time
2. ✅ Reduced mass vs time
3. ✅ Static margin vs time
4. ✅ Stability margin surface
5. ✅ Center of mass evolution
6. ✅ Center of pressure vs Mach
7. ✅ COM to CDM distance
8. ✅ Drag coefficients vs Mach
9. ✅ Inertia comparison
10. ✅ Inertia axial vs time
11. ✅ Inertia lateral vs time
12. ✅ Mass components comparison
13. ✅ Mass flow rate vs time
14. ✅ Rocket schematic
15. ✅ Thrust-to-weight ratio (optional)
16. ✅ Total lift coefficient derivative (optional)

**Environment Plots (2):**
1. ✅ Atmospheric profile
2. ✅ Wind profile

**Trajectory Plots (5):**
1. ✅ 2D trajectory
2. ✅ 3D trajectory
3. ✅ Altitude vs time
4. ✅ Velocity vs time
5. ✅ Acceleration vs time

**Output Files:**
- ✅ State files (initial/final, JSON/TXT)
- ✅ Trajectory CSV
- ✅ Summary JSON
- ✅ Log files

## 🔗 Related Documentation

- **Developer Documentation**: [docs/developer/](../developer/)
- **Implementation Details**: [docs/implementation/](../implementation/)
- **API Reference**: [docs/developer/MODULE_REFERENCE.md](../developer/MODULE_REFERENCE.md)

## 📞 Getting Help

1. **Check documentation** in this directory
2. **Review examples** in [examples/](../../examples/)
3. **Check RocketPy documentation**: https://docs.rocketpy.org/
4. **Search issues** on GitHub

## 🎓 Learning Path

**Beginner:**
1. Read main [README.md](../../README.md)
2. Try `examples/01_basic_simulation.py`
3. Browse [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) for parameter meanings
4. Check [PLOTS_AND_OUTPUT_REFERENCE.md](PLOTS_AND_OUTPUT_REFERENCE.md) to understand results

**Intermediate:**
1. Use [template_complete_documented.yaml](../../configs/templates/template_complete_documented.yaml)
2. Customize rocket parameters
3. Validate results using plot reference
4. Try Monte Carlo simulations

**Advanced:**
1. Create custom drag curves
2. Implement sensitivity analysis
3. Develop custom analysis scripts
4. Contribute to documentation

---

**Last Updated:** November 2024  
**Package Version:** 1.0  
**Based on:** RocketPy v1.x

For questions or corrections, please open an issue on GitHub.
