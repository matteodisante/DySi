"""Environment builder for creating RocketPy environment instances.

This module provides the EnvironmentBuilder class for constructing RocketPy
Environment objects from configuration dataclasses.
"""

from pathlib import Path
from typing import Optional
import logging
import numpy as np

try:
    from rocketpy import Environment
except ImportError:
    Environment = None

from src.config_loader import EnvironmentConfig
from src.weather_fetcher import WeatherFetcher

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
        # Check if new weather configuration is used
        if hasattr(self.config, 'weather') and self.config.weather.source != "standard_atmosphere":
            self._setup_weather_model()
            return

        # Fall back to old atmospheric_model field for backward compatibility
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

        else:
            raise ValueError(
                f"Unsupported atmospheric model: '{self.config.atmospheric_model}'. "
                "Use weather.source for advanced models (wyoming, gfs, era5)"
            )

    def _setup_weather_model(self) -> None:
        """Setup weather model using WeatherFetcher integration.

        Supports Wyoming soundings, GFS forecasts, ERA5 reanalysis, and custom profiles.
        Wind is included automatically in weather data sources.
        """
        weather_config = self.config.weather
        source = weather_config.source.lower()

        logger.info(f"Setting up weather from source: {source}")

        if source == "wyoming":
            # Wyoming sounding
            if not weather_config.wyoming_station:
                raise ValueError("Wyoming source requires wyoming_station ID")

            date = None
            if self.config.date:
                from datetime import datetime, timezone
                date = datetime(*self.config.date, tzinfo=timezone.utc)

            url = WeatherFetcher.fetch_wyoming_sounding(
                station=weather_config.wyoming_station,
                date=date,
            )

            self.environment.set_atmospheric_model(
                type='wyoming_sounding',
                file=url
            )
            logger.info(f"Using Wyoming sounding from station {weather_config.wyoming_station}")

        elif source == "gfs":
            # GFS forecast
            if not self.config.date:
                raise ValueError("GFS forecast requires date to be set")

            from datetime import datetime, timezone
            forecast_date = datetime(*self.config.date, tzinfo=timezone.utc)

            self.environment.set_atmospheric_model(type='Forecast', file='GFS')
            logger.info(f"Using GFS forecast for {forecast_date}")

        elif source == "era5":
            # ERA5 reanalysis
            if not self.config.date:
                raise ValueError("ERA5 reanalysis requires date to be set")

            from datetime import datetime, timezone
            reanalysis_date = datetime(*self.config.date, tzinfo=timezone.utc)

            self.environment.set_atmospheric_model(type='Reanalysis', file='ERA5')
            logger.info(f"Using ERA5 reanalysis for {reanalysis_date}")

        elif source == "custom":
            # Custom atmospheric profile
            if not weather_config.custom_file:
                raise ValueError("Custom weather source requires custom_file path")

            file_path = WeatherFetcher.load_custom_atmospheric_profile(
                weather_config.custom_file
            )

            self.environment.set_atmospheric_model(
                type='custom_atmosphere',
                file=str(file_path)
            )
            logger.info(f"Using custom atmospheric profile: {file_path}")

        else:
            raise ValueError(
                f"Unsupported weather source: '{source}'. "
                "Supported: wyoming, gfs, era5, custom, standard_atmosphere"
            )

    def _setup_wind_model(self) -> None:
        """Setup wind model based on configuration.

        The wind model can be:
        - constant: Constant wind velocity and direction
        - from_weather: Wind profile from weather data (Wyoming, GFS, ERA5)
        - function: Custom wind function (not yet implemented)
        - custom: Custom wind data (not yet implemented)

        NOTE: Wind must be set when calling set_atmospheric_model() with wind_u and wind_v.
        This method should be called AFTER _setup_atmospheric_model() and will update
        the atmospheric model with wind if needed.
        """
        wind_model = self.config.wind.model.lower()

        if wind_model == "constant":
            # Constant wind throughout altitude
            wind_velocity = self.config.wind.velocity_ms
            wind_direction = self.config.wind.direction_deg

            logger.debug(
                f"Setting constant wind: {wind_velocity} m/s from {wind_direction}°"
            )

            if wind_velocity == 0:
                # No wind - already set by atmospheric model
                logger.debug("No wind (velocity = 0)")
            else:
                # Convert meteorological direction to wind components
                #
                # METEOROLOGICAL CONVENTION (used by RocketPy):
                # Wind direction = where wind comes FROM (0° = North, 90° = East, ...)
                #
                # Examples:
                #   - Wind from North (0°):   blows South  → u=0,  v=-V
                #   - Wind from East (90°):   blows West   → u=-V, v=0
                #   - Wind from South (180°): blows North  → u=0,  v=+V
                #   - Wind from West (270°):  blows East   → u=+V, v=0
                #
                # Formula: u = -V*sin(θ), v = -V*cos(θ)
                # Negative sign because wind COMES FROM direction (not GOES TO)

                direction_rad = np.deg2rad(wind_direction)

                # Calculate wind components (RocketPy convention)
                wind_u = -wind_velocity * np.sin(direction_rad)  # East component (m/s)
                wind_v = -wind_velocity * np.cos(direction_rad)  # North component (m/s)

                # Get current atmospheric model settings
                atm_type = self.environment.atmospheric_model_type
                atm_file = self.environment.atmospheric_model_file

                # Re-apply atmospheric model with wind
                self.environment.set_atmospheric_model(
                    type=atm_type,
                    file=atm_file if atm_file else None,
                    wind_u=lambda h: wind_u,  # Constant with altitude
                    wind_v=lambda h: wind_v,  # Constant with altitude
                )

                logger.info(
                    f"Constant wind set: {wind_velocity:.1f} m/s from {wind_direction}° "
                    f"(u={wind_u:.1f}, v={wind_v:.1f} m/s)"
                )

        elif wind_model == "from_weather":
            # Wind profile comes from weather data source
            # Wyoming, GFS, and ERA5 include wind profiles automatically
            logger.info("Using wind profile from weather data source")
            # Wind is already set by _setup_weather_model() for these sources

        elif wind_model in ["function", "custom"]:
            logger.warning(
                f"Wind model '{wind_model}' not fully implemented. "
                "Using no wind for now."
            )

        else:
            raise ValueError(
                f"Unsupported wind model: '{wind_model}'. "
                "Supported: constant, from_weather, function, custom"
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
