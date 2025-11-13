.. _config-environment-params:

=====================================
Environment Parameters Reference
=====================================

This reference documents all parameters in the ``environment`` configuration section.
The environment section defines launch site location, atmospheric conditions, wind profile, and environmental models.

.. contents:: On this page
   :local:
   :depth: 2

--------

Overview
========

The environment configuration controls:

.. grid:: 2
    :gutter: 2

    .. grid-item-card:: **Location**
        :class-card: sd-shadow-sm

        - Launch site coordinates (lat/lon)
        - Elevation above sea level
        - Gravity

    .. grid-item-card:: **Atmosphere**
        :class-card: sd-shadow-sm

        - Atmospheric model (standard, custom, real-time)
        - Temperature, pressure, density profiles
        - Weather data sources

    .. grid-item-card:: **Wind**
        :class-card: sd-shadow-sm

        - Wind velocity and direction
        - Altitude-dependent wind profiles
        - Constant, custom, or weather-based models

    .. grid-item-card:: **Time**
        :class-card: sd-shadow-sm

        - Launch date and time (optional)
        - For real-time weather fetching

--------

Launch Site Location
====================

latitude_deg
------------

:Type: ``float``
:Required: **Yes**
:Unit: degrees (°)
:Range: -90 to +90

**Latitude of launch site** in decimal degrees.

.. code-block:: yaml

    environment:
      latitude_deg: 39.3897  # North latitude (positive)

.. important::
   **Sign convention:**
   
   - **Positive (+)**: North latitude
   - **Negative (−)**: South latitude
   
   Examples:
   
   - Florida, USA: ``+28.5``
   - Atacama Desert, Chile: ``−24.5``

.. admonition:: How to Find Coordinates
   :class: dropdown

   **Method 1: Google Maps**
   
   1. Navigate to launch site in Google Maps
   2. Right-click on location → "What's here?"
   3. Click coordinates at bottom → copy latitude
   
   **Method 2: GPS device**
   
   Use smartphone GPS or handheld GPS unit:
   
   - iOS Maps: Drop pin → swipe up → see coordinates
   - Android Maps: Long press → coordinates displayed
   
   **Method 3: Launch site databases**
   
   - `Spaceport America <https://www.spaceportamerica.com/>`_: 32.9903°N
   - `Esrange Space Center <https://www.sscspace.com/esrange-space-center/>`_: 67.8900°N
   - `Alcantara Space Center <https://en.wikipedia.org/wiki/Alcantara_Launch_Center>`_: -2.3738°S

.. tip::
   **Precision requirements:**
   
   - **±0.1°** (~11 km error): Acceptable for most simulations
   - **±0.01°** (~1 km error): Good for competition launches
   - **±0.001°** (~100 m error): High-precision simulations
   
   3-4 decimal places is usually sufficient.

--------

longitude_deg
-------------

:Type: ``float``
:Required: **Yes**
:Unit: degrees (°)
:Range: -180 to +180

**Longitude of launch site** in decimal degrees.

.. code-block:: yaml

    environment:
      longitude_deg: -8.2889  # West longitude (negative)

.. important::
   **Sign convention:**
   
   - **Positive (+)**: East longitude
   - **Negative (−)**: West longitude
   
   Examples:
   
   - London, UK: ``−0.1276``
   - Tokyo, Japan: ``+139.6917``
   - New York, USA: ``−74.0060``

--------

elevation_m
-----------

:Type: ``float``
:Required: No
:Default: ``0.0``
:Unit: meters (m)

**Elevation of launch site above mean sea level (MSL)**.

.. code-block:: yaml

    environment:
      elevation_m: 1400.0  # Launch pad at 1400 m MSL

Affects:

- Initial atmospheric pressure/density
- Gravity calculation
- Altitude measurements (apogee is **above ground level**, not MSL)

