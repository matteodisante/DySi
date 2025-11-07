# Rocket Simulation Framework

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://TUO-USERNAME.github.io/rocket-sim/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A modular, production-ready rocket dynamics simulation framework built on [RocketPy](https://github.com/RocketPy-Team/RocketPy). This project provides a clean, maintainable architecture for rocket trajectory simulations, Monte Carlo uncertainty analysis, and **variance-based sensitivity analysis**.

📚 **[View Full Documentation](https://TUO-USERNAME.github.io/rocket-sim/)**

## Features

### Core Capabilities
- 🚀 **Complete Simulation Pipeline**: End-to-end rocket flight simulation with RocketPy integration
- 📊 **Monte Carlo Analysis**: Uncertainty quantification with 100+ parallel simulations
- 🔬 **Sensitivity Analysis**: Variance-based and OAT methods for parameter importance ranking
- 📁 **YAML Configuration**: Human-readable configuration files with comprehensive validation
- ✅ **Type Safety**: Full type hints and dataclass-based configuration objects
- 🔍 **Validation Layer**: Automatic physical plausibility checks and stability analysis
- 📈 **Visualization Suite**: Publication-quality plots (3D trajectory, altitude, velocity, acceleration)
- 💾 **Multiple Export Formats**: CSV, JSON, KML, RocketPy-compatible formats

### Advanced Features
- **Variance-Based Sensitivity**: Statistical sensitivity coefficients with Linear Approximation Error (LAE)
- **OAT Screening**: Quick parameter screening with tornado diagrams
- **Parallel Execution**: Multi-core Monte Carlo simulations
- **Data Pipeline**: Seamless integration Monte Carlo → Sensitivity Analysis
- **CLI Tools**: Command-line scripts for batch processing

## Project Status

✅ **Phases 1-5 Complete**: Full simulation pipeline with advanced sensitivity analysis

**Completed:**
- ✅ Phase 1: Configuration system and validation layer
- ✅ Phase 2: Builder pattern implementations (Motor, Environment, Rocket)
- ✅ Phase 3: Core simulation engine with visualization
- ✅ Phase 4: Monte Carlo analysis framework
- ✅ **Phase 5: Variance-based sensitivity analysis** ⭐ NEW
- ✅ Complete test suite (150+ tests passing)
- ✅ CLI scripts for single, Monte Carlo, and sensitivity analysis
- ✅ 4 comprehensive Jupyter notebooks

**Production Ready:**
- 🎯 Single flight simulations
- 🎲 Monte Carlo uncertainty quantification
- 📊 Variance-based sensitivity analysis
- 📝 Complete API documentation (inline)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd rocket-simulation
```

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Verify installation**:
```bash
python -c "import rocketpy; import statsmodels; print('✓ All dependencies installed')"
```

## Documentation

📖 **Full documentation is available at: [https://TUO-USERNAME.github.io/rocket-sim/](https://TUO-USERNAME.github.io/rocket-sim/)**

The documentation includes:
- **User Guide**: Installation, quickstart, key concepts, and configuration reference
- **Examples**: Detailed tutorials for basic simulations, Monte Carlo analysis, sensitivity studies, weather integration, and air brakes control
- **API Reference**: Complete API documentation with examples
- **Development Guide**: Contributing guidelines, architecture overview, testing guide, and code style standards

### Building Documentation Locally

```bash
cd docs
make html
open _build/html/index.html  # Or: python -m http.server 8000 -d _build/html
```

## Quick Start

### 1. Run Your First Simulation (5 minutes)

See the [Getting Started Notebook](notebooks/00_getting_started.ipynb) for an interactive tutorial.

```python
from src.config_loader import ConfigLoader
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator

# Load configuration
config_loader = ConfigLoader()
config_loader.load_from_yaml('configs/simple_rocket.yaml')

rocket_cfg = config_loader.get_rocket_config()
motor_cfg = config_loader.get_motor_config()
env_cfg = config_loader.get_environment_config()
sim_cfg = config_loader.get_simulation_config()

# Build components
motor = MotorBuilder(motor_cfg).build()
environment = EnvironmentBuilder(env_cfg).build()
rocket = RocketBuilder(rocket_cfg).build(motor)

# Run simulation
simulator = FlightSimulator(rocket, motor, environment)
flight = simulator.run()

# View results
simulator.print_summary()
# Output:
#   Apogee: 1247.3 m
#   Max velocity: 145.2 m/s (Mach 0.42)
#   Flight time: 87.4 s
```

### 2. Monte Carlo Uncertainty Analysis

```python
from src.monte_carlo_runner import MonteCarloRunner

# Create Monte Carlo runner
mc_runner = MonteCarloRunner(
    base_rocket_config=rocket_cfg,
    base_motor_config=motor_cfg,
    base_environment_config=env_cfg,
    base_simulation_config=sim_cfg,
    num_simulations=200
)

# Add parameter uncertainties
mc_runner.add_parameter_variation(
    "rocket.dry_mass_kg",
    mean=10.0,
    std=0.5,  # ±0.5 kg uncertainty
    distribution="normal"
)

mc_runner.add_parameter_variation(
    "environment.wind.velocity_ms",
    mean=5.0,
    std=2.0,  # ±2 m/s wind variation
    distribution="normal"
)

# Run ensemble
results = mc_runner.run(parallel=True, max_workers=4)

# Analyze statistics
stats = mc_runner.get_statistics()
print(f"Apogee: {stats['apogee_m']['mean']:.1f} ± {stats['apogee_m']['std']:.1f} m")
print(f"90% prediction interval: [{stats['apogee_m']['p05']:.1f}, {stats['apogee_m']['p95']:.1f}] m")
```

### 3. Variance-Based Sensitivity Analysis ⭐ NEW

```python
from src.variance_sensitivity import VarianceBasedSensitivityAnalyzer

# Export Monte Carlo data
params_df, targets_df = mc_runner.export_for_sensitivity()

# Create sensitivity analyzer
analyzer = VarianceBasedSensitivityAnalyzer(
    parameter_names=["rocket.dry_mass_kg", "environment.wind.velocity_ms"],
    target_names=["apogee_m"]
)

# Set nominal parameters
metadata = mc_runner.get_parameter_metadata()
analyzer.set_nominal_parameters(
    means={p: m['mean'] for p, m in metadata.items()},
    stds={p: m['std'] for p, m in metadata.items()}
)

# Fit regression models and calculate sensitivities
analyzer.fit(params_df, targets_df)

# Print results
analyzer.print_summary()
# Output:
#   Sensitivity Analysis Summary: apogee_m
#   ====================================
#   Parameter              Sensitivity(%) Nominal mean  Nominal sd  Effect per sd
#   rocket.dry_mass_kg            71.20        10.000       0.500         -98.70
#   wind.velocity_ms              23.40         5.000       2.000          42.30
#   ====================================
#   Linear Approx Error (LAE)      5.40
#
#   ✓ LAE < 10%: Linear approximation is excellent

# Generate sensitivity bar plot
analyzer.plot_sensitivity_bars('outputs/sensitivity_bars.png')
```

**Interpretation**: 71% of apogee variance is due to mass uncertainty. Improving mass measurement accuracy would reduce prediction uncertainty significantly.

## CLI Scripts

### Single Flight Simulation

```bash
python scripts/run_single_simulation.py \
  --config configs/complete_example.yaml \
  --output-dir outputs/single_flight \
  --verbose
```

### Monte Carlo Ensemble

```bash
python scripts/run_monte_carlo.py \
  --config configs/complete_example.yaml \
  --samples 200 \
  --parallel \
  --workers 4 \
  --output-dir outputs/monte_carlo
```

### Sensitivity Analysis ⭐ NEW

```bash
# Variance-based method (recommended)
python scripts/run_sensitivity.py \
  --method variance \
  --monte-carlo-dir outputs/monte_carlo \
  --parameters rocket.dry_mass_kg,environment.wind.velocity_ms \
  --targets apogee_m \
  --plot \
  --output-dir outputs/sensitivity

# OAT method (quick screening)
python scripts/run_sensitivity.py \
  --method oat \
  --config configs/complete_example.yaml \
  --parameters rocket.dry_mass_kg,environment.wind.velocity_ms \
  --targets apogee_m \
  --variation 10 \
  --plot \
  --output-dir outputs/sensitivity_oat
```

## Project Structure

```
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
