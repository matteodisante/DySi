Configuration Reference
=======================

This page provides a complete reference for all configuration options.

Configuration File Structure
-----------------------------

A complete configuration file has four main sections:

.. code-block:: yaml

    motor:
      # Motor parameters

    rocket:
      # Rocket parameters

    environment:
      # Environment parameters

    simulation:
      # Simulation parameters

Motor Configuration
-------------------

Required Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Type
     - Description
   * - ``thrust_source``
     - string
     - Path to .eng file or thrust multiplier
   * - ``burn_out_time_s``
     - float
     - Motor burn duration (seconds)
   * - ``dry_mass_kg``
     - float
     - Motor dry mass (kg)
   * - ``dry_inertia_11``
     - float
     - Axial moment of inertia (kg·m²)
   * - ``dry_inertia_22``
     - float
     - Lateral moment of inertia (kg·m²)
   * - ``dry_inertia_33``
     - float
     - Lateral moment of inertia (kg·m²)
   * - ``nozzle_radius_m``
     - float
     - Nozzle exit radius (m)
   * - ``grain_separation_m``
     - float
     - Separation between grain segments (m)
   * - ``grain_density_kg_m3``
     - float
     - Propellant grain density (kg/m³)
   * - ``grain_outer_radius_m``
     - float
     - Grain outer radius (m)
   * - ``grain_initial_inner_radius_m``
     - float
     - Grain initial inner radius (m)
   * - ``grain_initial_height_m``
     - float
     - Grain initial height (m)
   * - ``grains_center_of_dry_mass_position_m``
     - float
     - Center of mass position relative to nozzle (m)
   * - ``nozzle_position_m``
     - float
     - Nozzle position coordinate (m)
   * - ``position_m``
     - float
     - Motor position in rocket (m from nose tip)

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 30 20

   * - Parameter
     - Type
     - Default
     - Description
   * - ``interpolation_method``
     - string
     - "linear"
     - Thrust curve interpolation
   * - ``coordinate_system_orientation``
     - string
     - "nozzle_to_combustion_chamber"
     - Motor coordinate system

Example
~~~~~~~

.. code-block:: yaml

    motor:
      thrust_source: "Cesaroni_M1670.eng"
      burn_out_time_s: 3.9
      dry_mass_kg: 1.815
      dry_inertia_11: 0.125
      dry_inertia_22: 0.125
      dry_inertia_33: 0.002
      nozzle_radius_m: 0.033
      grain_separation_m: 0.005
      grain_density_kg_m3: 1815
      grain_outer_radius_m: 0.033
      grain_initial_inner_radius_m: 0.015
      grain_initial_height_m: 0.12
      grains_center_of_dry_mass_position_m: 0.317
      nozzle_position_m: 0.0
      position_m: -1.255  # REQUIRED - no safe default exists

Rocket Configuration
--------------------

Required Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Type
     - Description
   * - ``radius_m``
     - float
     - Rocket body radius (m)
   * - ``mass_kg``
     - float
     - Rocket dry mass without motor (kg)
   * - ``inertia_11``
     - float
     - Axial moment of inertia (kg·m²)
   * - ``inertia_22``
     - float
     - Lateral moment of inertia (kg·m²)
   * - ``inertia_33``
     - float
     - Lateral moment of inertia (kg·m²)
   * - ``center_of_mass_without_motor_m``
     - float
     - Center of mass position without motor (m from nose)
   * - ``power_off_drag``
     - string
     - Path to power-off drag coefficient CSV file
   * - ``power_on_drag``
     - string
     - Path to power-on drag coefficient CSV file

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 30 20

   * - Parameter
     - Type
     - Default
     - Description
   * - ``coordinate_system_orientation``
     - string
     - "tail_to_nose"
     - Rocket coordinate system

Aerodynamic Surfaces
~~~~~~~~~~~~~~~~~~~~

Nose Cone
^^^^^^^^^

.. code-block:: yaml

    rocket:
      nose:
        length_m: 0.55829
        kind: "vonKarman"
        position_m: 1.278

Fins
^^^^

.. code-block:: yaml

    rocket:
      fins:
        - n: 4
          root_chord_m: 0.12
          tip_chord_m: 0.04
          span_m: 0.1
          position_m: -1.04956
          cant_angle_deg: 0.0
          airfoil: null

Tail
^^^^

.. code-block:: yaml

    rocket:
      tail:
        top_radius_m: 0.0635
        bottom_radius_m: 0.0435
        length_m: 0.06
        position_m: -1.194656

Parachutes
^^^^^^^^^^

.. code-block:: yaml

    rocket:
      parachutes:
        - name: "Main"
          cd_s: 10.0
          trigger: "lambda p, h, y: y[5] < 0 and h < 800"
          sampling_rate_hz: 105
          lag_s: 1.5
          noise_bias: 0.0
          noise_deviation: 0.0
          noise_corr: [[1.0]]

        - name: "Drogue"
          cd_s: 1.0
          trigger: "apogee"
          sampling_rate_hz: 105
          lag_s: 1.5

Air Brakes
^^^^^^^^^^

