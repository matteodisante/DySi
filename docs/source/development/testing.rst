Testing
=======

This page describes how to run and write tests for the framework.

Running Tests
-------------

All Tests
~~~~~~~~~

.. code-block:: bash

    pytest tests/

Specific Module
~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest tests/test_config.py

With Coverage
~~~~~~~~~~~~~

.. code-block:: bash

    pytest --cov=src tests/
    pytest --cov=src --cov-report=html tests/

Verbose Output
~~~~~~~~~~~~~~

.. code-block:: bash

    pytest -v tests/

Test Organization
-----------------

.. code-block:: text

    tests/
    ├── test_config.py             # Configuration tests
    ├── test_motor_builder.py      # Motor builder tests
    ├── test_rocket_builder.py     # Rocket builder tests
    ├── test_environment.py        # Environment tests
    ├── test_simulator.py          # Simulator tests
    ├── test_monte_carlo.py        # Monte Carlo tests
    ├── test_air_brakes.py         # Air brakes tests
    ├── test_sensitivity.py        # Sensitivity tests
    └── fixtures/                  # Test data and fixtures
        ├── test_configs/
        └── test_data/

Writing Tests
-------------

Unit Tests
~~~~~~~~~~

Test individual functions/methods in isolation:

.. code-block:: python

    import pytest
    from src.config import MotorConfig, load_config

    def test_motor_config_creation():
        """Test MotorConfig instantiation."""
        config = MotorConfig(
            thrust_source="test.eng",
            burn_out_time_s=3.9,
            dry_mass_kg=1.815,
            position_m=-1.255,
            # ... other required fields
        )
        assert config.thrust_source == "test.eng"
        assert config.position_m == -1.255

    def test_load_config():
        """Test loading configuration from YAML."""
        config = load_config("tests/fixtures/test_config.yaml")
        assert config.motor.thrust_source == "Cesaroni_M1670.eng"

Integration Tests
~~~~~~~~~~~~~~~~~

Test component interactions:

.. code-block:: python

    from src.motor_builder import MotorBuilder
    from src.rocket_builder import RocketBuilder

    def test_rocket_with_motor():
        """Test rocket construction with motor."""
        # Build motor
        motor_config = load_config("tests/fixtures/test_config.yaml").motor
        motor = MotorBuilder(motor_config).build()

        # Build rocket with motor
        rocket_config = load_config("tests/fixtures/test_config.yaml").rocket
        rocket_builder = RocketBuilder(
            rocket_config,
            motor=motor,
            motor_config=motor_config
        )
        rocket = rocket_builder.build()

        # Verify integration
        assert rocket.motor is not None
        assert rocket.mass > rocket_config.mass_kg

End-to-End Tests
~~~~~~~~~~~~~~~~

Test complete workflows:

.. code-block:: python

    from src.simulator import RocketSimulator

    def test_complete_simulation():
        """Test full simulation workflow."""
        # Load configuration
        config = load_config("tests/fixtures/test_config.yaml")

        # Build components
        motor = MotorBuilder(config.motor).build()
        environment = EnvironmentBuilder(config.environment).build()
        rocket = RocketBuilder(
            config.rocket,
            motor=motor,
            motor_config=config.motor
        ).build()

        # Run simulation
        simulator = RocketSimulator(rocket, environment, config.simulation)
        flight = simulator.run()
        summary = simulator.get_summary()

        # Verify results
        assert summary["apogee_m"] > 0
        assert summary["max_velocity_mps"] > 0

Test Fixtures
-------------

Using pytest Fixtures
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytest

    @pytest.fixture
    def motor_config():
        """Provide a test motor configuration."""
        return MotorConfig(
            thrust_source="test.eng",
            burn_out_time_s=3.9,
            dry_mass_kg=1.815,
            position_m=-1.255,
            # ... other fields
        )

    @pytest.fixture
    def motor(motor_config):
        """Provide a built motor."""
        return MotorBuilder(motor_config).build()

    def test_with_fixtures(motor):
        """Test using fixtures."""
        assert motor.dry_mass == 1.815

Configuration Files
~~~~~~~~~~~~~~~~~~~

Store test configurations in ``tests/fixtures/``:

.. code-block:: yaml

    # tests/fixtures/minimal_config.yaml
    motor:
      thrust_source: "test.eng"
      position_m: -1.255
      # ... minimal required fields

    rocket:
      mass_kg: 10.0
      # ... minimal required fields

    environment:
      latitude_deg: 0.0
      longitude_deg: 0.0
      elevation_m: 0

    simulation:
      rail_length_m: 5.0
      inclination_deg: 90
      heading_deg: 0

