# Weather Integration Guide

Comprehensive guide for integrating real-world weather data into the Rocket Simulation Framework.

## Table of Contents

1. [Overview](#overview)
2. [Weather Data Sources](#weather-data-sources)
3. [RocketPy Weather Capabilities](#rocketpy-weather-capabilities)
4. [Implementation Guide](#implementation-guide)
5. [Configuration Reference](#configuration-reference)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [References](#references)

---

## Overview

### Why Real Weather Data?

Using real atmospheric conditions dramatically improves simulation accuracy:

| Aspect | Standard Atmosphere | Real Weather Data | Improvement |
|--------|-------------------|------------------|-------------|
| Temperature Profile | Fixed (ISA) | Actual soundings | ±10-20% density accuracy |
| Pressure Profile | Exponential model | Measured data | ±5-15% drag accuracy |
| Wind Profile | Constant or simple | Altitude-dependent | ±50-200m apogee accuracy |
| Launch Decision | Assumptions | Real-time forecasts | Go/No-go confidence |

### Use Cases

1. **Flight Predictions**: Accurate apogee and landing point forecasts
2. **Launch Windows**: Identify optimal launch conditions
3. **Risk Assessment**: Quantify weather-related uncertainties
4. **Recovery Planning**: Predict landing zones under varying winds
5. **Flight Validation**: Compare post-flight data with actual conditions

---

## Weather Data Sources

### 1. Wyoming Atmospheric Soundings

**Type**: Upper-air observations (radiosondes)

**Website**: http://weather.uwyo.edu/upperair/sounding.html

**Coverage**:
- Global network of ~850 stations
- Twice daily launches (00:00 and 12:00 UTC)
- Altitude range: Surface to ~30 km

**Data Provided**:
- Pressure (hPa)
- Temperature (°C)
- Dew point (°C)
- Wind speed (m/s) and direction (°)
- Altitude (m)

**Advantages**:
- ✅ Direct measurements (high accuracy)
- ✅ Altitude-resolved wind profiles
- ✅ Free and publicly accessible
- ✅ Historical data available

**Limitations**:
- ❌ Coarse temporal resolution (twice daily)
- ❌ Sparse spatial coverage (hundreds of km between stations)
- ❌ Data not always available (launch failures, data gaps)

**RocketPy Integration**:
```python
from rocketpy import Environment

env = Environment(latitude=32.99, longitude=-106.97)

# Fetch Wyoming sounding (station, date)
env.set_atmospheric_model(
    type='wyoming_sounding',
    file='http://weather.uwyo.edu/cgi-bin/sounding?...',
)
```

---

### 2. GFS (Global Forecast System)

**Type**: Numerical Weather Prediction model

**Provider**: NOAA (National Oceanic and Atmospheric Administration)

**Coverage**:
- Global coverage
- Forecasts out to 16 days
- Temporal resolution: 1-3 hours
- Spatial resolution: 0.25° (~25 km)

**Data Provided**:
- Temperature
- Pressure
- Geopotential height
- Wind (U/V components)
- Humidity

**Advantages**:
- ✅ Global coverage
- ✅ Forecast capability (predict future conditions)
- ✅ High temporal resolution
- ✅ Free and accessible via API

**Limitations**:
- ❌ Model-based (not direct measurements)
- ❌ Forecast accuracy degrades with time
- ❌ Coarse spatial resolution (not local effects)

**RocketPy Integration**:
```python
from rocketpy import Environment
from datetime import datetime, timedelta

env = Environment(latitude=39.39, longitude=-8.29)

# Fetch GFS forecast
forecast_date = datetime.now() + timedelta(days=1)  # Tomorrow
env.set_atmospheric_model(
    type='Forecast',
    file='GFS',
)
env.set_date(forecast_date)
```

---

### 3. NOAA RUCSOUNDINGS

**Type**: Rapid Update Cycle (RUC) model soundings

**Provider**: NOAA

**Coverage**:
- North America
- Hourly updates
- Spatial resolution: 13 km

**Advantages**:
- ✅ High temporal resolution (hourly)
- ✅ Better spatial resolution than GFS
- ✅ Good for North American launches

**Limitations**:
- ❌ North America only
- ❌ Shorter forecast horizon (18 hours)

---

### 4. HIRESW (High-Resolution Rapid Refresh)

**Type**: High-resolution regional model

**Coverage**:
- North America
- 3-15 km resolution
- 48-hour forecasts

**Advantages**:
- ✅ High resolution (captures local features)
- ✅ Better for terrain effects

---

### 5. ERA5 Reanalysis

**Type**: Historical weather reanalysis

**Provider**: ECMWF (European Centre for Medium-Range Weather Forecasts)

**Coverage**:
- Global
- 1979-present
- Hourly data
- 31 km resolution

**Use Cases**:
- Historical flight reconstructions
- Statistical analysis (climatology)
- Model validation

**Limitations**:
- ❌ Not real-time (3-month delay)
- ❌ Reanalysis (not forecasts)

---

### 6. Custom Atmospheric Profiles

**Type**: User-provided data

**Format**: Text file with altitude, temperature, pressure

**Example**:
```
# Altitude (m), Temperature (K), Pressure (Pa)
0, 288.15, 101325
1000, 281.65, 89874
2000, 275.15, 79495
...
```

**Use Cases**:
- Research experiments with specific profiles
- Testing edge cases (inversions, wind shear)

---

## RocketPy Weather Capabilities

### Environment Class

RocketPy's `Environment` class handles atmospheric modeling:

```python
from rocketpy import Environment

env = Environment(
    latitude=39.3897,   # Launch site latitude (degrees)
    longitude=-8.2889,  # Launch site longitude (degrees)
    elevation=100.0,    # Elevation above sea level (m)
)
```

### Setting Atmospheric Models

#### 1. Standard Atmosphere (Default)

```python
env.set_atmospheric_model(type='standard_atmosphere')
```

**Properties**:
- ISA (International Standard Atmosphere)
- Temperature: 15°C at sea level, -6.5°C/km lapse rate
- Pressure: Exponential decay

#### 2. Custom Atmosphere File

```python
env.set_atmospheric_model(
    type='custom_atmosphere',
    file='data/atmospheric/custom_profile.txt',
)
```

#### 3. Wyoming Sounding

```python
# Fetch directly from URL
env.set_atmospheric_model(
    type='wyoming_sounding',
    file='http://weather.uwyo.edu/cgi-bin/sounding?...',
)

# Or from saved file
env.set_atmospheric_model(
    type='wyoming_sounding',
    file='data/weather/sounding_20240615_12Z.txt',
)
```

#### 4. GFS Forecast

```python
from datetime import datetime

env.set_atmospheric_model(type='Forecast', file='GFS')
env.set_date((2024, 6, 15, 12))  # Year, month, day, hour (UTC)
```

#### 5. Ensemble Forecasts

```python
# Fetch all ensemble members
env.set_atmospheric_model(type='Ensemble', file='GEFS')
```

### Setting Wind Models

#### 1. Constant Wind

```python
# Wind speed (m/s), wind direction (meteorological degrees)
# 0° = North, 90° = East, 180° = South, 270° = West
env.set_wind(speed=5.0, direction=90.0)
```

#### 2. Wind Function (Altitude-Dependent)

```python
def wind_profile(altitude):
    """
    Custom wind function.

    Args:
        altitude (float): Altitude above sea level (m)

    Returns:
        tuple: (wind_u, wind_v) in m/s
            wind_u: East-West component (positive = eastward)
            wind_v: North-South component (positive = northward)
    """
    # Example: Power law wind profile
    surface_wind_speed = 5.0  # m/s
    surface_wind_dir = 90.0   # degrees
    reference_height = 10.0   # m
    alpha = 0.2  # Exponent (terrain-dependent)

    # Power law scaling
    if altitude < reference_height:
        speed = surface_wind_speed * (altitude / reference_height) ** alpha
    else:
        speed = surface_wind_speed * ((altitude - env.elevation) / reference_height) ** alpha

    # Convert to components
    import math
    direction_rad = math.radians(surface_wind_dir)
    wind_u = speed * math.sin(direction_rad)
    wind_v = speed * math.cos(direction_rad)

    return wind_u, wind_v

env.set_atmospheric_model(type='custom_atmosphere', wind=wind_profile)
```

#### 3. Wyoming Sounding Wind

Wind data is automatically extracted from Wyoming soundings:

```python
env.set_atmospheric_model(type='wyoming_sounding', file='...')
# Wind profile is automatically set from sounding data
```

#### 4. Forecast Wind

```python
env.set_atmospheric_model(type='Forecast', file='GFS')
# Wind profile is automatically extracted from forecast
```

### Date and Time

Set launch date/time for time-dependent atmospheric models:

```python
# UTC time: (year, month, day, hour)
env.set_date((2024, 6, 15, 14))  # June 15, 2024, 14:00 UTC

# Or with datetime
from datetime import datetime, timezone
env.set_date(datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc))
```

**Important**: Always use UTC time for consistency with weather data sources.

---

## Implementation Guide

### Phase 1: Basic Weather Integration

#### Step 1: Extend EnvironmentConfig

Add weather source configuration to `config_loader.py`:

```python
@dataclass
class WeatherConfig:
    """Weather data source configuration."""
    source: str = "standard_atmosphere"  # standard_atmosphere, wyoming, gfs, custom
    wyoming_station: Optional[str] = None  # e.g., "72340" (Oakland, CA)
    custom_file: Optional[str] = None
    fetch_real_time: bool = False

@dataclass
class EnvironmentConfig:
    latitude_deg: float
    longitude_deg: float
    elevation_m: float = 0.0
    date: Optional[Tuple[int, int, int, int]] = None
    wind: WindConfig = field(default_factory=WindConfig)
    weather: WeatherConfig = field(default_factory=WeatherConfig)  # NEW
    # ...
```

#### Step 2: Create Weather Fetcher Module

Create `src/weather_fetcher.py`:

```python
"""Weather data fetcher for real-time atmospheric conditions."""

from datetime import datetime, timezone
from typing import Optional, Tuple
import logging

try:
    from rocketpy import Environment
except ImportError:
    Environment = None

logger = logging.getLogger(__name__)


class WeatherFetcher:
    """Fetch real-world weather data for simulations."""

    @staticmethod
    def fetch_wyoming_sounding(
        station: str,
        date: Optional[datetime] = None,
    ) -> str:
        """
        Fetch Wyoming atmospheric sounding.

        Args:
            station: Station ID (e.g., "72340" for Oakland)
            date: Date/time for sounding (default: latest)

        Returns:
            URL or file path to sounding data

        Example:
            >>> url = WeatherFetcher.fetch_wyoming_sounding("72340")
            >>> env.set_atmospheric_model(type='wyoming_sounding', file=url)
        """
        if date is None:
            date = datetime.now(timezone.utc)

        year = date.year
        month = date.month
        day = date.day
        hour = 12 if date.hour >= 12 else 0  # Soundings at 00Z and 12Z

        url = (
            f"http://weather.uwyo.edu/cgi-bin/sounding?"
            f"region=naconf&TYPE=TEXT%3ALIST&YEAR={year}&MONTH={month:02d}&"
            f"FROM={day:02d}{hour:02d}&TO={day:02d}{hour:02d}&STNM={station}"
        )

        logger.info(f"Fetching Wyoming sounding: {url}")
        return url

    @staticmethod
    def fetch_gfs_forecast(
        latitude: float,
        longitude: float,
        date: datetime,
    ) -> dict:
        """
        Fetch GFS forecast for location and time.

        Args:
            latitude: Latitude in degrees
            longitude: Longitude in degrees
            date: Forecast date/time (UTC)

        Returns:
            Dictionary with forecast parameters

        Note:
            RocketPy handles GFS fetching internally via:
            env.set_atmospheric_model(type='Forecast', file='GFS')
        """
        logger.info(f"GFS forecast for ({latitude}, {longitude}) at {date}")
        return {'type': 'Forecast', 'file': 'GFS', 'date': date}
```

#### Step 3: Update EnvironmentBuilder

Modify `src/environment_setup.py`:

```python
from src.weather_fetcher import WeatherFetcher

class EnvironmentBuilder:
    def build(self) -> Environment:
        """Build environment with weather data."""
        env = Environment(
            latitude=self.config.latitude_deg,
            longitude=self.config.longitude_deg,
            elevation=self.config.elevation_m,
        )

        # Set date if provided
        if self.config.date is not None:
            env.set_date(self.config.date)

        # Set atmospheric model based on weather source
        weather_source = self.config.weather.source

        if weather_source == "standard_atmosphere":
            env.set_atmospheric_model(type='standard_atmosphere')

        elif weather_source == "wyoming":
            if self.config.weather.wyoming_station is None:
                raise ValueError("Wyoming station ID required")

            url = WeatherFetcher.fetch_wyoming_sounding(
                station=self.config.weather.wyoming_station,
                date=self._get_date_as_datetime(),
            )
            env.set_atmospheric_model(type='wyoming_sounding', file=url)

        elif weather_source == "gfs":
            env.set_atmospheric_model(type='Forecast', file='GFS')

        elif weather_source == "custom":
            if self.config.weather.custom_file is None:
                raise ValueError("Custom atmospheric file path required")
            env.set_atmospheric_model(
                type='custom_atmosphere',
                file=self.config.weather.custom_file,
            )

        else:
            raise ValueError(f"Unknown weather source: {weather_source}")

        # Set wind
        self._setup_wind_model()

        return env
```

#### Step 4: Configuration Example

Update `configs/competition_rocket.yaml`:

```yaml
environment:
  latitude_deg: 39.3897
  longitude_deg: -8.2889
  elevation_m: 100.0
  date: [2024, 6, 15, 12]  # June 15, 2024, 12:00 UTC

  weather:
    source: "wyoming"  # or "gfs", "standard_atmosphere", "custom"
    wyoming_station: "08495"  # Lisbon, Portugal station
    fetch_real_time: true

  wind:
    model: "from_weather"  # Extract from weather data
```

### Phase 2: Wind Profile Functions

#### Proper Wind Function Implementation

Currently, the framework stores wind as private attributes. RocketPy expects **callable wind functions**.

**Fix in `environment_setup.py`**:

```python
def _setup_wind_model(self) -> None:
    """Setup wind model using RocketPy's wind function interface."""
    import math

    wind_config = self.config.wind

    if wind_config.model == "constant":
        # Create constant wind function
        speed_ms = wind_config.velocity_ms
        direction_rad = math.radians(wind_config.direction_deg)

        def constant_wind(altitude):
            """Constant wind at all altitudes."""
            wind_u = speed_ms * math.sin(direction_rad)
            wind_v = speed_ms * math.cos(direction_rad)
            return wind_u, wind_v

        # Set wind function (not attributes!)
        self.environment.set_atmospheric_model(
            type=self.environment.atmospheric_model_type,
            wind_u=lambda h: constant_wind(h)[0],
            wind_v=lambda h: constant_wind(h)[1],
        )

    elif wind_config.model == "from_weather":
        # Wind is already set from weather data source
        pass

    elif wind_config.model == "custom":
        # Load custom wind function from file or definition
        raise NotImplementedError("Custom wind functions not yet implemented")
```

---

## Configuration Reference

### Weather Configuration Schema

```yaml
environment:
  # Location
  latitude_deg: 39.3897
  longitude_deg: -8.2889
  elevation_m: 100.0

  # Date/Time (UTC)
  date: [2024, 6, 15, 12]  # [year, month, day, hour]

  # Weather Source
  weather:
    source: "wyoming"  # Options: standard_atmosphere, wyoming, gfs, custom
    wyoming_station: "08495"  # Required for wyoming source
    custom_file: "data/atmospheric/profile.txt"  # Required for custom source
    fetch_real_time: true  # Fetch latest data vs. historical

  # Wind Configuration
  wind:
    model: "from_weather"  # Options: constant, from_weather, power_law, custom
    velocity_ms: 5.0  # Only for constant model
    direction_deg: 90.0  # Only for constant model
```

### Wyoming Station Codes

Common U.S. stations:

| Location | Station Code | Notes |
|----------|-------------|-------|
| Oakland, CA | 72340 | West Coast |
| Las Cruces, NM | 23048 | Spaceport America region |
| Denver, CO | 72469 | High elevation |
| White Sands, NM | 74794 | Near testing ranges |
| Cape Canaveral, FL | 72206 | Eastern launch sites |

International stations:

| Location | Station Code | Country |
|----------|-------------|---------|
| Lisbon | 08495 | Portugal |
| Stuttgart | 10739 | Germany |
| Prague | 11520 | Czech Republic |
| Rome | 16245 | Italy |

**Full list**: http://weather.uwyo.edu/upperair/sounding.html

---

## Best Practices

### 1. Launch Day Weather Workflow

**Timeline**: T-24 hours to T-0

#### T-24 Hours: Forecast Check
```python
# Fetch GFS forecast for launch day
env.set_atmospheric_model(type='Forecast', file='GFS')
env.set_date(launch_date)

# Run Monte Carlo with forecast uncertainties
mc_config = MonteCarloConfig(
    num_simulations=100,
    variations={
        'wind_speed_std_ms': 3.0,  # Forecast uncertainty
        'temperature_std_k': 2.0,
    }
)
```

**Action**: Go/No-go preliminary decision based on forecast.

#### T-6 Hours: Wyoming Sounding
```python
# Fetch latest radiosonde data
url = WeatherFetcher.fetch_wyoming_sounding(station="08495")
env.set_atmospheric_model(type='wyoming_sounding', file=url)

# Re-run prediction with actual profile
```

**Action**: Update apogee and landing predictions.

#### T-2 Hours: Final Forecast
```python
# Latest GFS update
env.set_atmospheric_model(type='Forecast', file='GFS')
env.set_date(launch_time)
```

**Action**: Final go/no-go decision.

### 2. Historical Flight Reconstruction

Use ERA5 reanalysis for post-flight analysis:

```python
from rocketpy import Environment

# Exact launch time
launch_time = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)

env.set_atmospheric_model(type='Reanalysis', file='ERA5')
env.set_date(launch_time)

# Compare simulated vs. actual flight data
```

### 3. Ensemble Forecasting

Run multiple forecasts for uncertainty quantification:

```python
# GFS ensemble members
env.set_atmospheric_model(type='Ensemble', file='GEFS')

# Run simulation for each ensemble member
for member in env.ensemble_members:
    env.select_ensemble_member(member)
    flight = run_simulation(rocket, env, config)
    results.append(flight.apogee)

# Analyze spread (forecast uncertainty)
mean_apogee = np.mean(results)
std_apogee = np.std(results)
```

### 4. Wind Sensitivity Analysis

Quantify wind impact:

```python
# Vary wind speed/direction
wind_speeds = [0, 3, 5, 7, 10]  # m/s
wind_directions = [0, 45, 90, 135, 180, 225, 270, 315]  # degrees

for speed in wind_speeds:
    for direction in wind_directions:
        env.set_wind(speed=speed, direction=direction)
        flight = run_simulation(rocket, env, config)
        log_results(speed, direction, flight.apogee, flight.x_impact, flight.y_impact)
```

### 5. Atmospheric Model Validation

Compare models for your location:

```python
# Standard atmosphere
env_std = build_environment(config, weather_source="standard_atmosphere")
flight_std = run_simulation(rocket, env_std, config)

# Wyoming sounding
env_wyo = build_environment(config, weather_source="wyoming")
flight_wyo = run_simulation(rocket, env_wyo, config)

# GFS forecast
env_gfs = build_environment(config, weather_source="gfs")
flight_gfs = run_simulation(rocket, env_gfs, config)

# Compare
print(f"Standard: {flight_std.apogee:.0f} m")
print(f"Wyoming:  {flight_wyo.apogee:.0f} m")
print(f"GFS:      {flight_gfs.apogee:.0f} m")
```

---

## Troubleshooting

### Issue: Wyoming Sounding Download Fails

**Symptom**: Error fetching data from weather.uwyo.edu

**Causes**:
1. No sounding data available for requested date/time
2. Station code incorrect
3. Network connectivity issues

**Solutions**:
```python
import requests

url = WeatherFetcher.fetch_wyoming_sounding("72340")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    print("✓ Sounding data available")
except requests.HTTPError as e:
    print(f"✗ HTTP error: {e}")
    print("Possible causes:")
    print("  - No sounding launched at this time")
    print("  - Station code invalid")
    print("  - Date/time out of range")
```

**Fallback**: Use GFS forecast or standard atmosphere.

### Issue: GFS Forecast Not Available

**Symptom**: RocketPy fails to fetch GFS data

**Causes**:
1. Forecast date too far in future (>16 days)
2. Network issues
3. NOAA server downtime

**Solutions**:
```python
from datetime import datetime, timedelta

# Check forecast horizon
max_forecast_days = 16
forecast_date = datetime.now() + timedelta(days=10)

if forecast_date - datetime.now() > timedelta(days=max_forecast_days):
    print("⚠ Forecast date beyond GFS horizon")
    print("  Using climatology or standard atmosphere instead")
```

### Issue: Wind Profile Discontinuities

**Symptom**: Sudden jumps in wind speed causing simulation instability

**Cause**: Wyoming soundings may have sparse data or missing levels

**Solution**: Interpolate and smooth:
```python
import numpy as np
from scipy.interpolate import interp1d

def smooth_wind_profile(altitudes, wind_speeds):
    """Smooth wind profile using cubic spline interpolation."""
    # Remove duplicates and NaNs
    valid_idx = ~np.isnan(wind_speeds)
    alt_clean = np.array(altitudes)[valid_idx]
    wind_clean = np.array(wind_speeds)[valid_idx]

    # Interpolate
    interp_func = interp1d(
        alt_clean,
        wind_clean,
        kind='cubic',
        fill_value='extrapolate',
    )

    # Generate smooth profile
    alt_smooth = np.linspace(alt_clean.min(), alt_clean.max(), 100)
    wind_smooth = interp_func(alt_smooth)

    return alt_smooth, wind_smooth
```

---

## References

### Weather Data Sources

1. **Wyoming Atmospheric Soundings**: http://weather.uwyo.edu/upperair/sounding.html
2. **NOAA GFS**: https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast
3. **ERA5 Reanalysis**: https://www.ecmwf.int/en/forecasts/datasets/reanalysis-datasets/era5
4. **RUCSOUNDINGS**: https://rucsoundings.noaa.gov/

### RocketPy Documentation

5. **Environment Class**: https://docs.rocketpy.org/en/latest/user/environment.html
6. **Weather Integration Examples**: https://github.com/RocketPy-Team/RocketPy/tree/master/docs/notebooks

### Meteorology Resources

7. **Radiosonde Data Interpretation**: https://www.weather.gov/jetstream/radiosondes
8. **Wind Profiles in ABL**: Stull, R. B. (2017). *Practical Meteorology: An Algebra-based Survey of Atmospheric Science*.

### Scientific Papers

9. **GFS Model Description**: Environmental Modeling Center (2003). *NCEP Office Note 442*.
10. **ERA5 Reanalysis**: Hersbach et al. (2020). "The ERA5 Global Reanalysis." *Quarterly Journal of the Royal Meteorological Society*.

---

## Appendix: Example Scripts

### Script: Fetch and Plot Wyoming Sounding

```python
#!/usr/bin/env python
"""Fetch and plot Wyoming atmospheric sounding."""

import matplotlib.pyplot as plt
from rocketpy import Environment
from datetime import datetime


def plot_sounding(station: str, date: datetime):
    """Plot temperature and wind profiles from sounding."""
    env = Environment(latitude=40.0, longitude=-105.0)

    # Fetch sounding
    url = f"http://weather.uwyo.edu/cgi-bin/sounding?..." # Construct URL
    env.set_atmospheric_model(type='wyoming_sounding', file=url)

    # Extract profiles
    altitudes = env.altitude
    temperatures = [env.temperature(h) for h in altitudes]
    wind_speeds = [env.wind_speed(h) for h in altitudes]

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    ax1.plot(temperatures, altitudes)
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Altitude (m)')
    ax1.set_title('Temperature Profile')
    ax1.grid(True)

    ax2.plot(wind_speeds, altitudes)
    ax2.set_xlabel('Wind Speed (m/s)')
    ax2.set_title('Wind Speed Profile')
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig(f'sounding_{station}_{date.strftime("%Y%m%d")}.png')
    print(f"✓ Saved sounding plot")


if __name__ == '__main__':
    plot_sounding(station="72340", date=datetime(2024, 6, 15, 12))
```

### Script: Compare Weather Sources

```python
#!/usr/bin/env python
"""Compare apogee predictions using different weather sources."""

from src.config_loader import ConfigLoader
from src.flight_simulator import FlightSimulator
import pandas as pd


def compare_weather_sources(config_path: str):
    """Run simulation with different weather sources."""
    results = []

    weather_sources = ['standard_atmosphere', 'wyoming', 'gfs']

    for source in weather_sources:
        # Load config and modify weather source
        loader = ConfigLoader()
        loader.load_from_yaml(config_path)

        env_config = loader.get_environment_config()
        env_config.weather.source = source

        # Build and run
        env = EnvironmentBuilder(env_config).build()
        motor = MotorBuilder(loader.get_motor_config()).build()
        rocket = RocketBuilder(loader.get_rocket_config()).build(motor)

        simulator = FlightSimulator(rocket, env, loader.get_simulation_config())
        flight = simulator.run()
        summary = simulator.get_summary()

        results.append({
            'source': source,
            'apogee_m': summary['apogee_m'],
            'max_velocity_ms': summary['max_velocity_ms'],
            'lateral_drift_m': summary['lateral_drift_m'],
        })

    # Display results
    df = pd.DataFrame(results)
    print(df)
    df.to_csv('weather_comparison.csv', index=False)


if __name__ == '__main__':
    compare_weather_sources('configs/competition_rocket.yaml')
```

---

**End of Document**

For implementation details, see [API_REFERENCE.md](API_REFERENCE.md).
For system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
For configuration examples, see [../configs/](../configs/).
