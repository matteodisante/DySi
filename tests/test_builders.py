"""Tests for builder classes (MotorBuilder, EnvironmentBuilder, RocketBuilder).

Note: These tests require RocketPy to be installed. Tests will be skipped
if RocketPy is not available.
"""

import pytest
from pathlib import Path

# Check if RocketPy is available
try:
    import rocketpy
    ROCKETPY_AVAILABLE = True
except ImportError:
    ROCKETPY_AVAILABLE = False

from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder


# Pytest marker for RocketPy-dependent tests
requires_rocketpy = pytest.mark.skipif(
    not ROCKETPY_AVAILABLE,
    reason="RocketPy not installed"
)


class TestMotorBuilder:
    """Test MotorBuilder class."""

    def test_initialization(self, valid_motor_config):
        """Test MotorBuilder initialization."""
        if not ROCKETPY_AVAILABLE:
            # Test that ImportError is raised when RocketPy is not available
            with pytest.raises(ImportError, match="RocketPy is not installed"):
                MotorBuilder(valid_motor_config)
        else:
            builder = MotorBuilder(valid_motor_config)
            assert builder.config == valid_motor_config
            assert builder.motor is None

    @requires_rocketpy
    def test_unsupported_motor_type(self, valid_motor_config):
        """Test that unsupported motor types raise ValueError."""
        valid_motor_config.type = "LiquidMotor"
        builder = MotorBuilder(valid_motor_config)

        with pytest.raises(ValueError, match="Motor type.*not supported"):
            builder.build()

    @requires_rocketpy
    def test_missing_thrust_file_raises_error(self, valid_motor_config):
        """Test that missing thrust file raises FileNotFoundError."""
        valid_motor_config.thrust_source = "nonexistent_file.eng"
        builder = MotorBuilder(valid_motor_config)

        with pytest.raises(FileNotFoundError, match="Thrust curve file not found"):
            builder.build()

    @requires_rocketpy
    def test_get_summary_before_build_raises_error(self, valid_motor_config):
        """Test that get_summary() raises error before build()."""
        valid_motor_config.thrust_source = ""  # Avoid file not found error
        builder = MotorBuilder(valid_motor_config)

        with pytest.raises(RuntimeError, match="Motor not built yet"):
            builder.get_summary()

    @requires_rocketpy
    def test_from_eng_file_missing_file(self):
        """Test from_eng_file with missing file."""
        with pytest.raises(FileNotFoundError):
            MotorBuilder.from_eng_file("nonexistent.eng")

    def test_validate_thrust_curve_before_build(self, valid_motor_config):
        """Test validate_thrust_curve before build raises error."""
        if ROCKETPY_AVAILABLE:
            builder = MotorBuilder(valid_motor_config)
            with pytest.raises(RuntimeError, match="Motor not built yet"):
                builder.validate_thrust_curve()


