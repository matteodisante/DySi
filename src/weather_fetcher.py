"""Weather data fetcher for real-time atmospheric conditions.

This module provides classes and functions to fetch real-world weather data
from various sources for accurate rocket flight simulation:
- Wyoming atmospheric soundings (radiosonde data)
- GFS (Global Forecast System) forecasts
- ERA5 reanalysis (historical data)
- Custom atmospheric profiles

The fetched data integrates seamlessly with RocketPy's Environment class
for realistic atmospheric modeling.
"""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class WeatherConfig:
    """Weather data source configuration."""

    source: str = "standard_atmosphere"  # standard_atmosphere, wyoming, gfs, era5, custom
    wyoming_station: Optional[str] = None  # Station ID (e.g., "72340" for Oakland)
    custom_file: Optional[str] = None  # Path to custom atmospheric profile
    fetch_real_time: bool = False  # Fetch latest data vs. use specified date


class WeatherFetcher:
    """Fetch real-world weather data for flight simulations.

    This class provides methods to fetch atmospheric data from various sources
    and integrate with RocketPy's Environment class.

    Attributes:
        config: WeatherConfig with data source configuration

    Example:
        >>> config = WeatherConfig(
        ...     source="wyoming",
        ...     wyoming_station="72340",  # Oakland, CA
        ... )
        >>> fetcher = WeatherFetcher(config)
        >>> url = fetcher.fetch_wyoming_sounding(datetime(2024, 6, 15, 12))
        >>> env.set_atmospheric_model(type='wyoming_sounding', file=url)
    """

    def __init__(self, config: WeatherConfig):
        """Initialize WeatherFetcher.

        Args:
            config: WeatherConfig with data source parameters
        """
        self.config = config

    @staticmethod
    def fetch_wyoming_sounding(
        station: str,
        date: Optional[datetime] = None,
    ) -> str:
        """Fetch Wyoming atmospheric sounding URL.

        Wyoming soundings are radiosonde measurements providing direct
        atmospheric profile data (temperature, pressure, wind) with altitude.
        Data is available twice daily (00Z and 12Z UTC) from ~850 stations worldwide.

        Args:
            station: Station ID (e.g., "72340" for Oakland, CA)
            date: Date/time for sounding (default: latest)

        Returns:
            URL string to Wyoming sounding data (TEXT:LIST format)

        Example:
            >>> # Get sounding for Oakland on June 15, 2024 at 12Z
            >>> url = WeatherFetcher.fetch_wyoming_sounding(
            ...     station="72340",
            ...     date=datetime(2024, 6, 15, 12, tzinfo=timezone.utc)
            ... )
            >>> # Use with RocketPy
            >>> env.set_atmospheric_model(type='wyoming_sounding', file=url)

        Note:
            Soundings are launched at 00Z and 12Z UTC. The function automatically
            selects the closest sounding time to the provided date.
        """
        if date is None:
            date = datetime.now(timezone.utc)
        elif date.tzinfo is None:
            # Assume UTC if no timezone provided
            date = date.replace(tzinfo=timezone.utc)

        year = date.year
        month = date.month
        day = date.day

        # Select closest sounding time (00Z or 12Z)
        if date.hour < 6:
            hour = 0  # 00Z sounding
        elif date.hour < 18:
            hour = 12  # 12Z sounding
        else:
            # After 18Z, use next day's 00Z
            hour = 0
            date = date + timedelta(days=1)
            year, month, day = date.year, date.month, date.day

        # Construct Wyoming URL (TEXT:LIST format for RocketPy compatibility)
        url = (
            f"http://weather.uwyo.edu/cgi-bin/sounding?"
            f"region=naconf&TYPE=TEXT%3ALIST&YEAR={year}&MONTH={month:02d}&"
            f"FROM={day:02d}{hour:02d}&TO={day:02d}{hour:02d}&STNM={station}"
        )

        logger.info(
            f"Wyoming sounding: station={station}, "
            f"date={year}-{month:02d}-{day:02d} {hour:02d}Z"
        )
        logger.debug(f"URL: {url}")

        return url

    @staticmethod
    def get_gfs_forecast_params(
        latitude: float,
        longitude: float,
        date: datetime,
    ) -> Dict[str, Any]:
        """Get parameters for GFS forecast fetching.

        GFS (Global Forecast System) provides numerical weather predictions
        with global coverage and forecasts out to 16 days.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            date: Forecast date/time (UTC)

        Returns:
            Dictionary with GFS parameters for RocketPy

        Example:
            >>> params = WeatherFetcher.get_gfs_forecast_params(
            ...     latitude=39.39,
            ...     longitude=-8.29,
            ...     date=datetime(2024, 6, 15, 14, tzinfo=timezone.utc)
            ... )
            >>> # Use with RocketPy
            >>> env.set_atmospheric_model(type='Forecast', file='GFS')
            >>> env.set_date(params['date'])

        Note:
            RocketPy handles GFS fetching internally. This method provides
            configuration parameters for the Environment.set_atmospheric_model() call.
        """
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)

        # Check forecast horizon (GFS provides up to 16 days)
        time_delta = date - datetime.now(timezone.utc)
        if time_delta.days > 16:
            logger.warning(
                f"GFS forecast requested for {time_delta.days} days ahead. "
                f"GFS only provides forecasts up to 16 days."
            )

        logger.info(
            f"GFS forecast: lat={latitude:.2f}°, lon={longitude:.2f}°, "
            f"date={date.strftime('%Y-%m-%d %H:%M UTC')}"
        )

        return {
            'type': 'Forecast',
            'file': 'GFS',
            'latitude': latitude,
            'longitude': longitude,
            'date': (date.year, date.month, date.day, date.hour),
        }

    @staticmethod
    def get_era5_reanalysis_params(
        latitude: float,
        longitude: float,
        date: datetime,
    ) -> Dict[str, Any]:
        """Get parameters for ERA5 reanalysis data.

        ERA5 provides historical weather reanalysis from 1979 to present
        with hourly resolution and 31 km spatial resolution.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            date: Historical date/time (UTC)

        Returns:
            Dictionary with ERA5 parameters for RocketPy

        Example:
            >>> # Get reanalysis for past flight reconstruction
            >>> params = WeatherFetcher.get_era5_reanalysis_params(
            ...     latitude=39.39,
            ...     longitude=-8.29,
            ...     date=datetime(2024, 5, 1, 14, tzinfo=timezone.utc)
            ... )
            >>> env.set_atmospheric_model(type='Reanalysis', file='ERA5')
            >>> env.set_date(params['date'])

        Note:
            ERA5 data has a ~3 month delay. Use for historical analysis,
            not real-time forecasting.
        """
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)

        # Check if date is too recent (ERA5 has ~3 month delay)
        time_since = datetime.now(timezone.utc) - date
        if time_since.days < 90:
            logger.warning(
                f"ERA5 reanalysis requested for {time_since.days} days ago. "
                f"ERA5 typically has a 3-month delay. Data may not be available yet."
            )

        logger.info(
            f"ERA5 reanalysis: lat={latitude:.2f}°, lon={longitude:.2f}°, "
            f"date={date.strftime('%Y-%m-%d %H:%M UTC')}"
        )

        return {
            'type': 'Reanalysis',
            'file': 'ERA5',
            'latitude': latitude,
            'longitude': longitude,
            'date': (date.year, date.month, date.day, date.hour),
        }

    @staticmethod
    def load_custom_atmospheric_profile(file_path: str) -> Path:
        """Load custom atmospheric profile from file.

        Custom profiles allow testing with specific atmospheric conditions
        or using data from other sources.

        Args:
            file_path: Path to atmospheric profile file

        Returns:
            Resolved Path object to the file

        Raises:
            FileNotFoundError: If file does not exist

        File Format:
            Text file with columns: altitude (m), temperature (K), pressure (Pa)
            Example:
                0, 288.15, 101325
                1000, 281.65, 89874
                2000, 275.15, 79495
                ...

        Example:
            >>> file = WeatherFetcher.load_custom_atmospheric_profile(
            ...     "data/atmospheric/custom_profile.txt"
            ... )
            >>> env.set_atmospheric_model(type='custom_atmosphere', file=str(file))
        """
        path = Path(file_path)

        if not path.exists():
            # Try relative to project root
            project_root = Path(__file__).parent.parent
            path = project_root / file_path
            if not path.exists():
                raise FileNotFoundError(
                    f"Atmospheric profile file not found: {file_path}"
                )

        logger.info(f"Loading custom atmospheric profile: {path}")

        return path