.. admonition:: How to Find Elevation
   :class: dropdown

   **Method 1: Google Earth**
   
   1. Navigate to launch site
   2. Elevation displayed at bottom-right
   
   **Method 2: Topographic maps**
   
   - `USGS TopoView (USA) <https://ngmdb.usgs.gov/topoview/>`_
   - `OpenTopoMap <https://opentopomap.org/>`_
   
   **Method 3: GPS/smartphone**
   
   - Many GPS apps show elevation
   - Note: GPS elevation can be ±10-50 m inaccurate
   
   **Method 4: Google Maps API**
   
   Use Elevation API with lat/lon coordinates

.. tip::
   **Common launch site elevations:**
   
   .. list-table::
      :header-rows: 1
      :widths: 60 40
      
      * - Launch Site
        - Elevation (m)
      * - Sea level (coastal)
        - 0 - 50
      * - Spaceport America, NM, USA
        - 1400
      * - Black Rock Desert, NV, USA
        - 1190
      * - Esrange, Sweden
        - 300
      * - Interlagos, Portugal
        - 100

.. warning::
   **High-altitude launch sites** (>1000 m) have significantly reduced air density!
   
   - Lower drag → higher apogee
   - Different motor performance
   - Adjust parachute sizing accordingly

--------

Atmospheric Model
=================

atmospheric_model
-----------------

:Type: ``string``
:Required: No
:Default: ``"standard_atmosphere"``
:Options: ``"standard_atmosphere"``, ``"custom_atmosphere"``

**Atmospheric model** for temperature, pressure, and density profiles.

.. deprecated:: 1.0
   Use ``weather.source`` instead. This parameter is maintained for backward compatibility.

.. code-block:: yaml

    environment:
      atmospheric_model: "standard_atmosphere"

.. tab-set::

    .. tab-item:: standard_atmosphere (Default)

        **International Standard Atmosphere (ISA)**
        
        - Standard temperature/pressure profiles
        - No real weather variations
        - Deterministic (same every time)
        
        .. code-block:: yaml
        
            environment:
              atmospheric_model: "standard_atmosphere"
        
        ✅ **When to use:**
        
        - Design studies, preliminary simulations
        - Competition predictions (conservative)
        - No weather data available
        
        ⚠️ **Limitations:**
        
        - Ignores real weather (temperature, pressure variations)
        - Not suitable for high-accuracy predictions

    .. tab-item:: custom_atmosphere

        **Custom atmospheric profile from file**
        
        Load temperature/pressure data from file:
        
        .. code-block:: yaml
        
            environment:
              atmospheric_model: "custom_atmosphere"
              atmospheric_model_file: "data/atmosphere_2024-03-15.csv"
        
        ✅ **When to use:**
        
        - Custom atmospheric profiles (soundings, reanalysis data)
        - Historical weather conditions
        - Specific atmospheric scenarios

.. seealso::
   - :ref:`config-environment-weather` for modern weather data sources
   - :ref:`how-to-create-custom-atmosphere` for file format

--------

atmospheric_model_file
----------------------

:Type: ``string`` or ``null``
:Required: Only if ``atmospheric_model = "custom_atmosphere"``

**Path to custom atmospheric profile file**.

.. deprecated:: 1.0
   Use ``weather.custom_file`` instead.

.. code-block:: yaml

    environment:
      atmospheric_model: "custom_atmosphere"
      atmospheric_model_file: "data/atmosphere.csv"

.. admonition:: File Format
   :class: dropdown

   CSV file with altitude, temperature, pressure:
   
   .. code-block:: text
      :caption: data/atmosphere.csv
   
       # Altitude (m), Temperature (K), Pressure (Pa)
       0, 288.15, 101325
       500, 284.9, 95460
       1000, 281.7, 89870
       1500, 278.4, 84550
       2000, 275.2, 79490
       5000, 255.7, 54020
       10000, 223.3, 26430
   
   - Altitude in meters above MSL
   - Temperature in Kelvin
   - Pressure in Pascals

--------

.. _config-environment-weather:

Weather Data Sources
====================

The ``weather`` subsection provides access to real-time and historical atmospheric data.

.. code-block:: yaml

    environment:
      weather:
        source: "wyoming"
        wyoming_station: "72340"
        fetch_real_time: false

