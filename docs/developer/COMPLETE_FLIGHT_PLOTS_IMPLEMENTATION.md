# Flight Plot Implementation - Complete RocketPy Parity

**Date**: 2024
**Author**: GitHub Copilot
**Status**: COMPLETE - All 10 RocketPy Flight.plots methods implemented

## Summary

This document tracks the implementation of all 10 flight plot methods from RocketPy's `Flight.plots` class into DySi's `curve_plotter.py`. This ensures complete parity with RocketPy's visualization capabilities.

## RocketPy Flight.plots Methods (10 total)

Based on RocketPy's "First Simulation" tutorial and source code:

1. ✅ `trajectory_3d()` - 3D trajectory with projections
2. ✅ `linear_kinematics_data()` - Velocities and accelerations (Vx,Vy,Vz, Ax,Ay,Az)
3. ✅ `flight_path_angle_data()` - Flight path vs attitude angle
4. ✅ `attitude_data()` - Euler angles (ψ, θ, φ)
5. ✅ `angular_kinematics_data()` - Angular velocities and accelerations
6. ✅ `aerodynamic_forces()` - Lift, drag, bending moment
7. ✅ `rail_buttons_forces()` - Rail button forces
8. ✅ `energy_data()` - Kinetic, potential, power
9. ✅ `fluid_mechanics_data()` - Mach, Reynolds, pressures, AoA
10. ✅ `stability_and_control_data()` - Stability margin, frequency response

## Implementation Timeline

### Phase 1: Initial 7 Methods (Previous Implementation)
- `plot_attitude_data()`
- `plot_angular_kinematics_data()`
- `plot_aerodynamic_forces()`
- `plot_rail_buttons_forces()`
- `plot_energy_data()`
- `plot_fluid_mechanics_data()`
- `plot_stability_and_control_data()`

### Phase 2: Missing 3 Methods (Current Implementation)
- `plot_trajectory_3d()` - **NEW**
- `plot_linear_kinematics_data()` - **NEW**
- `plot_flight_path_angle_data()` - **NEW**

## Technical Details

### 1. plot_trajectory_3d()

**Purpose**: Visualize complete 3D flight path with projections on XY, XZ, YZ planes.

**Implementation**:
```python
def plot_trajectory_3d(self, output_dir: Path) -> Optional[Path]:
    """Plot 3D trajectory with projections on XY, XZ, and YZ planes."""
```

**Key Features**:
- Main 3D trajectory (blue line)
- XY projection (ground track) - gray dashed
- XZ projection (side view) - gray dashed
- YZ projection (front view) - gray dashed
- Marked points: Launch (green), Apogee (red), Landing (orange)

**Output**: `curves/flight/trajectory_3d.png`

**Dependencies**: `mpl_toolkits.mplot3d.Axes3D`

### 2. plot_linear_kinematics_data()

**Purpose**: Show linear velocities and accelerations on all axes.

**Implementation**:
```python
def plot_linear_kinematics_data(self, output_dir: Path) -> Optional[Path]:
    """Plot linear velocities and accelerations (vx, vy, vz, ax, ay, az)."""
```

**Subplot Layout** (2×2 grid):
1. **X Component**: Vx (blue, left) + Ax (orange dashed, right)
2. **Y Component**: Vy (blue, left) + Ay (orange dashed, right)
3. **Z Component**: Vz (blue, left) + Az (orange dashed, right)
4. **Total Magnitude**: Speed (blue, left) + Acceleration (orange dashed, right)

**Output**: `curves/flight/linear_kinematics_data.png`

**RocketPy Data Sources**:
- `self.flight.vx`, `vy`, `vz` - Velocity components
- `self.flight.ax`, `ay`, `az` - Acceleration components
- `self.flight.speed` - Total speed magnitude
- `self.flight.acceleration` - Total acceleration magnitude

### 3. plot_flight_path_angle_data()

