"""Pytest configuration and shared fixtures for tests."""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.config_loader import (
    RocketConfig,
    MotorConfig,
    EnvironmentConfig,
    SimulationConfig,
    InertiaConfig,
    GeometryConfig,
    FinConfig,
    ParachuteConfig,
    WindConfig,
    RailConfig,
)


@pytest.fixture
def valid_rocket_config():
    """Return a valid RocketConfig for testing."""
    return RocketConfig(
        name="Test Rocket",
        dry_mass_kg=10.0,
        inertia=InertiaConfig(ixx_kg_m2=5.0, iyy_kg_m2=5.0, izz_kg_m2=0.03),
        geometry=GeometryConfig(caliber_m=0.1, length_m=1.5),
        cg_location_m=0.9,
        cp_location_m=1.2,
        fins=FinConfig(
            count=4,
            root_chord_m=0.1,
            tip_chord_m=0.05,
            span_m=0.08,
            thickness_m=0.003,
            position_m=-0.7,
        ),
        parachute=ParachuteConfig(
            enabled=True,
            cd_s=8.0,
            trigger="apogee",
        ),
    )


@pytest.fixture
def valid_motor_config():
    """Return a valid MotorConfig for testing."""
    return MotorConfig(
        type="SolidMotor",
        thrust_source="data/motors/test_motor.eng",
        dry_mass_kg=1.5,
        position_m=-1.2,
    )


@pytest.fixture
def valid_environment_config():
    """Return a valid EnvironmentConfig for testing."""
    return EnvironmentConfig(
        latitude_deg=40.0,
        longitude_deg=-8.0,
        elevation_m=50.0,
        wind=WindConfig(velocity_ms=3.0, direction_deg=0.0),
    )


@pytest.fixture
def valid_simulation_config():
    """Return a valid SimulationConfig for testing."""
    return SimulationConfig(
        max_time_s=600.0,
        rail=RailConfig(
            length_m=5.0,
            inclination_deg=85.0,
            heading_deg=0.0,
        ),
    )


@pytest.fixture
def sample_yaml_config(tmp_path):
    """Create a temporary YAML configuration file for testing.

    Args:
        tmp_path: Pytest temporary directory fixture.

    Returns:
        Path to temporary YAML file.
    """
    config_data = {
        "rocket": {
            "name": "Test Rocket",
            "dry_mass_kg": 10.0,
            "inertia": {
                "ixx_kg_m2": 5.0,
                "iyy_kg_m2": 5.0,
                "izz_kg_m2": 0.03,
            },
            "geometry": {
                "caliber_m": 0.1,
                "length_m": 1.5,
            },
            "cg_location_m": 0.9,
            "cp_location_m": 1.2,
            "fins": {
                "count": 4,
                "root_chord_m": 0.1,
                "tip_chord_m": 0.05,
                "span_m": 0.08,
                "thickness_m": 0.003,
                "position_m": -0.7,
            },
            "parachute": {
                "enabled": True,
                "cd_s": 8.0,
                "trigger": "apogee",
            },
        },
        "motor": {
            "type": "SolidMotor",
            "thrust_source": "data/motors/test_motor.eng",
            "dry_mass_kg": 1.5,
            "position_m": -1.2,
        },
        "environment": {
            "latitude_deg": 40.0,
            "longitude_deg": -8.0,
            "elevation_m": 50.0,
            "wind": {
                "velocity_ms": 3.0,
                "direction_deg": 0.0,
            },
        },
        "simulation": {
            "max_time_s": 600.0,
            "rail": {
                "length_m": 5.0,
                "inclination_deg": 85.0,
                "heading_deg": 0.0,
            },
        },
    }

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    return config_file


@pytest.fixture
def invalid_rocket_config():
    """Return an invalid RocketConfig for testing validation failures."""
    return RocketConfig(
        name="Invalid Rocket",
        dry_mass_kg=-5.0,  # Invalid: negative mass
        inertia=InertiaConfig(ixx_kg_m2=5.0, iyy_kg_m2=5.0, izz_kg_m2=0.03),
        geometry=GeometryConfig(caliber_m=0.1, length_m=1.5),
        cg_location_m=0.9,
        cp_location_m=0.5,  # Invalid: CP ahead of CG
    )
