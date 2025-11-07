Basic Simulation
================

This example demonstrates a basic rocket simulation with standard atmosphere.

Configuration File
------------------

Create ``configs/basic_example.yaml``:

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
          cant_angle_deg: 0.0
          airfoil: null

      tail:
        top_radius_m: 0.0635
        bottom_radius_m: 0.0435
        length_m: 0.06
        position_m: -1.194656

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
          noise_bias: 0.0
          noise_deviation: 0.0
          noise_corr: [[1.0]]

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7
      heading_deg: 90

Running the Simulation
----------------------

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/basic_example.yaml \
        --plots \
        --output results/

Python Script
~~~~~~~~~~~~~

.. code-block:: python

    from src.config import load_config
    from src.motor_builder import MotorBuilder
    from src.environment_setup import EnvironmentBuilder
    from src.rocket_builder import RocketBuilder
    from src.simulator import RocketSimulator

    # Load configuration
    config = load_config("configs/basic_example.yaml")

    # Build components
    motor_builder = MotorBuilder(config.motor)
    motor = motor_builder.build()

    env_builder = EnvironmentBuilder(config.environment)
    environment = env_builder.build()

    rocket_builder = RocketBuilder(
        config.rocket,
        motor=motor,
        motor_config=config.motor
    )
    rocket = rocket_builder.build()

    # Run simulation
    simulator = RocketSimulator(
        rocket=rocket,
        environment=environment,
        simulation_config=config.simulation
    )
    flight = simulator.run()

    # Get results
    summary = simulator.get_summary()
    print(f"Apogee: {summary['apogee_m']:.2f} m")
    print(f"Max velocity: {summary['max_velocity_mps']:.2f} m/s")
    print(f"Flight time: {summary['t_final_s']:.2f} s")

Expected Output
---------------

.. code-block:: text

    ✅ configs/basic_example.yaml

    📊 Simulation Results:
    ├─ Apogee: 2538.63 m (8329.49 ft)
    ├─ Max velocity: 289.45 m/s (Mach 0.85)
    ├─ Max acceleration: 98.23 m/s² (10.02 g)
    ├─ Flight time: 156.23 s
    ├─ Impact velocity: 5.23 m/s
    └─ Apogee time: 18.45 s

    🎯 Stability Analysis:
    ├─ Static margin (motor full): 2.34 calibers
    ├─ Static margin (motor empty): 2.56 calibers
    └─ Stability: STABLE ✓

    💾 Output saved to: results/basic_example_*.json

Generated Plots
---------------

The simulation generates the following plots:

1. **Trajectory Plot**: 3D flight path visualization
2. **Altitude vs Time**: Altitude profile throughout flight
3. **Velocity vs Time**: Velocity components over time
4. **Acceleration vs Time**: Acceleration profile
5. **Angular Position**: Pitch, yaw, roll angles
6. **Drag Coefficient**: Drag coefficient vs Mach number
7. **Stability Margin**: Static margin throughout flight

Understanding Results
---------------------

Apogee
~~~~~~

The maximum altitude reached by the rocket. Affected by:

- Motor thrust and burn time
- Rocket mass and drag
- Launch angle and rail length
- Wind conditions

Maximum Velocity
~~~~~~~~~~~~~~~~

Peak velocity typically occurs at motor burnout. Depends on:

- Thrust-to-weight ratio
- Drag coefficient
- Atmospheric density

Static Margin
~~~~~~~~~~~~~

Distance between center of gravity (CG) and center of pressure (CP):

- **> 2 calibers**: Stable (recommended)
- **1-2 calibers**: Marginally stable
- **< 1 caliber**: Unstable (dangerous)

The framework checks stability for both motor-full and motor-empty conditions.

Flight Phases
~~~~~~~~~~~~~

1. **Rail Phase**: Guided flight on launch rail (~0-1s)
2. **Powered Ascent**: Motor burning (~1-4s)
3. **Coasting**: Unpowered ascent to apogee (~4-18s)
4. **Drogue Descent**: Drogue parachute deployed (~18-40s)
5. **Main Descent**: Main parachute deployed (~40-156s)

Next Steps
----------

- :doc:`monte_carlo` - Add uncertainty quantification
- :doc:`weather_integration` - Use real weather data
- :doc:`air_brakes` - Add active control system
- :doc:`../user_guide/configuration` - Explore configuration options