# Common Wyoming station codes for reference
WYOMING_STATIONS = {
    # United States
    "72340": "Oakland, CA",
    "23048": "Las Cruces, NM",
    "72469": "Denver, CO",
    "74794": "White Sands, NM",
    "72206": "Cape Canaveral, FL",
    "72403": "Vandenberg AFB, CA",
    "72393": "Point Mugu, CA",

    # International
    "08495": "Lisbon, Portugal",
    "10739": "Stuttgart, Germany",
    "11520": "Prague, Czech Republic",
    "16245": "Rome, Italy",
    "03005": "Lerwick, UK",
    "06610": "Valentia, Ireland",
}


def get_station_name(station_id: str) -> str:
    """Get station name from ID.

    Args:
        station_id: Wyoming station ID

    Returns:
        Station name if known, else "Unknown Station"

    Example:
        >>> name = get_station_name("72340")
        >>> print(name)  # "Oakland, CA"
    """
    return WYOMING_STATIONS.get(station_id, "Unknown Station")


def list_wyoming_stations() -> None:
    """Print list of common Wyoming station IDs and names.

    Example:
        >>> list_wyoming_stations()
        Wyoming Atmospheric Sounding Stations:
        72340: Oakland, CA
        23048: Las Cruces, NM
        ...
    """
    print("Wyoming Atmospheric Sounding Stations:")
    for station_id, name in sorted(WYOMING_STATIONS.items()):
        print(f"  {station_id}: {name}")


