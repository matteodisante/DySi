Air Brakes Control
==================

Active control system for precise apogee targeting.

Overview
--------

Air brakes are deployable surfaces that increase drag to control apogee. The framework includes PID, bang-bang, and model-predictive controllers.

Configuration
-------------

Basic Setup
~~~~~~~~~~~

.. code-block:: yaml

    rocket:
      air_brakes:
        # Drag characteristics
        drag_coefficient_curve: "data/air_brakes/cd_data.csv"
        reference_area_m2: 0.01

        # Controller settings
        controller_type: "pid"
        target_apogee_m: 3000

        # Control loop
        sampling_rate_hz: 10
        control_loop_dt_s: 0.1

        # Hardware constraints
        max_deployment: 1.0
        deployment_rate_limit: 0.2

        # Tuning
        overshoot_bias_factor: 1.0
        altitude_filter_alpha: 0.9
        velocity_filter_alpha: 0.8

Drag Curve
~~~~~~~~~~

CSV file with deployment vs drag coefficient:

.. code-block:: text

    # deployment, cd
    0.0, 0.0
    0.2, 0.15
    0.4, 0.28
    0.6, 0.39
    0.8, 0.48
    1.0, 0.55

Controller Types
----------------

PID Controller
~~~~~~~~~~~~~~

Proportional-Integral-Derivative control:

.. code-block:: yaml

    rocket:
      air_brakes:
        controller_type: "pid"
        target_apogee_m: 3000
        overshoot_bias_factor: 1.05  # Prefer slight overshoot

**Best for**: Smooth, stable control with minimal oscillation

Bang-Bang Controller
~~~~~~~~~~~~~~~~~~~~

Binary on/off control:

.. code-block:: yaml

    rocket:
      air_brakes:
        controller_type: "bang_bang"
        target_apogee_m: 3000
        max_deployment: 1.0

**Best for**: Simple hardware, fast response

Model Predictive Controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Predictive control with constraints:

.. code-block:: yaml

    rocket:
      air_brakes:
        controller_type: "mpc"
        target_apogee_m: 3000
        prediction_horizon_s: 2.0

**Best for**: Optimal performance, complex constraints

Hardware Constraints
--------------------

Deployment Limits
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    air_brakes:
      max_deployment: 1.0  # 0.0 = closed, 1.0 = fully open
      deployment_rate_limit: 0.2  # Max change per second

Prevents:

- Over-deployment (physical damage)
- Excessive deployment rates (servo overload)

Control Loop Timing
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    air_brakes:
      sampling_rate_hz: 10        # Sensor sample rate
      control_loop_dt_s: 0.1      # Control update interval

Tuning Parameters
-----------------

Overshoot Bias
~~~~~~~~~~~~~~

.. code-block:: yaml

    air_brakes:
      overshoot_bias_factor: 1.05  # Target 5% overshoot

- ``< 1.0``: Conservative (undershoot preferred)
- ``= 1.0``: Neutral
- ``> 1.0``: Aggressive (overshoot preferred)

Sensor Filtering
~~~~~~~~~~~~~~~~

.. code-block:: yaml

    air_brakes:
      altitude_filter_alpha: 0.9   # Altitude smoothing
      velocity_filter_alpha: 0.8   # Velocity smoothing

Higher values = more smoothing, less noise, more lag

State Reset
~~~~~~~~~~~

The controller automatically resets state between Monte Carlo runs:

.. code-block:: python

    def reset_state(self):
        """Reset controller state for new simulation."""
        self._integral = 0.0
        self._prev_error = 0.0
        self._commanded_deployment = 0.0
        self._actual_deployment = 0.0

This prevents state contamination in Monte Carlo analysis.

Running with Air Brakes
------------------------

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/air_brakes_example.yaml \
        --plots \
        --output results/

Expected Output
---------------

.. code-block:: text

    ✅ Simulation completed successfully

    📊 Simulation Results:
    ├─ Target apogee: 3000.00 m
    ├─ Actual apogee: 2998.45 m
    ├─ Error: -1.55 m (0.05%)
    └─ Max air brake deployment: 0.73

    🎮 Air Brakes Performance:
    ├─ Activation time: 12.3 s
    ├─ Peak deployment: 0.73 (73%)
    ├─ Total control effort: 45.2
    └─ Apogee accuracy: 99.95%

Generated Plots
---------------

1. **Air Brake Deployment**: Deployment level vs time
2. **Apogee Tracking**: Predicted vs target apogee
3. **Control Error**: Error signal evolution
4. **Drag Force**: Air brake drag contribution

Complete Example
----------------

.. code-block:: yaml

    motor:
      thrust_source: "Cesaroni_M1670.eng"
      # ... motor config ...
      position_m: -1.255

    rocket:
      # ... rocket config ...
      mass_kg: 19.197

      # Air brakes configuration
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

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7
      heading_deg: 90

Monte Carlo with Air Brakes
----------------------------

Test controller robustness:

.. code-block:: yaml

    parameter_variations:
      motor.thrust_source:
        type: "normal"
        mean: 1.0
        std: 0.033

      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

Run:

.. code-block:: bash

    python scripts/run_monte_carlo.py \
        --config configs/air_brakes_monte_carlo.yaml \
        --n-sims 1000 \
        --plots \
        --output mc_air_brakes/

Results show:

- Apogee distribution with active control
- Controller performance statistics
- Robustness to parameter variations

Tuning Guidelines
-----------------

1. **Start Conservative**: Low ``overshoot_bias_factor`` (0.95-1.0)
2. **Test in Simulation**: Run Monte Carlo to verify robustness
3. **Iterate**: Adjust based on performance metrics
4. **Validate**: Compare to flight test data if available

Common Issues
-------------

Oscillation
~~~~~~~~~~~

If deployment oscillates:

- Increase filter alphas (more smoothing)
- Reduce overshoot bias
- Decrease control loop frequency

Undershoot
~~~~~~~~~~

If consistently undershoots target:

- Increase overshoot bias factor
- Check drag curve accuracy
- Verify deployment limits

Next Steps
----------

- :doc:`monte_carlo` - Test controller robustness
- :doc:`../user_guide/configuration` - All air brake options