.. code-block:: yaml

    rocket:
      air_brakes:
        drag_coefficient_curve: "data/air_brakes/cd_data.csv"
        reference_area_m2: 0.01
        controller_type: "pid"
        target_apogee_m: 3000
        sampling_rate_hz: 10
        control_loop_dt_s: 0.1
        max_deployment: 1.0
        deployment_rate_limit: 0.2
        overshoot_bias_factor: 1.0
        altitude_filter_alpha: 0.9
        velocity_filter_alpha: 0.8

Environment Configuration
-------------------------

Required Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Type
     - Description
   * - ``latitude_deg``
     - float
     - Launch site latitude (degrees)
   * - ``longitude_deg``
     - float
     - Launch site longitude (degrees)
   * - ``elevation_m``
     - float
     - Launch site elevation above sea level (m)

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 30 20

   * - Parameter
     - Type
     - Default
     - Description
   * - ``date``
     - string
     - None
     - Date/time for weather data (ISO format)
   * - ``atmospheric_model_type``
     - string
     - "standard_atmosphere"
     - Atmospheric model type
   * - ``atmospheric_model_file``
     - string
     - None
     - Path to custom atmospheric profile
   * - ``max_expected_height_m``
     - float
     - 10000
     - Maximum simulation altitude (m)

Weather Data Sources
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    environment:
      # Wyoming sounding
      atmospheric_model_type: "wyoming_sounding"
      atmospheric_model_file: "https://weather.uwyo.edu/..."

      # GFS forecast
      atmospheric_model_type: "gfs_forecast"
      date: "2024-10-01 12:00:00"

      # ERA5 reanalysis
      atmospheric_model_type: "era5_reanalysis"
      date: "2024-10-01 12:00:00"

      # Custom file
      atmospheric_model_type: "custom_atmosphere"
      atmospheric_model_file: "data/atmosphere.csv"

Wind Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    environment:
      # Constant wind
      wind_velocity_x_mps: 2.0
      wind_velocity_y_mps: 0.0

      # Or specify magnitude and direction
      wind_speed_mps: 5.0
      wind_direction_deg: 45  # FROM direction (meteorological convention)

Simulation Configuration
------------------------

Required Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Parameter
     - Type
     - Description
   * - ``rail_length_m``
     - float
     - Launch rail length (m)
   * - ``inclination_deg``
     - float
     - Rail inclination from horizontal (degrees, 90=vertical)
   * - ``heading_deg``
     - float
     - Rail azimuth heading (degrees, 0=North, 90=East)

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 20 30 20

   * - Parameter
     - Type
     - Default
     - Description
   * - ``terminate_on_apogee``
     - bool
     - false
     - Stop simulation at apogee
   * - ``verbose``
     - bool
     - false
     - Print detailed simulation progress

Monte Carlo Configuration
-------------------------

Parameter Variations
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parameter_variations:
      # Normal distribution
      motor.thrust_source:
        type: "normal"
        mean: 1.0      # Multiplier on nominal thrust
        std: 0.033     # Standard deviation

      # Uniform distribution
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

      # Truncated normal
      rocket.mass_kg:
        type: "truncated_normal"
        mean: 19.197
        std: 0.5
        min: 18.0
        max: 20.0

Sensitivity Analysis
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    sensitivity_analysis:
      method: "sobol"  # or "lae"
      n_samples: 1000
      target_variable: "apogee_m"
      parameters:
        - "motor.thrust_source"
        - "rocket.mass_kg"
        - "environment.wind_speed_mps"

Complete Example
----------------

.. code-block:: yaml

    motor:
      thrust_source: "Cesaroni_M1670.eng"
      burn_out_time_s: 3.9
      dry_mass_kg: 1.815
      dry_inertia_11: 0.125
      dry_inertia_22: 0.125
      dry_inertia_33: 0.002
      nozzle_radius_m: 0.033
      grain_separation_m: 0.005
      grain_density_kg_m3: 1815
      grain_outer_radius_m: 0.033
      grain_initial_inner_radius_m: 0.015
      grain_initial_height_m: 0.12
      grains_center_of_dry_mass_position_m: 0.317
      nozzle_position_m: 0.0
      position_m: -1.255

    rocket:
      radius_m: 0.0635
      mass_kg: 19.197
      inertia_11: 6.321
      inertia_22: 6.321
      inertia_33: 0.034
      center_of_mass_without_motor_m: 0.0
      power_off_drag: "data/calisto/powerOffDragCurve.csv"
      power_on_drag: "data/calisto/powerOnDragCurve.csv"

      nose:
        length_m: 0.55829
        kind: "vonKarman"
        position_m: 1.278

      fins:
        - n: 4
          root_chord_m: 0.12
          tip_chord_m: 0.04
          span_m: 0.1
          position_m: -1.04956

      parachutes:
        - name: "Main"
          cd_s: 10.0
          trigger: "lambda p, h, y: y[5] < 0 and h < 800"
          sampling_rate_hz: 105
          lag_s: 1.5

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0
      date: "2024-10-01 12:00:00"
      atmospheric_model_type: "standard_atmosphere"

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7
      heading_deg: 90

    parameter_variations:
      motor.thrust_source:
        type: "normal"
        mean: 1.0
        std: 0.033
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

See Also
--------

- :doc:`quickstart` - Quick start guide
- :doc:`key_concepts` - Framework concepts
- :doc:`../examples/index` - Configuration examples