# Convenience functions for common use cases

def fetch_latest_wyoming_sounding(station: str) -> str:
    """Fetch latest available Wyoming sounding for a station.

    Args:
        station: Station ID (e.g., "72340")

    Returns:
        URL to latest sounding data

    Example:
        >>> url = fetch_latest_wyoming_sounding("72340")
        >>> env.set_atmospheric_model(type='wyoming_sounding', file=url)
    """
    # Get latest sounding (current time, will select closest 00Z or 12Z)
    return WeatherFetcher.fetch_wyoming_sounding(station, datetime.now(timezone.utc))


def fetch_gfs_forecast_for_location(
    latitude: float,
    longitude: float,
    forecast_hours_ahead: int = 24
) -> Dict[str, Any]:
    """Fetch GFS forecast for location N hours ahead.

    Args:
        latitude: Latitude in degrees
        longitude: Longitude in degrees
        forecast_hours_ahead: Hours ahead to forecast (default: 24)

    Returns:
        Dictionary with GFS parameters

    Example:
        >>> # Get forecast for 24 hours from now
        >>> params = fetch_gfs_forecast_for_location(39.39, -8.29, forecast_hours_ahead=24)
        >>> env.set_atmospheric_model(type='Forecast', file='GFS')
        >>> env.set_date(params['date'])
    """
    forecast_date = datetime.now(timezone.utc) + timedelta(hours=forecast_hours_ahead)
    return WeatherFetcher.get_gfs_forecast_params(latitude, longitude, forecast_date)
