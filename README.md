# Rocket Simulation Framework

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://matteodisante.github.io/DySi/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A modular, production-ready rocket dynamics simulation framework built on [RocketPy](https://github.com/RocketPy-Team/RocketPy). This project provides a clean, maintainable architecture for rocket trajectory simulations with advanced features like air brakes control and real-time weather data integration.

📚 **[View Full Documentation](https://matteodisante.github.io/DySi/)**

---

## ✨ Features

### Core Capabilities
- 🚀 **Complete Flight Simulation** - 6-DOF trajectory analysis with RocketPy integration
- 📁 **YAML Configuration** - Type-safe configuration files with comprehensive validation
- ✅ **Validation Layer** - Automatic physical plausibility checks and stability analysis
- 📈 **Publication-Quality Plots** - 3D trajectories, altitude, velocity, acceleration profiles
- 💾 **Multiple Export Formats** - CSV, JSON, KML, and RocketPy-compatible formats
- 🎯 **Complete Motor State Export** - 35+ scalar attributes + 11 time-dependent curve plots

### Advanced Features
- **🎯 Air Brakes Control** - PID, bang-bang, and model-predictive controllers for active apogee targeting
- **🌤️ Weather Integration** - Real atmospheric data from Wyoming soundings, GFS forecasts, and ERA5 reanalysis
- **📊 Smart Dual Y-Axis Plots** - Intelligent dual y-axis detection for plots with different scales
- **📂 Organized Output Structure** - Automatic organization in `motor/`, `rocket/`, `environment/` subdirectories
- **�� CLI Tools** - Command-line scripts for batch processing

### 🚧 In Development
- **📊 Monte Carlo Analysis** - Uncertainty quantification with parallel simulations *(coming soon)*

---

## 🚀 Quick Start

### Installation

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Setup

1. **Clone the repository**:
\`\`\`bash
git clone https://github.com/matteodisante/rocket-sim.git
cd rocket-sim
\`\`\`

2. **Create virtual environment** (recommended):
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies**:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Verify installation**:
\`\`\`bash
python -c "import rocketpy; print('✓ Dependencies installed')"
\`\`\`

### Run Your First Simulation

\`\`\`bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/01_minimal.yaml \
    --name my_first_rocket \
    --plots
\`\`\`

**Output**: Results will be in `outputs/my_first_rocket/` with plots, data files, and motor curves.

---

## 📋 Usage Examples

### Single Flight Simulation

**Basic usage:**
\`\`\`bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/01_minimal.yaml \
    --name test_flight
\`\`\`

**With all features:**
\`\`\`bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --name artemis \
    --plots \
    --verbose \
    --log-file simulation.log
\`\`\`

### Configuration Files

Available configurations in `configs/`:
- `single_sim/01_minimal.yaml` - Minimal configuration for quick tests
- `single_sim/02_complete.yaml` - Complete configuration with all features
- `monte_carlo/` - Monte Carlo configurations *(in development)*
- `templates/template_complete_documented.yaml` - Fully documented template
- `weather_example.yaml` - Weather integration example

---

## 📚 Documentation

### User Guides
- [Configuration Reference](docs/user/CONFIGURATION_REFERENCE.md)
- [Motor State Export Guide](docs/user/MOTOR_STATE_EXPORT_GUIDE.md)
- [Plots and Output Reference](docs/user/PLOTS_AND_OUTPUT_REFERENCE.md)
- [Troubleshooting](docs/user/TROUBLESHOOTING.md)

### Developer Documentation
- [Architecture](docs/developer/ARCHITECTURE.md)
- [API Reference](docs/developer/API_REFERENCE.md)
- [Module Reference](docs/developer/MODULE_REFERENCE.md)
- [Contributing](docs/developer/CONTRIBUTING.md)

### Additional Resources
- [CHANGELOG](CHANGELOG.md)
- [RocketPy Documentation](https://docs.rocketpy.org/)
- [RocketPy GitHub](https://github.com/RocketPy-Team/RocketPy)

---

## 🎯 Project Status

### ✅ Production Ready
- Single flight simulations with comprehensive validation
- Motor state export system (35+ attributes, 11 plots)
- Air brakes control (PID, bang-bang, MPC)
- Weather data integration (Wyoming, GFS, ERA5)
- Publication-quality visualization
- Complete test suite

### 🚧 In Development
- Monte Carlo uncertainty analysis
- Parallel execution framework
- Advanced statistical analysis

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **RocketPy Team** - For the excellent rocket simulation library
- **STARPI Team** - For project requirements and aerospace expertise

Built for the **STARPI rocket team** 🚀
