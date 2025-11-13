# Documentation Index

Welcome to the DySi rocket simulation framework documentation!

---

## 🚀 Quick Start

New to DySi? Start here:

1. **[Main README](../README.md)** - Project overview and installation
2. **[Sphinx Documentation](source/index.rst)** - Complete online documentation
3. **[Quick Plot Reference](source/user/quick_plot_reference.rst)** - Interpret simulation plots
4. **[Examples](../examples/)** - Runnable code examples

---

## 📚 Documentation Structure

### Sphinx Documentation (source/)

Complete, browsable documentation with search and cross-references:

- **Getting Started**: Installation, quickstart, key concepts
- **User Guide**: 
  - **Quick Plot Reference** - At-a-glance plot interpretation ⭐ NEW
  - Tutorials - Step-by-step learning
  - How-To Guides - Task-focused recipes
  - Configuration Reference - All parameters
  - **Technical Deep Dives**:
    - **Plot Interpretation** - Complete guide for all 27 plot types ⭐ NEW
    - Stability Analysis - Theory and practice
  - Examples - Real-world configurations
- **API Reference**: Complete module documentation
- **Developer Guide**: Architecture, contributing, extending

### Developer Documentation (developer/)

Markdown files for technical details:

- **[PLOT_DOCUMENTATION_UPDATE.md](developer/PLOT_DOCUMENTATION_UPDATE.md)** - Documentation update summary ⭐ NEW
- **[STATIC_MARGIN_PLOT_EXPLANATION.md](developer/STATIC_MARGIN_PLOT_EXPLANATION.md)** - Static vs stability margin ⭐ NEW
- **[NEW_FLIGHT_PLOTS_IMPLEMENTATION.md](developer/NEW_FLIGHT_PLOTS_IMPLEMENTATION.md)** - Implementation details ⭐ NEW
- **[STABILITY_MARGIN_CLARIFICATION.md](developer/STABILITY_MARGIN_CLARIFICATION.md)** - Stability theory clarification
- **[ARCHITECTURE.md](developer/ARCHITECTURE.md)** - System architecture and design decisions
- **[API_REFERENCE.md](developer/API_REFERENCE.md)** - Complete API documentation
- **[MODULE_REFERENCE.md](developer/MODULE_REFERENCE.md)** - Detailed module documentation
- **[MOTOR_ATTRIBUTES_CLASSIFICATION.md](developer/MOTOR_ATTRIBUTES_CLASSIFICATION.md)** - RocketPy motor attributes
- **[CONTRIBUTING.md](developer/CONTRIBUTING.md)** - How to contribute

---

## 🎯 Finding What You Need

### I want to interpret simulation plots
→ **[Quick Plot Reference](source/user/quick_plot_reference.rst)** (compact) or **[Plot Interpretation Guide](source/user/technical/plot_interpretation.rst)** (detailed)

### I want to understand stability margins
→ **[Stability Analysis](source/user/technical/stability_analysis.rst)** or **[Static Margin Explanation](developer/STATIC_MARGIN_PLOT_EXPLANATION.md)**

### I want to learn the system
→ **[Tutorials](source/user/tutorials/)** or **[Examples](../examples/)**

### I want to configure a simulation
→ **[Configuration Reference](source/user/configuration/)**

### I want to contribute code
→ **[Contributing Guide](developer/CONTRIBUTING.md)** and **[Architecture](developer/ARCHITECTURE.md)**

---

## 📊 Recent Updates (November 13, 2025)

### New Plot Interpretation Documentation

Added comprehensive documentation for interpreting simulation output plots:

✅ **Quick Plot Reference** - Compact reference card with checklists and typical values

✅ **Complete Plot Interpretation Guide** - Detailed explanations for all 27 plot types:
- Motor plots (thrust, mass, Kn, inertia, etc.)
- Rocket plots (drag coefficient, CP position)
- Stability plots (envelope, surface, CP travel)
- Flight plots (attitude, kinematics, forces, energy, fluid mechanics)
- Environment plots (wind, atmospheric profiles)

✅ **Developer Documentation** - Implementation details and design decisions

✅ **7 New Flight Plots** - Comprehensive flight data analysis

See **[PLOT_DOCUMENTATION_UPDATE.md](developer/PLOT_DOCUMENTATION_UPDATE.md)** for complete details.

---

## 🔧 Implementation Details

Technical implementation documentation:

- **[Motor Export Implementation](implementation/IMPLEMENTATION_SUMMARY.md)** - Motor state export system details
- **[Complete Implementation Summary](implementation/IMPLEMENTATION_COMPLETE_SUMMARY.md)** - Full implementation details

---

## 📖 Resources

### Internal
- [CHANGELOG](../CHANGELOG.md) - Project history and changes
- [Examples](../examples/) - Code examples
- [Notebooks](../notebooks/) - Interactive Jupyter notebooks
- [Configuration Templates](../configs/templates/) - YAML configuration templates

### External
- [RocketPy Documentation](https://docs.rocketpy.org/) - Official RocketPy library docs
- [RocketPy GitHub](https://github.com/RocketPy-Team/RocketPy) - RocketPy source code

---

## 🎯 Documentation Status

### ✅ Complete
- Configuration reference
- Motor state export guide
- Output reference
- Troubleshooting
- Architecture documentation
- API reference
- Contributing guidelines

### 🚧 In Progress
- Installation guide
- Quick start tutorial
- Air brakes documentation
- Weather integration guide

---

**Last Updated**: November 12, 2025  
**Status**: Active development
