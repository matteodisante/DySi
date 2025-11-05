"""Environment builder for creating RocketPy environment instances.

This module provides the EnvironmentBuilder class for constructing RocketPy
Environment objects from configuration dataclasses.
"""

from pathlib import Path
from typing import Optional
import logging

try:
    from rocketpy import Environment
except ImportError:
    Environment = None

from src.config_loader import EnvironmentConfig

logger = logging.getLogger(__name__)


class EnvironmentBuilder:
    """Builder for RocketPy Environment instances.

    This class constructs RocketPy Environment objects from EnvironmentConfig
    dataclasses, handling atmospheric models, wind setup, and date/time
    configuration.

    Attributes:
        config: EnvironmentConfig object with environment parameters.
        environment: Constructed Environment instance (after build()).

    Example:
        >>> env_config = EnvironmentConfig(
        ...     latitude_deg=39.3897,
        ...     longitude_deg=-8.2889,
        ...     elevation_m=100.0,
        ... )
        >>> builder = EnvironmentBuilder(env_config)
        >>> env = builder.build()
    """

    def __init__(self, config: EnvironmentConfig):
        """Initialize EnvironmentBuilder.

        Args:
            config: EnvironmentConfig object with environment parameters.

        Raises:
            ImportError: If RocketPy is not installed.
        """
        if Environment is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        self.config = config
        self.environment: Optional[Environment] = None

    def build(self) -> Environment:
        """Build and return Environment instance.

        Returns:
            Configured RocketPy Environment object.

        Raises:
            FileNotFoundError: If atmospheric model file does not exist.
            ValueError: If configuration is invalid.

        Example:
            >>> builder = EnvironmentBuilder(env_config)
            >>> env = builder.build()
            >>> print(f"Elevation: {env.elevation} m")
        """
        logger.info(
            f"Building Environment at ({self.config.latitude_deg}°, "
            f"{self.config.longitude_deg}°), elevation={self.config.elevation_m}m"
        )

        # Create base Environment instance
        self.environment = Environment(
            latitude=self.config.latitude_deg,
            longitude=self.config.longitude_deg,
            elevation=self.config.elevation_m,
        )

        # Note: Gravity is typically handled by RocketPy internally
        # Custom gravity can be set via environment attributes if needed
        logger.debug(f"Using gravity: {self.config.gravity_ms2} m/s²")

        # Set date if provided
        if self.config.date is not None:
            self.environment.set_date(self.config.date)
            logger.debug(f"Date set to {self.config.date}")

        # Set atmospheric model
        self._setup_atmospheric_model()

        # Set wind model
        self._setup_wind_model()

        # Set max expected height for atmospheric data range
        self.environment.max_expected_height = self.config.max_expected_height_m
        logger.debug(
            f"Max expected height set to {self.config.max_expected_height_m} m"
        )

        logger.info("Environment built successfully")
        return self.environment

    def _setup_atmospheric_model(self) -> None:
        """Setup atmospheric model based on configuration.

        Raises:
            FileNotFoundError: If custom atmosphere file does not exist.
            ValueError: If atmospheric model type is not supported.
        """
        model = self.config.atmospheric_model.lower()

        if model == "standard_atmosphere":
            self.environment.set_atmospheric_model(type="standard_atmosphere")
            logger.debug("Using standard atmosphere model (ISA)")

        elif model == "custom_atmosphere":
            if not self.config.atmospheric_model_file:
                raise ValueError(
                    "Custom atmosphere model requires atmospheric_model_file"
                )

            atm_file = Path(self.config.atmospheric_model_file)
            if not atm_file.exists():
                # Try relative to project root
                project_root = Path(__file__).parent.parent
                atm_file = project_root / self.config.atmospheric_model_file
                if not atm_file.exists():
                    raise FileNotFoundError(
                        f"Atmospheric model file not found: "
                        f"{self.config.atmospheric_model_file}"
                    )

            self.environment.set_atmospheric_model(
                type="custom_atmosphere",
                file=str(atm_file),
            )
            logger.debug(f"Using custom atmosphere from {atm_file}")

        elif model in ["forecast", "reanalysis", "ensemble"]:
            # These require additional configuration (GFS, ERA5, etc.)
            logger.warning(
                f"Atmospheric model '{model}' requires additional configuration. "
                "Falling back to standard atmosphere."
            )
            self.environment.set_atmospheric_model(type="standard_atmosphere")

        else:
            raise ValueError(
                f"Unsupported atmospheric model: '{self.config.atmospheric_model}'. "
                "Supported: standard_atmosphere, custom_atmosphere"
            )

    def _setup_wind_model(self) -> None:
        """Setup wind model based on configuration.

        The wind model can be:
        - constant: Constant wind velocity and direction
        - function: Custom wind function (not yet implemented)
        - custom: Custom wind data (not yet implemented)
        """
        wind_model = self.config.wind.model.lower()

        if wind_model == "constant":
            # Constant wind throughout altitude
            wind_velocity = self.config.wind.velocity_ms
            wind_direction = self.config.wind.direction_deg

            # RocketPy uses wind heading in degrees
            # Wind direction in meteorological convention: where wind comes FROM
            # Convert to heading: where wind is going TO
            wind_heading = (wind_direction + 180) % 360

            logger.debug(
                f"Setting constant wind: {wind_velocity} m/s from {wind_direction}° "
                f"(heading {wind_heading}°)"
            )

            # Set constant wind velocity
            # RocketPy Environment.set_atmospheric_model handles wind internally
            # For constant wind, we can use the basic approach:
            if wind_velocity == 0:
                # No wind - set wind velocity to zero function
                self.environment.set_atmospheric_model(type="standard_atmosphere")
                logger.debug("No wind (velocity = 0)")
            else:
                # For simplicity with constant wind, we set it after atmospheric model
                # The wind will be applied uniformly
                # Note: This is a simplified implementation
                # Full implementation would require wind velocity functions
                logger.info(
                    f"Constant wind: {wind_velocity:.1f} m/s from {wind_direction}°"
                )
                # Store wind info for later use in flight setup
                self.environment._wind_velocity_ms = wind_velocity
                self.environment._wind_direction_deg = wind_direction

        elif wind_model in ["function", "custom"]:
            logger.warning(
                f"Wind model '{wind_model}' not fully implemented. "
                "Using no wind for now."
            )

        else:
            raise ValueError(
                f"Unsupported wind model: '{wind_model}'. "
                "Supported: constant, function, custom"
            )

    def get_atmospheric_conditions(self, altitude_m: float = 0.0) -> dict:
        """Get atmospheric conditions at specified altitude.

        Args:
            altitude_m: Altitude in meters ASL.

        Returns:
            Dictionary with atmospheric properties.

        Raises:
            RuntimeError: If environment has not been built yet.

        Example:
            >>> builder.build()
            >>> conditions = builder.get_atmospheric_conditions(1000.0)
            >>> print(f"Temperature: {conditions['temperature_k']:.1f} K")
        """
        if self.environment is None:
            raise RuntimeError("Environment not built yet. Call build() first.")

        return {
            "altitude_m": altitude_m,
            "pressure_pa": float(self.environment.pressure(altitude_m)),
            "temperature_k": float(self.environment.temperature(altitude_m)),
            "density_kg_m3": float(self.environment.density(altitude_m)),
            "speed_of_sound_ms": float(self.environment.speed_of_sound(altitude_m)),
            "gravity_ms2": float(self.environment.gravity(altitude_m)),
        }

    def get_summary(self) -> dict:
        """Get summary of environment configuration.

        Returns:
            Dictionary with environment properties.

        Raises:
            RuntimeError: If environment has not been built yet.

        Example:
            >>> summary = builder.get_summary()
            >>> print(f"Location: {summary['location']}")
        """
        if self.environment is None:
            raise RuntimeError("Environment not built yet. Call build() first.")

        # Get sea level conditions
        sea_level = self.get_atmospheric_conditions(0.0)

        # Get conditions at elevation
        at_elevation = self.get_atmospheric_conditions(self.config.elevation_m)

        return {
            "location": f"({self.config.latitude_deg}°, {self.config.longitude_deg}°)",
            "elevation_m": self.config.elevation_m,
            "atmospheric_model": self.config.atmospheric_model,
            "wind_velocity_ms": self.config.wind.velocity_ms,
            "wind_direction_deg": self.config.wind.direction_deg,
            "gravity_ms2": self.config.gravity_ms2,
            "sea_level_pressure_pa": sea_level["pressure_pa"],
            "sea_level_temperature_k": sea_level["temperature_k"],
            "sea_level_density_kg_m3": sea_level["density_kg_m3"],
            "elevation_pressure_pa": at_elevation["pressure_pa"],
            "elevation_temperature_k": at_elevation["temperature_k"],
            "elevation_density_kg_m3": at_elevation["density_kg_m3"],
        }

    @staticmethod
    def from_location(
        latitude_deg: float,
        longitude_deg: float,
        elevation_m: float = 0.0,
    ) -> Environment:
        """Create Environment from minimal location parameters.

        This is a simplified factory method for quickly creating environments
        with default atmospheric model and no wind.

        Args:
            latitude_deg: Latitude in degrees.
            longitude_deg: Longitude in degrees.
            elevation_m: Elevation above sea level in meters.

        Returns:
            Configured Environment instance.

        Example:
            >>> env = EnvironmentBuilder.from_location(
            ...     latitude_deg=39.3897,
            ...     longitude_deg=-8.2889,
            ...     elevation_m=100.0,
            ... )
        """
        if Environment is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        logger.info(
            f"Creating Environment at ({latitude_deg}°, {longitude_deg}°), "
            f"elevation={elevation_m}m"
        )

        env = Environment(
            latitude=latitude_deg,
            longitude=longitude_deg,
            elevation=elevation_m,
        )

        # Set standard atmosphere
        env.set_atmospheric_model(type="standard_atmosphere")

        logger.info("Environment created with standard atmosphere, no wind")

        return env
