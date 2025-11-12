.. _howto_troubleshoot:

Troubleshoot Simulation Issues
================================

This guide helps you diagnose and fix common simulation problems.

Quick Diagnostics
-----------------

Run Basic Health Check
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check configuration validity
   python scripts/run_single_simulation.py configs/single_sim/my_rocket.yaml --validate
   
   # Enable verbose output
   python scripts/run_single_simulation.py configs/single_sim/my_rocket.yaml --verbose
   
   # Enable debug logging
   python scripts/run_single_simulation.py configs/single_sim/my_rocket.yaml --log-level DEBUG

Common Error Categories
-----------------------

Category 1: Configuration Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70
   
   * - Symptom
     - Solution
   * - ``FileNotFoundError: motor file not found``
     - Check ``motor_path`` in config - use absolute or relative path from config directory
   * - ``KeyError: missing required field``
     - Add missing field to YAML (check against template in ``configs/templates/``)
   * - ``ValueError: invalid parameter value``
     - Verify units and range (e.g., masses must be positive, angles in degrees)
   * - ``YAML parsing error``
     - Check YAML syntax - indentation must be consistent, use spaces not tabs

Category 2: Physics Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70
   
   * - Symptom
     - Solution
   * - Negative stability margin
     - Move CoM forward or add/enlarge fins (see :ref:`howto_validate_design`)
   * - Rail exit velocity too low
     - Use more powerful motor or longer rail
   * - Flight hangs at simulation start
     - Check motor thrust curve - must have non-zero values
   * - Unrealistic apogee
     - Verify rocket mass and motor total impulse

Category 3: Integration Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70
   
   * - Symptom
     - Solution
   * - ``RuntimeError: integration failed``
     - Reduce ``max_time_step`` or increase ``max_iterations``
   * - Oscillating trajectory
     - Use stricter tolerances (``rtol: 1e-6``, ``atol: 1e-9``)
   * - Simulation very slow
     - Increase ``max_time_step`` or reduce ``max_time`` if flight is complete

Detailed Troubleshooting
-------------------------

Problem: Simulation Doesn't Start
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- Script exits immediately
- No output files created
- Error message before flight initialization

**Diagnostic steps:**

.. code-block:: bash

   # Check if configuration loads
   python -c "
   import yaml
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   print('Config loaded:', config['name'])
   "
   
   # Check motor file
   python -c "
   from rocketpy import SolidMotor
   motor = SolidMotor(
       thrust_source='data/motors/my_motor.eng',
       burn_time=3.0,
       dry_mass=0.5,
       dry_inertia=(0.1, 0.1, 0.01),
       center_of_dry_mass_position=0.0,
       grains_center_of_mass_position=0.0,
       nozzle_radius=0.033,
       grain_number=5,
       grain_separation=0.005,
       grain_density=1815,
       grain_outer_radius=0.033,
       grain_initial_inner_radius=0.015,
       grain_initial_height=0.12,
       nozzle_position=0.0,
       throat_radius=0.011
   )
   print('Motor loaded OK')
   "

**Common fixes:**

1. **Missing motor file:**

   .. code-block:: yaml
   
      # Wrong (relative to script location)
      motor_path: my_motor.eng
      
      # Correct (relative to config file)
      motor_path: ../../data/motors/my_motor.eng

2. **Invalid YAML syntax:**

   .. code-block:: yaml
   
      # Wrong (missing colon)
      name my_rocket
      
      # Wrong (tabs instead of spaces)
      fins:
      	number: 3
      
      # Correct
      name: my_rocket
      fins:
        number: 3

3. **Missing required fields:**

   .. code-block:: bash
   
      # Compare with template
      diff configs/single_sim/my_rocket.yaml configs/templates/single_sim_template.yaml

Problem: Unstable Flight
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- Rocket tumbles immediately after launch
- Negative stability margin in output
- Wild trajectory in plots

**Diagnostic steps:**

.. code-block:: python

   import yaml
   
   # Check stability margin
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   
   # Extract key parameters
   rocket_length = config['rocket']['length_m']
   radius = config['rocket']['radius_m']
   
   # Print CoM/CP (from output)
   with open('outputs/my_rocket/final_state_READABLE.txt') as f:
       for line in f:
           if 'Center of Mass' in line or 'Center of Pressure' in line:
               print(line.strip())

**Solution workflow:**

