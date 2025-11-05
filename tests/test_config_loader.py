"""Tests for configuration loading functionality."""

import pytest
from pathlib import Path
import yaml

from src.config_loader import (
    ConfigLoader,
    RocketConfig,
    MotorConfig,
    EnvironmentConfig,
    SimulationConfig,
    InertiaConfig,
    GeometryConfig,
)


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_load_yaml_success(self, sample_yaml_config):
        """Test successful YAML file loading."""
        loader = ConfigLoader()
        data = loader.load_yaml(sample_yaml_config)

        assert isinstance(data, dict)
        assert "rocket" in data
        assert "motor" in data
        assert "environment" in data
        assert "simulation" in data

    def test_load_yaml_file_not_found(self):
        """Test loading non-existent YAML file raises FileNotFoundError."""
        loader = ConfigLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_yaml("nonexistent_file.yaml")

    def test_load_from_yaml(self, sample_yaml_config):
        """Test load_from_yaml method."""
        loader = ConfigLoader()
        loader.load_from_yaml(sample_yaml_config)

        assert loader.config_path == Path(sample_yaml_config)
        assert isinstance(loader.config_data, dict)
        assert len(loader.config_data) > 0

    def test_merge_configs(self):
        """Test configuration merging."""
        loader = ConfigLoader()

        base = {"a": 1, "b": {"c": 2, "d": 3}}
        update = {"b": {"d": 4, "e": 5}, "f": 6}

        merged = loader.merge_configs(base, update)

        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 4
        assert merged["b"]["e"] == 5
        assert merged["f"] == 6

    def test_get_rocket_config(self, sample_yaml_config):
        """Test parsing RocketConfig from YAML."""
        loader = ConfigLoader()
        loader.load_from_yaml(sample_yaml_config)
        rocket_cfg = loader.get_rocket_config()

        assert isinstance(rocket_cfg, RocketConfig)
        assert rocket_cfg.name == "Test Rocket"
        assert rocket_cfg.dry_mass_kg == 10.0
        assert rocket_cfg.geometry.caliber_m == 0.1
        assert rocket_cfg.cg_location_m == 0.9
        assert rocket_cfg.fins is not None
        assert rocket_cfg.fins.count == 4

    def test_get_rocket_config_missing_section(self):
        """Test getting rocket config without rocket section raises KeyError."""
        loader = ConfigLoader()
        loader.config_data = {"motor": {}}

        with pytest.raises(KeyError, match="'rocket' section not found"):
            loader.get_rocket_config()

    def test_get_motor_config(self, sample_yaml_config):
        """Test parsing MotorConfig from YAML."""
        loader = ConfigLoader()
        loader.load_from_yaml(sample_yaml_config)
        motor_cfg = loader.get_motor_config()

        assert isinstance(motor_cfg, MotorConfig)
        assert motor_cfg.type == "SolidMotor"
        assert motor_cfg.dry_mass_kg == 1.5
        assert motor_cfg.thrust_source == "data/motors/test_motor.eng"

    def test_get_motor_config_missing_section(self):
        """Test getting motor config without motor section raises KeyError."""
        loader = ConfigLoader()
        loader.config_data = {"rocket": {}}

        with pytest.raises(KeyError, match="'motor' section not found"):
            loader.get_motor_config()

    def test_get_environment_config(self, sample_yaml_config):
        """Test parsing EnvironmentConfig from YAML."""
        loader = ConfigLoader()
        loader.load_from_yaml(sample_yaml_config)
        env_cfg = loader.get_environment_config()

        assert isinstance(env_cfg, EnvironmentConfig)
        assert env_cfg.latitude_deg == 40.0
        assert env_cfg.longitude_deg == -8.0
        assert env_cfg.elevation_m == 50.0
        assert env_cfg.wind.velocity_ms == 3.0

    def test_get_environment_config_missing_section(self):
        """Test getting environment config without section raises KeyError."""
        loader = ConfigLoader()
        loader.config_data = {"rocket": {}}

        with pytest.raises(KeyError, match="'environment' section not found"):
            loader.get_environment_config()

    def test_get_simulation_config(self, sample_yaml_config):
        """Test parsing SimulationConfig from YAML."""
        loader = ConfigLoader()
        loader.load_from_yaml(sample_yaml_config)
        sim_cfg = loader.get_simulation_config()

        assert isinstance(sim_cfg, SimulationConfig)
        assert sim_cfg.max_time_s == 600.0
        assert sim_cfg.rail.length_m == 5.0
        assert sim_cfg.rail.inclination_deg == 85.0

    def test_get_simulation_config_defaults(self):
        """Test simulation config with default values."""
        loader = ConfigLoader()
        loader.config_data = {}
        sim_cfg = loader.get_simulation_config()

        assert isinstance(sim_cfg, SimulationConfig)
        assert sim_cfg.max_time_s == 600.0
        assert sim_cfg.rtol == 1e-6
        assert sim_cfg.atol == 1e-6

    def test_load_complete_config(self, sample_yaml_config):
        """Test loading all configurations at once."""
        loader = ConfigLoader()
        rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(
            sample_yaml_config
        )

        assert isinstance(rocket_cfg, RocketConfig)
        assert isinstance(motor_cfg, MotorConfig)
        assert isinstance(env_cfg, EnvironmentConfig)
        assert isinstance(sim_cfg, SimulationConfig)

        assert rocket_cfg.name == "Test Rocket"
        assert motor_cfg.type == "SolidMotor"
        assert env_cfg.latitude_deg == 40.0
        assert sim_cfg.max_time_s == 600.0


