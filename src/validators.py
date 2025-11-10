"""Validation utilities for rocket configuration parameters.

This module provides validation functions to check physical plausibility
and parameter constraints for rocket, motor, and environment configurations.
"""

from typing import List
import logging

from src.config_loader import (
    RocketConfig,
    MotorConfig,
    EnvironmentConfig,
    SimulationConfig,
)

logger = logging.getLogger(__name__)


class ValidationWarning:
    """Represents a validation warning."""

    def __init__(self, category: str, message: str):
        """Initialize validation warning.

        Args:
            category: Category of warning (e.g., "stability", "mass", "geometry").
            message: Descriptive warning message.
        """
        self.category = category
        self.message = message

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.category}] {self.message}"


class ValidationError(Exception):
    """Raised when configuration validation fails critically."""

    pass


class RocketValidator:
    """Validator for rocket configuration."""

    @staticmethod
    def validate(config: RocketConfig) -> List[ValidationWarning]:
        """Validate rocket configuration.

        Args:
            config: RocketConfig object to validate.

        Returns:
            List of ValidationWarning objects.

        Raises:
            ValidationError: If critical validation fails.
        """
        warnings = []

        # Mass validation
        if config.dry_mass_kg <= 0:
            raise ValidationError("Rocket dry mass must be positive")

        if config.dry_mass_kg < 0.5:
            warnings.append(
                ValidationWarning(
                    "mass",
                    f"Rocket dry mass ({config.dry_mass_kg:.2f} kg) is very low. "
                    "Is this correct?",
                )
            )

        if config.dry_mass_kg > 100:
            warnings.append(
                ValidationWarning(
                    "mass",
                    f"Rocket dry mass ({config.dry_mass_kg:.2f} kg) is very high. "
                    "Check if this is intentional.",
                )
            )

        # Inertia validation
        inertia = config.inertia
        if inertia.ixx_kg_m2 <= 0 or inertia.iyy_kg_m2 <= 0 or inertia.izz_kg_m2 <= 0:
            raise ValidationError("All inertia moments must be positive")

        # For cylindrical body, typically Ixx ≈ Iyy >> Izz
        if not (0.5 < inertia.ixx_kg_m2 / inertia.iyy_kg_m2 < 2.0):
            warnings.append(
                ValidationWarning(
                    "inertia",
                    f"Ixx/Iyy ratio ({inertia.ixx_kg_m2/inertia.iyy_kg_m2:.2f}) "
                    "is unusual for cylindrical rocket. Check inertia values.",
                )
            )

        # Geometry validation
        if config.geometry.caliber_m <= 0:
            raise ValidationError("Rocket caliber must be positive")

        if config.geometry.length_m <= 0:
            raise ValidationError("Rocket length must be positive")

        # Check reasonable length-to-diameter ratio
        length_to_diameter = config.geometry.length_m / config.geometry.caliber_m
        if length_to_diameter < 5:
            warnings.append(
                ValidationWarning(
                    "geometry",
                    f"Length-to-diameter ratio ({length_to_diameter:.1f}) is low. "
                    "Rocket may have high drag.",
                )
            )

        if length_to_diameter > 30:
            warnings.append(
                ValidationWarning(
                    "geometry",
                    f"Length-to-diameter ratio ({length_to_diameter:.1f}) is very high. "
                    "Rocket may be structurally weak.",
                )
            )

        # CG validation
        if config.cg_location_m < 0 or config.cg_location_m > config.geometry.length_m:
            raise ValidationError(
                f"CG location ({config.cg_location_m:.3f} m) must be between 0 and "
                f"rocket length ({config.geometry.length_m:.3f} m)"
            )

        # Stability validation (CP-CG margin)
        if config.cp_location_m is not None:
            cp_cg_margin = config.cp_location_m - config.cg_location_m

            if cp_cg_margin < 0:
                raise ValidationError(
                    f"CP ({config.cp_location_m:.3f} m) must be behind CG "
                    f"({config.cg_location_m:.3f} m) for stability"
                )

            # Static margin should be at least 1-2 calibers
            static_margin_calibers = cp_cg_margin / config.geometry.caliber_m

            if static_margin_calibers < 1.0:
                warnings.append(
                    ValidationWarning(
                        "stability",
                        f"Static margin ({static_margin_calibers:.2f} calibers) < 1. "
                        "Rocket may be marginally stable or unstable.",
                    )
                )

            if static_margin_calibers < 0.5:
                raise ValidationError(
                    f"Static margin ({static_margin_calibers:.2f} calibers) is too low. "
                    "Rocket is likely unstable."
                )

            if static_margin_calibers > 5.0:
                warnings.append(
                    ValidationWarning(
                        "stability",
                        f"Static margin ({static_margin_calibers:.2f} calibers) > 5. "
                        "Rocket is overstable and may weathercock excessively.",
                    )
                )

        # Fins validation
        if config.fins is not None:
            fins = config.fins

            if fins.count < 3:
                warnings.append(
                    ValidationWarning(
                        "fins",
                        f"Only {fins.count} fins. At least 3 fins recommended for stability.",
                    )
                )

            if fins.count > 6:
                warnings.append(
                    ValidationWarning(
                        "fins", f"{fins.count} fins is unusual. Typically 3-4 fins are used."
                    )
                )

            if fins.root_chord_m <= 0 or fins.tip_chord_m < 0 or fins.span_m <= 0:
                raise ValidationError("Fin dimensions must be positive")

            if fins.tip_chord_m > fins.root_chord_m:
                warnings.append(
                    ValidationWarning(
                        "fins",
                        "Tip chord > root chord is unusual. Check fin configuration.",
                    )
                )

            if fins.thickness_m <= 0:
                raise ValidationError("Fin thickness must be positive")

            if fins.thickness_m > 0.01:
                warnings.append(
                    ValidationWarning(
                        "fins",
                        f"Fin thickness ({fins.thickness_m*1000:.1f} mm) is very large.",
                    )
                )

        # Parachute validation
        if config.parachute is not None and config.parachute.enabled:
            para = config.parachute

            if para.cd_s <= 0:
                raise ValidationError("Parachute Cd*S must be positive")

            if para.cd_s < 0.5:
                warnings.append(
                    ValidationWarning(
                        "parachute",
                        f"Parachute Cd*S ({para.cd_s:.2f}) is very small. "
                        "May result in high impact velocity.",
                    )
                )

            if para.lag_s < 0:
                raise ValidationError("Parachute lag time cannot be negative")

            if para.lag_s > 5:
                warnings.append(
                    ValidationWarning(
                        "parachute",
                        f"Parachute lag time ({para.lag_s:.1f} s) is very long.",
                    )
                )

            if isinstance(para.trigger, (int, float)) and para.trigger < 0:
                raise ValidationError("Parachute trigger altitude cannot be negative")

        return warnings