.. code-block:: python

   # quick_stability.py - Check stability before full simulation
   
   from rocketpy import Rocket, SolidMotor
   import yaml
   
   # Load config
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   
   # Create minimal rocket (fast setup)
   motor = SolidMotor(
       thrust_source=config['motor']['motor_path'],
       burn_time=config['motor']['burn_time_s'],
       dry_mass=config['motor']['dry_mass_kg'],
       # ... other motor params
   )
   
   rocket = Rocket(
       radius=config['rocket']['radius_m'],
       mass=config['rocket']['mass_without_motor_kg'],
       inertia=(0.1, 0.1, 0.01),  # Rough estimate
       power_off_drag=0.5,
       power_on_drag=0.5,
       center_of_mass_without_motor=0.0,
       coordinate_system_orientation="tail_to_nose"
   )
   
   rocket.add_motor(motor, position=config['motor']['position_m'])
   
   # Add fins
   rocket.add_trapezoidal_fins(
       n=config['fins']['number'],
       root_chord=config['fins']['root_chord_m'],
       tip_chord=config['fins']['tip_chord_m'],
       span=config['fins']['span_m'],
       position=config['fins']['position_m']
   )
   
   # Check stability
   rocket.plots.static_margin()  # Generates plot
   
   print(f"\nStability margin: {rocket.static_margin(0):.2f} calibers")
   
   if rocket.static_margin(0) < 1.0:
       print("⚠️  WARNING: Unstable! Stability margin < 1.0")
       print("Solutions:")
       print("- Increase fin span")
       print("- Move fins further back")
       print("- Move motor forward (if possible)")
   elif rocket.static_margin(0) > 3.0:
       print("⚠️  WARNING: Overstable! May weathercock excessively")
       print("Solutions:")
       print("- Reduce fin span")
       print("- Move fins forward")
   else:
       print("✓ Stability margin OK (1.0 - 3.0)")

Problem: Parachute Doesn't Deploy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- High impact velocity (>20 m/s)
- No parachute event in output
- Rocket falls ballistically

**Diagnostic steps:**

.. code-block:: bash

   # Check parachute events in output
   grep -i "parachute" outputs/my_rocket/final_state_READABLE.txt
   
   # Check for deployment trigger
   grep -A 5 "parachute" outputs/my_rocket/my_rocket_log

**Common causes:**

1. **Trigger never satisfied:**

   .. code-block:: yaml
   
      # Wrong - apogee detection might fail if tolerance too strict
      parachutes:
        drogue:
          trigger: apogee
          # No trigger_value needed for apogee
      
      # Wrong - altitude trigger set too low
      parachutes:
        main:
          trigger: altitude
          trigger_value: 100  # Rocket might land before reaching 100m descent

2. **Invalid trigger function:**

   .. code-block:: yaml
   
      # Wrong - lambda syntax
      trigger_function: "lambda p, y: y[2] < 500"
      
      # Correct
      trigger_function: "lambda p, y: y[2] < 500 and y[5] < 0"
      # y[2] = altitude, y[5] = vertical velocity

**Quick test:**

.. code-block:: python

   # test_parachute_trigger.py
   
   # Simulate apogee condition
   def apogee_trigger(p, y):
       # y[5] is vertical velocity
       return y[5] < 0  # Triggers when descending
   
   # Test condition
   test_state = [0, 0, 1000, 0, 0, -0.1]  # At apogee, velocity just turned negative
   
   if apogee_trigger(0, test_state):
       print("✓ Trigger would activate at apogee")
   else:
       print("✗ Trigger would NOT activate")

Problem: Simulation Runs Forever
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- Script doesn't terminate
- Output files never finalize
- CPU usage stays high

**Diagnostic steps:**

.. code-block:: bash

   # Check simulation time in config
   grep "max_time" configs/single_sim/my_rocket.yaml
   
   # Monitor log in real-time
   tail -f outputs/my_rocket/my_rocket_log

**Common causes:**

1. **max_time too large:**

   .. code-block:: yaml
   
      # Wrong - flight ends in ~60s but simulating 1000s
      integration:
        max_time: 1000
      
      # Correct - reasonable upper bound
      integration:
        max_time: 200

2. **Parachute failure causing long descent:**

   .. code-block:: yaml
   
      # Check if parachute is deployed
      parachutes:
        drogue:
          cd_s: 0.5  # Too small? Rocket descends very slowly
      
      # Increase Cd*S for faster descent
      parachutes:
        drogue:
          cd_s: 2.0

**Force termination:**

.. code-block:: bash

   # Find process
   ps aux | grep run_single_simulation
   
   # Kill process (use PID from above)
   kill -9 <PID>

Problem: Unrealistic Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- Apogee much higher/lower than expected
- Impossible velocities or accelerations
- Trajectory goes underground

**Validation checklist:**

.. code-block:: python

   # validate_results.py
   
   import json
   
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json') as f:
       data = json.load(f)
   
   results = data['flight_results']
   
   # Check physically plausible ranges
   checks = {
       'Apogee < 10 km': results['apogee_m'] < 10000,
       'Max velocity < 500 m/s': results['max_velocity_ms'] < 500,
       'Max acceleration < 300 m/s²': results['max_acceleration_ms2'] < 300,
       'Flight time < 600 s': results['flight_time_s'] < 600,
       'Landing distance < 5 km': results['lateral_distance_m'] < 5000,
       'Impact velocity < 30 m/s': abs(results['impact_velocity_ms']) < 30,
   }
   
   print("Plausibility checks:")
   for check, passed in checks.items():
       status = "✓" if passed else "✗"
       print(f"{status} {check}")
   
   if not all(checks.values()):
       print("\n⚠️ Some checks failed - review configuration!")

