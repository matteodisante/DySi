"""Motor builder for creating RocketPy motor instances from configuration.

This module provides the MotorBuilder class for constructing RocketPy motor
objects from configuration dataclasses.
"""

from pathlib import Path
from typing import Optional
import logging

try:
    from rocketpy import SolidMotor
except ImportError:
    SolidMotor = None

from src.config_loader import MotorConfig

logger = logging.getLogger(__name__)


class MotorBuilder:
    """Builder for RocketPy SolidMotor instances.

    This class constructs RocketPy SolidMotor objects from MotorConfig
    dataclasses, handling thrust curve loading and parameter conversion.

    Attributes:
        config: MotorConfig object with motor parameters.
        motor: Constructed SolidMotor instance (after build()).

    Example:
        >>> motor_config = MotorConfig(
        ...     thrust_source="data/motors/Cesaroni_M1670.eng",
        ...     dry_mass_kg=1.815,
        ... )
        >>> builder = MotorBuilder(motor_config)
        >>> motor = builder.build()
    """

    def __init__(self, config: MotorConfig):
        """Initialize MotorBuilder.

        Args:
            config: MotorConfig object with motor parameters.

        Raises:
            ImportError: If RocketPy is not installed.
        """
        if SolidMotor is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        self.config = config
        self.motor: Optional[SolidMotor] = None

    def build(self) -> SolidMotor:
        """Build and return SolidMotor instance.

        Returns:
            Configured RocketPy SolidMotor object.

        Raises:
            FileNotFoundError: If thrust curve file does not exist.
            ValueError: If motor type is not supported.

        Example:
            >>> builder = MotorBuilder(motor_config)
            >>> motor = builder.build()
            >>> print(f"Total impulse: {motor.total_impulse:.0f} N·s")
        """
        if self.config.type != "SolidMotor":
            raise ValueError(
                f"Motor type '{self.config.type}' not supported. "
                "Currently only 'SolidMotor' is implemented."
            )

        # Validate thrust source file exists
        thrust_file = Path(self.config.thrust_source)
        if self.config.thrust_source and not thrust_file.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            thrust_file = project_root / self.config.thrust_source
            if not thrust_file.exists():
                raise FileNotFoundError(
                    f"Thrust curve file not found: {self.config.thrust_source}"
                )

        logger.info(f"Building SolidMotor from thrust curve: {thrust_file}")

        # Create SolidMotor instance
        self.motor = SolidMotor(
            thrust_source=str(thrust_file),
            dry_mass=self.config.dry_mass_kg,
            dry_inertia=self.config.dry_inertia,
            nozzle_radius=self.config.nozzle_radius_m,
            grain_number=self.config.grain_number,
            grain_density=self.config.grain_density_kg_m3,
            grain_outer_radius=self.config.grain_outer_radius_m,
            grain_initial_inner_radius=self.config.grain_initial_inner_radius_m,
            grain_initial_height=self.config.grain_initial_height_m,
            grain_separation=self.config.grain_separation_m,
            grains_center_of_mass_position=self.config.grains_center_of_mass_position_m,
            center_of_dry_mass_position=self.config.center_of_dry_mass_position_m,
            nozzle_position=self.config.nozzle_position_m,
            burn_time=self.config.burn_time_s,
            throat_radius=self.config.throat_radius_m,
            interpolation_method=self.config.interpolation_method,
            coordinate_system_orientation=self.config.coordinate_system_orientation,
            reference_pressure=self.config.reference_pressure,
        )

        logger.info(
            f"Motor built successfully: "
            f"Total impulse={self.motor.total_impulse:.0f} N·s, "
            f"Burn time={self.motor.burn_out_time:.2f} s"
        )

        return self.motor

    def get_summary(self) -> dict:
        """Get summary of motor properties.

        Returns:
            Dictionary with motor properties.

        Raises:
            RuntimeError: If motor has not been built yet.

        Example:
            >>> summary = builder.get_summary()
            >>> print(f"Average thrust: {summary['average_thrust_n']:.0f} N")
        """
        if self.motor is None:
            raise RuntimeError("Motor not built yet. Call build() first.")

        return {
            "total_impulse_ns": float(self.motor.total_impulse),
            "average_thrust_n": float(
                self.motor.total_impulse / self.motor.burn_out_time
            ),
            "burn_time_s": float(self.motor.burn_out_time),
            "propellant_mass_kg": float(
                self.motor.propellant_initial_mass
            ),
            "total_mass_kg": float(
                self.motor.dry_mass + self.motor.propellant_initial_mass
            ),
            "max_thrust_n": float(self.motor.max_thrust),
            "max_thrust_time_s": float(self.motor.max_thrust_time),
        }

    @staticmethod
    def from_eng_file(
        eng_file_path: str,
        dry_mass_kg: float = 1.5,
        nozzle_radius_m: float = 0.033,
        throat_radius_m: float = 0.011,
    ) -> SolidMotor:
        """Create SolidMotor from .eng file with minimal parameters.

        This is a simplified factory method for quickly creating motors
        from .eng files without full MotorConfig specification.

        Args:
            eng_file_path: Path to .eng thrust curve file.
            dry_mass_kg: Motor dry mass in kg.
            nozzle_radius_m: Nozzle exit radius in meters.
            throat_radius_m: Nozzle throat radius in meters.

        Returns:
            Configured SolidMotor instance.

        Raises:
            FileNotFoundError: If .eng file does not exist.

        Example:
            >>> motor = MotorBuilder.from_eng_file(
            ...     "data/motors/Cesaroni_M1670.eng",
            ...     dry_mass_kg=1.815,
            ... )
        """
        if SolidMotor is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        eng_file = Path(eng_file_path)
        if not eng_file.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            eng_file = project_root / eng_file_path
            if not eng_file.exists():
                raise FileNotFoundError(f"Thrust curve file not found: {eng_file_path}")

        logger.info(f"Creating SolidMotor from .eng file: {eng_file}")

        # Create motor with minimal parameters
        # RocketPy will extract burn time and impulse from .eng file
        motor = SolidMotor(
            thrust_source=str(eng_file),
            dry_mass=dry_mass_kg,
            dry_inertia=(0.125, 0.125, 0.002),  # Default values
            nozzle_radius=nozzle_radius_m,
            grain_number=5,  # Default
            grain_density=1815.0,  # Typical APCP density
            grain_outer_radius=nozzle_radius_m,
            grain_initial_inner_radius=nozzle_radius_m * 0.5,
            grain_initial_height=0.120,  # Default
            grain_separation=0.005,
            grains_center_of_mass_position=-0.85,
            center_of_dry_mass_position=0.317,
            nozzle_position=0.0,
            burn_time=None,  # Will be computed from thrust curve
            throat_radius=throat_radius_m,
            coordinate_system_orientation="nozzle_to_combustion_chamber",
        )

        logger.info(
            f"Motor created: "
            f"Total impulse={motor.total_impulse:.0f} N·s, "
            f"Burn time={motor.burn_out_time:.2f} s"
        )

        return motor

    def validate_thrust_curve(self) -> bool:
        """Validate that thrust curve is physically reasonable.

        Returns:
            True if thrust curve is valid.

        Raises:
            RuntimeError: If motor has not been built yet.
            ValueError: If thrust curve is invalid.

        Example:
            >>> builder.build()
            >>> is_valid = builder.validate_thrust_curve()
        """
        if self.motor is None:
            raise RuntimeError("Motor not built yet. Call build() first.")

        # Check total impulse
        if self.motor.total_impulse <= 0:
            raise ValueError("Total impulse must be positive")

        # Check burn time
        if self.motor.burn_out_time <= 0:
            raise ValueError("Burn time must be positive")

        # Check that thrust is non-negative throughout burn
        # Sample thrust curve at multiple points
        import numpy as np

        time_samples = np.linspace(0, self.motor.burn_out_time, 100)
        thrust_samples = [self.motor.thrust.get_value(t) for t in time_samples]

        if any(thrust < 0 for thrust in thrust_samples):
            raise ValueError("Thrust curve contains negative values")

        # Check for reasonable thrust levels
        max_thrust = max(thrust_samples)
        if max_thrust > 50000:  # 50 kN is very high for hobby rocketry
            logger.warning(
                f"Max thrust ({max_thrust:.0f} N) is very high. "
                "Check if this is intentional."
            )

        logger.debug("Thrust curve validation passed")
        return True
