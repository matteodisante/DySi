# Plot Documentation Update - November 13, 2025

## Summary

Comprehensive documentation added for interpreting DySi simulation output plots, based on RocketPy's approach and tailored for DySi's extended functionality.

## New Documentation Files

### 1. Technical Deep Dive: Plot Interpretation Guide

**File**: `docs/source/user/technical/plot_interpretation.rst`

**Purpose**: Complete, detailed guide for interpreting all simulation output plots

**Contents**:
- Organization of plots by category (motor, rocket, stability, environment, flight)
- Detailed explanation of each plot type
- What to look for (normal patterns, warning signs, critical issues)
- Physical interpretation of all metrics
- Recommended analysis workflow
- Advanced topics (static vs stability margin, transonic effects)
- Export and sharing guidelines

**Key Sections**:
- Motor Plots (thrust, mass, Kn, inertia)
- Rocket Plots (drag coefficient, CP position)
- Stability Plots (envelope, surface, CP travel) 
- Flight Data Plots (attitude, kinematics, forces, energy, fluid mechanics)
- Environment Plots (wind, atmospheric profiles)
- Common patterns and troubleshooting

**References**: 
- Cross-linked with stability analysis documentation
- Links to RocketPy documentation for deeper physics
- References to developer implementation docs

### 2. Quick Reference Card

**File**: `docs/source/user/quick_plot_reference.rst`

**Purpose**: Compact, at-a-glance reference for quick plot interpretation

**Features**:
- Critical plots to check first
- All plot categories in table format
- Quick interpretation guide (stability margins, flight regimes, typical values)
- Common patterns (normal, warning, critical)
- Pre-flight analysis checklist
- Performance validation checklist
- Quick tips and troubleshooting

**Use Case**: Print-friendly reference card for field use or quick checks

### 3. Supporting Documentation

**Files Updated**:
- `docs/source/user/technical/index.rst` - Added plot_interpretation to toctree
- `docs/source/user/index.rst` - Added quick_plot_reference and navigation links
- `docs/developer/STATIC_MARGIN_PLOT_EXPLANATION.md` - Technical explanation of static vs stability margin
- `docs/developer/NEW_FLIGHT_PLOTS_IMPLEMENTATION.md` - Implementation details of new plots

## Documentation Structure

```
docs/source/user/
├── quick_plot_reference.rst        ← NEW: Quick reference card
├── index.rst                        ← UPDATED: Added navigation
├── technical/
│   ├── plot_interpretation.rst     ← NEW: Complete interpretation guide
│   ├── stability_analysis.rst      ← EXISTING
│   └── index.rst                    ← UPDATED: Added to toctree
├── tutorials/
├── how_to_guides/
└── configuration/

docs/developer/
├── PLOT_DOCUMENTATION_UPDATE.md           ← NEW: This file
├── STATIC_MARGIN_PLOT_EXPLANATION.md      ← NEW: Technical explanation
├── NEW_FLIGHT_PLOTS_IMPLEMENTATION.md     ← NEW: Implementation details
├── STABILITY_MARGIN_CLARIFICATION.md      ← EXISTING
└── ...
```

## Integration Points

### User Guide Navigation

Added to dropdown menus in `user/index.rst`:

1. **"I'm new to rocket-sim"** dropdown:
   - Link to quick_plot_reference
   - Link to detailed plot_interpretation

2. **"I want to understand what's in the output plots"** dropdown (NEW):
   - Quick reference card
   - Complete interpretation guide
   - Tutorial walkthrough

3. **"I need to understand the theory"** dropdown:
   - Plot interpretation guide
   - Stability analysis theory

### Quick Navigation

Users can access plot documentation via:

1. **Homepage** → User Guide → Quick Plot Reference
2. **Homepage** → User Guide → Technical → Plot Interpretation
3. **User Guide** → Quick navigation dropdowns
4. **Search**: "plot", "interpretation", "stability margin", etc.

## Key Design Decisions

### 1. Two-Tier Documentation Approach

**Quick Reference** (quick_plot_reference.rst):
- Compact, scannable format
- Tables for quick lookup
- Checklists for workflow
- Print-friendly
- Field-ready

**Complete Guide** (plot_interpretation.rst):
- Detailed explanations
- Physical interpretation
- Examples and context
- Troubleshooting
- Advanced topics

**Rationale**: Different users need different levels of detail at different times.

### 2. Category-Based Organization

Plots organized by simulation component (motor, rocket, stability, environment, flight) rather than alphabetically.

**Rationale**: 
- Matches output directory structure
- Groups related plots together
- Easier mental model for users
- Supports systematic analysis workflow

### 3. Action-Oriented Language

Used checkmarks (✅), warnings (⚠️), and critical alerts (❌) throughout.

**Rationale**:
- Quick visual scanning
- Clear actionable guidance
- Reduces interpretation errors
- Supports decision-making

### 4. Integration with Existing Docs

Cross-referenced with:
- Stability analysis theory
- Tutorial walkthroughs
- How-to guides
- Developer documentation

**Rationale**: 
- Comprehensive learning paths
- Multiple entry points
- Context-appropriate detail
- Discoverability

## Plot Categories Covered

### Motor (11 plots documented)
- thrust_curve.png
- mass_evolution.png
- kn_curve.png
- center_of_mass.png
- grain_geometry.png
- burn_characteristics.png
- inertia_tensor.png
- propellant_inertia_tensor.png
- mass_flow_rate.png
- exhaust_velocity.png
- grain_volume.png