**Common parameter errors:**

.. code-block:: yaml

   # Wrong - mass too low (kg vs g confusion)
   mass_without_motor_kg: 0.5  # This is 500g - very light!
   
   # Correct
   mass_without_motor_kg: 5.0  # 5 kg
   
   # Wrong - radius in meters, should be diameter?
   radius_m: 0.1  # This is 200mm diameter - very large
   
   # Correct
   radius_m: 0.04  # 80mm diameter (typical HPR)

Problem: Monte Carlo Failures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptoms:**

- Some simulations fail in ensemble
- Missing output files
- Error in logs: "Simulation X failed"

**Diagnostic steps:**

.. code-block:: bash

   # Check how many failed
   grep -c "failed" outputs/monte_carlo_*/ensemble_log.txt
   
   # Find which simulations failed
   grep "failed" outputs/monte_carlo_*/ensemble_log.txt
   
   # Check first failed simulation
   ls outputs/monte_carlo_*/sim_0001/

**Common causes:**

1. **Random parameter out of valid range:**

   .. code-block:: yaml
   
      # Wrong - mass can be negative with this variation!
      mass_without_motor_kg:
        distribution: normal
        mean: 5.0
        std_dev: 10.0  # Too large!
      
      # Correct
      mass_without_motor_kg:
        distribution: normal
        mean: 5.0
        std_dev: 0.5  # ±10% variation

2. **Instability in some samples:**

   .. code-block:: yaml
   
      # Fin variation might cause instability
      fins:
        span_m:
          distribution: normal
          mean: 0.15
          std_dev: 0.05  # Some samples might have very small fins
      
      # Add lower bound or reduce variation

Advanced Debugging
------------------

Enable Full Debug Output
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # In config file, add:
   simulation:
     log_level: DEBUG
     verbose: true

Create Debug Script
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # debug_sim.py - Interactive debugging
   
   import yaml
   from src.simulation.single_flight import SingleFlightSimulation
   import pdb
   
   # Load config
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   
   # Create simulation
   sim = SingleFlightSimulation(config)
   
   # Set breakpoint before flight
   pdb.set_trace()
   
   # Run simulation (will stop at breakpoint)
   sim.run()

Check RocketPy Objects
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # inspect_objects.py - Examine RocketPy internals
   
   from rocketpy import Rocket, SolidMotor, Environment
   
   # Create objects
   motor = SolidMotor(...)
   rocket = Rocket(...)
   env = Environment(...)
   
   # Inspect motor
   print("Motor info:")
   motor.info()
   motor.plots.thrust()
   
   # Inspect rocket
   print("\nRocket info:")
   rocket.info()
   rocket.plots.static_margin()
   
   # Inspect environment
   print("\nEnvironment info:")
   env.info()

Validate Against OpenRocket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Export trajectory for comparison
   python scripts/export_for_openrocket.py outputs/my_rocket/
   
   # Compare apogees
   python -c "
   import json
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json') as f:
       data = json.load(f)
   print('RocketPy apogee:', data['flight_results']['apogee_m'])
   print('Compare with OpenRocket simulation')
   "

Getting Help
------------

Collect Diagnostic Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Create support bundle
   tar -czf debug_bundle.tar.gz \
       configs/single_sim/my_rocket.yaml \
       outputs/my_rocket/my_rocket_log \
       outputs/my_rocket/final_state_READABLE.txt \
       outputs/my_rocket/trajectory/my_rocket_summary.json

When Reporting Issues
~~~~~~~~~~~~~~~~~~~~~

Include:

1. **Configuration file** (YAML)
2. **Full error message** or log excerpt
3. **Expected vs. actual behavior**
4. **Python version** and dependency versions
5. **Rocket-sim version** (from ``git describe --tags``)

Report bugs at: https://github.com/your-org/rocket-sim/issues

Quick Reference: Error Messages
--------------------------------

.. code-block:: text

   Error: "Rocket is unstable"
   → Fix: Check stability margin with validate_design.py
   
   Error: "Motor file not found"
   → Fix: Use absolute path or check relative path from config directory
   
   Error: "Integration did not converge"
   → Fix: Reduce max_time_step or increase max_iterations
   
   Error: "Apogee detection failed"
   → Fix: Ensure sufficient max_time for complete flight
   
   Error: "Parachute trigger never activated"
   → Fix: Check trigger function and conditions
   
   Error: "Invalid parameter value: X must be positive"
   → Fix: Check units and sign of parameter X in config
   
   Warning: "Rail exit velocity low (<20 m/s)"
   → Fix: Use more powerful motor or longer rail
   
   Warning: "Impact velocity high (>15 m/s)"
   → Fix: Check parachute deployment and Cd*S values

.. seealso::

   - :ref:`howto_validate_design` - Pre-flight validation
   - :ref:`tutorial_first_simulation` - Basic simulation guide
   - :ref:`api_reference` - Configuration parameter reference