weather.source
--------------

:Type: ``string``
:Required: No
:Default: ``"standard_atmosphere"``
:Options: ``"standard_atmosphere"``, ``"wyoming"``, ``"gfs"``, ``"era5"``, ``"custom"``

**Weather data source** for atmospheric profiles.

.. code-block:: yaml

    environment:
      weather:
        source: "wyoming"

.. tab-set::

    .. tab-item:: standard_atmosphere (Default)

        **ISA standard atmosphere**
        
        - Same as ``atmospheric_model: "standard_atmosphere"``
        - No external data required
        
        .. code-block:: yaml
        
            environment:
              weather:
                source: "standard_atmosphere"

    .. tab-item:: wyoming

        **University of Wyoming sounding database**
        
        - Upper air soundings from worldwide weather stations
        - Historical data back to 1970s
        - Twice-daily soundings (00:00 and 12:00 UTC)
        
        .. code-block:: yaml
        
            environment:
              latitude_deg: 37.7749
              longitude_deg: -122.4194
              weather:
                source: "wyoming"
                wyoming_station: "72340"  # Oakland, CA
                fetch_real_time: false
              date: [2024, 6, 15, 12]  # June 15, 2024, 12:00 UTC
        
        ✅ **When to use:**
        
        - Post-flight analysis (match real conditions)
        - Competition predictions (use historical statistics)
        - Launch sites near weather stations
        
        ⚠️ **Requirements:**
        
        - Internet connection
        - Valid Wyoming station ID
        - Date within available data range

    .. tab-item:: gfs

        **NOAA Global Forecast System (GFS)**
        
        - Numerical weather prediction model
        - Forecast data (0-16 days ahead)
        - Global coverage, 0.25° resolution
        
        .. code-block:: yaml
        
            environment:
              weather:
                source: "gfs"
                fetch_real_time: true  # Use latest forecast
        
        ⚠️ **RocketPy integration required**
        
        Not yet fully supported in rocket-sim. Use RocketPy API directly.

    .. tab-item:: custom

        **Custom atmospheric file**
        
        .. code-block:: yaml
        
            environment:
              weather:
                source: "custom"
                custom_file: "data/atmosphere_2024-03-15.csv"

--------

weather.wyoming_station
-----------------------

:Type: ``string`` or ``null``
:Required: Only if ``weather.source = "wyoming"``

**Wyoming sounding station ID** (5-digit code).

.. code-block:: yaml

    environment:
      weather:
        source: "wyoming"
        wyoming_station: "72340"  # Oakland, CA

.. admonition:: Finding Wyoming Station IDs
   :class: dropdown

   **Step 1: Find nearest station**
   
   Browse map: `Wyoming Sounding Database <http://weather.uwyo.edu/upperair/sounding.html>`_
   
   **Step 2: Note station ID**
   
   Common stations:
   
   .. list-table::
      :header-rows: 1
      :widths: 40 40 20
      
      * - Location
        - Station Name
        - ID
      * - Oakland, CA, USA
        - KOAK
        - 72340
      * - Denver, CO, USA
        - KDNR
        - 72469
      * - Corpus Christi, TX, USA
        - KCRP
        - 72250
      * - Lisbon, Portugal
        - LPPT
        - 08562
      * - Stockholm, Sweden
        - ESSA
        - 02365
      * - Adelaide, Australia
        - YPAD
        - 94672
   
   **Step 3: Verify data availability**
   
   Check that station has data for your target date:
   
   1. Go to Wyoming website
   2. Select station, date, time
   3. Verify sounding appears

.. tip::
   **Choosing the right station:**
   
   - Select station **upwind** of launch site (wind carries air mass)
   - Closer is better (within ~100-200 km)
   - Check data availability for target date range

--------

weather.custom_file
-------------------

:Type: ``string`` or ``null``
:Required: Only if ``weather.source = "custom"``

**Path to custom atmospheric profile file**.

.. code-block:: yaml

    environment:
      weather:
        source: "custom"
        custom_file: "data/atmosphere_high_altitude.csv"