class MotorValidator:
    """Validator for motor configuration."""

    @staticmethod
    def validate(config: MotorConfig) -> List[ValidationWarning]:
        """Validate motor configuration.

        Args:
            config: MotorConfig object to validate.

        Returns:
            List of ValidationWarning objects.

        Raises:
            ValidationError: If critical validation fails.
        """
        warnings = []

        # Mass validation
        if config.dry_mass_kg <= 0:
            raise ValidationError("Motor dry mass must be positive")

        # Inertia validation
        for i, inertia_value in enumerate(config.dry_inertia):
            if inertia_value <= 0:
                raise ValidationError(f"Motor inertia component {i} must be positive")

        # Geometry validation
        if config.nozzle_radius_m <= 0:
            raise ValidationError("Nozzle radius must be positive")

        if config.throat_radius_m <= 0:
            raise ValidationError("Throat radius must be positive")

        if config.throat_radius_m > config.nozzle_radius_m:
            raise ValidationError("Throat radius must be <= nozzle radius")

        # Grain validation for solid motors
        if config.type == "SolidMotor":
            if config.grain_number < 1:
                raise ValidationError("Number of grains must be at least 1")

            if config.grain_density_kg_m3 <= 0:
                raise ValidationError("Grain density must be positive")

            if config.grain_density_kg_m3 < 1000 or config.grain_density_kg_m3 > 2500:
                warnings.append(
                    ValidationWarning(
                        "motor",
                        f"Grain density ({config.grain_density_kg_m3:.0f} kg/m³) "
                        "is outside typical range (1000-2500 kg/m³).",
                    )
                )

            if config.grain_outer_radius_m <= 0:
                raise ValidationError("Grain outer radius must be positive")

            if config.grain_initial_inner_radius_m < 0:
                raise ValidationError("Grain inner radius cannot be negative")

            if config.grain_initial_inner_radius_m >= config.grain_outer_radius_m:
                raise ValidationError("Grain inner radius must be < outer radius")

            if config.grain_initial_height_m <= 0:
                raise ValidationError("Grain height must be positive")

            if config.grain_separation_m < 0:
                raise ValidationError("Grain separation cannot be negative")

        # Burn time validation
        if config.burn_time_s is not None:
            if config.burn_time_s <= 0:
                raise ValidationError("Burn time must be positive")

            if config.burn_time_s < 0.5:
                warnings.append(
                    ValidationWarning(
                        "motor",
                        f"Burn time ({config.burn_time_s:.2f} s) is very short.",
                    )
                )

            if config.burn_time_s > 10:
                warnings.append(
                    ValidationWarning(
                        "motor",
                        f"Burn time ({config.burn_time_s:.2f} s) is very long for hobby rocket.",
                    )
                )

        # Thrust source validation
        if not config.thrust_source:
            warnings.append(
                ValidationWarning(
                    "motor", "No thrust source file specified. Motor will have no thrust."
                )
            )

        return warnings