class TestEnvironmentBuilder:
    """Test EnvironmentBuilder class."""

    def test_initialization(self, valid_environment_config):
        """Test EnvironmentBuilder initialization."""
        if not ROCKETPY_AVAILABLE:
            # Test that ImportError is raised when RocketPy is not available
            with pytest.raises(ImportError, match="RocketPy is not installed"):
                EnvironmentBuilder(valid_environment_config)
        else:
            builder = EnvironmentBuilder(valid_environment_config)
            assert builder.config == valid_environment_config
            assert builder.environment is None

    @requires_rocketpy
    def test_build_creates_environment(self, valid_environment_config):
        """Test that build() creates an Environment instance."""
        builder = EnvironmentBuilder(valid_environment_config)
        env = builder.build()

        assert env is not None
        assert builder.environment is not None
        assert env.latitude == valid_environment_config.latitude_deg
        assert env.longitude == valid_environment_config.longitude_deg
        assert env.elevation == valid_environment_config.elevation_m

    @requires_rocketpy
    def test_custom_atmosphere_without_file_raises_error(self, valid_environment_config):
        """Test custom atmosphere without file raises ValueError."""
        valid_environment_config.atmospheric_model = "custom_atmosphere"
        valid_environment_config.atmospheric_model_file = None

        builder = EnvironmentBuilder(valid_environment_config)

        with pytest.raises(ValueError, match="Custom atmosphere model requires"):
            builder.build()

    @requires_rocketpy
    def test_custom_atmosphere_missing_file_raises_error(self, valid_environment_config):
        """Test custom atmosphere with missing file raises FileNotFoundError."""
        valid_environment_config.atmospheric_model = "custom_atmosphere"
        valid_environment_config.atmospheric_model_file = "nonexistent_atmosphere.nc"

        builder = EnvironmentBuilder(valid_environment_config)

        with pytest.raises(FileNotFoundError, match="Atmospheric model file not found"):
            builder.build()

    @requires_rocketpy
    def test_unsupported_wind_model_raises_error(self, valid_environment_config):
        """Test unsupported wind model raises ValueError."""
        valid_environment_config.wind.model = "unsupported_model"

        builder = EnvironmentBuilder(valid_environment_config)

        with pytest.raises(ValueError, match="Unsupported wind model"):
            builder.build()

    @requires_rocketpy
    def test_get_atmospheric_conditions_before_build(self, valid_environment_config):
        """Test get_atmospheric_conditions before build raises error."""
        builder = EnvironmentBuilder(valid_environment_config)

        with pytest.raises(RuntimeError, match="Environment not built yet"):
            builder.get_atmospheric_conditions()

    @requires_rocketpy
    def test_get_summary_before_build(self, valid_environment_config):
        """Test get_summary before build raises error."""
        builder = EnvironmentBuilder(valid_environment_config)

        with pytest.raises(RuntimeError, match="Environment not built yet"):
            builder.get_summary()

    @requires_rocketpy
    def test_get_atmospheric_conditions_at_altitude(self, valid_environment_config):
        """Test getting atmospheric conditions at specific altitude."""
        builder = EnvironmentBuilder(valid_environment_config)
        builder.build()

        conditions = builder.get_atmospheric_conditions(altitude_m=1000.0)

        assert "altitude_m" in conditions
        assert "pressure_pa" in conditions
        assert "temperature_k" in conditions
        assert "density_kg_m3" in conditions
        assert conditions["altitude_m"] == 1000.0
        assert conditions["pressure_pa"] > 0
        assert conditions["temperature_k"] > 0
        assert conditions["density_kg_m3"] > 0

    @requires_rocketpy
    def test_from_location_factory(self):
        """Test from_location factory method."""
        env = EnvironmentBuilder.from_location(
            latitude_deg=40.0,
            longitude_deg=-8.0,
            elevation_m=100.0,
        )

        assert env is not None
        assert env.latitude == 40.0
        assert env.longitude == -8.0
        assert env.elevation == 100.0