See :ref:`how-to-create-custom-atmosphere` for file format.

--------

weather.fetch_real_time
-----------------------

:Type: ``boolean``
:Required: No
:Default: ``false``

**Fetch latest available weather data** instead of using ``date``.

.. code-block:: yaml

    environment:
      weather:
        source: "wyoming"
        wyoming_station: "72340"
        fetch_real_time: true  # Ignore 'date', use latest sounding

.. tab-set::

    .. tab-item:: false (Default)

        **Use specified date** from ``environment.date``:
        
        .. code-block:: yaml
        
            environment:
              date: [2024, 6, 15, 12]
              weather:
                source: "wyoming"
                wyoming_station: "72340"
                fetch_real_time: false

    .. tab-item:: true

        **Fetch latest available data**:
        
        .. code-block:: yaml
        
            environment:
              weather:
                source: "wyoming"
                wyoming_station: "72340"
                fetch_real_time: true  # Ignore 'date'
        
        Useful for:
        
        - Real-time launch decisions
        - Pre-launch simulations with current weather

--------

Date and Time
=============

date
----

:Type: ``list of int`` (4 elements) or ``null``
:Required: No
:Default: ``null``
:Format: ``[year, month, day, hour_utc]``

**Launch date and time** for weather data fetching.

.. code-block:: yaml

    environment:
      date: [2024, 6, 15, 12]  # June 15, 2024, 12:00 UTC

.. important::
   **Time is in UTC** (Coordinated Universal Time), not local time!
   
   Convert local time to UTC:
   
   - PDT (UTC-7): Add 7 hours
   - EDT (UTC-4): Add 4 hours
   - CET (UTC+1): Subtract 1 hour

.. tab-set::

    .. tab-item:: null (Default)

        **No specific date** (use standard atmosphere):
        
        .. code-block:: yaml
        
            environment:
              date: null
              weather:
                source: "standard_atmosphere"

    .. tab-item:: Specific date

        **Historical or forecast date**:
        
        .. code-block:: yaml
        
            environment:
              date: [2024, 6, 15, 12]  # June 15, 2024, 12:00 UTC
              weather:
                source: "wyoming"
                wyoming_station: "72340"
        
        Wyoming soundings available at:
        
        - **00:00 UTC** (midnight)
        - **12:00 UTC** (noon)
        
        Use nearest time to your launch.

.. admonition:: Date Format Examples
   :class: dropdown

   .. code-block:: yaml
   
       # Morning launch (9:00 AM local PDT = 16:00 UTC)
       # Use 12:00 UTC sounding (closest available)
       date: [2024, 7, 20, 12]
       
       # Evening launch (6:00 PM local CET = 17:00 UTC)
       # Use 12:00 UTC sounding
       date: [2024, 8, 5, 12]
       
       # Early morning launch (7:00 AM local EST = 12:00 UTC)
       date: [2024, 9, 10, 12]

--------

Wind Configuration
==================

The ``wind`` subsection defines wind velocity and direction profiles.

.. code-block:: yaml

    environment:
      wind:
        model: "constant"
        velocity_ms: 5.0
        direction_deg: 90.0

wind.model
----------

:Type: ``string``
:Required: No
:Default: ``"constant"``
:Options: ``"constant"``, ``"from_weather"``, ``"function"``, ``"custom"``

**Wind model type**.

.. code-block:: yaml

    environment:
      wind:
        model: "constant"

