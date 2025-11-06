# Rocket Simulation Framework

A modular, production-ready rocket dynamics simulation framework built on [RocketPy](https://github.com/RocketPy-Team/RocketPy). This project provides a clean, maintainable architecture for rocket trajectory simulations, Monte Carlo uncertainty analysis, and sensitivity studies.

## Features

- **Modular Architecture**: Clean separation between configuration, simulation logic, and analysis
- **YAML Configuration**: Human-readable configuration files with comprehensive validation
- **Type Safety**: Full type hints and dataclass-based configuration objects
- **Validation Layer**: Automatic physical plausibility checks and stability analysis
- **Extensible**: Easy to add new components, analyses, or custom workflows
- **Well-Tested**: Comprehensive test suite with >80% coverage goal
- **Documentation**: Detailed API documentation and usage examples

## Project Status

✅ **Phases 1-4 Complete**: Full simulation pipeline with Monte Carlo analysis

**Completed:**
- ✅ Phase 1: Configuration system and validation layer
- ✅ Phase 2: Builder pattern implementations (Motor, Environment, Rocket)
- ✅ Phase 3: Core simulation engine with visualization
- ✅ Phase 4: Monte Carlo analysis framework
- ✅ Complete test suite (102 tests passing)
- ✅ CLI scripts for single and ensemble simulations

**Ready for:**
- 📋 Sensitivity analysis tools
- 📋 Advanced optimization features
- 📋 Additional example notebooks

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

4. **Install in development mode**:
```bash
pip install -e .
```

## Quick Start

### Configuration-Based Simulation

1. **Create a configuration file** (see `configs/simple_rocket.yaml` for example):

```yaml
rocket:
  name: "My Rocket"
  dry_mass_kg: 10.0
  geometry:
    caliber_m: 0.1
    length_m: 1.5
  cg_location_m: 0.9

motor:
  type: "SolidMotor"
  thrust_source: "data/motors/Cesaroni_M1670.eng"

environment:
  latitude_deg: 40.0
  longitude_deg: -8.0

simulation:
  max_time_s: 600.0
```

2. **Load and validate configuration**:

```python
from src.config_loader import ConfigLoader
from src.validators import validate_all_configs

# Load configuration
loader = ConfigLoader()
rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(
    "configs/simple_rocket.yaml"
)

# Validate
warnings = validate_all_configs(rocket_cfg, motor_cfg, env_cfg, sim_cfg)

# Check warnings
for warning in warnings:
    print(f"Warning: {warning}")
```

### Programmatic Configuration

```python
from src.config_loader import (
    RocketConfig,
    InertiaConfig,
    GeometryConfig,
    FinConfig,
)

# Create configuration objects
rocket_cfg = RocketConfig(
    name="Test Rocket",
    dry_mass_kg=10.0,
    inertia=InertiaConfig(ixx_kg_m2=5.0, iyy_kg_m2=5.0, izz_kg_m2=0.03),
    geometry=GeometryConfig(caliber_m=0.1, length_m=1.5),
    cg_location_m=0.9,
    fins=FinConfig(
        count=4,
        root_chord_m=0.1,
        tip_chord_m=0.05,
        span_m=0.08,
        thickness_m=0.003,
    ),
)
```

## Project Structure

```
rocket-simulation/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
├── .gitignore               # Git ignore rules
├── .editorconfig            # Editor configuration
│
├── configs/                 # Configuration files
│   ├── README_CONFIGS.md    # Configuration guide
│   ├── complete_example.yaml  # Full configuration example
│   └── simple_rocket.yaml   # Minimal configuration
│
├── src/                     # Source code
│   ├── __init__.py
│   ├── config_loader.py     # Configuration loading and dataclasses
│   ├── validators.py        # Configuration validation
│   ├── rocket_builder.py    # Rocket construction (TODO)
│   ├── motor_builder.py     # Motor construction (TODO)
│   ├── environment_setup.py # Environment setup (TODO)
│   ├── flight_simulator.py  # Flight simulation (TODO)
│   ├── monte_carlo_runner.py # Monte Carlo analysis (TODO)
│   ├── sensitivity_analyzer.py # Sensitivity analysis (TODO)
│   ├── data_handler.py      # Data export utilities (TODO)
│   ├── visualizer.py        # Plotting utilities (TODO)
│   └── utils.py             # Common utilities (TODO)
│
├── scripts/                 # Command-line scripts
│   ├── run_single_simulation.py  # Single flight (TODO)
│   ├── run_monte_carlo.py        # Monte Carlo (TODO)
│   ├── run_sensitivity.py        # Sensitivity analysis (TODO)
│   └── generate_report.py        # Report generation (TODO)
│
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_config_loader.py
│   ├── test_validators.py
│   └── ...                  # More tests (TODO)
│
├── notebooks/               # Jupyter notebooks
│   ├── 00_getting_started.ipynb  # (TODO)
│   ├── 01_single_flight_simulation.ipynb  # (TODO)
│   ├── 02_monte_carlo_ensemble.ipynb  # (TODO)
│   └── ...
│
├── outputs/                 # Simulation outputs
│   ├── results/            # CSV, JSON data files
│   ├── plots/              # Generated plots
│   └── reports/            # Analysis reports
│
└── docs/                    # Documentation
    ├── ARCHITECTURE.md      # Architecture overview (TODO)
    ├── CONTRIBUTING.md      # Development guidelines (TODO)
    └── API_REFERENCE.md     # API documentation (TODO)
```

## Architecture

### Design Principles

1. **Separation of Concerns**: Clear boundaries between configuration, simulation, and analysis
2. **Type Safety**: Complete type hints for IDE support and early error detection
3. **Validation First**: Validate configurations before running expensive simulations
4. **Modularity**: Each component is independently testable and reusable
5. **Documentation**: Self-documenting code with comprehensive docstrings

### Configuration System

The configuration system uses **dataclasses** for type-safe configuration objects and **YAML files** for human-readable input:

- **`config_loader.py`**: Defines configuration dataclasses and YAML loading logic
- **`validators.py`**: Physical plausibility checks and constraint validation
- **YAML files**: User-facing configuration with comprehensive documentation

### Validation Layers

The validation system provides two levels:

1. **Critical Errors**: Stop simulation if physical laws are violated (negative mass, unstable rocket, etc.)
2. **Warnings**: Alert user to unusual values that may indicate mistakes

Example validation checks:
- Positive mass, inertia, and dimensions
- Static stability margin (CP behind CG by ≥1 caliber)
- Reasonable parameter ranges (mass, L/D ratio, burn time, etc.)
- Cross-configuration consistency

## Configuration Guide

See [`configs/README_CONFIGS.md`](configs/README_CONFIGS.md) for comprehensive configuration documentation including:

- Complete YAML schema
- Parameter descriptions and units
- Coordinate system conventions
- Configuration examples
- Validation rules
- Common troubleshooting

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config_loader.py

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

### Development Workflow

1. **Create a feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes** and add tests

3. **Run tests and linting**:
```bash
pytest
black src/ tests/
flake8 src/ tests/
mypy src/
```

4. **Commit changes**:
```bash
git add .
git commit -m "Add feature: description"
```

5. **Push and create pull request**

## Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure
- [x] Configuration system with YAML support
- [x] Validation framework
- [x] Test infrastructure (76 tests)

### Phase 2: Builder Pattern ✅ COMPLETE
- [x] MotorBuilder implementation
- [x] EnvironmentBuilder implementation
- [x] RocketBuilder implementation
- [x] Integration tests (27 additional tests)

### Phase 3: Core Simulation ✅ COMPLETE
- [x] FlightSimulator implementation
- [x] DataHandler for exports (CSV, JSON, KML)
- [x] Visualizer with 5 plot types
- [x] Single simulation CLI script

### Phase 4: Monte Carlo Analysis ✅ COMPLETE
- [x] MonteCarloRunner implementation
- [x] Statistical analysis utilities
- [x] Parameter variation framework
- [x] Monte Carlo CLI script

### Phase 5: Sensitivity Analysis (FUTURE)
- [ ] SensitivityAnalyzer implementation
- [ ] Parameter importance ranking
- [ ] Tornado diagrams
- [ ] Sensitivity script

### Phase 6: Documentation & Polish (FUTURE)
- [ ] API documentation
- [ ] Architecture documentation
- [ ] Example Jupyter notebooks
- [ ] GitHub Actions CI/CD
- [ ] Performance optimization

## Dependencies

### Core Dependencies
- **rocketpy**: Rocket physics simulation engine
- **numpy**: Numerical computing
- **scipy**: Scientific computing and integration
- **matplotlib**: Plotting and visualization
- **pyyaml**: YAML configuration parsing

### Data Handling
- **pandas**: Data analysis and manipulation
- **h5py**: HDF5 file format support

### Development
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

See [`requirements.txt`](requirements.txt) for complete dependency list.

## Contributing

We welcome contributions! Please see [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for guidelines (coming soon).

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

## License

[MIT License](LICENSE) (or specify your license)

## Acknowledgments

- **RocketPy Team**: For the excellent rocket simulation library
- **STARPI Team**: For project requirements and aerospace expertise

## Contact

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/your-org/rocket-simulation/issues)
- **Documentation**: [`docs/`](docs/) directory
- **Email**: your-email@example.com

## References

- [RocketPy Documentation](https://docs.rocketpy.org/)
- [RocketPy GitHub Repository](https://github.com/RocketPy-Team/RocketPy)
- [Getting Started Notebook](notebooks/00_getting_started.ipynb) (coming soon)

---

**Built with ❤️ for the STARPI rocket team**