### Rocket (2 plots documented)
- drag_coefficient.png
- cp_position_vs_mach.png

### Stability (5 plots documented)
- stability_envelope.png ⭐ (MOST IMPORTANT)
- stability_margin_surface.png
- stability_cp_travel.png
- stability_cp_com_evolution.png
- stability_margin_enhanced.png

### Flight (7 plots documented)
- attitude_data.png
- angular_kinematics_data.png
- aerodynamic_forces.png
- rail_buttons_forces.png
- energy_data.png
- fluid_mechanics_data.png
- stability_and_control_data.png

### Environment (2 plots documented)
- wind_profile.png
- atmospheric_profile.png

**Total**: 27 distinct plot types fully documented

## Key Technical Explanations

### Static Margin vs Stability Margin

Created dedicated explanation (`STATIC_MARGIN_PLOT_EXPLANATION.md`) clarifying:

- **Static margin**: CP always at Mach=0 (conservative design metric)
- **Stability margin**: CP at actual Mach (realistic flight metric)
- When to use each
- Why RocketPy plots static margin "vs time" (CoM changes, CP fixed)
- Why DySi uses stability margin for flight analysis

### Transonic Effects

Documented critical transonic behavior:

- Drag coefficient peak (~2x subsonic)
- CP shift (usually aft → improves stability)
- Max-Q occurrence
- Shock wave formation
- Design implications

### Flight Regimes

Clear definitions with Mach ranges:

- Subsonic: M < 0.8
- Transonic: M = 0.8-1.2 (CRITICAL)
- Supersonic: M > 1.2

### Stability Margin Zones

Color-coded safety zones:

- Red (< 1.0 cal): Dangerous - DO NOT FLY
- Yellow (1.0-1.5 cal): Marginal - risky
- Light Green (1.5-2.0 cal): Safe
- Dark Green (2.0-2.5 cal): Optimal
- Blue (> 2.5 cal): Overstable

## Analysis Workflows

### Pre-Flight Approval Checklist

8-point checklist covering:
1. Stability margin throughout flight
2. Thrust curve validation
3. Structural loads (Max-Q, bending moments)
4. Flight attitude
5. Warning analysis
6. Drag coefficient
7. CP travel understanding
8. Energy conservation

### Performance Validation Checklist

6-point checklist covering:
1. Max Mach validation
2. Apogee prediction
3. Burnout timing
4. Max-Q altitude
5. Flight stability
6. Angular kinematics damping

### Recommended Analysis Sequence

5-step workflow:
1. Stability first (envelope plot)
2. Flight performance (energy, fluid mechanics)
3. Structural loads (aerodynamic forces)
4. Flight quality (attitude, kinematics)
5. Cross-validation (all plots)

## Examples and Use Cases

### Example Interpretations

Provided interpretation examples for:

- Normal thrust curve
- Stability margin at critical events
- Typical drag coefficient behavior
- Expected energy transfer
- Proper attitude behavior

### Common Warning Signs

Documented 5 categories:
- Marginal stability
- Attitude oscillations
- High angle of attack
- Irregular thrust
- Growing instabilities

### Critical Issue Indicators

Clear stop conditions:
- Stability margin < 1.0 cal
- Extreme bending moments
- Extreme AoA (> 20°)
- Negative stability margin

## Accessibility Features

1. **Multiple entry points**: Homepage, user guide, technical section, quick reference
2. **Progressive disclosure**: Quick reference → detailed guide
3. **Visual hierarchy**: Icons, colors, tables, checklists
4. **Search optimization**: Keywords, cross-references, see-also sections
5. **Print-friendly**: Quick reference designed for printing
6. **Mobile-friendly**: Responsive tables, collapsible sections

## Future Enhancements

Potential additions identified:

1. **Interactive plots**: Hover tooltips, zoom capabilities
2. **Example gallery**: Annotated real-world examples
3. **Video tutorials**: Screencast walkthroughs
4. **Comparison examples**: Good vs bad designs
5. **Troubleshooting flowcharts**: Diagnostic decision trees
6. **Plot export guide**: Publication-quality figure preparation
7. **Custom plot creation**: User-defined analysis plots

## Maintenance Notes

### Keeping Documentation Current

When plots are modified:

1. Update plot_interpretation.rst with new features
2. Update quick_plot_reference.rst if critical
3. Update examples if interpretation changes
4. Cross-check with RocketPy updates
5. Review developer documentation

### Version Tracking

- Documentation version: 1.0 (November 13, 2025)
- Covers: DySi plot output as of November 2025
- Based on: RocketPy concepts + DySi extensions

## References

### RocketPy Documentation
- [Flight Plots](https://docs.rocketpy.org/)
- First Simulation tutorial
- Plot method documentation

### Internal DySi Documentation
- STABILITY_MARGIN_CLARIFICATION.md
- NEW_FLIGHT_PLOTS_IMPLEMENTATION.md
- ARCHITECTURE.md

### External References
- Aerospace stability guidelines (Barrowman, Niskanen)
- Diátaxis documentation framework
- Sphinx documentation best practices

## Acknowledgments

Plot interpretation approach based on:
- RocketPy Team's excellent documentation practices
- STARPI team feedback and needs
- Aerospace engineering best practices
- User experience testing

---

**Author**: GitHub Copilot for DySi  
**Date**: November 13, 2025  
**Status**: Complete ✅  
**Review**: Ready for user testing
