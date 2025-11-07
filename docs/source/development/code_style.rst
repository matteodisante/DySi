Code Style
==========

Coding standards and style guidelines for the framework.

Python Style Guide
------------------

Follow PEP 8
~~~~~~~~~~~~

The framework follows `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ with minor exceptions:

- **Line length**: 100 characters (not 79)
- **Imports**: Grouped and sorted
- **Naming**: See conventions below

Formatting with Black
~~~~~~~~~~~~~~~~~~~~~

Use `Black <https://github.com/psf/black>`_ for automatic formatting:

.. code-block:: bash

    black src/ scripts/ tests/

Black configuration in ``pyproject.toml``:

.. code-block:: toml

    [tool.black]
    line-length = 100
    target-version = ['py38']

Naming Conventions
------------------

Variables and Functions
~~~~~~~~~~~~~~~~~~~~~~~

Use ``snake_case``:

.. code-block:: python

    # Good
    motor_position_m = -1.255
    def calculate_apogee():
        pass

    # Bad
    motorPosition = -1.255
    def CalculateApogee():
        pass

Classes
~~~~~~~

Use ``PascalCase``:

.. code-block:: python

    # Good
    class MotorBuilder:
        pass

    # Bad
    class motor_builder:
        pass

Constants
~~~~~~~~~

Use ``UPPER_SNAKE_CASE``:

.. code-block:: python

    # Good
    DEFAULT_RAIL_LENGTH_M = 5.2
    MAX_ITERATIONS = 1000

    # Bad
    default_rail_length = 5.2

Type Annotations
----------------