class EnvironmentValidator:
    """Validator for environment configuration."""

    @staticmethod
    def validate(config: EnvironmentConfig) -> List[ValidationWarning]:
        """Validate environment configuration.

        Args:
            config: EnvironmentConfig object to validate.

        Returns:
            List of ValidationWarning objects.

        Raises:
            ValidationError: If critical validation fails.
        """
        warnings = []

        # Location validation
        if not (-90 <= config.latitude_deg <= 90):
            raise ValidationError(
                f"Latitude ({config.latitude_deg}°) must be between -90 and 90"
            )

        if not (-180 <= config.longitude_deg <= 180):
            raise ValidationError(
                f"Longitude ({config.longitude_deg}°) must be between -180 and 180"
            )

        if config.elevation_m < -500:
            raise ValidationError("Elevation cannot be below -500 m (Dead Sea level)")

        if config.elevation_m > 5000:
            warnings.append(
                ValidationWarning(
                    "environment",
                    f"Elevation ({config.elevation_m:.0f} m) is very high. "
                    "Check atmospheric model validity.",
                )
            )

        # Gravity validation
        if config.gravity_ms2 <= 0:
            raise ValidationError("Gravity must be positive")

        if not (9.7 <= config.gravity_ms2 <= 9.9):
            warnings.append(
                ValidationWarning(
                    "environment",
                    f"Gravity ({config.gravity_ms2:.3f} m/s²) is outside typical "
                    "Earth range (9.78-9.83 m/s²).",
                )
            )

        # Wind validation
        if config.wind.velocity_ms < 0:
            raise ValidationError("Wind velocity cannot be negative")

        if config.wind.velocity_ms > 20:
            warnings.append(
                ValidationWarning(
                    "environment",
                    f"Wind velocity ({config.wind.velocity_ms:.1f} m/s) is very high. "
                    "Launch may be unsafe.",
                )
            )

        if not (0 <= config.wind.direction_deg < 360):
            warnings.append(
                ValidationWarning(
                    "environment",
                    f"Wind direction ({config.wind.direction_deg:.0f}°) should be "
                    "normalized to 0-360 degrees.",
                )
            )

        # Max expected height validation
        if config.max_expected_height_m <= 0:
            raise ValidationError("Max expected height must be positive")

        if config.max_expected_height_m > 100000:
            warnings.append(
                ValidationWarning(
                    "environment",
                    f"Max expected height ({config.max_expected_height_m:.0f} m) "
                    "is very high. Check if this is correct.",
                )
            )

        return warnings


