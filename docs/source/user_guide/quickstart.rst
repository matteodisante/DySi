Quick Start Guide
=================

This guide will help you run your first rocket simulation in just a few minutes.

Basic Simulation
----------------

1. Create a YAML Configuration File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a file named ``my_rocket.yaml``:

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

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0
      date: "2024-10-01 12:00:00"

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7
      heading_deg: 90

2. Run the Simulation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/my_rocket.yaml \
        --plots \
        --output results/

3. View Results
~~~~~~~~~~~~~~~

The simulation will generate:

- **Terminal output**: Apogee, max velocity, stability metrics
- **Plots**: Trajectory, velocity, acceleration profiles
- **JSON file**: Complete flight data in ``results/`` directory

Expected output:

.. code-block:: text

    ✅ Simulation completed successfully
    📊 Apogee: 2538.63 m
    🚀 Max velocity: 289.45 m/s
    ⏱️ Flight time: 156.2 s

Monte Carlo Analysis
---------------------

Run uncertainty quantification with parameter variations:

.. code-block:: bash

    python scripts/run_monte_carlo.py \
        --config configs/complete_example.yaml \
        --n-sims 1000 \
        --plots \
        --output monte_carlo_results/

The Monte Carlo configuration extends your base YAML with parameter distributions:

.. code-block:: yaml

    parameter_variations:
      motor.thrust_source:
        type: "normal"
        mean: 1.0
        std: 0.05
      rocket.mass_kg:
        type: "normal"
        mean: 19.197
        std: 0.5
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

Results include:

- Statistical distributions of apogee, velocity, impact point
- Sensitivity analysis (Sobol indices)
- Dispersion plots
- Summary statistics

Next Steps
----------

- :doc:`key_concepts` - Understand the framework architecture
- :doc:`configuration` - Complete configuration reference
- :doc:`../examples/index` - Explore advanced examples
- :doc:`../api/index` - API documentation
