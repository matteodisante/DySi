# Contributing Guidelines

Thank you for considering contributing to the Rocket Simulation Framework! This document provides guidelines and best practices for contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Testing Guidelines](#testing-guidelines)
5. [Commit Message Conventions](#commit-message-conventions)
6. [Pull Request Process](#pull-request-process)
7. [Issue Reporting](#issue-reporting)
8. [Documentation](#documentation)
9. [Adding New Features](#adding-new-features)

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git for version control
- Familiarity with RocketPy library
- Basic understanding of rocket dynamics (helpful but not required)

### First-Time Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rocket-simulation.git
   cd rocket-simulation
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_REPO/rocket-simulation.git
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Install Pre-Commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install
```

This will automatically run linters and formatters on each commit.

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check code style
black --check src/ tests/
flake8 src/ tests/
mypy src/
```

---

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings (enforced by Black)
- **Imports**: Organized using `isort`

### Formatting Tools

We use the following tools for code formatting:

1. **Black** - Uncompromising code formatter
   ```bash
   black src/ tests/ scripts/
   ```

2. **isort** - Import sorting
   ```bash
   isort src/ tests/ scripts/
   ```

3. **flake8** - Linting
   ```bash
   flake8 src/ tests/ scripts/
   ```

4. **mypy** - Static type checking
   ```bash
   mypy src/
   ```

### Configuration Files

Our configuration is defined in:

- `pyproject.toml`: Black, isort, pytest configuration
- `.flake8`: Flake8 configuration
- `mypy.ini`: Type checking configuration

### Type Hints

**All new code must include type hints**:

```python
# Good ✓
def calculate_apogee(
    thrust_n: float,
    mass_kg: float,
    drag_coefficient: float,
) -> float:
    """Calculate estimated apogee altitude."""
    # Implementation
    return altitude_m

# Bad ✗
def calculate_apogee(thrust_n, mass_kg, drag_coefficient):
    return altitude_m
```

### Docstrings

Use **Google-style docstrings** for all public functions and classes:

```python
def run_simulation(rocket: Rocket, environment: Environment) -> Flight:
    """Execute rocket flight simulation.

    This function creates a Flight instance and runs the trajectory
    integration using RocketPy's ODE solver.

    Args:
        rocket: Configured Rocket instance with motor and components.
        environment: Environment instance with atmospheric model and wind.

    Returns:
        Flight instance with simulation results.

    Raises:
        RuntimeError: If simulation fails due to numerical instability.
        ValueError: If rocket or environment are not properly configured.

    Example:
        >>> rocket = build_rocket(config)
        >>> env = build_environment(config)
        >>> flight = run_simulation(rocket, env)
        >>> print(f"Apogee: {flight.apogee:.0f} m")
        Apogee: 3500 m
    """
    # Implementation
```

### Naming Conventions

- **Classes**: PascalCase (`RocketBuilder`, `FlightSimulator`)
- **Functions/Methods**: snake_case (`build_rocket`, `get_summary`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_ALTITUDE_M`, `DEFAULT_RTOL`)
- **Private members**: Leading underscore (`_internal_method`)
- **Dataclasses**: PascalCase with `Config` suffix (`RocketConfig`, `MotorConfig`)

### Code Organization

```python
# 1. Standard library imports
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 2. Third-party imports
import numpy as np
import pandas as pd
from rocketpy import Rocket

# 3. Local imports
from src.config_loader import RocketConfig
from src.validators import RocketValidator
```

---

## Testing Guidelines

### Test Structure

Tests are organized by module:

```
tests/
├── test_config_loader.py
├── test_motor_builder.py
├── test_rocket_builder.py
├── test_flight_simulator.py
├── test_monte_carlo_runner.py
└── ...
```

### Writing Tests

Use **pytest** for all tests:

```python
import pytest
from src.rocket_builder import RocketBuilder
from src.config_loader import RocketConfig, InertiaConfig, GeometryConfig


@pytest.fixture
def simple_rocket_config():
    """Fixture providing minimal rocket configuration."""
    return RocketConfig(
        name="TestRocket",
        dry_mass_kg=15.0,
        inertia=InertiaConfig(6.32, 6.32, 0.034),
        geometry=GeometryConfig(0.127, 2.0),
        cg_location_m=1.2,
    )


def test_rocket_builder_creates_valid_rocket(simple_rocket_config, motor_fixture):
    """Test that RocketBuilder creates valid Rocket instance."""
    builder = RocketBuilder(simple_rocket_config)
    rocket = builder.build(motor_fixture)

    assert rocket is not None
    assert rocket.mass > 0
    assert rocket.radius == simple_rocket_config.radius_m


def test_rocket_builder_raises_on_missing_motor(simple_rocket_config):
    """Test that builder raises error if motor is required but not provided."""
    builder = RocketBuilder(simple_rocket_config)

    with pytest.raises(ValueError, match="Motor is required"):
        builder.build()
```

### Test Coverage

- **Target**: Maintain >80% code coverage
- **Requirement**: All new features must include tests
- **Check coverage**:
  ```bash
  pytest --cov=src --cov-report=html
  open htmlcov/index.html
  ```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_rocket_builder.py

# Run specific test
pytest tests/test_rocket_builder.py::test_rocket_builder_creates_valid_rocket

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"
```

### Test Markers

Use pytest markers for test categorization:

```python
@pytest.mark.slow
def test_monte_carlo_1000_simulations():
    """Test Monte Carlo with 1000 simulations (slow)."""
    # Implementation

@pytest.mark.integration
def test_full_simulation_pipeline():
    """Test complete pipeline from config to results."""
    # Implementation

@pytest.mark.parametrize("thrust", [1000, 1500, 2000])
def test_different_thrust_values(thrust):
    """Test simulation with various thrust values."""
    # Implementation
```

### Mocking External Dependencies

Use `pytest-mock` or `unittest.mock` for mocking:

```python
from unittest.mock import Mock, patch


def test_flight_simulator_handles_rocketpy_error(mocker):
    """Test that FlightSimulator handles RocketPy errors gracefully."""
    mock_flight = mocker.patch('rocketpy.Flight')
    mock_flight.side_effect = RuntimeError("Integration failed")

    simulator = FlightSimulator(rocket, env, config)

    with pytest.raises(RuntimeError, match="Integration failed"):
        simulator.run()
```

---

## Commit Message Conventions

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, build, etc.)
- **perf**: Performance improvements

### Examples

```
feat(sensitivity): add Sobol indices sensitivity analysis

Implement Sobol sensitivity analysis using SALib library.
Provides first-order and total-order indices for comprehensive
sensitivity analysis.

Closes #42
```

```
fix(monte_carlo): correct wind variation sampling

Fix bug where wind direction variation was applied incorrectly
in Monte Carlo simulations. Now uses proper meteorological
convention (0° = North).

Fixes #89
```

```
docs(api): update API reference with new methods

Add documentation for MonteCarloRunner.export_for_sensitivity()
and VarianceBasedSensitivityAnalyzer.get_prediction_interval().
```

### Commit Guidelines

1. **Keep commits atomic**: One logical change per commit
2. **Write descriptive messages**: Explain *why*, not just *what*
3. **Reference issues**: Use `Closes #123` or `Fixes #456`
4. **Follow conventions**: Use types and scopes consistently

---

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**:
   ```bash
   pytest
   ```

2. **Check code style**:
   ```bash
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

3. **Update documentation**:
   - Add/update docstrings
   - Update README if adding features
   - Add examples to notebooks if applicable

4. **Add tests** for new functionality

5. **Update CHANGELOG.md** if adding user-facing features

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that changes existing behavior)
- [ ] Documentation update

## Testing
Describe testing performed:
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Dependent changes merged

## Related Issues
Closes #(issue number)
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Address feedback** promptly
4. **Squash commits** if requested (keep history clean)
5. **Merge** after approval

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
Clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Load configuration '...'
2. Run simulation with '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- RocketPy version: [e.g., 1.2.0]
- Framework version: [e.g., 1.1.0]

**Error message / traceback**
```
Full traceback here
```

**Configuration file (if applicable)**
```yaml
# Your YAML config
```

**Additional context**
Any other relevant information.
```

### Feature Requests

```markdown
**Feature description**
Clear description of the desired feature.

**Use case**
Explain why this feature is needed and how it would be used.

**Proposed solution**
Your ideas for implementation (optional).

**Alternatives considered**
Other approaches you've considered.

**Additional context**
Screenshots, diagrams, references, etc.
```

---

## Documentation

### Documentation Structure

```
docs/
├── ARCHITECTURE.md       # System architecture
├── API_REFERENCE.md      # Complete API documentation
├── CONTRIBUTING.md       # This file
├── SENSITIVITY_ANALYSIS.md  # Theory and math
└── WEATHER_INTEGRATION.md   # Weather data guide
```

### Updating Documentation

When adding features:

1. **Add docstrings** to all public classes and methods
2. **Update API_REFERENCE.md** with new API
3. **Update README.md** if user-facing feature
4. **Create/update notebooks** with usage examples
5. **Update ARCHITECTURE.md** if changing design

### Documentation Tools

- **Markdown**: All documentation files
- **Sphinx** (planned): For auto-generated API docs from docstrings
- **Jupyter notebooks**: For tutorials and examples

---

## Adding New Features

### Feature Development Workflow

1. **Create an issue** describing the feature
2. **Discuss design** in the issue (if non-trivial)
3. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Implement feature** following guidelines
5. **Add tests** with >80% coverage
6. **Update documentation**
7. **Submit pull request**

### Example: Adding Air Brakes Support

#### 1. Configuration (config_loader.py)

```python
@dataclass
class AirBrakesConfig:
    """Air brakes configuration."""
    enabled: bool = True
    drag_coefficient: float = 1.5
    reference_area_m2: float = 0.01
    position_m: float = -0.5
    controller: Optional[ControllerConfig] = None
```

#### 2. Validation (validators.py)

```python
class AirBrakesValidator:
    """Validator for air brakes configuration."""

    @staticmethod
    def validate(config: AirBrakesConfig) -> None:
        """Validate air brakes configuration."""
        if config.drag_coefficient <= 0:
            raise ValueError("Drag coefficient must be positive")
        if config.reference_area_m2 <= 0:
            raise ValueError("Reference area must be positive")
        # More validation...
```

#### 3. Builder Integration (rocket_builder.py)

```python
class RocketBuilder:
    def add_air_brakes(self) -> 'RocketBuilder':
        """Add air brakes to rocket."""
        if self.config.air_brakes is None:
            return self

        AirBrakesValidator.validate(self.config.air_brakes)

        self.rocket.add_air_brakes(
            drag_coefficient=self.config.air_brakes.drag_coefficient,
            reference_area=self.config.air_brakes.reference_area_m2,
            position=self.config.air_brakes.position_m,
        )
        return self
```

#### 4. Tests (test_air_brakes.py)

```python
def test_air_brakes_validation():
    """Test that air brakes validation catches invalid configs."""
    config = AirBrakesConfig(drag_coefficient=-1.0)

    with pytest.raises(ValueError, match="must be positive"):
        AirBrakesValidator.validate(config)


def test_rocket_builder_adds_air_brakes(rocket_config, motor):
    """Test that RocketBuilder adds air brakes correctly."""
    rocket_config.air_brakes = AirBrakesConfig()
    builder = RocketBuilder(rocket_config)
    rocket = builder.build(motor)

    assert hasattr(rocket, 'air_brakes')
```

#### 5. Documentation

- Add `AirBrakesConfig` to API_REFERENCE.md
- Update README.md with air brakes example
- Create notebook example: `04_air_brakes_control.ipynb`
- Update ARCHITECTURE.md if new patterns introduced

---

## Code Review Checklist

### For Reviewers

- [ ] Code follows style guidelines (Black, flake8, mypy pass)
- [ ] Tests are comprehensive (>80% coverage)
- [ ] Documentation is complete and accurate
- [ ] No unnecessary complexity
- [ ] Error handling is appropriate
- [ ] Performance is acceptable
- [ ] Breaking changes are clearly marked
- [ ] Examples/notebooks work correctly

### For Authors

Before requesting review:

- [ ] Self-review completed
- [ ] All tests pass locally
- [ ] Code is formatted (Black, isort)
- [ ] Type hints are complete
- [ ] Docstrings are complete
- [ ] Documentation updated
- [ ] CHANGELOG updated (if applicable)
- [ ] Examples added/updated

---

## Development Best Practices

### 1. Keep Functions Small and Focused

```python
# Good ✓
def build_motor(config: MotorConfig) -> SolidMotor:
    """Build motor from configuration."""
    validate_motor_config(config)
    thrust_curve = load_thrust_curve(config.thrust_source)
    return SolidMotor(...)

def validate_motor_config(config: MotorConfig) -> None:
    """Validate motor configuration."""
    # Validation logic

def load_thrust_curve(filepath: str) -> np.ndarray:
    """Load thrust curve from file."""
    # Loading logic


# Bad ✗ (too many responsibilities)
def build_motor(config: MotorConfig) -> SolidMotor:
    """Build motor."""
    # Validation
    if config.thrust_source == "":
        raise ValueError("...")
    # File loading
    with open(config.thrust_source) as f:
        data = f.read()
    # Parsing
    thrust_curve = parse_eng_file(data)
    # Building
    motor = SolidMotor(...)
    # More logic...
    return motor
```

### 2. Prefer Composition Over Inheritance

```python
# Good ✓
class FlightSimulator:
    def __init__(self, rocket: Rocket, environment: Environment):
        self.rocket = rocket
        self.environment = environment

# Bad ✗ (tight coupling)
class FlightSimulator(Rocket, Environment):
    pass
```

### 3. Use Type Hints Everywhere

```python
# Good ✓
def calculate_drag(
    velocity_ms: float,
    cd: float,
    area_m2: float,
    rho_kg_m3: float,
) -> float:
    """Calculate drag force."""
    return 0.5 * rho_kg_m3 * velocity_ms**2 * cd * area_m2


# Bad ✗
def calculate_drag(velocity_ms, cd, area_m2, rho_kg_m3):
    return 0.5 * rho_kg_m3 * velocity_ms**2 * cd * area_m2
```

### 4. Handle Errors Gracefully

```python
# Good ✓
try:
    config = load_config(config_path)
    validate_config(config)
except FileNotFoundError as e:
    logger.error(f"Config file not found: {e}")
    raise
except ValueError as e:
    logger.error(f"Invalid configuration: {e}")
    raise


# Bad ✗
config = load_config(config_path)  # Crashes on missing file
validate_config(config)  # Crashes on invalid config
```

### 5. Write Self-Documenting Code

```python
# Good ✓
GRAVITY_EARTH_MS2 = 9.80665
STABILITY_MARGIN_MIN_CALIBERS = 1.5

def is_rocket_stable(cp_m: float, cg_m: float, caliber_m: float) -> bool:
    """Check if rocket has adequate static margin."""
    margin_calibers = (cp_m - cg_m) / caliber_m
    return margin_calibers >= STABILITY_MARGIN_MIN_CALIBERS


# Bad ✗
g = 9.80665
sm = 1.5

def check(x, y, z):
    return (x - y) / z >= sm
```

---

## Performance Guidelines

### Profiling

Use profiling tools to identify bottlenecks:

```python
import cProfile
import pstats

# Profile code
cProfile.run('run_monte_carlo()', 'profile_stats')

# Analyze results
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 functions
```

### Optimization Tips

1. **Use NumPy** for numerical operations (vectorization)
2. **Avoid premature optimization** - profile first
3. **Cache expensive computations** when appropriate
4. **Use multiprocessing** for embarrassingly parallel tasks (Monte Carlo)
5. **Minimize file I/O** - read/write in batches

---

## Getting Help

- **Documentation**: Check `docs/` directory
- **Examples**: See `notebooks/` for tutorials
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **RocketPy Docs**: https://docs.rocketpy.org/

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

## Acknowledgments

Thank you for contributing to the Rocket Simulation Framework! Your efforts help make this project better for the entire rocketry community.