class SimulationValidator:
    """Validator for simulation configuration."""

    @staticmethod
    def validate(config: SimulationConfig) -> List[ValidationWarning]:
        """Validate simulation configuration.

        Args:
            config: SimulationConfig object to validate.

        Returns:
            List of ValidationWarning objects.

        Raises:
            ValidationError: If critical validation fails.
        """
        warnings = []

        # Time validation
        if config.max_time_s <= 0:
            raise ValidationError("Max simulation time must be positive")

        if config.max_time_s < 10:
            warnings.append(
                ValidationWarning(
                    "simulation",
                    f"Max time ({config.max_time_s:.1f} s) is very short. "
                    "Flight may not complete.",
                )
            )

        if config.min_time_step_s < 0:
            raise ValidationError("Min time step cannot be negative")

        if config.max_time_step_s <= 0:
            raise ValidationError("Max time step must be positive")

        if config.min_time_step_s > config.max_time_step_s:
            raise ValidationError("Min time step cannot exceed max time step")

        # Tolerance validation - convert to float if string (e.g., "1e-6" from YAML)
        rtol = float(config.rtol) if isinstance(config.rtol, str) else config.rtol
        atol = float(config.atol) if isinstance(config.atol, str) else config.atol
        
        if rtol <= 0 or atol <= 0:
            raise ValidationError("Tolerances must be positive")

        if rtol > 1e-3 or atol > 1e-3:
            warnings.append(
                ValidationWarning(
                    "simulation",
                    "Tolerances are loose. Simulation accuracy may be reduced.",
                )
            )

        # Rail configuration validation
        if config.rail.length_m <= 0:
            raise ValidationError("Rail length must be positive")

        if config.rail.length_m < 1.0:
            warnings.append(
                ValidationWarning(
                    "simulation",
                    f"Rail length ({config.rail.length_m:.2f} m) is very short. "
                    "Rocket may be unstable off the rail.",
                )
            )

        if config.rail.length_m > 20:
            warnings.append(
                ValidationWarning(
                    "simulation",
                    f"Rail length ({config.rail.length_m:.2f} m) is very long.",
                )
            )

        if not (0 <= config.rail.inclination_deg <= 90):
            raise ValidationError("Rail inclination must be between 0 and 90 degrees")

        if config.rail.inclination_deg < 80:
            warnings.append(
                ValidationWarning(
                    "simulation",
                    f"Rail inclination ({config.rail.inclination_deg:.1f}°) "
                    "is low. This is intentional non-vertical launch.",
                )
            )

        if not (0 <= config.rail.heading_deg < 360):
            warnings.append(
                ValidationWarning(
                    "simulation",
                    f"Rail heading ({config.rail.heading_deg:.0f}°) should be "
                    "normalized to 0-360 degrees.",
                )
            )

        return warnings


def validate_all_configs(
    rocket: RocketConfig,
    motor: MotorConfig,
    environment: EnvironmentConfig,
    simulation: SimulationConfig,
) -> List[ValidationWarning]:
    """Validate all configuration objects.

    Args:
        rocket: RocketConfig object.
        motor: MotorConfig object.
        environment: EnvironmentConfig object.
        simulation: SimulationConfig object.

    Returns:
        Combined list of all ValidationWarning objects.

    Raises:
        ValidationError: If any critical validation fails.
    """
    all_warnings = []

    logger.info("Validating rocket configuration...")
    all_warnings.extend(RocketValidator.validate(rocket))

    logger.info("Validating motor configuration...")
    all_warnings.extend(MotorValidator.validate(motor))

    logger.info("Validating environment configuration...")
    all_warnings.extend(EnvironmentValidator.validate(environment))

    logger.info("Validating simulation configuration...")
    all_warnings.extend(SimulationValidator.validate(simulation))

    # Cross-configuration validation
    # Check if rail length is reasonable compared to rocket length
    if simulation.rail.length_m > rocket.geometry.length_m:
        all_warnings.append(
            ValidationWarning(
                "cross-config",
                f"Rail length ({simulation.rail.length_m:.2f} m) > rocket length "
                f"({rocket.geometry.length_m:.2f} m). This is unusual.",
            )
        )

    if all_warnings:
        logger.warning(f"Found {len(all_warnings)} validation warnings:")
        for warning in all_warnings:
            logger.warning(f"  {warning}")
    else:
        logger.info("All validations passed without warnings.")

    return all_warnings
