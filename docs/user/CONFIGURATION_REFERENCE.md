# Configuration Reference - Complete Parameter Guide

**Based on:** RocketPy v1.x Official Documentation  
**Last Updated:** November 2024  
**Document Type:** Complete Reference Manual

> **Note:** This document integrates official RocketPy documentation with additional explanations. 
> Sections marked with 🤖 contain AI-generated supplementary information to provide context and practical guidance.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Configuration File Structure](#configuration-file-structure)
3. [Rocket Parameters](#rocket-parameters)
4. [Motor Parameters](#motor-parameters)
5. [Environment Parameters](#environment-parameters)
6. [Simulation Parameters](#simulation-parameters)
7. [Output Reference](#output-reference)
8. [Plot Reference](#plot-reference)

---

## 1. Introduction

This document provides **complete documentation** for all configuration parameters used in rocket-sim, based on RocketPy's official API documentation.

### Quick Reference

```yaml
# Minimal working configuration
rocket:
  name: "MyRocket"
  mass: 10.0        # kg, dry mass without motor
  radius: 0.0635    # m, body tube radius
  # ... (see full reference below)

motor:
  thrust_source: "data/motors/motor.eng"
  # ... (motor parameters)

environment:
  latitude: 39.3897
  longitude: -8.2889
  # ... (environment parameters)

simulation:
  inclination: 85   # degrees from horizontal
  heading: 90       # degrees (0=North, 90=East)
```

---

## 2. Configuration File Structure

The configuration is divided into four main sections:

```yaml
rocket:          # Rocket geometry, mass properties, aerodynamics
motor:           # Motor thrust curve and properties  
environment:     # Launch site conditions, atmosphere, wind
simulation:      # Launch conditions and simulation settings
```

---

## 3. Rocket Parameters

### 3.1 Basic Properties

#### `name` (string, required)
**RocketPy Documentation:**
- Rocket identification string
- Used in plots and output files

🤖 **Additional Context:**
- **Recommendation**: Use descriptive names without spaces (e.g., `"Hermes"`, `"TestRocket_v2"`)
- **Impact**: Determines output folder name (`outputs/{name}/`)
- **Examples**: `"Artemis"`, `"Calisto"`, `"NDRT_2020"`

#### `radius` (float, required)
**RocketPy Documentation:**
- Rocket outer radius in meters
- Used as reference for aerodynamic calculations
- Units: meters

🤖 **Additional Context:**
- **Measurement**: Outer diameter of body tube / 2
- **Typical Values**:
  - Model rockets: 0.020 - 0.040 m (2-4 cm)
  - High-power rockets: 0.040 - 0.100 m (4-10 cm)  
  - Research rockets: 0.100 - 0.300 m (10-30 cm)
- **Impact**: Affects drag area, stability calibers, fin sizing
- **Related Outputs**: Static margin (in calibers = body diameters)

#### `mass` (float, required)
**RocketPy Documentation:**
- Total mass of the rocket WITHOUT propellant in kg
- Includes: airframe, fins, nosecone, recovery, avionics, motor casing (empty)
- Excludes: Motor propellant (added by RocketPy automatically)
- Units: kilograms

🤖 **Additional Context:**
- **Measurement**: Weigh complete rocket with empty motor
- **Typical Mass Ratios**:
  - Propellant mass ≈ 20-40% of total launch mass
  - Empty rocket mass ≈ 60-80% of total launch mass
- **Impact**: Primary driver of acceleration and apogee
  - Lighter rocket → higher apogee
  - Heavier rocket → lower acceleration, lower apogee
- **Validation**: Check that `mass + motor.propellant_mass` matches launch weight

#### `inertia_i` (float, required)
**RocketPy Documentation:**
- Rocket's moment of inertia around lateral axis (perpendicular to rocket axis)
- Also called I_11 and I_22 (pitch and yaw inertia)
- Units: kg·m²

🤖 **Additional Context:**
- **Physics**: Resistance to rotation in pitch/yaw (wobbling)
- **Calculation**: `I = Σ(m_i × r_i²)` where r_i is distance from center of mass
- **Typical Values**:
  - Small rockets (< 5 kg): 0.01 - 0.05 kg·m²
  - Medium rockets (5-15 kg): 0.05 - 0.20 kg·m²
  - Large rockets (> 15 kg): 0.20 - 1.00 kg·m²
- **Estimation**: For slender rockets: `I ≈ (1/12) × mass × length²`
- **Impact**: Affects attitude stability, response to wind gusts
- **Related Plots**: `rocket/inertia_lateral_vs_time.png`

#### `inertia_z` (float, required)
**RocketPy Documentation:**
- Rocket's moment of inertia around longitudinal axis (rocket centerline)
- Also called I_33 (roll inertia)
- Units: kg·m²

🤖 **Additional Context:**
- **Physics**: Resistance to rotation around rocket axis (rolling)
- **Typical Values**: Usually 1/10 to 1/5 of `inertia_i`
  - Small rockets: 0.001 - 0.010 kg·m²
  - Medium rockets: 0.010 - 0.050 kg·m²
  - Large rockets: 0.050 - 0.200 kg·m²
- **Estimation**: For cylindrical rockets: `I_z ≈ (1/2) × mass × radius²`
- **Impact**: Affects roll rate, spin stabilization
- **Related Plots**: `rocket/inertia_axial_vs_time.png`

#### `center_of_mass_without_motor` (float, required)
**RocketPy Documentation:**
- Position of the rocket's center of mass without motor
- Measured from the rocket's coordinate system origin (user-defined)
- Typically measured from rocket tail (nozzle end)
- Units: meters

🤖 **Additional Context:**
- **Measurement**: Balance empty rocket horizontally to find balance point
- **Coordinate System**: 
  - Origin at rocket tail (position = 0.0 m)
  - Positive direction toward nosecone
  - Example: COM at 0.8 m means 0.8 m from tail toward nose
- **Typical Position**: 40-60% of total rocket length from tail
- **Critical for Stability**: Must be AHEAD of center of pressure
- **Validation**: Static margin = (CP - COM) / (2 × radius) should be > 1.0
- **Related Plots**: `rocket/center_of_mass_evolution.png`, `rocket/static_margin_vs_time.png`

---

### 3.2 Coordinate System

**RocketPy Coordinate System:**
- **Origin**: User-defined (typically at rocket tail/nozzle)
- **X-axis**: Perpendicular to rocket axis (lateral)
- **Y-axis**: Perpendicular to rocket axis (lateral)
- **Z-axis**: Along rocket centerline
  - Positive direction: Tail → Nosecone
  - Position 0.0 m: Rocket tail
  - Position = rocket length: Rocket nose

🤖 **Visualization:**
```
      ▲ Z+ (toward nose)
      |
    [===]  ← Nosecone (position = 1.5 m)
    [   ]
    [   ]  ← Body tube
    [   ]
    [/|\]  ← Fins (position ≈ 0.2 m)
    [===]  ← Motor
      ↑
    Origin (Z = 0.0 m, tail/nozzle)
```

---

### 3.3 Aerodynamic Surfaces

#### `nosecones` (list of dict, required)

Each nosecone entry contains:

##### `kind` (string, required)
**RocketPy Documentation:**
- Nosecone shape profile
- Available options:
  - `"vonKarman"`: Von Kármán ogive (minimum drag, recommended)
  - `"conical"`: Cone shape
  - `"ogive"`: Tangent ogive
  - `"elliptical"`: Elliptical profile
  - `"parabolic"`: Parabolic profile  
  - `"lvhaack"`: LV-Haack profile (minimum wave drag for supersonic)
  - `"powerseries"`: Power series profile
  - `"haack"`: Haack series profile

🤖 **Additional Context:**
- **Drag Performance Ranking** (subsonic):
  1. `"vonKarman"` - Best (lowest drag)
  2. `"ogive"` - Good
  3. `"elliptical"` - Moderate
  4. `"parabolic"` - Moderate
  5. `"conical"` - Highest drag
- **Recommendation**: Use `"vonKarman"` for general-purpose high-power rockets
- **Supersonic**: Use `"lvhaack"` for supersonic flight (M > 1.2)
- **Impact**: Can affect apogee by 5-15% depending on shape

##### `length` (float, required)
**RocketPy Documentation:**
- Nosecone length from tip to base
- Units: meters

🤖 **Additional Context:**
- **Fineness Ratio**: `length / diameter` determines drag
  - Low fineness (< 3): Higher drag, more stability
  - Optimal fineness (3-5): Best drag performance
  - High fineness (> 5): Marginal drag benefit, structural issues
- **Typical Values**:
  - Von Kármán/Ogive: 2-4 × body diameter
  - Conical: 3-5 × body diameter
  - Elliptical: 1.5-3 × body diameter
- **Example**: For 0.1 m diameter rocket → 0.2-0.4 m length

##### `position` (float, required)
**RocketPy Documentation:**
- Position of nosecone base measured from coordinate system origin
- Units: meters

🤖 **Additional Context:**
- **Typical Value**: Should equal total rocket length (at front end)
- **Example**: 1.5 m long rocket → `position: 1.5`
- **Purpose**: Defines mass distribution for inertia calculations

##### `base_radius` (float, optional)
**RocketPy Documentation:**
- Radius of nosecone at base (if different from body tube)
- Defaults to rocket radius if not specified
- Units: meters

##### `rocket_radius` (float, optional)
**RocketPy Documentation:**
- Reference radius for nosecone aerodynamic calculations
- Defaults to rocket radius if not specified
- Units: meters

---

#### `fins` (list of dict, required)

Each fin set entry contains:

##### `n` (integer, required)
**RocketPy Documentation:**
- Number of fins in the set
- Common values: 3 or 4

🤖 **Additional Context:**
- **3 fins**: Minimum for stability (120° spacing)
  - Advantages: Lower drag, lighter weight
  - Disadvantages: Less stability margin
- **4 fins**: Most common (90° spacing)
  - Advantages: Better stability, easier to align
  - Disadvantages: Slightly higher drag
- **6+ fins**: Rare (used for very small fins or special requirements)
- **Impact**: More fins = more stability but also more drag

##### `root_chord` (float, required)
**RocketPy Documentation:**
- Length of fin at root (where it attaches to body tube)
- Units: meters

🤖 **Additional Context:**
- **Design Rule**: Typically 1.5-3 times body diameter
- **Typical Values**:
  - Small rockets: 0.08 - 0.15 m
  - Medium rockets: 0.15 - 0.30 m
  - Large rockets: 0.30 - 0.60 m
- **Structural**: Must be long enough for strong attachment
- **Aerodynamic**: Primary determinant of fin lift and CP location
- **Impact**: Longer root chord → CP moves aft → more stability

##### `tip_chord` (float, required)
**RocketPy Documentation:**
- Length of fin at tip (trailing edge)
- Units: meters

🤖 **Additional Context:**
- **Taper Ratio**: `tip_chord / root_chord`
  - Rectangular fins: ratio = 1.0
  - Tapered fins: ratio = 0.3-0.7 (reduces drag)
  - Clipped delta: ratio = 0.0 (pointed tip)
- **Recommendation**: Use taper ratio of 0.4-0.6 for good drag/stability balance
- **Impact**: Taper reduces weight and drag with minimal stability loss

##### `span` (float, required)
**RocketPy Documentation:**
- Height of fin from body surface to tip (semi-span)
- Units: meters

🤖 **Additional Context:**
- **Design Rule**: Typically 0.5-1.5 times body radius
- **Typical Values**:
  - Small rockets: 0.04 - 0.08 m
  - Medium rockets: 0.08 - 0.15 m
  - Large rockets: 0.15 - 0.30 m
- **Limitations**:
  - Too short: Insufficient stability
  - Too long: Risk of flutter, breakage at high speeds
- **Flutter Speed**: `V_flutter ≈ K × √(G × t³ / (ρ × span²))` where:
  - G = shear modulus of fin material
  - t = fin thickness
  - ρ = air density
  - K = empirical constant
- **Impact**: PRIMARY driver of center of pressure location and stability

##### `position` (float, required)
**RocketPy Documentation:**
- Position of fin root leading edge measured from coordinate system origin
- Units: meters

🤖 **Additional Context:**
- **Typical Position**: Near rocket tail, about 0.1-0.3 m from tail
- **Stability Rule**: Fins must be BEHIND center of mass
- **Example**: For 1.5 m rocket → `position: 0.15` (15 cm from tail)
- **Impact**: Critical for stability margin
  - Fins too far forward: Unstable rocket
  - Fins too far aft: Excessive stability (weathercocking)
- **Related Outputs**: Static margin calculation uses fin CP location

##### `cant_angle` (float, optional)
**RocketPy Documentation:**
- Cant angle in degrees for inducing roll
- Positive angle causes clockwise roll (viewed from tail)
- Default: 0 degrees (no cant)
- Units: degrees

🤖 **Additional Context:**
- **Purpose**: Create spin for gyroscopic stabilization
- **Typical Values**:
  - 0°: No roll (most common)
  - 2-5°: Moderate spin rate
  - 5-10°: High spin (passive stabilization)
- **Trade-offs**:
  - Advantages: Gyroscopic stability, averages out asymmetries
  - Disadvantages: Increased drag, reduced apogee altitude
- **Use Case**: Alternative to active stabilization for simple rockets

##### `sweep_length` (float, optional)
**RocketPy Documentation:**
- Sweep length (horizontal distance from root LE to tip LE)
- Default: None (straight leading edge)
- Units: meters

##### `sweep_angle` (float, optional)
**RocketPy Documentation:**
- Sweep angle of fin leading edge
- Default: None
- Units: degrees

🤖 **Additional Context:**
- **Purpose**: Delay transonic drag rise, reduce wave drag
- **Typical Values**:
  - 0°: No sweep (subsonic rockets)
  - 20-30°: Moderate sweep (transonic)
  - 30-45°: High sweep (supersonic)
- **Impact**: Most significant at transonic speeds (M = 0.8-1.2)

##### `rocket_radius` (float, optional)
**RocketPy Documentation:**
- Body tube radius at fin attachment point
- Defaults to rocket radius if not specified
- Units: meters

---

#### `tails` (list of dict, optional)

Tail sections (boat tails, tail cones) for drag reduction.

##### `top_radius` (float, required)
**RocketPy Documentation:**
- Radius at top of tail section
- Units: meters

##### `bottom_radius` (float, required)
**RocketPy Documentation:**
- Radius at bottom of tail section
- Units: meters

🤖 **Additional Context:**
- **Purpose**: Reduce base drag by tapering body
- **Typical Ratio**: `bottom_radius = 0.6-0.8 × top_radius`
- **Benefit**: Can reduce drag by 5-15% at high speeds

##### `length` (float, required)
**RocketPy Documentation:**
- Length of tail section
- Units: meters

🤖 **Additional Context:**
- **Typical Length**: 1-3 times body radius
- **Principle**: Longer taper = smoother flow = less drag

##### `position` (float, required)
**RocketPy Documentation:**
- Position of tail section top measured from coordinate system origin
- Units: meters

🤖 **Additional Context:**
- **Typical Position**: At or near rocket tail (0.0-0.2 m from tail end)

---

### 3.4 Parachutes

#### `parachutes` (list of dict, optional)

Each parachute entry contains:

##### `name` (string, required)
**RocketPy Documentation:**
- Parachute identifier
- Common names: "Drogue", "Main", "Pilot"

##### `cd_s` (float, required)
**RocketPy Documentation:**
- Product of drag coefficient and reference area: CD × S
- Units: m²

🤖 **Additional Context:**
- **Calculation**: `cd_s = CD × π × r²` where:
  - CD ≈ 1.5 for round parachutes (typical)
  - CD ≈ 2.2 for cruciform parachutes
  - r = parachute radius
- **Example Calculation**:
  - Parachute diameter = 1.0 m → radius = 0.5 m
  - Area = π × (0.5)² = 0.785 m²
  - cd_s = 1.5 × 0.785 = 1.18 m²
- **Descent Rate**: `v = sqrt(2 × m × g / (ρ × cd_s))`
  - For 10 kg rocket, cd_s = 1.0 m²: v ≈ 14 m/s (unsafe)
  - For 10 kg rocket, cd_s = 3.0 m²: v ≈ 8 m/s (safe)
- **Typical Values**:
  - Drogue: 0.1 - 0.5 m² (high-speed descent)
  - Main: 1.0 - 5.0 m² (low-speed landing)

##### `trigger` (string, required)
**RocketPy Documentation:**
- Deployment trigger condition
- Options:
  - `"apogee"`: Deploy at maximum altitude
  - `"altitude"`: Deploy at specified altitude AGL
  - `"time"`: Deploy at specified time after launch

🤖 **Additional Context:**
- **Typical Strategy**:
  - Drogue: `trigger: "apogee"` - Deploy at peak for stabilized descent
  - Main: `trigger: "altitude"`, `deploy_altitude: 300` - Deploy low for accuracy
- **Safety**: Main chute should deploy high enough to ensure full inflation before landing

##### `sampling_rate` (integer, required)
**RocketPy Documentation:**
- Sampling rate for trigger condition checking
- Units: Hertz (Hz)

🤖 **Additional Context:**
- **Typical Value**: 100-105 Hz
- **Impact**: Higher rate = more accurate trigger detection
- **Recommendation**: 100 Hz is adequate for most applications

##### `lag` (float, required)
**RocketPy Documentation:**
- Time delay between trigger and full deployment
- Accounts for ejection charge, extraction, and inflation time
- Units: seconds

🤖 **Additional Context:**
- **Components of Lag**:
  1. Ejection charge ignition: 0.1-0.3 s
  2. Parachute extraction: 0.2-0.5 s
  3. Parachute inflation: 0.3-2.0 s
- **Typical Total Lag**:
  - Electronic deployment: 0.5 - 1.0 s
  - Mechanical deployment: 1.0 - 2.0 s
  - Large parachutes: 1.5 - 3.0 s
- **Impact**: Affects actual deployment altitude
  - Example: Trigger at 300 m, lag = 2 s, falling at 30 m/s → deploys at 240 m

##### `deploy_altitude` (float, conditional)
**RocketPy Documentation:**
- Altitude AGL (Above Ground Level) for deployment
- Required if `trigger: "altitude"`
- Units: meters

##### `deploy_time` (float, conditional)
**RocketPy Documentation:**
- Time after launch for deployment
- Required if `trigger: "time"`
- Units: seconds

##### `noise` (list of 3 floats, optional)
**RocketPy Documentation:**
- Measurement noise parameters: `[mean, std_dev, time_correlation]`
- Used for Monte Carlo simulations with sensor uncertainty
- Default: `[0, 0, 0]` (perfect measurement)

---

### 3.5 Drag Curves

#### `drag_curves` (string or list, optional)
**RocketPy Documentation:**
- Path(s) to CSV file(s) containing drag coefficient vs Mach number
- Format: CSV with columns `Mach, CD`
- If not provided, RocketPy calculates drag from geometry

🤖 **Additional Context:**
- **When to Provide**: Use custom drag curves if you have:
  - Wind tunnel data
  - CFD simulation results
  - Empirical flight data
- **Default Behavior**: RocketPy uses Barrowman equations to estimate CD
- **CSV Format Example**:
  ```csv
  Mach,CD
  0.0,0.35
  0.3,0.36
  0.5,0.38
  0.8,0.45
  0.9,0.65  # Transonic drag rise
  1.0,0.85  # Peak drag
  1.2,0.60
  2.0,0.50
  ```
- **Impact**: Accurate drag curves critical for apogee prediction

#### `power_off_drag` (string, optional)
**RocketPy Documentation:**
- Drag curve for coasting flight (motor burned out)
- Format: same as `drag_curves`

🤖 **Additional Context:**
- **Difference from powered drag**: Base drag changes without exhaust plume
- **Typical Effect**: Power-off CD ≈ 5-15% higher than power-on CD

#### `power_on_drag` (string, optional)
**RocketPy Documentation:**
- Drag curve during powered flight (motor burning)
- Format: same as `drag_curves`

🤖 **Additional Context:**
- **Physical Effect**: Exhaust plume reduces base drag
- **Typical Effect**: Power-on CD ≈ 5-15% lower than power-off CD

---

### 3.6 Rail Buttons

#### `rail_buttons` (list of dict, required)

**RocketPy Documentation:**
- Rail buttons guide the rocket on the launch rail
- Ensures straight launch trajectory

##### `upper_button_position` (float, required)
**RocketPy Documentation:**
- Position of upper rail button from coordinate origin
- Units: meters

🤖 **Additional Context:**
- **Typical Position**: Near nosecone, about 0.1-0.3 m from nose
- **Purpose**: Provides moment arm for rail guidance stability

##### `lower_button_position` (float, required)
**RocketPy Documentation:**
- Position of lower rail button from coordinate origin
- Units: meters

🤖 **Additional Context:**
- **Typical Position**: Near tail, above fins
- **Design Rule**: Maximize separation between buttons for stability
- **Recommended Separation**: > 50% of rocket length

##### `angular_position` (float, required)
**RocketPy Documentation:**
- Angular position of buttons around rocket body
- Units: degrees (0-360)

🤖 **Additional Context:**
- **Typical Value**: 45° or 90° offset from fin cant direction
- **Purpose**: Prevents interference with fins during rail exit

---

## 4. Motor Parameters

### 4.1 Motor Type and Thrust

#### `motor_type` (string, required)
**RocketPy Documentation:**
- Type of rocket motor
- Options: `"solid"`, `"hybrid"`, `"liquid"`

🤖 **Additional Context:**
- **Current Support**: Primarily `"solid"` motors fully supported
- **File Format Compatibility**:
  - Solid: `.eng` (RASP), `.rse` (RockSim)
  - Hybrid/Liquid: Requires additional parameters

#### `thrust_source` (string, required)
**RocketPy Documentation:**
- Path to thrust curve data file
- Supported formats:
  - `.eng`: RASP engine file format (most common)
  - `.rse`: RockSim engine format
  - `.csv`: Custom CSV format (time, thrust)

🤖 **Additional Context:**
- **Data Sources**:
  - ThrustCurve.org (download .eng files)
  - Motor manufacturer test data
  - Custom ground test measurements
- **File Format (.eng)**:
  ```
  ; Comment line
  Motor_Name diameter length delays propellant_weight total_weight manufacturer
  time1 thrust1
  time2 thrust2
  ...
  ```
- **Impact**: Thrust curve is THE primary driver of flight performance

##### (continued in next section...)