class TestRocketConfig:
    """Test RocketConfig dataclass."""

    def test_radius_property(self, valid_rocket_config):
        """Test radius_m property calculation."""
        assert valid_rocket_config.radius_m == 0.05  # caliber_m / 2

    def test_static_margin_calculation(self, valid_rocket_config):
        """Test static margin calculation."""
        # cp_location_m = 1.2, cg_location_m = 0.9, caliber_m = 0.1
        # static_margin = (1.2 - 0.9) / 0.1 = 3.0 calibers
        assert valid_rocket_config.static_margin_calibers == pytest.approx(3.0)

    def test_static_margin_none_when_cp_none(self, valid_rocket_config):
        """Test static margin is None when CP is not specified."""
        valid_rocket_config.cp_location_m = None
        assert valid_rocket_config.static_margin_calibers is None


class TestInertiaConfig:
    """Test InertiaConfig dataclass."""

    def test_to_tuple(self):
        """Test conversion to tuple."""
        inertia = InertiaConfig(ixx_kg_m2=1.0, iyy_kg_m2=2.0, izz_kg_m2=0.5)
        assert inertia.to_tuple() == (1.0, 2.0, 0.5)


class TestEnvironmentConfig:
    """Test EnvironmentConfig dataclass with date handling."""

    def test_date_parsing(self, tmp_path):
        """Test parsing date from configuration."""
        config_data = {
            "environment": {
                "latitude_deg": 40.0,
                "longitude_deg": -8.0,
                "elevation_m": 50.0,
                "date": [2023, 6, 15, 12],
            }
        }

        config_file = tmp_path / "test_date_config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        loader = ConfigLoader()
        loader.load_from_yaml(config_file)
        env_cfg = loader.get_environment_config()

        assert env_cfg.date == (2023, 6, 15, 12)

    def test_date_none_when_not_provided(self, valid_environment_config):
        """Test date is None when not provided."""
        assert valid_environment_config.date is None


class TestMotorConfig:
    """Test MotorConfig dataclass."""

    def test_default_values(self):
        """Test default motor configuration values."""
        motor = MotorConfig()
        assert motor.type == "SolidMotor"
        assert motor.grain_number == 5
        assert motor.dry_mass_kg == 1.5


class TestSimulationConfig:
    """Test SimulationConfig dataclass."""

    def test_default_tolerance_values(self, valid_simulation_config):
        """Test default tolerance values."""
        assert valid_simulation_config.rtol == 1e-6
        assert valid_simulation_config.atol == 1e-6
        assert valid_simulation_config.verbose is False
        assert valid_simulation_config.terminate_on_apogee is False