.. tab-set::

    .. tab-item:: constant (Default)

        **Constant wind at all altitudes**
        
        - Same velocity and direction from ground to max altitude
        - Simplest model
        
        .. code-block:: yaml
        
            environment:
              wind:
                model: "constant"
                velocity_ms: 5.0
                direction_deg: 90.0  # Easterly wind
        
        ✅ **When to use:**
        
        - Initial design studies
        - Conservative estimates (worst-case wind)
        - No detailed wind data available

    .. tab-item:: from_weather

        **Extract wind from weather data source**
        
        Uses wind profile from Wyoming sounding, GFS, etc.:
        
        .. code-block:: yaml
        
            environment:
              weather:
                source: "wyoming"
                wyoming_station: "72340"
              wind:
                model: "from_weather"
        
        ✅ **When to use:**
        
        - Real weather data available
        - Altitude-dependent wind analysis
        - Competition predictions

    .. tab-item:: custom

        **Custom wind profile from file**
        
        Load wind data from CSV:
        
        .. code-block:: yaml
        
            environment:
              wind:
                model: "custom"
                # Custom file path defined separately
        
        ⚠️ **Advanced feature** - requires RocketPy API for file specification

--------

wind.velocity_ms
----------------

:Type: ``float``
:Required: Only if ``wind.model = "constant"``
:Unit: meters per second (m/s)

**Wind speed** (constant model).

.. code-block:: yaml

    environment:
      wind:
        model: "constant"
        velocity_ms: 5.0

.. admonition:: Wind Speed Conversions
   :class: dropdown

   .. list-table::
      :header-rows: 1
      :widths: 30 30 40
      
      * - m/s
        - km/h
        - mph (knots)
      * - 0 - 2
        - 0 - 7
        - Calm (0-4 kt)
      * - 2 - 5
        - 7 - 18
        - Light breeze (4-10 kt)
      * - 5 - 10
        - 18 - 36
        - Moderate wind (10-20 kt)
      * - 10 - 15
        - 36 - 54
        - Strong wind (20-30 kt)
      * - 15 - 20
        - 54 - 72
        - Very strong (30-40 kt)
      * - >20
        - >72
        - Dangerous (>40 kt)
   
   **Conversion factors:**
   
   - mph → m/s: divide by 2.237
   - km/h → m/s: divide by 3.6
   - knots → m/s: divide by 1.944

.. warning::
   **Launch wind limits:**
   
   - **< 5 m/s (10 mph)**: Safe for most rockets
   - **5-10 m/s (10-20 mph)**: Experienced fliers, large rockets only
   - **> 10 m/s (20 mph)**: Generally unsafe, scrub launch

--------

wind.direction_deg
------------------

:Type: ``float``
:Required: Only if ``wind.model = "constant"``
:Unit: degrees (°)
:Range: 0 to 360

**Wind direction** in meteorological convention.

.. code-block:: yaml

    environment:
      wind:
        model: "constant"
        direction_deg: 90.0  # Wind FROM the East

.. important::
   **Meteorological convention:** Direction wind is **coming FROM**, not blowing toward.
   
   .. code-block:: text
   
       direction_deg = 0°   → Wind from North (northerly)
       direction_deg = 90°  → Wind from East (easterly)
       direction_deg = 180° → Wind from South (southerly)
       direction_deg = 270° → Wind from West (westerly)

.. image:: /_static/images/wind_direction_compass.png
   :alt: Wind direction compass rose
   :width: 300px
   :align: center

.. admonition:: Wind Direction Examples
   :class: dropdown

   .. code-block:: yaml
   
       # Scenario 1: Wind blowing toward launch pad from the ocean (West)
       wind:
         direction_deg: 270.0  # Westerly wind
       
       # Scenario 2: Wind from mountains (North-East)
       wind:
         direction_deg: 45.0  # NE wind
       
       # Scenario 3: Onshore breeze (from water, East)
       wind:
         direction_deg: 90.0  # Easterly wind

--------

Gravity
=======

gravity_ms2
-----------

:Type: ``float``
:Required: No
:Default: ``9.80665``
:Unit: meters per second squared (m/s²)

**Gravitational acceleration** at launch site.

.. code-block:: yaml

    environment:
      gravity_ms2: 9.80665  # Standard Earth gravity

RocketPy can compute gravity from latitude and elevation.

.. admonition:: Latitude/Altitude Variations
   :class: dropdown

   Gravity varies by ~0.5% across Earth:
   
   .. list-table::
      :header-rows: 1
      :widths: 50 50
      
      * - Location
        - gravity_ms2
      * - Equator, sea level
        - 9.7803
      * - 45° latitude, sea level
        - 9.8062
      * - North Pole, sea level
        - 9.8322
      * - Mount Everest (8848 m)
        - 9.7640
   
   **For most simulations**, use default ``9.80665`` (standard gravity).

