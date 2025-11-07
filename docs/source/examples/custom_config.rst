Custom Configurations
=====================

Advanced configuration techniques and patterns.

Multi-Stage Rockets
-------------------

While the framework currently focuses on single-stage rockets, you can simulate staging by running separate simulations for each stage.

Custom Drag Curves
------------------

Subsonic to Supersonic
~~~~~~~~~~~~~~~~~~~~~~

Create CSV files with Mach number vs drag coefficient:

.. code-block:: text

    # mach, cd
    0.0, 0.45
    0.3, 0.46
    0.6, 0.48
    0.8, 0.52
    0.9, 0.68
    1.0, 0.95
    1.2, 0.82
    1.5, 0.65
    2.0, 0.58

From CFD Analysis
~~~~~~~~~~~~~~~~~

Export CFD results to CSV format and reference in config:

.. code-block:: yaml

    rocket:
      power_off_drag: "data/cfd/power_off_drag.csv"
      power_on_drag: "data/cfd/power_on_drag.csv"

Complex Parachute Logic
------------------------

Altitude-Based Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    rocket:
      parachutes:
        - name: "Drogue"
          cd_s: 1.0
          trigger: "apogee"
          sampling_rate_hz: 105
          lag_s: 1.5

        - name: "Main"
          cd_s: 10.0
          trigger: "lambda p, h, y: y[5] < 0 and h < 800"
          sampling_rate_hz: 105
          lag_s: 1.5

The lambda function receives:

- ``p``: Pressure (Pa)
- ``h``: Altitude (m)
- ``y``: State vector [x, y, z, vx, vy, vz, ...]

Velocity-Based Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parachutes:
      - name: "Main"
        cd_s: 10.0
        trigger: "lambda p, h, y: y[5] < 0 and abs(y[5]) < 30"  # vz < 30 m/s

Time-Based Deployment
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parachutes:
      - name: "Backup"
        cd_s: 5.0
        trigger: "lambda p, h, y: y[5] < 0 and t > 45"  # After 45 seconds

Sensor Noise Modeling
----------------------

.. code-block:: yaml

    parachutes:
      - name: "Main"
        cd_s: 10.0
        trigger: "lambda p, h, y: y[5] < 0 and h < 800"
        sampling_rate_hz: 105
        lag_s: 1.5
        noise_bias: 5.0              # +5m bias
        noise_deviation: 2.0          # ±2m random
        noise_corr: [[1.0]]           # No correlation

Advanced Fin Configurations
---------------------------

Canted Fins (Roll Induction)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    rocket:
      fins:
        - n: 4
          root_chord_m: 0.12
          tip_chord_m: 0.04
          span_m: 0.1
          position_m: -1.04956
          cant_angle_deg: 2.0  # Induces roll
          airfoil: null

Custom Airfoils
~~~~~~~~~~~~~~~

.. code-block:: yaml

    rocket:
      fins:
        - n: 3
          root_chord_m: 0.15
          tip_chord_m: 0.05
          span_m: 0.12
          position_m: -1.0
          cant_angle_deg: 0.0
          airfoil: ["data/airfoils/naca_0012.txt", "radians"]

Airfoil file format (angle of attack, lift coefficient):

.. code-block:: text

    -0.174533, -0.45
    -0.087266, -0.23
    0.0, 0.0
    0.087266, 0.23
    0.174533, 0.45

Environment Profiles
--------------------

Custom Atmospheric Layers
~~~~~~~~~~~~~~~~~~~~~~~~~

Create multi-layer atmosphere with varying properties:

.. code-block:: text

    # altitude_m, temperature_K, pressure_Pa
    0, 288.15, 101325
    1000, 281.65, 89874.57
    2000, 275.15, 79495.22
    3000, 268.65, 70108.50
    5000, 255.65, 54019.90
    10000, 223.15, 26436.27

Reference in config:

.. code-block:: yaml

    environment:
      atmospheric_model_type: "custom_atmosphere"
      atmospheric_model_file: "data/custom_atmosphere.csv"

Wind Shear Profiles
~~~~~~~~~~~~~~~~~~~

Create altitude-dependent wind:

.. code-block:: text

    # altitude_m, wind_u_mps, wind_v_mps
    0, 2.0, 1.0
    1000, 3.5, 2.0
    2000, 5.0, 3.5
    3000, 6.0, 4.5
    5000, 7.5, 6.0

Note: Wind shear is automatically handled when using weather data sources (Wyoming, GFS, ERA5).

Parameter Sweeps
----------------

Study effect of single parameter:

.. code-block:: yaml

    # Base configuration
    motor:
      thrust_source: "Cesaroni_M1670.eng"
      position_m: -1.255

    rocket:
      mass_kg: 19.197

    # Sweep simulation config
    parameter_variations:
      simulation.inclination_deg:
        type: "uniform"
        min: 80
        max: 90

Run with many simulations to get full sweep:

.. code-block:: bash

    python scripts/run_monte_carlo.py \
        --config configs/inclination_sweep.yaml \
        --n-sims 100 \
        --plots \
        --output sweep_results/

Configuration Templates
-----------------------

Create reusable templates for common scenarios:

Competition Template
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # configs/templates/competition.yaml
    motor:
      thrust_source: "CHANGEME.eng"
      position_m: CHANGEME

    rocket:
      mass_kg: CHANGEME
      # ... standard competition rocket ...

    environment:
      latitude_deg: CHANGEME
      longitude_deg: CHANGEME

    air_brakes:
      target_apogee_m: 3000  # Competition target
      controller_type: "pid"

Research Template
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    # configs/templates/research.yaml
    # High-fidelity configuration for research

    motor:
      # Detailed motor model
      thrust_source: "motor.eng"
      interpolation_method: "spline"

    environment:
      # Real weather data
      atmospheric_model_type: "era5_reanalysis"
      date: "CHANGEME"

    # High-resolution Monte Carlo
    parameter_variations:
      # All uncertainties modeled

Validation and Testing
----------------------

Check Configuration Validity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from src.config import load_config

    try:
        config = load_config("configs/my_rocket.yaml")
        print("✅ Configuration valid")
    except Exception as e:
        print(f"❌ Configuration error: {e}")

Test Configuration
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Quick test with plots
    python scripts/run_single_simulation.py \
        --config configs/my_rocket.yaml \
        --plots

Best Practices
--------------

1. **Version Control**: Keep configs in git
2. **Documentation**: Comment complex configurations
3. **Validation**: Always test configs before production
4. **Templates**: Create templates for common scenarios
5. **Naming**: Use descriptive file names (e.g., ``calisto_competition_2024.yaml``)

Next Steps
----------

- :doc:`../user_guide/configuration` - Complete configuration reference
- :doc:`../api/index` - API documentation for custom code