class TestRocketBuilder:
    """Test RocketBuilder class."""

    def test_initialization(self, valid_rocket_config):
        """Test RocketBuilder initialization."""
        if not ROCKETPY_AVAILABLE:
            # Test that ImportError is raised when RocketPy is not available
            with pytest.raises(ImportError, match="RocketPy is not installed"):
                RocketBuilder(valid_rocket_config)
        else:
            builder = RocketBuilder(valid_rocket_config)
            assert builder.config == valid_rocket_config
            assert builder.motor is None
            assert builder.rocket is None

    @requires_rocketpy
    def test_build_creates_rocket(self, valid_rocket_config):
        """Test that build() creates a Rocket instance."""
        builder = RocketBuilder(valid_rocket_config)
        rocket = builder.build()

        assert rocket is not None
        assert builder.rocket is not None
        assert rocket.radius == valid_rocket_config.radius_m
        assert rocket.dry_mass == valid_rocket_config.dry_mass_kg

    @requires_rocketpy
    def test_missing_drag_file_raises_error(self, valid_rocket_config):
        """Test that missing drag file raises FileNotFoundError."""
        valid_rocket_config.power_off_drag = "nonexistent_drag.csv"

        builder = RocketBuilder(valid_rocket_config)

        with pytest.raises(FileNotFoundError, match="Drag curve file not found"):
            builder.build()

    @requires_rocketpy
    def test_add_motor_before_build_raises_error(self, valid_rocket_config):
        """Test that add_motor() before build() raises error."""
        from rocketpy import SolidMotor

        builder = RocketBuilder(valid_rocket_config)

        # Create a mock motor (this would normally come from MotorBuilder)
        # For testing, we'll just pass None and expect an error
        with pytest.raises(RuntimeError, match="Rocket not created yet"):
            builder.add_motor(None)

    @requires_rocketpy
    def test_add_nose_cone_without_config_raises_error(self, valid_rocket_config):
        """Test that add_nose_cone() without config raises error."""
        valid_rocket_config.nose_cone = None

        builder = RocketBuilder(valid_rocket_config)
        builder.build()

        with pytest.raises(ValueError, match="Nose cone configuration is missing"):
            builder.add_nose_cone()

    @requires_rocketpy
    def test_add_fins_without_config_raises_error(self, valid_rocket_config):
        """Test that add_fins() without config raises error."""
        valid_rocket_config.fins = None

        builder = RocketBuilder(valid_rocket_config)
        builder.build()

        with pytest.raises(ValueError, match="Fin configuration is missing"):
            builder.add_fins()

    @requires_rocketpy
    def test_add_parachute_without_config_raises_error(self, valid_rocket_config):
        """Test that add_parachute() without config raises error."""
        valid_rocket_config.parachute = None

        builder = RocketBuilder(valid_rocket_config)
        builder.build()

        with pytest.raises(ValueError, match="Parachute configuration is missing"):
            builder.add_parachute()

    @requires_rocketpy
    def test_get_stability_info_before_build(self, valid_rocket_config):
        """Test get_stability_info before build raises error."""
        builder = RocketBuilder(valid_rocket_config)

        with pytest.raises(RuntimeError, match="Rocket not built yet"):
            builder.get_stability_info()

    @requires_rocketpy
    def test_get_summary_before_build(self, valid_rocket_config):
        """Test get_summary before build raises error."""
        builder = RocketBuilder(valid_rocket_config)

        with pytest.raises(RuntimeError, match="Rocket not built yet"):
            builder.get_summary()

    @requires_rocketpy
    def test_validate_stability_before_build(self, valid_rocket_config):
        """Test validate_stability before build raises error."""
        builder = RocketBuilder(valid_rocket_config)

        with pytest.raises(RuntimeError, match="Rocket not built yet"):
            builder.validate_stability()

    @requires_rocketpy
    def test_build_with_all_components(self, valid_rocket_config):
        """Test building rocket with all components."""
        builder = RocketBuilder(valid_rocket_config)
        rocket = builder.build()

        # Verify rocket was created
        assert rocket is not None

        # Verify components were added (check via summary)
        summary = builder.get_summary()
        assert summary["name"] == valid_rocket_config.name
        assert summary["has_fins"] == True
        assert summary["fin_count"] == valid_rocket_config.fins.count
        assert summary["has_parachute"] == True


class TestBuilderIntegration:
    """Integration tests for builder classes working together."""

    @requires_rocketpy
    def test_complete_rocket_assembly(
        self,
        valid_rocket_config,
        valid_motor_config,
        valid_environment_config,
    ):
        """Test complete rocket assembly with motor and environment."""
        # Note: This test requires actual motor file to exist
        # For now, we'll skip the motor build
        pytest.skip("Requires actual thrust curve file")

        # Build motor
        motor_builder = MotorBuilder(valid_motor_config)
        motor = motor_builder.build()

        # Build rocket with motor
        rocket_builder = RocketBuilder(valid_rocket_config, motor=motor)
        rocket = rocket_builder.build()

        # Build environment
        env_builder = EnvironmentBuilder(valid_environment_config)
        env = env_builder.build()

        # Verify all components
        assert rocket is not None
        assert motor is not None
        assert env is not None

        # Get summaries
        rocket_summary = rocket_builder.get_summary()
        motor_summary = motor_builder.get_summary()
        env_summary = env_builder.get_summary()

        assert rocket_summary["has_motor"] == True
        assert motor_summary["burn_time_s"] > 0
        assert env_summary["elevation_m"] == valid_environment_config.elevation_m