.. tip::
   Leave at default unless:
   
   - Extreme latitude (polar regions)
   - Very high elevation (>3000 m)
   - High-precision trajectory analysis

--------

Simulation Limits
=================

max_expected_height_m
---------------------

:Type: ``float``
:Required: No
:Default: ``10000.0``
:Unit: meters (m)

**Maximum expected altitude** for pre-allocating atmospheric data.

.. code-block:: yaml

    environment:
      max_expected_height_m: 5000.0

RocketPy pre-computes atmospheric properties up to this altitude.

.. tip::
   **Setting max_expected_height:**
   
   - Set ~20-30% above estimated apogee
   - Too low: simulation may fail if rocket exceeds limit
   - Too high: wastes memory, slower initialization
   
   Examples:
   
   - Small model rocket (300 m apogee): ``max_expected_height_m: 500``
   - High-power L motor (1500 m apogee): ``max_expected_height_m: 2000``
   - Competition M motor (3000 m apogee): ``max_expected_height_m: 5000``

--------

Complete Examples
=================

Simple Launch Site
------------------

.. code-block:: yaml

    environment:
      # Spaceport America, New Mexico, USA
      latitude_deg: 32.9903
      longitude_deg: -106.9750
      elevation_m: 1400.0
      
      # Standard atmosphere, light wind
      atmospheric_model: "standard_atmosphere"
      wind:
        model: "constant"
        velocity_ms: 3.0
        direction_deg: 180.0  # Southerly wind
      
      gravity_ms2: 9.80665
      max_expected_height_m: 5000.0

Real Weather Data
-----------------

.. code-block:: yaml

    environment:
      # Competition launch - use historical weather
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 100.0
      date: [2024, 6, 15, 12]  # June 15, 2024, 12:00 UTC
      
      # Fetch Wyoming sounding
      weather:
        source: "wyoming"
        wyoming_station: "08562"  # Lisbon, Portugal
        fetch_real_time: false
      
      # Use wind from weather data
      wind:
        model: "from_weather"
      
      max_expected_height_m: 3500.0

High-Altitude Launch
--------------------

.. code-block:: yaml

    environment:
      # High-altitude desert launch site
      latitude_deg: 40.6505
      longitude_deg: -119.2053
      elevation_m: 1190.0  # Black Rock Desert, NV
      
      # Custom atmosphere file (thin air at altitude)
      atmospheric_model: "custom_atmosphere"
      atmospheric_model_file: "data/atmosphere_black_rock.csv"
      
      # Strong desert wind
      wind:
        model: "constant"
        velocity_ms: 8.0
        direction_deg: 270.0  # Westerly wind
      
      gravity_ms2: 9.805  # Slightly reduced at latitude 40°N
      max_expected_height_m: 8000.0

--------

See Also
========

.. seealso::

   **Configuration References:**
   
   - :ref:`config-rocket-params` - Rocket geometry and mass properties
   - :ref:`config-motor-params` - Motor and propulsion system
   - :ref:`config-simulation-params` - Simulation settings and rail configuration
   
   **Tutorials:**
   
   - :ref:`tutorial-basic-flight` - Complete first simulation
   - :ref:`tutorial-weather-data` - Using real atmospheric data
   
   **How-To Guides:**
   
   - :ref:`how-to-find-launch-coordinates` - Determining lat/lon/elevation
   - :ref:`how-to-wyoming-soundings` - Fetching historical weather
   - :ref:`how-to-create-custom-atmosphere` - Custom atmospheric profiles
   - :ref:`how-to-wind-analysis` - Wind drift prediction
   
   **Examples:**
   
   - :ref:`example-weather-sensitivity` - Impact of weather on apogee
   - :ref:`example-multi-location` - Comparing launch sites

--------

**Next:** :ref:`config-simulation-params`