Always Use Type Hints
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from typing import Optional, List, Dict

    def calculate_apogee(
        velocity: float,
        altitude: float,
        drag_coefficient: float
    ) -> float:
        """Calculate predicted apogee."""
        return altitude + velocity**2 / (2 * 9.81)

    def process_results(
        results: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Process simulation results."""
        return {"mean": sum(r["apogee_m"] for r in results) / len(results)}

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from typing import Optional

    def add_motor(
        self,
        motor: SolidMotor,
        position_m: Optional[float] = None
    ) -> None:
        """Add motor to rocket."""
        pass

Return Types
~~~~~~~~~~~~

Always specify return types:

.. code-block:: python

    def get_summary(self) -> Dict[str, float]:
        """Get simulation summary."""
        return {"apogee_m": self.apogee}

Docstrings
----------

NumPy Style
~~~~~~~~~~~

Use NumPy-style docstrings:

.. code-block:: python

    def calculate_stability_margin(
        center_of_mass: float,
        center_of_pressure: float,
        rocket_diameter: float
    ) -> float:
        """Calculate static stability margin.

        The stability margin is the distance between center of mass
        and center of pressure, measured in calibers (rocket diameters).

        Parameters
        ----------
        center_of_mass : float
            Center of mass position (m from nose tip)
        center_of_pressure : float
            Center of pressure position (m from nose tip)
        rocket_diameter : float
            Rocket body diameter (m)

        Returns
        -------
        float
            Static margin in calibers

        Raises
        ------
        ValueError
            If rocket diameter is zero or negative

        Examples
        --------
        >>> calculate_stability_margin(1.0, 1.5, 0.1)
        5.0

        Notes
        -----
        A stability margin greater than 2 calibers is recommended
        for stable flight.
        """
        if rocket_diameter <= 0:
            raise ValueError("Rocket diameter must be positive")

        return (center_of_pressure - center_of_mass) / rocket_diameter

Module Docstrings
~~~~~~~~~~~~~~~~~

Every module should have a docstring:

.. code-block:: python

    """Motor builder for RocketPy integration.

    This module provides MotorBuilder class for constructing RocketPy
    SolidMotor objects from configuration dataclasses.
    """

Class Docstrings
~~~~~~~~~~~~~~~~

.. code-block:: python

    class MotorBuilder:
        """Builder for RocketPy SolidMotor objects.

        Constructs a SolidMotor from MotorConfig dataclass, handling
        thrust curve loading, grain geometry, and nozzle parameters.

        Parameters
        ----------
        config : MotorConfig
            Motor configuration dataclass

        Attributes
        ----------
        config : MotorConfig
            Stored configuration
        motor : SolidMotor or None
            Built motor object (None until build() is called)

        Examples
        --------
        >>> config = MotorConfig(...)
        >>> builder = MotorBuilder(config)
        >>> motor = builder.build()
        """

Imports
-------

Order and Grouping
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Standard library imports
    import os
    import sys
    from typing import Optional, List

    # Third-party imports
    import numpy as np
    import pandas as pd
    from rocketpy import SolidMotor, Rocket

    # Local imports
    from src.config import MotorConfig, RocketConfig
    from src.utils import load_data

Absolute vs Relative
~~~~~~~~~~~~~~~~~~~~

Prefer absolute imports:

.. code-block:: python

    # Good
    from src.config import MotorConfig
    from src.motor_builder import MotorBuilder

    # Avoid
    from .config import MotorConfig
    from .motor_builder import MotorBuilder

Error Handling
--------------

Specific Exceptions
~~~~~~~~~~~~~~~~~~~

Raise specific exceptions with clear messages:

.. code-block:: python

    # Good
    if position_m is None:
        raise ValueError(
            "Motor position_m is required. Specify 'position_m' "
            "in motor config section."
        )

    # Bad
    if position_m is None:
        raise Exception("Missing position")

Exception Context
~~~~~~~~~~~~~~~~~

Provide context in error messages:

.. code-block:: python

    try:
        motor = MotorBuilder(config).build()
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Motor thrust file not found: {config.thrust_source}. "
            f"Ensure file exists in data directory."
        ) from e

Logging
-------

Use Logging Module
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    def build_motor(config: MotorConfig) -> SolidMotor:
        """Build motor from configuration."""
        logger.debug(f"Building motor with thrust source: {config.thrust_source}")

        motor = SolidMotor(...)

        logger.info(f"Motor built successfully: dry mass = {motor.dry_mass:.2f} kg")
        return motor

Log Levels
~~~~~~~~~~

- ``DEBUG``: Detailed diagnostic information
- ``INFO``: General informational messages
- ``WARNING``: Warning messages (potential issues)
- ``ERROR``: Error messages (failures)
- ``CRITICAL``: Critical failures

Comments
--------

Explain "Why", Not "What"
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # Good: Explains why
    # Use meteorological convention: wind direction = FROM direction
    wind_u = -wind_velocity * np.sin(direction_rad)

    # Bad: Explains what (obvious from code)
    # Calculate wind u component
    wind_u = -wind_velocity * np.sin(direction_rad)

Complex Algorithms
~~~~~~~~~~~~~~~~~~

Document complex logic:

.. code-block:: python

    # Sobol sensitivity analysis:
    # 1. Generate Sobol sequences (low-discrepancy sampling)
    # 2. Run simulations with sampled parameters
    # 3. Calculate first-order (S1) and total-order (ST) indices
    # 4. S1 measures direct effect, ST includes interactions

TODOs
~~~~~

Mark incomplete work:

.. code-block:: python

    # TODO: Add support for hybrid motors
    # TODO(username): Optimize parallel execution
    # FIXME: This breaks with negative altitudes

Code Organization
-----------------

File Structure
~~~~~~~~~~~~~~

.. code-block:: python

    """Module docstring."""

    # Imports
    import os
    from typing import Optional

    # Constants
    DEFAULT_VALUE = 42

    # Classes
    class MyClass:
        pass

    # Functions
    def my_function():
        pass

    # Main execution (if applicable)
    if __name__ == "__main__":
        main()

Function Length
~~~~~~~~~~~~~~~

Keep functions focused (typically <50 lines):

.. code-block:: python

    # Good: Focused function
    def calculate_apogee(velocity: float, altitude: float) -> float:
        """Calculate predicted apogee."""
        return altitude + velocity**2 / (2 * 9.81)

    # If function is too long, split it:
    def build_rocket(config: RocketConfig) -> Rocket:
        """Build rocket from configuration."""
        rocket = self._create_base_rocket()
        self._add_nose_cone(rocket)
        self._add_fins(rocket)
        self._add_motor(rocket)
        return rocket

Testing Standards
-----------------

Test File Names
~~~~~~~~~~~~~~~

Mirror source structure:

.. code-block:: text

    src/motor_builder.py  →  tests/test_motor_builder.py
    src/config.py         →  tests/test_config.py

Test Function Names
~~~~~~~~~~~~~~~~~~~

Use descriptive names:

.. code-block:: python

    # Good
    def test_motor_position_required_when_not_in_config():
        pass

    def test_rocket_mass_includes_motor_mass():
        pass

    # Bad
    def test_1():
        pass

Linting Tools
-------------

Flake8
~~~~~~

Check code style:

.. code-block:: bash

    flake8 src/ scripts/ tests/

Configuration in ``.flake8``:

.. code-block:: ini

    [flake8]
    max-line-length = 100
    exclude = .git,__pycache__,venv

MyPy
~~~~

Static type checking:

.. code-block:: bash

    mypy src/

Configuration in ``mypy.ini``:

.. code-block:: ini

    [mypy]
    python_version = 3.8
    warn_return_any = True
    warn_unused_configs = True
    disallow_untyped_defs = True

Pre-commit Hooks
----------------

Setup
~~~~~

Install pre-commit hooks:

.. code-block:: bash

    pip install pre-commit
    pre-commit install

Configuration in ``.pre-commit-config.yaml``:

.. code-block:: yaml

    repos:
      - repo: https://github.com/psf/black
        rev: 23.3.0
        hooks:
          - id: black

      - repo: https://github.com/pycqa/flake8
        rev: 6.0.0
        hooks:
          - id: flake8

      - repo: https://github.com/pre-commit/mirrors-mypy
        rev: v1.3.0
        hooks:
          - id: mypy

Best Practices Summary
----------------------

1. **Use type hints** everywhere
2. **Write NumPy-style docstrings** for all public APIs
3. **Format with Black** before committing
4. **Keep functions focused** (<50 lines typically)
5. **Test error cases** not just success paths
6. **Log appropriately** (debug for diagnostics, info for results)
7. **Handle errors gracefully** with specific exceptions
8. **Comment "why"**, not "what"
9. **Follow naming conventions** consistently
10. **Run linters** before committing

Next Steps
----------

- :doc:`contributing` - Start contributing
- :doc:`architecture` - Understand the codebase
- :doc:`testing` - Write and run tests