Mocking
-------

Mock External Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from unittest.mock import Mock, patch

    def test_with_mock_rocketpy():
        """Test with mocked RocketPy objects."""
        mock_flight = Mock()
        mock_flight.apogee = 2500.0

        with patch('rocketpy.Flight', return_value=mock_flight):
            # Test code that uses Flight
            pass

Mock File I/O
~~~~~~~~~~~~~

.. code-block:: python

    from unittest.mock import mock_open, patch

    def test_config_loading():
        """Test configuration loading with mocked file."""
        yaml_content = """
        motor:
          thrust_source: "test.eng"
        """

        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = load_config("fake_path.yaml")
            assert config.motor.thrust_source == "test.eng"

Parametrized Tests
------------------

Test Multiple Inputs
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pytest

    @pytest.mark.parametrize("inclination,expected_apogee", [
        (85, 2400),
        (87, 2500),
        (90, 2550),
    ])
    def test_inclination_effect(inclination, expected_apogee):
        """Test effect of inclination on apogee."""
        # Setup with given inclination
        config = load_config("tests/fixtures/test_config.yaml")
        config.simulation.inclination_deg = inclination

        # Run simulation
        # ... simulation code ...

        # Verify apogee is close to expected
        assert abs(apogee - expected_apogee) < 100

Test Coverage
-------------

Measuring Coverage
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest --cov=src --cov-report=term-missing tests/

HTML Coverage Report
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest --cov=src --cov-report=html tests/
    open htmlcov/index.html

Coverage Goals
~~~~~~~~~~~~~~

- **Overall**: >80%
- **Core modules**: >90%
- **Utilities**: >70%

Testing Best Practices
-----------------------

Test Structure (AAA Pattern)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def test_example():
        # Arrange: Set up test data
        config = MotorConfig(...)

        # Act: Execute the code under test
        motor = MotorBuilder(config).build()

        # Assert: Verify the results
        assert motor.dry_mass == 1.815

Test Naming
~~~~~~~~~~~

Use descriptive names:

.. code-block:: python

    # Good
    def test_motor_position_required_when_not_in_config():
        pass

    # Bad
    def test_motor():
        pass

Test Independence
~~~~~~~~~~~~~~~~~

Each test should be independent:

.. code-block:: python

    # Good: Uses fresh fixture
    def test_a(motor_config):
        motor_config.dry_mass_kg = 2.0
        assert motor_config.dry_mass_kg == 2.0

    def test_b(motor_config):
        # Gets fresh motor_config, unaffected by test_a
        assert motor_config.dry_mass_kg == 1.815

Test Error Cases
~~~~~~~~~~~~~~~~

Test both success and failure:

.. code-block:: python

    def test_motor_position_missing_raises_error():
        """Test that missing motor position raises ValueError."""
        with pytest.raises(ValueError, match="Motor position_m is required"):
            # Code that should raise
            builder.add_motor(motor, position_m=None)

Continuous Integration
----------------------

GitHub Actions
~~~~~~~~~~~~~~

Tests run automatically on every push/PR:

.. code-block:: yaml

    # .github/workflows/tests.yml
    name: Tests

    on: [push, pull_request]

    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - uses: actions/setup-python@v2
            with:
              python-version: 3.9
          - run: pip install -r requirements.txt
          - run: pip install -r requirements-dev.txt
          - run: pytest tests/ --cov=src

Debugging Tests
---------------

Run Single Test
~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest tests/test_config.py::test_load_config -v

Drop into Debugger on Failure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest --pdb tests/

Print Debug Output
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pytest -s tests/  # Show print statements

Performance Testing
-------------------

Time Tests
~~~~~~~~~~

.. code-block:: python

    import time

    def test_simulation_performance():
        """Test simulation completes within time limit."""
        start = time.time()

        # Run simulation
        flight = simulator.run()

        duration = time.time() - start
        assert duration < 2.0, f"Simulation took {duration:.2f}s"

Profile Tests
~~~~~~~~~~~~~

.. code-block:: bash

    pytest --profile tests/

Next Steps
----------

- :doc:`contributing` - Contribution guidelines
- :doc:`architecture` - Understand the codebase
- :doc:`code_style` - Follow coding standards
