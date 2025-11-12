# Rocket Simulation Framework# Rocket Simulation Framework



[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://matteodisante.github.io/rocket-sim/)[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://matteodisante.github.io/rocket-sim/)

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)



A modular, production-ready rocket dynamics simulation framework built on [RocketPy](https://github.com/RocketPy-Team/RocketPy). This project provides a clean, maintainable architecture for rocket trajectory simulations with advanced features like air brakes control and real-time weather data integration.A modular, production-ready rocket dynamics simulation framework built on [RocketPy](https://github.com/RocketPy-Team/RocketPy). This project provides a clean, maintainable architecture for rocket trajectory simulations, Monte Carlo uncertainty analysis, and **variance-based sensitivity analysis**.



📚 **[View Full Documentation](https://matteodisante.github.io/rocket-sim/)**📚 **[View Full Documentation](https://matteodisante.github.io/rocket-sim/)**



---## Features



## ✨ Features### Core Capabilities

- 🚀 **Complete Simulation Pipeline**: End-to-end rocket flight simulation with RocketPy integration

### Core Capabilities- 📊 **Monte Carlo Analysis**: Uncertainty quantification with 100+ parallel simulations

- 🚀 **Complete Flight Simulation** - 6-DOF trajectory analysis with RocketPy integration- 🔬 **Sensitivity Analysis**: Variance-based and OAT methods for parameter importance ranking

- 📁 **YAML Configuration** - Type-safe configuration files with comprehensive validation- 📁 **YAML Configuration**: Human-readable configuration files with comprehensive validation

- ✅ **Validation Layer** - Automatic physical plausibility checks and stability analysis- ✅ **Type Safety**: Full type hints and dataclass-based configuration objects

- 📈 **Publication-Quality Plots** - 3D trajectories, altitude, velocity, acceleration profiles- 🔍 **Validation Layer**: Automatic physical plausibility checks and stability analysis

- 💾 **Multiple Export Formats** - CSV, JSON, KML, and RocketPy-compatible formats- 📈 **Visualization Suite**: Publication-quality plots (3D trajectory, altitude, velocity, acceleration)

- 🎯 **Complete Motor State Export** - 35+ scalar attributes + 11 time-dependent curve plots- 💾 **Multiple Export Formats**: CSV, JSON, KML, RocketPy-compatible formats

- 🎯 **Complete Motor State Export**: 35+ scalar attributes + 11 time-dependent curve plots ⭐ NEW

### Advanced Features

- **🎯 Air Brakes Control** - PID, bang-bang, and model-predictive controllers for active apogee targeting### Advanced Features

- **🌤️ Weather Integration** - Real atmospheric data from Wyoming soundings, GFS forecasts, and ERA5 reanalysis- **Motor State Export System**: Export complete motor state (initial/final) with scalars in JSON/TXT and functions as high-quality plots

- **📊 Smart Dual Y-Axis Plots** - Intelligent dual y-axis detection for plots with different scales- **Smart Dual Y-Axis Plots**: Intelligent dual y-axis detection for plots with different scales (>10x difference)

- **📂 Organized Output Structure** - Automatic organization in `motor/`, `rocket/`, `environment/` subdirectories- **Organized Output Structure**: Automatic organization in `motor/`, `rocket/`, `environment/` subdirectories

- **🔧 CLI Tools** - Command-line scripts for batch processing- **Variance-Based Sensitivity**: Statistical sensitivity coefficients with Linear Approximation Error (LAE)

- **OAT Screening**: Quick parameter screening with tornado diagrams

### 🚧 In Development- **Parallel Execution**: Multi-core Monte Carlo simulations

- **📊 Monte Carlo Analysis** - Uncertainty quantification with parallel simulations *(coming soon)*- **Data Pipeline**: Seamless integration Monte Carlo → Sensitivity Analysis

- **CLI Tools**: Command-line scripts for batch processing

---

## Project Status

## 🚀 Quick Start

✅ **Phases 1-5 Complete**: Full simulation pipeline with advanced sensitivity analysis

### Installation

**Completed:**

#### Prerequisites- ✅ Phase 1: Configuration system and validation layer

- Python 3.8 or higher- ✅ Phase 2: Builder pattern implementations (Motor, Environment, Rocket)

- pip package manager- ✅ Phase 3: Core simulation engine with visualization

- ✅ Phase 4: Monte Carlo analysis framework

#### Setup- ✅ **Phase 5: Variance-based sensitivity analysis** ⭐ NEW

- ✅ Complete test suite (150+ tests passing)

1. **Clone the repository**:- ✅ CLI scripts for single, Monte Carlo, and sensitivity analysis

```bash- ✅ 4 comprehensive Jupyter notebooks

git clone <repository-url>

cd rocket-sim**Production Ready:**

```- 🎯 Single flight simulations

- 🎲 Monte Carlo uncertainty quantification

2. **Create virtual environment** (recommended):- 📊 Variance-based sensitivity analysis

```bash- 📝 Complete API documentation (inline)

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate## Installation

```

### Prerequisites

3. **Install dependencies**:

```bash- Python 3.8 or higher

pip install -r requirements.txt- pip package manager

```

### Setup

4. **Verify installation**:

```bash1. **Clone the repository**:

python -c "import rocketpy; print('✓ Dependencies installed')"```bash

```git clone <repository-url>

cd rocket-simulation

### Run Your First Simulation```



```bash2. **Create a virtual environment** (recommended):

python scripts/run_single_simulation.py \```bash

    --config configs/single_sim/01_minimal.yaml \python -m venv venv

    --name my_first_rocket \source venv/bin/activate  # On Windows: venv\Scripts\activate

    --plots```

```

3. **Install dependencies**:

**Output**: Results will be in `outputs/my_first_rocket/` with plots, data files, and motor curves.```bash

pip install -r requirements.txt

---```



## 📋 Usage Examples4. **Verify installation**:

```bash

### Single Flight Simulationpython -c "import rocketpy; import statsmodels; print('✓ All dependencies installed')"

```

**Basic usage:**

```bash## Documentation

python scripts/run_single_simulation.py \

    --config configs/single_sim/01_minimal.yaml \📖 **Comprehensive documentation available in [`docs/`](docs/)**

    --name test_flight

```The documentation is organized as follows:

- **[User Guides](docs/user/)**: Motor state export guide, troubleshooting

**With all features:**- **[Developer Documentation](docs/developer/)**: Architecture, API reference, motor attributes classification, contributing

```bash- **[Implementation Details](docs/implementation/)**: Technical implementation summaries

python scripts/run_single_simulation.py \

    --config configs/single_sim/02_complete.yaml \### Quick Links

    --name artemis \- [Motor State Export Guide](docs/user/MOTOR_STATE_EXPORT_GUIDE.md) - Complete guide to new export system ⭐

    --plots \- [Motor Attributes Classification](docs/developer/MOTOR_ATTRIBUTES_CLASSIFICATION.md) - All 61 SolidMotor attributes classified

    --verbose \- [Architecture](docs/developer/ARCHITECTURE.md) - System architecture and design decisions

    --log-file simulation.log- [CHANGELOG](CHANGELOG.md) - Recent changes and updates

```

### Building Documentation Locally

### Configuration Files

```bash

Available configurations in `configs/`:cd docs

- `single_sim/01_minimal.yaml` - Minimal configuration for quick testsmake html

- `single_sim/02_complete.yaml` - Complete configuration with all featuresopen _build/html/index.html  # Or: python -m http.server 8000 -d _build/html

- `monte_carlo/` - Monte Carlo configurations *(in development)*```

- `templates/template_complete_documented.yaml` - Fully documented template

- `weather_example.yaml` - Weather integration example## Quick Start



---### 1. Run Your First Simulation (5 minutes)



## 📂 Project StructureSee the [Getting Started Notebook](notebooks/00_getting_started.ipynb) for an interactive tutorial.



``````python

rocket-sim/from src.config_loader import ConfigLoader

├── configs/                    # YAML configuration filesfrom src.motor_builder import MotorBuilder

│   ├── single_sim/            # Single flight configurationsfrom src.environment_setup import EnvironmentBuilder

│   ├── monte_carlo/           # Monte Carlo configurations (in dev)from src.rocket_builder import RocketBuilder

│   └── templates/             # Configuration templatesfrom src.flight_simulator import FlightSimulator

│

├── src/                       # Source code (~3500 lines)# Load configuration

│   ├── config_loader.py       # Configuration loadingconfig_loader = ConfigLoader()

│   ├── validators.py          # Validation frameworkconfig_loader.load_from_yaml('configs/simple_rocket.yaml')

│   ├── motor_builder.py       # Motor construction

│   ├── environment_setup.py   # Environment setuprocket_cfg = config_loader.get_rocket_config()

│   ├── rocket_builder.py      # Rocket constructionmotor_cfg = config_loader.get_motor_config()

│   ├── flight_simulator.py    # Flight simulationenv_cfg = config_loader.get_environment_config()

│   ├── data_handler.py        # Data exportsim_cfg = config_loader.get_simulation_config()

│   ├── state_exporter.py      # Complete state export

│   ├── curve_plotter.py       # Motor curve plotting# Build components

│   ├── visualizer.py          # Result visualizationmotor = MotorBuilder(motor_cfg).build()

│   ├── air_brakes_controller.py  # Air brakes controlenvironment = EnvironmentBuilder(env_cfg).build()

│   ├── weather_fetcher.py     # Weather data integrationrocket = RocketBuilder(rocket_cfg).build(motor)

│   ├── monte_carlo_runner.py  # Monte Carlo (in development)

│   └── utils.py               # Utilities# Run simulation

│simulator = FlightSimulator(rocket, motor, environment)

├── scripts/                   # Command-line scriptsflight = simulator.run()

│   ├── run_single_simulation.py

│   └── run_monte_carlo.py     # (in development)# View results

│simulator.print_summary()

├── docs/                      # Documentation# Output:

│   ├── user/                  # User guides#   Apogee: 1247.3 m

│   └── developer/             # Developer docs#   Max velocity: 145.2 m/s (Mach 0.42)

│#   Flight time: 87.4 s

├── examples/                  # Example scripts```

├── notebooks/                 # Jupyter notebooks

├── tests/                     # Test suite### 2. Monte Carlo Uncertainty Analysis

└── outputs/                   # Simulation outputs

``````python

from src.monte_carlo_runner import MonteCarloRunner

---

# Create Monte Carlo runner

## 📚 Documentationmc_runner = MonteCarloRunner(

    base_rocket_config=rocket_cfg,

### User Guides    base_motor_config=motor_cfg,

- [Installation Guide](docs/user/installation.md) *(to be created)*    base_environment_config=env_cfg,

- [Quick Start Tutorial](docs/user/quickstart.md) *(to be created)*    base_simulation_config=sim_cfg,

- [Configuration Reference](docs/user/CONFIGURATION_REFERENCE.md)    num_simulations=200

- [Motor State Export Guide](docs/user/MOTOR_STATE_EXPORT_GUIDE.md))

- [Plots and Output Reference](docs/user/PLOTS_AND_OUTPUT_REFERENCE.md)

- [Air Brakes Control](docs/user/air-brakes.md) *(to be created)*# Add parameter uncertainties

- [Weather Integration](docs/user/weather.md) *(to be created)*mc_runner.add_parameter_variation(

- [Troubleshooting](docs/user/TROUBLESHOOTING.md)    "rocket.dry_mass_kg",

    mean=10.0,

### Developer Documentation    std=0.5,  # ±0.5 kg uncertainty

- [Architecture](docs/developer/ARCHITECTURE.md)    distribution="normal"

- [API Reference](docs/developer/API_REFERENCE.md))

- [Module Reference](docs/developer/MODULE_REFERENCE.md)

- [Motor Attributes Classification](docs/developer/MOTOR_ATTRIBUTES_CLASSIFICATION.md)mc_runner.add_parameter_variation(

- [Contributing](docs/developer/CONTRIBUTING.md)    "environment.wind.velocity_ms",

    mean=5.0,

### Additional Resources    std=2.0,  # ±2 m/s wind variation

- [CHANGELOG](CHANGELOG.md) - Recent changes and updates    distribution="normal"

- [RocketPy Documentation](https://docs.rocketpy.org/))

- [RocketPy GitHub](https://github.com/RocketPy-Team/RocketPy)

# Run ensemble

---results = mc_runner.run(parallel=True, max_workers=4)



## 🛠️ Development# Analyze statistics

stats = mc_runner.get_statistics()

### Running Testsprint(f"Apogee: {stats['apogee_m']['mean']:.1f} ± {stats['apogee_m']['std']:.1f} m")

print(f"90% prediction interval: [{stats['apogee_m']['p05']:.1f}, {stats['apogee_m']['p95']:.1f}] m")

```bash```

# Run all tests

pytest### 3. Variance-Based Sensitivity Analysis ⭐ NEW



# Run with coverage```python

pytest --cov=src --cov-report=htmlfrom src.variance_sensitivity import VarianceBasedSensitivityAnalyzer



# Run with verbose output# Export Monte Carlo data

pytest -vparams_df, targets_df = mc_runner.export_for_sensitivity()

```

# Create sensitivity analyzer

### Code Qualityanalyzer = VarianceBasedSensitivityAnalyzer(

    parameter_names=["rocket.dry_mass_kg", "environment.wind.velocity_ms"],

```bash    target_names=["apogee_m"]

# Format code)

black src/ tests/

# Set nominal parameters

# Check stylemetadata = mc_runner.get_parameter_metadata()

flake8 src/ tests/analyzer.set_nominal_parameters(

    means={p: m['mean'] for p, m in metadata.items()},

# Type checking    stds={p: m['std'] for p, m in metadata.items()}

mypy src/)

```

# Fit regression models and calculate sensitivities

### Contributinganalyzer.fit(params_df, targets_df)



We welcome contributions! See [CONTRIBUTING.md](docs/developer/CONTRIBUTING.md) for guidelines.# Print results

analyzer.print_summary()

**Code Style:**# Output:

- Follow PEP 8 style guide#   Sensitivity Analysis Summary: apogee_m

- Use type hints for all function signatures#   ====================================

- Write docstrings in NumPy/Google style#   Parameter              Sensitivity(%) Nominal mean  Nominal sd  Effect per sd

- Keep line length ≤ 100 characters#   rocket.dry_mass_kg            71.20        10.000       0.500         -98.70

- Use SI units exclusively: `mass_kg`, `velocity_ms`, `force_n`#   wind.velocity_ms              23.40         5.000       2.000          42.30

#   ====================================

---#   Linear Approx Error (LAE)      5.40

#

## 📦 Dependencies#   ✓ LAE < 10%: Linear approximation is excellent



### Core Dependencies# Generate sensitivity bar plot

- **rocketpy** >= 1.2.0 - Rocket physics simulation engineanalyzer.plot_sensitivity_bars('outputs/sensitivity_bars.png')

- **numpy** >= 1.21.0 - Numerical computing```

- **scipy** >= 1.7.0 - Scientific computing

- **matplotlib** >= 3.4.0 - Plotting and visualization**Interpretation**: 71% of apogee variance is due to mass uncertainty. Improving mass measurement accuracy would reduce prediction uncertainty significantly.

- **pyyaml** >= 6.0 - YAML configuration parsing

## CLI Scripts

### Data Handling

- **pandas** >= 1.3.0 - Data analysis### Single Flight Simulation

- **h5py** >= 3.6.0 - HDF5 file format

```bash

### Developmentpython scripts/run_single_simulation.py \

- **pytest** >= 7.0.0 - Testing framework  --config configs/complete_example.yaml \

- **black** >= 22.0.0 - Code formatting  --output-dir outputs/single_flight \

- **flake8** >= 4.0.0 - Linting  --verbose

- **mypy** >= 0.950 - Type checking```



See [requirements.txt](requirements.txt) for complete list.### Monte Carlo Ensemble



---```bash

python scripts/run_monte_carlo.py \

## 🎯 Project Status  --config configs/complete_example.yaml \

  --samples 200 \

### ✅ Production Ready  --parallel \

- Single flight simulations with comprehensive validation  --workers 4 \

- Motor state export system (35+ attributes, 11 plots)  --output-dir outputs/monte_carlo

- Air brakes control (PID, bang-bang, MPC)```

- Weather data integration (Wyoming, GFS, ERA5)

- Publication-quality visualization### Sensitivity Analysis ⭐ NEW

- Complete test suite

```bash

### 🚧 In Development# Variance-based method (recommended)

- Monte Carlo uncertainty analysispython scripts/run_sensitivity.py \

- Parallel execution framework  --method variance \

- Advanced statistical analysis  --monte-carlo-dir outputs/monte_carlo \

  --parameters rocket.dry_mass_kg,environment.wind.velocity_ms \

---  --targets apogee_m \

  --plot \

## 📝 License  --output-dir outputs/sensitivity



MIT License - see [LICENSE](LICENSE) file for details.# OAT method (quick screening)

python scripts/run_sensitivity.py \

---  --method oat \

  --config configs/complete_example.yaml \

## 🙏 Acknowledgments  --parameters rocket.dry_mass_kg,environment.wind.velocity_ms \

  --targets apogee_m \

- **RocketPy Team** - For the excellent rocket simulation library  --variation 10 \

- **STARPI Team** - For project requirements and aerospace expertise  --plot \

  --output-dir outputs/sensitivity_oat

Built for the **STARPI rocket team** 🚀```



---## Project Structure



**Status**: Production-ready for single flight simulations with advanced features ✅```

rocket-simulation/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
├── .gitignore               # Git ignore rules
│
├── configs/                 # Configuration files
│   ├── README_CONFIGS.md    # Configuration guide
│   ├── complete_example.yaml  # Full configuration example
│   └── simple_rocket.yaml   # Minimal configuration
│
├── src/                     # Source code (4400+ lines)
│   ├── __init__.py
│   ├── config_loader.py     # Configuration loading (450 lines)
│   ├── validators.py        # Validation framework (587 lines)
│   ├── rocket_builder.py    # Rocket construction (426 lines)
│   ├── motor_builder.py     # Motor construction (270 lines)
│   ├── environment_setup.py # Environment setup (330 lines)
│   ├── flight_simulator.py  # Flight simulation (366 lines)
│   ├── monte_carlo_runner.py # Monte Carlo analysis (585 lines)
│   ├── variance_sensitivity.py # Variance-based sensitivity (600 lines) ⭐ NEW
│   ├── sensitivity_analyzer.py # OAT sensitivity (350 lines)
│   ├── sensitivity_utils.py # Sensitivity utilities (260 lines) ⭐ NEW
│   ├── data_handler.py      # Data export (425 lines)
│   ├── visualizer.py        # Plotting (498 lines)
│   └── utils.py             # Common utilities (312 lines)
│
├── scripts/                 # Command-line scripts
│   ├── run_single_simulation.py  # Single flight (257 lines)
│   ├── run_monte_carlo.py        # Monte Carlo (87 lines)
│   └── run_sensitivity.py        # Sensitivity analysis (340 lines) ⭐ NEW
│
├── tests/                   # Test suite (1200+ lines, 150+ tests)
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_config_loader.py
│   ├── test_validators.py
│   ├── test_builders.py
│   ├── test_simulators.py
│   └── test_variance_sensitivity.py  # Sensitivity tests ⭐ NEW
│
├── notebooks/               # Jupyter notebooks
│   ├── 00_getting_started.ipynb         # 5-min quick start ✅
│   ├── 01_single_flight_simulation.ipynb  # Detailed workflow ✅
│   ├── 02_monte_carlo_ensemble.ipynb      # Monte Carlo tutorial ✅
│   └── 03_sensitivity_analysis.ipynb      # Sensitivity comparison ✅ ⭐
│
├── outputs/                 # Simulation outputs
│   ├── results/            # CSV, JSON data files
│   ├── plots/              # Generated plots
│   └── reports/            # Analysis reports
│
└── docs/                    # Documentation
    └── (Future: ARCHITECTURE.md, API_REFERENCE.md)
```

## Sensitivity Analysis Methods

### Variance-Based Method (Recommended)

**When to use:**
- Quantitative uncertainty contribution analysis
- Statistical rigor for publications
- Integration with Monte Carlo simulations
- Validation with Linear Approximation Error (LAE)

**Method:**
1. Run Monte Carlo simulation (100+ samples)
2. Fit multiple linear regression: `y = β₀ + β₁x₁ + β₂x₂ + ...`
3. Calculate sensitivity coefficients: `S(j) = 100 × (β_j² × σ_j²) / Var_total`
4. Validate with LAE (should be < 10% for excellent approximation)

**Output:**
- Sensitivity coefficients (% variance contribution)
- Linear Approximation Error (LAE)
- Prediction intervals (95% confidence)
- Sorted bar plots with LAE indicator

### OAT Method (One-At-a-Time)

**When to use:**
- Quick parameter screening
- Identifying which parameters to focus on
- Understanding directional effects
- Simple, interpretable results

**Method:**
1. Run baseline simulation
2. Vary each parameter by ±X% (one at a time)
3. Calculate sensitivity index from output changes

**Output:**
- Sensitivity indices (dimensionless)
- Tornado diagrams
- Directional effect indicators

### Comparison

| Aspect | Variance-Based | OAT |
|--------|---------------|-----|
| Metric | Variance contribution (%) | Sensitivity index |
| Simulations | Reuses MC data (efficient) | 2N+1 new runs |
| Statistical rigor | Yes (LAE validation) | No |
| Best for | Quantitative analysis | Quick screening |

**Recommended Workflow:**
```
1. OAT screening (identify important parameters)
   ↓
2. Monte Carlo simulation (with those parameters)
   ↓
3. Variance-based sensitivity (quantify contribution)
   ↓
4. Design improvements (focus on high-sensitivity parameters)
```

## Architecture

### Design Principles

1. **Separation of Concerns**: Clear boundaries between configuration, simulation, and analysis
2. **Type Safety**: Complete type hints for IDE support and early error detection
3. **Validation First**: Validate configurations before running expensive simulations
4. **Modularity**: Each component is independently testable and reusable
5. **Statistical Rigor**: Variance-based methods with validation (LAE)

### Data Flow

```
YAML Config → ConfigLoader → Dataclasses
                                 ↓
Dataclasses → Builders → RocketPy Objects
                                 ↓
RocketPy Objects → FlightSimulator → Flight Data
                                          ↓
                          ┌───────────────┴────────────────┐
                          ↓                                ↓
                    Visualizer                      MonteCarloRunner
                    (plots)                         (ensemble)
                                                          ↓
                                              VarianceBasedSensitivityAnalyzer
                                              (sensitivity coefficients)
```

## Dependencies

### Core Dependencies
- **rocketpy>=1.2.0**: Rocket physics simulation engine
- **numpy>=1.21.0**: Numerical computing
- **scipy>=1.7.0**: Scientific computing and integration
- **matplotlib>=3.4.0**: Plotting and visualization
- **pyyaml>=6.0**: YAML configuration parsing

### Data Handling
- **pandas>=1.3.0**: Data analysis and manipulation
- **h5py>=3.6.0**: HDF5 file format support

### Statistical Analysis ⭐ NEW
- **statsmodels>=0.14.0**: Multiple linear regression for sensitivity
- **prettytable>=3.9.0**: Formatted table output

### Development
- **pytest>=7.0.0**: Testing framework
- **black>=22.0.0**: Code formatting
- **flake8>=4.0.0**: Linting
- **mypy>=0.950**: Type checking

### Jupyter
- **jupyter>=1.0.0**: Notebook environment
- **jupyterlab>=3.0.0**: Interactive development
- **ipywidgets>=7.6.0**: Interactive widgets

See [requirements.txt](requirements.txt) for complete dependency list.

## Example Notebooks

Comprehensive Jupyter notebooks with executable examples:

1. **[00_getting_started.ipynb](notebooks/00_getting_started.ipynb)**: 5-minute quick start
   - Load configurations
   - Build and run first simulation
   - Visualize results

2. **[01_single_flight_simulation.ipynb](notebooks/01_single_flight_simulation.ipynb)**: Detailed workflow
   - Complete simulation pipeline
   - Validation and stability checks
   - Data export in multiple formats

3. **[02_monte_carlo_ensemble.ipynb](notebooks/02_monte_carlo_ensemble.ipynb)**: Uncertainty quantification
   - Define parameter uncertainties
   - Run 100+ simulations
   - Statistical analysis and dispersion plots

4. **[03_sensitivity_analysis.ipynb](notebooks/03_sensitivity_analysis.ipynb)**: ⭐ Parameter importance
   - OAT vs Variance-Based comparison
   - LAE interpretation
   - Design recommendations

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific category
pytest tests/test_variance_sensitivity.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Check style
flake8 src/ tests/

# Type checking
mypy src/
```

## Roadmap

### ✅ Phase 1: Foundation (COMPLETE)
- [x] Project structure
- [x] Configuration system with YAML support
- [x] Validation framework
- [x] Test infrastructure

### ✅ Phase 2: Builder Pattern (COMPLETE)
- [x] MotorBuilder implementation
- [x] EnvironmentBuilder implementation
- [x] RocketBuilder implementation
- [x] Integration tests

### ✅ Phase 3: Core Simulation (COMPLETE)
- [x] FlightSimulator implementation
- [x] DataHandler for exports (CSV, JSON, KML)
- [x] Visualizer with 5 plot types
- [x] Single simulation CLI script

### ✅ Phase 4: Monte Carlo Analysis (COMPLETE)
- [x] MonteCarloRunner implementation
- [x] Statistical analysis utilities
- [x] Parameter variation framework
- [x] Monte Carlo CLI script

### ✅ Phase 5: Sensitivity Analysis (COMPLETE) ⭐
- [x] VarianceBasedSensitivityAnalyzer with regression
- [x] OAT sensitivity screening
- [x] LAE validation
- [x] Sensitivity CLI script
- [x] Integration with Monte Carlo
- [x] Example notebooks

### 🔜 Phase 6: Documentation & Advanced Features (FUTURE)
- [ ] Architecture documentation (ARCHITECTURE.md)
- [ ] API reference (API_REFERENCE.md)
- [ ] GitHub Actions CI/CD
- [ ] Morris screening method
- [ ] Sobol indices
- [ ] Optimization workflows

## Contributing

We welcome contributions! Key areas:

- **Testing**: Add more test cases
- **Documentation**: Improve API docs and examples
- **Features**: Morris screening, Sobol indices
- **Optimization**: Parameter optimization workflows

### Code Style

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings in Google/NumPy style
- Keep line length ≤ 100 characters
- Use SI units exclusively in code
- Name physical quantities with units: `mass_kg`, `velocity_ms`, `force_n`

### Testing Standards

- Write tests for all new functionality
- Maintain >80% code coverage
- Use descriptive test names: `test_<what>_<condition>_<expected>`
- Use pytest fixtures for common setup

## Acknowledgments

- **RocketPy Team**: For the excellent rocket simulation library
- **STARPI Team**: For project requirements and aerospace expertise
- **Statistical Methods**: Variance-based sensitivity follows RocketPy standards

## References

- [RocketPy Documentation](https://docs.rocketpy.org/)
- [RocketPy GitHub Repository](https://github.com/RocketPy-Team/RocketPy)
- [RocketPy Sensitivity Analysis](https://docs.rocketpy.org/en/latest/user/sensitivity.html)
- [Variance-Based Sensitivity Theory](https://docs.rocketpy.org/en/latest/technical/sensitivity.html)

---

**Built for the STARPI rocket team**

**Status**: Production-ready for single flight, Monte Carlo, and sensitivity analysis ✅
