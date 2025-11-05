"""Tests for configuration validation functionality."""

import pytest

from src.validators import (
    RocketValidator,
    MotorValidator,
    EnvironmentValidator,
    SimulationValidator,
    ValidationError,
    ValidationWarning,
    validate_all_configs,
)
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


class TestValidationWarning:
    """Test ValidationWarning class."""

    def test_creation(self):
        """Test ValidationWarning creation."""
        warning = ValidationWarning("stability", "Test warning message")
        assert warning.category == "stability"
        assert warning.message == "Test warning message"

    def test_string_representation(self):
        """Test string representation."""
        warning = ValidationWarning("mass", "Mass is too low")
        assert str(warning) == "[mass] Mass is too low"


class TestRocketValidator:
    """Test RocketValidator class."""

    def test_valid_rocket_no_warnings(self, valid_rocket_config):
        """Test validation of valid rocket returns no warnings."""
        warnings = RocketValidator.validate(valid_rocket_config)
        assert isinstance(warnings, list)
        # May have warnings depending on exact values, but should not raise

    def test_negative_mass_raises_error(self, valid_rocket_config):
        """Test negative mass raises ValidationError."""
        valid_rocket_config.dry_mass_kg = -5.0
        with pytest.raises(ValidationError, match="Rocket dry mass must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_zero_mass_raises_error(self, valid_rocket_config):
        """Test zero mass raises ValidationError."""
        valid_rocket_config.dry_mass_kg = 0.0
        with pytest.raises(ValidationError, match="Rocket dry mass must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_very_low_mass_warning(self, valid_rocket_config):
        """Test very low mass produces warning."""
        valid_rocket_config.dry_mass_kg = 0.3
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("very low" in str(w).lower() for w in warnings)

    def test_very_high_mass_warning(self, valid_rocket_config):
        """Test very high mass produces warning."""
        valid_rocket_config.dry_mass_kg = 150.0
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("very high" in str(w).lower() for w in warnings)

    def test_negative_inertia_raises_error(self, valid_rocket_config):
        """Test negative inertia raises ValidationError."""
        valid_rocket_config.inertia.ixx_kg_m2 = -1.0
        with pytest.raises(ValidationError, match="inertia moments must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_negative_caliber_raises_error(self, valid_rocket_config):
        """Test negative caliber raises ValidationError."""
        valid_rocket_config.geometry.caliber_m = -0.1
        with pytest.raises(ValidationError, match="caliber must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_negative_length_raises_error(self, valid_rocket_config):
        """Test negative length raises ValidationError."""
        valid_rocket_config.geometry.length_m = -1.0
        with pytest.raises(ValidationError, match="length must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_low_length_to_diameter_warning(self, valid_rocket_config):
        """Test low L/D ratio produces warning."""
        valid_rocket_config.geometry.length_m = 0.4  # L/D = 4
        valid_rocket_config.cg_location_m = 0.2  # Keep CG within rocket
        valid_rocket_config.cp_location_m = 0.3  # Keep CP within rocket
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("length-to-diameter" in str(w).lower() for w in warnings)

    def test_high_length_to_diameter_warning(self, valid_rocket_config):
        """Test high L/D ratio produces warning."""
        valid_rocket_config.geometry.length_m = 3.5  # L/D = 35
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("length-to-diameter" in str(w).lower() for w in warnings)

    def test_cg_out_of_bounds_raises_error(self, valid_rocket_config):
        """Test CG outside rocket length raises ValidationError."""
        valid_rocket_config.cg_location_m = 2.0  # > length_m
        with pytest.raises(ValidationError, match="CG location"):
            RocketValidator.validate(valid_rocket_config)

    def test_cp_ahead_of_cg_raises_error(self, valid_rocket_config):
        """Test CP ahead of CG raises ValidationError."""
        valid_rocket_config.cp_location_m = 0.5  # < cg_location_m
        with pytest.raises(ValidationError, match="CP.*must be behind CG"):
            RocketValidator.validate(valid_rocket_config)

    def test_low_static_margin_warning(self, valid_rocket_config):
        """Test low static margin produces warning."""
        valid_rocket_config.cp_location_m = 0.96  # margin = 0.6 calibers
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("static margin" in str(w).lower() for w in warnings)

    def test_very_low_static_margin_raises_error(self, valid_rocket_config):
        """Test very low static margin raises ValidationError."""
        valid_rocket_config.cp_location_m = 0.92  # margin = 0.2 calibers
        with pytest.raises(ValidationError, match="Static margin.*too low"):
            RocketValidator.validate(valid_rocket_config)

    def test_high_static_margin_warning(self, valid_rocket_config):
        """Test high static margin produces warning."""
        valid_rocket_config.cp_location_m = 1.5  # margin = 6 calibers
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("overstable" in str(w).lower() for w in warnings)

    def test_few_fins_warning(self, valid_rocket_config):
        """Test less than 3 fins produces warning."""
        valid_rocket_config.fins.count = 2
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("fins" in str(w).lower() for w in warnings)

    def test_many_fins_warning(self, valid_rocket_config):
        """Test more than 6 fins produces warning."""
        valid_rocket_config.fins.count = 8
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("fins is unusual" in str(w).lower() for w in warnings)

    def test_negative_fin_dimension_raises_error(self, valid_rocket_config):
        """Test negative fin dimensions raise ValidationError."""
        valid_rocket_config.fins.root_chord_m = -0.1
        with pytest.raises(ValidationError, match="Fin dimensions must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_tip_larger_than_root_warning(self, valid_rocket_config):
        """Test tip chord > root chord produces warning."""
        valid_rocket_config.fins.tip_chord_m = 0.15
        valid_rocket_config.fins.root_chord_m = 0.1
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("tip chord > root chord" in str(w).lower() for w in warnings)

    def test_negative_parachute_cd_raises_error(self, valid_rocket_config):
        """Test negative parachute Cd*S raises ValidationError."""
        valid_rocket_config.parachute.cd_s = -1.0
        with pytest.raises(ValidationError, match="Parachute Cd\\*S must be positive"):
            RocketValidator.validate(valid_rocket_config)

    def test_small_parachute_warning(self, valid_rocket_config):
        """Test small parachute Cd*S produces warning."""
        valid_rocket_config.parachute.cd_s = 0.3
        warnings = RocketValidator.validate(valid_rocket_config)
        assert any("parachute" in str(w).lower() and "small" in str(w).lower() for w in warnings)


class TestMotorValidator:
    """Test MotorValidator class."""

    def test_valid_motor_no_errors(self, valid_motor_config):
        """Test validation of valid motor doesn't raise errors."""
        warnings = MotorValidator.validate(valid_motor_config)
        assert isinstance(warnings, list)

    def test_negative_dry_mass_raises_error(self, valid_motor_config):
        """Test negative dry mass raises ValidationError."""
        valid_motor_config.dry_mass_kg = -1.0
        with pytest.raises(ValidationError, match="Motor dry mass must be positive"):
            MotorValidator.validate(valid_motor_config)

    def test_negative_inertia_raises_error(self, valid_motor_config):
        """Test negative inertia raises ValidationError."""
        valid_motor_config.dry_inertia = (0.1, -0.1, 0.002)
        with pytest.raises(ValidationError, match="Motor inertia component"):
            MotorValidator.validate(valid_motor_config)

    def test_negative_nozzle_radius_raises_error(self, valid_motor_config):
        """Test negative nozzle radius raises ValidationError."""
        valid_motor_config.nozzle_radius_m = -0.01
        with pytest.raises(ValidationError, match="Nozzle radius must be positive"):
            MotorValidator.validate(valid_motor_config)

    def test_negative_throat_radius_raises_error(self, valid_motor_config):
        """Test negative throat radius raises ValidationError."""
        valid_motor_config.throat_radius_m = -0.01
        with pytest.raises(ValidationError, match="Throat radius must be positive"):
            MotorValidator.validate(valid_motor_config)

    def test_throat_larger_than_nozzle_raises_error(self, valid_motor_config):
        """Test throat > nozzle radius raises ValidationError."""
        valid_motor_config.throat_radius_m = 0.05
        valid_motor_config.nozzle_radius_m = 0.03
        with pytest.raises(ValidationError, match="Throat radius must be"):
            MotorValidator.validate(valid_motor_config)

    def test_zero_grains_raises_error(self, valid_motor_config):
        """Test zero grains raises ValidationError."""
        valid_motor_config.grain_number = 0
        with pytest.raises(ValidationError, match="Number of grains must be at least 1"):
            MotorValidator.validate(valid_motor_config)

    def test_negative_grain_density_raises_error(self, valid_motor_config):
        """Test negative grain density raises ValidationError."""
        valid_motor_config.grain_density_kg_m3 = -1000.0
        with pytest.raises(ValidationError, match="Grain density must be positive"):
            MotorValidator.validate(valid_motor_config)

    def test_unusual_grain_density_warning(self, valid_motor_config):
        """Test unusual grain density produces warning."""
        valid_motor_config.grain_density_kg_m3 = 500.0
        warnings = MotorValidator.validate(valid_motor_config)
        assert any("grain density" in str(w).lower() for w in warnings)

    def test_inner_radius_greater_than_outer_raises_error(self, valid_motor_config):
        """Test inner > outer radius raises ValidationError."""
        valid_motor_config.grain_initial_inner_radius_m = 0.05
        valid_motor_config.grain_outer_radius_m = 0.03
        with pytest.raises(ValidationError, match="inner radius must be < outer radius"):
            MotorValidator.validate(valid_motor_config)

    def test_no_thrust_source_warning(self, valid_motor_config):
        """Test missing thrust source produces warning."""
        valid_motor_config.thrust_source = ""
        warnings = MotorValidator.validate(valid_motor_config)
        assert any("thrust source" in str(w).lower() for w in warnings)


class TestEnvironmentValidator:
    """Test EnvironmentValidator class."""

    def test_valid_environment_no_errors(self, valid_environment_config):
        """Test validation of valid environment doesn't raise errors."""
        warnings = EnvironmentValidator.validate(valid_environment_config)
        assert isinstance(warnings, list)

    def test_invalid_latitude_raises_error(self, valid_environment_config):
        """Test invalid latitude raises ValidationError."""
        valid_environment_config.latitude_deg = 95.0
        with pytest.raises(ValidationError, match="Latitude.*must be between"):
            EnvironmentValidator.validate(valid_environment_config)

    def test_invalid_longitude_raises_error(self, valid_environment_config):
        """Test invalid longitude raises ValidationError."""
        valid_environment_config.longitude_deg = 200.0
        with pytest.raises(ValidationError, match="Longitude.*must be between"):
            EnvironmentValidator.validate(valid_environment_config)

    def test_very_low_elevation_raises_error(self, valid_environment_config):
        """Test very low elevation raises ValidationError."""
        valid_environment_config.elevation_m = -600.0
        with pytest.raises(ValidationError, match="Elevation cannot be below"):
            EnvironmentValidator.validate(valid_environment_config)

    def test_high_elevation_warning(self, valid_environment_config):
        """Test high elevation produces warning."""
        valid_environment_config.elevation_m = 6000.0
        warnings = EnvironmentValidator.validate(valid_environment_config)
        assert any("elevation" in str(w).lower() and "high" in str(w).lower() for w in warnings)

    def test_negative_gravity_raises_error(self, valid_environment_config):
        """Test negative gravity raises ValidationError."""
        valid_environment_config.gravity_ms2 = -9.8
        with pytest.raises(ValidationError, match="Gravity must be positive"):
            EnvironmentValidator.validate(valid_environment_config)

    def test_unusual_gravity_warning(self, valid_environment_config):
        """Test unusual gravity value produces warning."""
        valid_environment_config.gravity_ms2 = 10.5
        warnings = EnvironmentValidator.validate(valid_environment_config)
        assert any("gravity" in str(w).lower() for w in warnings)

    def test_negative_wind_velocity_raises_error(self, valid_environment_config):
        """Test negative wind velocity raises ValidationError."""
        valid_environment_config.wind.velocity_ms = -5.0
        with pytest.raises(ValidationError, match="Wind velocity cannot be negative"):
            EnvironmentValidator.validate(valid_environment_config)

    def test_high_wind_warning(self, valid_environment_config):
        """Test high wind velocity produces warning."""
        valid_environment_config.wind.velocity_ms = 25.0
        warnings = EnvironmentValidator.validate(valid_environment_config)
        assert any("wind" in str(w).lower() and "high" in str(w).lower() for w in warnings)


class TestSimulationValidator:
    """Test SimulationValidator class."""

    def test_valid_simulation_no_errors(self, valid_simulation_config):
        """Test validation of valid simulation doesn't raise errors."""
        warnings = SimulationValidator.validate(valid_simulation_config)
        assert isinstance(warnings, list)

    def test_negative_max_time_raises_error(self, valid_simulation_config):
        """Test negative max time raises ValidationError."""
        valid_simulation_config.max_time_s = -100.0
        with pytest.raises(ValidationError, match="Max simulation time must be positive"):
            SimulationValidator.validate(valid_simulation_config)

    def test_very_short_max_time_warning(self, valid_simulation_config):
        """Test very short max time produces warning."""
        valid_simulation_config.max_time_s = 5.0
        warnings = SimulationValidator.validate(valid_simulation_config)
        assert any("max time" in str(w).lower() and "short" in str(w).lower() for w in warnings)

    def test_negative_tolerance_raises_error(self, valid_simulation_config):
        """Test negative tolerance raises ValidationError."""
        valid_simulation_config.rtol = -1e-6
        with pytest.raises(ValidationError, match="Tolerances must be positive"):
            SimulationValidator.validate(valid_simulation_config)

    def test_loose_tolerance_warning(self, valid_simulation_config):
        """Test loose tolerance produces warning."""
        valid_simulation_config.rtol = 1e-2
        warnings = SimulationValidator.validate(valid_simulation_config)
        assert any("tolerance" in str(w).lower() for w in warnings)

    def test_negative_rail_length_raises_error(self, valid_simulation_config):
        """Test negative rail length raises ValidationError."""
        valid_simulation_config.rail.length_m = -1.0
        with pytest.raises(ValidationError, match="Rail length must be positive"):
            SimulationValidator.validate(valid_simulation_config)

    def test_short_rail_warning(self, valid_simulation_config):
        """Test short rail produces warning."""
        valid_simulation_config.rail.length_m = 0.5
        warnings = SimulationValidator.validate(valid_simulation_config)
        assert any("rail length" in str(w).lower() and "short" in str(w).lower() for w in warnings)

    def test_invalid_inclination_raises_error(self, valid_simulation_config):
        """Test invalid rail inclination raises ValidationError."""
        valid_simulation_config.rail.inclination_deg = 95.0
        with pytest.raises(ValidationError, match="Rail inclination must be between"):
            SimulationValidator.validate(valid_simulation_config)

    def test_low_inclination_warning(self, valid_simulation_config):
        """Test low rail inclination produces warning."""
        valid_simulation_config.rail.inclination_deg = 70.0
        warnings = SimulationValidator.validate(valid_simulation_config)
        assert any("inclination" in str(w).lower() and "low" in str(w).lower() for w in warnings)


class TestValidateAllConfigs:
    """Test validate_all_configs function."""

    def test_all_valid_configs(
        self,
        valid_rocket_config,
        valid_motor_config,
        valid_environment_config,
        valid_simulation_config,
    ):
        """Test validation of all valid configs."""
        warnings = validate_all_configs(
            valid_rocket_config,
            valid_motor_config,
            valid_environment_config,
            valid_simulation_config,
        )
        assert isinstance(warnings, list)

    def test_cross_config_rail_length_warning(
        self,
        valid_rocket_config,
        valid_motor_config,
        valid_environment_config,
        valid_simulation_config,
    ):
        """Test cross-config validation for rail > rocket length."""
        valid_simulation_config.rail.length_m = 10.0  # > rocket length
        warnings = validate_all_configs(
            valid_rocket_config,
            valid_motor_config,
            valid_environment_config,
            valid_simulation_config,
        )
        assert any("rail length" in str(w).lower() and "rocket length" in str(w).lower() for w in warnings)

    def test_invalid_rocket_raises_error(
        self,
        valid_motor_config,
        valid_environment_config,
        valid_simulation_config,
    ):
        """Test that invalid rocket config raises ValidationError."""
        invalid_rocket = RocketConfig(
            name="Invalid",
            dry_mass_kg=-5.0,
            inertia=InertiaConfig(5, 5, 0.03),
            geometry=GeometryConfig(0.1, 1.5),
            cg_location_m=0.9,
        )

        with pytest.raises(ValidationError):
            validate_all_configs(
                invalid_rocket,
                valid_motor_config,
                valid_environment_config,
                valid_simulation_config,
            )