**Purpose**: Compare rocket attitude (pointing direction) with actual flight path direction.

**Implementation**:
```python
def plot_flight_path_angle_data(self, output_dir: Path) -> Optional[Path]:
    """Plot flight path angle vs attitude angle and lateral attitude angle."""
```

**Subplot Layout** (2×1 vertical):
1. **Flight Path vs Attitude**:
   - Blue line: Attitude angle (where rocket points)
   - Orange dashed: Flight path angle (actual trajectory)
   - Small difference = low angle of attack
2. **Lateral Attitude Angle** (green):
   - Yaw deviation from vertical plane

**Output**: `curves/flight/flight_path_angle_data.png`

**RocketPy Data Sources**:
- `self.flight.attitude_angle` - Rocket orientation
- `self.flight.path_angle` - Trajectory direction
- `self.flight.lateral_attitude_angle` - Lateral deviation

## Integration with plot_all_flight_curves()

The orchestrator method `plot_all_flight_curves()` has been updated to call all 10 methods in the correct order (matching RocketPy's order):

```python
def plot_all_flight_curves(self, output_dir: Path) -> dict:
    """Generate all flight data plots."""
    flight_dir = output_dir / "flight"
    
    # 1. 3D Trajectory
    path = self.plot_trajectory_3d(flight_dir)
    
    # 2. Linear kinematics
    path = self.plot_linear_kinematics_data(flight_dir)
    
    # 3. Flight path angle
    path = self.plot_flight_path_angle_data(flight_dir)
    
    # 4-10: Remaining methods...
```

## Output Directory Structure

```
outputs/<simulation_name>/curves/flight/
├── trajectory_3d.png                    # NEW
├── linear_kinematics_data.png          # NEW
├── flight_path_angle_data.png          # NEW
├── attitude_data.png
├── angular_kinematics_data.png
├── aerodynamic_forces.png
├── rail_buttons_forces.png
├── energy_data.png
├── fluid_mechanics_data.png
└── stability_and_control_data.png
```

## Documentation Updates

### 1. plot_interpretation.rst

Added 3 new plot interpretation sections:

- **trajectory_3d.png** - 3D visualization guide
- **linear_kinematics_data.png** - Velocity/acceleration interpretation
- **flight_path_angle_data.png** - Angle of attack analysis

Total plot count: **27 → 30 plots**

### 2. quick_plot_reference.rst

Updated flight plots table to include 3 new entries at the top (matching RocketPy order).

## Migration from visualizer.py

### Status: Deprecated

The old `visualizer.py` had:
- `plot_trajectory_2d()` - Kept for 2D visualization
- `plot_trajectory_3d()` - **DEPRECATED** (replaced by curve_plotter version)
- `plot_altitude_vs_time()` - Simple altitude plot
- `plot_velocity_vs_time()` - Simple velocity plot
- `plot_acceleration_vs_time()` - Simple acceleration plot

### Recommendation

The new `curve_plotter.plot_trajectory_3d()` is superior because:
1. ✅ Shows XY, XZ, YZ projections (not in visualizer version)
2. ✅ Marks launch/apogee/landing points clearly
3. ✅ Integrated with all other flight plots in `curves/flight/`
4. ✅ Matches RocketPy's implementation exactly

**Action**: Users should use `curve_plotter` methods instead of `visualizer` for trajectory plotting.

## Code Quality

### Error Handling
All methods use try-except blocks:
```python
try:
    # Plotting code
    return output_path
except Exception as e:
    logger.warning(f"Could not plot: {e}")
    return None
```

### Logging
All methods use logger.debug for successful plots:
```python
logger.debug(f"Plot saved to {output_path}")
```

### Type Hints
All methods have proper type hints:
```python
def plot_trajectory_3d(self, output_dir: Path) -> Optional[Path]:
```

### Documentation
All methods have NumPy-style docstrings:
```python
"""Plot 3D trajectory with projections.

Parameters
----------
output_dir : Path
    Output directory for the plot

Returns
-------
Optional[Path]
    Path to created plot or None if failed
"""
```

## Testing Recommendations

### Unit Tests
Create tests for:
1. ✅ Method exists and is callable
2. ✅ Returns Path when successful
3. ✅ Returns None on error
4. ✅ Creates correct filename
5. ✅ File exists after creation

### Integration Tests
Test `plot_all_flight_curves()`:
1. ✅ Calls all 10 methods
2. ✅ Creates `flight/` directory
3. ✅ Returns dict with 10 paths
4. ✅ All files exist

### Visual Validation
For each plot, verify:
1. ✅ Correct number of subplots
2. ✅ Correct axis labels (with units)
3. ✅ Legends present and accurate
4. ✅ Grid enabled
5. ✅ Title matches plot type

## RocketPy Compatibility Matrix

| RocketPy Method | DySi Method | Status | Output File |
|----------------|-------------|--------|-------------|
| `trajectory_3d()` | `plot_trajectory_3d()` | ✅ COMPLETE | `trajectory_3d.png` |
| `linear_kinematics_data()` | `plot_linear_kinematics_data()` | ✅ COMPLETE | `linear_kinematics_data.png` |
| `flight_path_angle_data()` | `plot_flight_path_angle_data()` | ✅ COMPLETE | `flight_path_angle_data.png` |
| `attitude_data()` | `plot_attitude_data()` | ✅ COMPLETE | `attitude_data.png` |
| `angular_kinematics_data()` | `plot_angular_kinematics_data()` | ✅ COMPLETE | `angular_kinematics_data.png` |
| `aerodynamic_forces()` | `plot_aerodynamic_forces()` | ✅ COMPLETE | `aerodynamic_forces.png` |
| `rail_buttons_forces()` | `plot_rail_buttons_forces()` | ✅ COMPLETE | `rail_buttons_forces.png` |
| `energy_data()` | `plot_energy_data()` | ✅ COMPLETE | `energy_data.png` |
| `fluid_mechanics_data()` | `plot_fluid_mechanics_data()` | ✅ COMPLETE | `fluid_mechanics_data.png` |
| `stability_and_control_data()` | `plot_stability_and_control_data()` | ✅ COMPLETE | `stability_and_control_data.png` |

**Total: 10/10 methods implemented (100% parity)**

## Known Limitations

1. **3D Plot Rotation**: Static PNG output (RocketPy uses interactive matplotlib viewer)
   - **Mitigation**: Save as high-res PNG with optimal viewing angle

2. **Data Availability**: Some Flight attributes may not exist for all simulations
   - **Mitigation**: Wrapped in try-except blocks, returns None on missing data

3. **Time Range**: Uses `first_event_time` (apogee) as default xlim
   - **Mitigation**: Matches RocketPy behavior for cleaner plots

## Future Enhancements

1. **Interactive 3D**: Export 3D trajectory to HTML using plotly
2. **Animation**: Create MP4 animation of trajectory
3. **Comparison Mode**: Overlay multiple flights on same plot
4. **Export to CSV**: Allow data export for external analysis

## References

- RocketPy Documentation: "First Simulation" tutorial
- RocketPy Source: `rocketpy/plots/flight_plots.py`
- DySi Implementation: `src/curve_plotter.py` (lines 2665-2920)
- Documentation: `docs/source/user/technical/plot_interpretation.rst`

## Conclusion

✅ **All 10 RocketPy Flight.plots methods are now implemented in DySi**

This ensures complete visualization parity with RocketPy, allowing users to:
- Analyze flight performance comprehensively
- Validate simulations against RocketPy results
- Use familiar plot formats from RocketPy documentation
- Integrate DySi into existing RocketPy workflows

The implementation follows DySi coding standards:
- NumPy-style docstrings
- snake_case naming
- Comprehensive error handling
- Detailed logging
- Type hints throughout
