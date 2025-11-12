# Configuration Templates

This directory contains template configuration files for rocket simulations.

## Available Templates

### `template_complete_documented.yaml`
**Comprehensive template with extensive inline documentation**

- Contains ALL available configuration parameters
- Each parameter includes:
  - Physical meaning and purpose
  - Units of measurement
  - Typical values and ranges
  - Available options
  - Usage notes
- Best for: Learning the system, understanding all options, creating complex configurations

**Use this when:**
- Setting up a new rocket design from scratch
- You need to understand what each parameter does
- You want to explore all available features
- Creating a reference configuration

### How to Use

1. **Copy the template:**
   ```bash
   cp configs/templates/template_complete_documented.yaml configs/single_sim/my_rocket.yaml
   ```

2. **Customize for your rocket:**
   - Update rocket name and basic properties
   - Set mass and inertia values from CAD or measurements
   - Define aerodynamic surfaces (nose cone, fins, tail)
   - Configure motor parameters
   - Set launch site location and environment
   - Adjust simulation settings

3. **Run simulation:**
   ```bash
   python examples/01_basic_simulation.py --config configs/single_sim/my_rocket.yaml
   ```

## Parameter Categories

### Rocket Configuration
- **Mass properties**: dry_mass, inertia tensor (I_xx, I_yy, I_zz, products)
- **Geometry**: caliber, length, coordinate system
- **Aerodynamics**: nose cone, fins, tail, custom drag curves
- **Stability**: center of mass, center of pressure, eccentricities
- **Recovery**: parachute configuration
- **Active control**: air brakes (optional)

### Motor Configuration
- **Type**: SolidMotor, HybridMotor, LiquidMotor
- **Performance**: thrust curve, burn time
- **Mass**: dry mass, propellant properties
- **Geometry**: nozzle, throat, grain configuration
- **Critical**: reference_pressure for altitude correction

### Environment Configuration
- **Location**: latitude, longitude, elevation
- **Atmosphere**: standard or custom model
- **Wind**: constant, weather-based, or custom
- **Gravity**: local gravitational acceleration

### Simulation Settings
- **Integration**: time steps, tolerances
- **Launch rail**: length, inclination, heading
- **Termination**: conditions for stopping simulation
- **Output**: verbosity, export options

## Tips for Success

### 1. Start Simple
Begin with minimal required parameters, then add complexity:
```yaml
rocket:
  name: "TestRocket"
  dry_mass_kg: 15.0
  inertia:
    ixx_kg_m2: 6.0
    iyy_kg_m2: 6.0
    izz_kg_m2: 0.03
  # ... add more as needed
```

### 2. Validate Your Design
Before running full simulations:
- Check static stability margin (should be 1.5-3.0 calibers)
- Verify thrust-to-weight ratio at liftoff (minimum 5:1)
- Ensure rail velocity is adequate (> 15 m/s typically)

### 3. Use Reference Pressure Correctly
**Critical for accurate results!**
```yaml
motor:
  reference_pressure: 101325  # Pa - if thrust measured at sea level
  # reference_pressure: 0      # Pa - if thrust measured in vacuum
```

### 4. Coordinate Systems Matter
**Rocket:** `nose_to_tail` (origin at nose, positive toward tail)
**Motor:** `nozzle_to_combustion_chamber` (origin at nozzle exit)

All positions in rocket frame measured from nose.

### 5. Inertia Tensor for Symmetric Rockets
For axially symmetric designs:
```yaml
inertia:
  ixx_kg_m2: 6.0    # Lateral
  iyy_kg_m2: 6.0    # Lateral (equal to I_xx)
  izz_kg_m2: 0.03   # Axial (much smaller)
  # Products all zero for symmetric rockets
  ixy_kg_m2: 0.0
  ixz_kg_m2: 0.0
  iyz_kg_m2: 0.0
```

### 6. Monte Carlo for Uncertainty
Add uncertainty quantification:
```yaml
monte_carlo:
  num_simulations: 100
  variations:
    motor_thrust_std_pct: 5.0      # ±5% thrust uncertainty
    wind_speed_std_ms: 2.0         # ±2 m/s wind variation
    dry_mass_std_kg: 0.5           # ±0.5 kg mass uncertainty
```

## Common Issues and Solutions

### Issue: Unstable Flight
**Check:**
- Static margin (CoP should be behind CoM by 1.5-3 calibers)
- Fin size and position
- Mass distribution

### Issue: Incorrect Apogee
**Check:**
- Motor reference_pressure setting
- Drag coefficient values
- Mass properties accuracy
- Wind conditions

### Issue: Rail Departure Too Slow
**Check:**
- Rail length (increase to 5-8m)
- Thrust-to-weight ratio
- Total mass (reduce if possible)

### Issue: Simulation Fails
**Check:**
- All required parameters present
- Coordinate systems consistent
- File paths correct
- Units correct (meters, kg, seconds)

## Additional Resources

- **RocketPy Documentation**: https://docs.rocketpy.org/
- **Example Configurations**: See `configs/single_sim/` directory
- **Implementation Plan**: `docs/implementation/ROCKET_STATE_EXPORT_IMPLEMENTATION_PLAN.md`
- **GitHub Issues**: Report problems or ask questions

## Version History

- **v1.0** (2024-11-12): Initial comprehensive template with complete documentation
  - All rocket parameters documented
  - All motor parameters documented
  - Environment and simulation settings
  - Monte Carlo configuration
  - Extensive inline comments
