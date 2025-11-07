Weather Integration
===================

Use real weather data from multiple sources for accurate simulations.

Data Sources
------------

Wyoming Soundings
~~~~~~~~~~~~~~~~~

Atmospheric profiles from radiosonde measurements:

.. code-block:: yaml

    environment:
      latitude_deg: 32.990254
      longitude_deg: -106.974998
      atmospheric_model_type: "wyoming_sounding"
      atmospheric_model_file: "http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR=2019&MONTH=02&FROM=0500&TO=0512&STNM=23050"
      date: "2019-02-05 12:00:00"

GFS Forecast
~~~~~~~~~~~~

NOAA Global Forecast System predictions:

.. code-block:: yaml

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      atmospheric_model_type: "gfs_forecast"
      date: "2024-10-01 12:00:00"

ERA5 Reanalysis
~~~~~~~~~~~~~~~

High-resolution historical data:

.. code-block:: yaml

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      atmospheric_model_type: "era5_reanalysis"
      date: "2024-10-01 12:00:00"

Custom Atmosphere
~~~~~~~~~~~~~~~~~

User-defined atmospheric profile (CSV):

.. code-block:: yaml

    environment:
      atmospheric_model_type: "custom_atmosphere"
      atmospheric_model_file: "data/custom_atmosphere.csv"

CSV format (altitude, temperature, pressure):

.. code-block:: text

    0, 288.15, 101325
    1000, 281.65, 89874.57
    2000, 275.15, 79495.22
    ...

Wind Configuration
------------------

Constant Wind
~~~~~~~~~~~~~

.. code-block:: yaml

    environment:
      wind_velocity_x_mps: 2.0  # East component
      wind_velocity_y_mps: 3.0  # North component

Or using magnitude and direction:

.. code-block:: yaml

    environment:
      wind_speed_mps: 5.0
      wind_direction_deg: 45  # FROM North-East

Wind Direction Convention
~~~~~~~~~~~~~~~~~~~~~~~~~

The framework uses **meteorological convention**:

- Wind direction = where wind **comes FROM**
- 0° = North, 90° = East, 180° = South, 270° = West
- Formula: ``u = -V*sin(θ)``, ``v = -V*cos(θ)``

Examples:

- **North wind (0°)**: Blows toward South → u=0, v=-V
- **East wind (90°)**: Blows toward West → u=-V, v=0
- **South wind (180°)**: Blows toward North → u=0, v=+V
- **West wind (270°)**: Blows toward East → u=+V, v=0

Example: Complete Weather Setup
--------------------------------

.. code-block:: yaml

    environment:
      # Location
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0

      # Weather source
      atmospheric_model_type: "gfs_forecast"
      date: "2024-10-01 12:00:00"

      # Wind (will be overridden by forecast if available)
      wind_speed_mps: 5.0
      wind_direction_deg: 270  # West wind

      # Limits
      max_expected_height_m: 15000

Running with Weather
--------------------

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/weather_example.yaml \
        --plots \
        --output results/

The simulation will:

1. Fetch atmospheric data from the specified source
2. Extract wind profile at different altitudes
3. Use temperature/pressure profile for air density
4. Run simulation with real weather conditions

Tips
----

- Always specify ``date`` for forecast/reanalysis sources
- Use ``max_expected_height_m`` to limit atmosphere queries
- Wyoming soundings are best for launch day predictions
- ERA5 is best for historical analysis
- GFS is best for near-term forecasts (0-16 days)

Next Steps
----------

- :doc:`monte_carlo` - Add weather uncertainty
- :doc:`../user_guide/configuration` - All weather options
