"""Rocket builder for creating RocketPy rocket instances from configuration.

This module provides the RocketBuilder class for constructing RocketPy Rocket
objects from configuration dataclasses with progressive component addition.
"""

from pathlib import Path
from typing import Optional
import logging

try:
    from rocketpy import Rocket, SolidMotor
except ImportError:
    Rocket = None
    SolidMotor = None

from src.config_loader import RocketConfig
from src.motor_builder import MotorBuilder

logger = logging.getLogger(__name__)


class RocketBuilder:
    """Builder for RocketPy Rocket instances.

    This class constructs RocketPy Rocket objects from RocketConfig
    dataclasses, handling progressive component addition with method chaining.

    Attributes:
        config: RocketConfig object with rocket parameters.
        motor: Optional SolidMotor instance to be added.
        rocket: Constructed Rocket instance (after build()).

    Example:
        >>> rocket_config = RocketConfig(name="Calisto", ...)
        >>> motor = motor_builder.build()
        >>> builder = RocketBuilder(rocket_config, motor)
        >>> rocket = builder.build()
    """

    def __init__(
        self,
        config: RocketConfig,
        motor: Optional[SolidMotor] = None,
    ):
        """Initialize RocketBuilder.

        Args:
            config: RocketConfig object with rocket parameters.
            motor: Optional SolidMotor instance. If provided, will be added
                   during build().

        Raises:
            ImportError: If RocketPy is not installed.
        """
        if Rocket is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        self.config = config
        self.motor = motor
        self.rocket: Optional[Rocket] = None

    def build(self) -> Rocket:
        """Build and return Rocket instance with all components.

        This method creates the base rocket and progressively adds:
        1. Motor (if provided)
        2. Nose cone (if configured)
        3. Fins (if configured)
        4. Parachute (if configured)
        5. Air brakes (if configured)

        Returns:
            Configured RocketPy Rocket object.

        Raises:
            FileNotFoundError: If drag curve files do not exist.

        Example:
            >>> builder = RocketBuilder(rocket_config, motor)
            >>> rocket = builder.build()
            >>> print(f"Static margin: {rocket.static_margin(0):.2f} calibers")
        """
        logger.info(f"Building Rocket: {self.config.name}")

        # Create base rocket
        self._create_base_rocket()

        # Add motor if provided
        if self.motor is not None:
            self.add_motor(self.motor)

        # Add nose cone if configured
        if self.config.nose_cone is not None:
            self.add_nose_cone()

        # Add fins if configured
        if self.config.fins is not None:
            self.add_fins()

        # Add parachute if configured
        if self.config.parachute is not None and self.config.parachute.enabled:
            self.add_parachute()

        # Add air brakes if configured
        if self.config.air_brakes is not None and self.config.air_brakes.enabled:
            self.add_air_brakes()

        logger.info(
            f"Rocket '{self.config.name}' built successfully "
            f"(mass={self.rocket.mass:.2f} kg)"
        )

        return self.rocket

    def _create_base_rocket(self) -> None:
        """Create base Rocket instance without components."""
        # Handle drag curves
        power_off_drag = self._resolve_drag_curve(self.config.power_off_drag)
        power_on_drag = self._resolve_drag_curve(self.config.power_on_drag)

        # RocketPy requires drag curves or will use default values
        # If not provided, use a typical value for rockets (Cd ~ 0.5)
        if power_off_drag is None:
            power_off_drag = 0.5  # Typical drag coefficient
        if power_on_drag is None:
            power_on_drag = 0.5  # Typical drag coefficient

        logger.debug(
            f"Creating base rocket: radius={self.config.radius_m}m, "
            f"mass={self.config.dry_mass_kg}kg"
        )

        self.rocket = Rocket(
            radius=self.config.radius_m,
            mass=self.config.dry_mass_kg,
            inertia=self.config.inertia.to_tuple(),
            power_off_drag=power_off_drag,
            power_on_drag=power_on_drag,
            center_of_mass_without_motor=self.config.cg_location_m,
            coordinate_system_orientation=self.config.coordinate_system,
        )

        logger.debug("Base rocket created")

    def _resolve_drag_curve(self, drag_curve: Optional[str]) -> Optional[str]:
        """Resolve drag curve file path.

        Args:
            drag_curve: Path to drag curve file or None.

        Returns:
            Resolved absolute path or None.

        Raises:
            FileNotFoundError: If file is specified but does not exist.
        """
        if drag_curve is None:
            return None

        drag_file = Path(drag_curve)
        if not drag_file.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            drag_file = project_root / drag_curve
            if not drag_file.exists():
                raise FileNotFoundError(f"Drag curve file not found: {drag_curve}")

        return str(drag_file)

    def add_motor(self, motor: SolidMotor, position_m: Optional[float] = None) -> "RocketBuilder":
        """Add motor to rocket.

        Args:
            motor: SolidMotor instance.
            position_m: Motor position along rocket axis. If None, uses
                       config.motor.position_m if available.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If rocket has not been created yet.

        Example:
            >>> builder.build().add_motor(motor, position_m=-1.373)
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not created yet. Call build() first.")

        # Use position from config if not provided
        if position_m is None:
            # Position should be provided in motor config
            logger.warning("Motor position not specified, using default -1.373 m")
            position_m = -1.373

        self.rocket.add_motor(motor, position=position_m)
        logger.debug(f"Motor added at position {position_m} m")

        return self

    def add_nose_cone(self) -> "RocketBuilder":
        """Add nose cone to rocket based on configuration.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If rocket has not been created yet.
            ValueError: If nose cone configuration is missing.

        Example:
            >>> builder.build().add_nose_cone()
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not created yet. Call build() first.")

        if self.config.nose_cone is None:
            raise ValueError("Nose cone configuration is missing")

        nose = self.config.nose_cone

        self.rocket.add_nose(
            length=nose.length_m,
            kind=nose.kind,
            position=nose.position_m,
        )

        logger.debug(
            f"Nose cone added: kind={nose.kind}, length={nose.length_m}m, "
            f"position={nose.position_m}m"
        )

        return self

    def add_fins(self) -> "RocketBuilder":
        """Add fin set to rocket based on configuration.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If rocket has not been created yet.
            ValueError: If fin configuration is missing.

        Example:
            >>> builder.build().add_fins()
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not created yet. Call build() first.")

        if self.config.fins is None:
            raise ValueError("Fin configuration is missing")

        fins = self.config.fins

        # Prepare airfoil parameter
        airfoil = None
        if fins.airfoil:
            airfoil_file = Path(fins.airfoil)
            if not airfoil_file.exists():
                project_root = Path(__file__).parent.parent
                airfoil_file = project_root / fins.airfoil
                if not airfoil_file.exists():
                    logger.warning(f"Airfoil file not found: {fins.airfoil}")
                    airfoil = None
                else:
                    airfoil = (str(airfoil_file), "m")
            else:
                airfoil = (str(airfoil_file), "m")

        self.rocket.add_trapezoidal_fins(
            n=fins.count,
            root_chord=fins.root_chord_m,
            tip_chord=fins.tip_chord_m,
            span=fins.span_m,
            position=fins.position_m,
            cant_angle=fins.cant_angle_deg,
            airfoil=airfoil,
        )

        logger.debug(
            f"Fins added: count={fins.count}, root={fins.root_chord_m}m, "
            f"tip={fins.tip_chord_m}m, span={fins.span_m}m, position={fins.position_m}m"
        )

        return self

    def add_parachute(self) -> "RocketBuilder":
        """Add parachute to rocket based on configuration.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If rocket has not been created yet.
            ValueError: If parachute configuration is missing.

        Example:
            >>> builder.build().add_parachute()
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not created yet. Call build() first.")

        if self.config.parachute is None:
            raise ValueError("Parachute configuration is missing")

        para = self.config.parachute

        self.rocket.add_parachute(
            name=para.name,
            cd_s=para.cd_s,
            trigger=para.trigger,
            sampling_rate=para.sampling_rate_hz,
            lag=para.lag_s,
            noise=para.noise_std,
        )

        logger.debug(
            f"Parachute added: name={para.name}, cd_s={para.cd_s}, "
            f"trigger={para.trigger}"
        )

        return self

    def add_air_brakes(self) -> "RocketBuilder":
        """Add air brakes to rocket based on configuration.

        Air brakes provide active drag control for apogee targeting in competitions.
        This method adds aerodynamic brakes that can be deployed during flight.

        Returns:
            Self for method chaining.

        Raises:
            RuntimeError: If rocket has not been created yet.
            ValueError: If air brakes configuration is missing.

        Example:
            >>> builder.build().add_air_brakes()

        Note:
            RocketPy's air brakes implementation may vary by version.
            This method uses the add_air_brakes() API if available,
            or adds as a generic surface with appropriate drag characteristics.
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not created yet. Call build() first.")

        if self.config.air_brakes is None:
            raise ValueError("Air brakes configuration is missing")

        ab = self.config.air_brakes

        # Calculate cd_s if not overridden
        cd_s = ab.override_cd_s if ab.override_cd_s is not None else (
            ab.drag_coefficient * ab.reference_area_m2 * ab.deployment_level
        )

        # Try to use RocketPy's native air brakes if available
        if hasattr(self.rocket, 'add_air_brakes'):
            self.rocket.add_air_brakes(
                drag_coefficient=ab.drag_coefficient,
                reference_area=ab.reference_area_m2,
                position=ab.position_m,
                deployment_level=ab.deployment_level,
            )
            logger.debug(
                f"Air brakes added (native): cd={ab.drag_coefficient}, "
                f"area={ab.reference_area_m2}m², position={ab.position_m}m, "
                f"deployment={ab.deployment_level}"
            )
        else:
            # Fallback: Add as generic surface with drag
            # Note: This is a simplified implementation
            # For full active control, use RocketPy's AirBrakes class directly
            logger.warning(
                "RocketPy air brakes not available. "
                "Air brakes added as static drag component. "
                "Consider upgrading RocketPy for full active control support."
            )

            # Add air brakes effect as additional drag
            # This modifies the rocket's drag coefficient
            if hasattr(self.rocket, 'add_generic_surface'):
                self.rocket.add_generic_surface(
                    name="AirBrakes",
                    cd=ab.drag_coefficient,
                    reference_area=ab.reference_area_m2,
                    position=ab.position_m,
                )
                logger.debug(
                    f"Air brakes added (generic surface): cd={ab.drag_coefficient}, "
                    f"area={ab.reference_area_m2}m², cd_s={cd_s}"
                )
            else:
                logger.warning(
                    "Could not add air brakes: RocketPy version does not support "
                    "add_air_brakes() or add_generic_surface() methods."
                )

        return self

    def get_stability_info(self) -> dict:
        """Get stability information for the rocket.

        Returns:
            Dictionary with stability metrics.

        Raises:
            RuntimeError: If rocket has not been built yet.

        Example:
            >>> info = builder.get_stability_info()
            >>> print(f"Static margin: {info['static_margin_calibers']:.2f}")
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not built yet. Call build() first.")

        # Get static margin at t=0 (before motor burn)
        static_margin_t0 = self.rocket.static_margin(0)

        # Get center of pressure (cp_position is a Function in RocketPy)
        cp_position = None
        if hasattr(self.rocket, 'cp_position'):
            try:
                # Try to evaluate it at Mach 0.3 (typical subsonic value)
                cp_position = float(self.rocket.cp_position(0.3))
            except (TypeError, AttributeError):
                cp_position = None

        return {
            "static_margin_calibers": float(static_margin_t0),
            "total_mass_kg": float(self.rocket.total_mass(0)),
            "dry_mass_kg": float(self.rocket.dry_mass),
            "center_of_mass_m": float(self.rocket.center_of_mass(0)),
            "center_of_pressure_m": cp_position,
            "coordinate_system": self.config.coordinate_system,
        }

    def get_summary(self) -> dict:
        """Get comprehensive summary of rocket configuration.

        Returns:
            Dictionary with rocket properties.

        Raises:
            RuntimeError: If rocket has not been built yet.

        Example:
            >>> summary = builder.get_summary()
            >>> print(f"Rocket: {summary['name']}")
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not built yet. Call build() first.")

        stability = self.get_stability_info()

        return {
            "name": self.config.name,
            "radius_m": self.config.radius_m,
            "length_m": self.config.geometry.length_m,
            "dry_mass_kg": stability["dry_mass_kg"],
            "total_mass_kg": stability["total_mass_kg"],
            "static_margin_calibers": stability["static_margin_calibers"],
            "has_motor": self.motor is not None,
            "has_nose_cone": self.config.nose_cone is not None,
            "has_fins": self.config.fins is not None,
            "fin_count": self.config.fins.count if self.config.fins else 0,
            "has_parachute": (
                self.config.parachute is not None and self.config.parachute.enabled
            ),
            "has_air_brakes": (
                self.config.air_brakes is not None and self.config.air_brakes.enabled
            ),
        }

    def validate_stability(self, min_margin_calibers: float = 1.0) -> bool:
        """Validate rocket stability.

        Args:
            min_margin_calibers: Minimum acceptable static margin in calibers.

        Returns:
            True if stable, False otherwise.

        Raises:
            RuntimeError: If rocket has not been built yet.

        Example:
            >>> is_stable = builder.validate_stability(min_margin_calibers=1.5)
        """
        if self.rocket is None:
            raise RuntimeError("Rocket not built yet. Call build() first.")

        stability_info = self.get_stability_info()
        static_margin = stability_info["static_margin_calibers"]

        if static_margin < min_margin_calibers:
            logger.warning(
                f"Rocket stability marginal: static margin = {static_margin:.2f} "
                f"calibers (minimum = {min_margin_calibers:.2f})"
            )
            return False

        logger.info(
            f"Rocket is stable: static margin = {static_margin:.2f} calibers"
        )
        return True
