.. _howto_motor_selection:

Select the Optimal Motor
=========================

This guide helps you choose the right motor to achieve your target apogee while maintaining safe flight characteristics.

.. admonition:: Quick Answer
   :class: tip
   
   Use the impulse-to-weight ratio method: Target I/W ratio of 80-120 N·s/kg for sport flights.

Prerequisites
-------------

- Know your rocket's dry mass (without motor)
- Know your target apogee
- Have access to motor specifications

Method 1: Target Apogee Approach
---------------------------------

Step 1: Estimate Required Impulse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this empirical formula for sport rockets:

.. math::

   I_{\text{required}} \approx 100 \times m_{\text{dry}} \times \sqrt{\frac{h_{\text{target}}}{1000}}

Where:

- :math:`I_{\text{required}}` = Total impulse (N·s)
- :math:`m_{\text{dry}}` = Rocket dry mass (kg)
- :math:`h_{\text{target}}` = Target apogee (m)

**Example calculation:**

.. code-block:: python

   import math
   
   # Rocket parameters
   dry_mass_kg = 8.5
   target_apogee_m = 2500
   
   # Estimate required impulse
   impulse_required = 100 * dry_mass_kg * math.sqrt(target_apogee_m / 1000)
   
   print(f"Required total impulse: {impulse_required:.0f} N·s")
   # Output: Required total impulse: 4250 N·s

Step 2: Find Motors in Range
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Search ThrustCurve.org or your motor inventory for motors with:

- Total impulse: 0.8× to 1.2× required (3400 - 5100 N·s in example)
- Diameter: Fits your motor mount
- Length: Fits your airframe

**Example candidates:**

.. code-block:: text

   Cesaroni M1670:  Total Impulse = 5467 N·s  ✓
   AeroTech M1315:  Total Impulse = 4392 N·s  ✓
   Loki M2020:      Total Impulse = 5280 N·s  ✓

Step 3: Simulate Each Option
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create test configs for each motor:

.. code-block:: bash

   # Test motor 1
   cp configs/my_rocket.yaml configs/test_m1670.yaml
   # Edit thrust_source to Cesaroni_M1670.eng
   python scripts/run_single_simulation.py --config configs/test_m1670.yaml --name m1670_test
   
   # Test motor 2
   cp configs/my_rocket.yaml configs/test_m1315.yaml
   # Edit thrust_source to AeroTech_M1315.eng
   python scripts/run_single_simulation.py --config configs/test_m1315.yaml --name m1315_test

Step 4: Compare Results
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Quick comparison script
   for motor in m1670_test m1315_test m2020_test; do
       echo "=== $motor ==="
       grep "Apogee:" outputs/$motor/final_state_READABLE.txt
       grep "Max Velocity:" outputs/$motor/final_state_READABLE.txt
       grep "Max Acceleration:" outputs/$motor/final_state_READABLE.txt
   done

**Example output:**

.. code-block:: text

   === m1670_test ===
   Apogee:           2605 m  (13m over target)
   Max Velocity:     248 m/s
   Max Acceleration: 132 m/s² (13.5g)
   
   === m1315_test ===
   Apogee:           2485 m  (15m under target)
   Max Velocity:     232 m/s
   Max Acceleration: 105 m/s² (10.7g)  ← Best match!
   
   === m2020_test ===
   Apogee:           2680 m  (180m over target)
   Max Velocity:     265 m/s
   Max Acceleration: 175 m/s² (17.8g)  ← Too aggressive

**Selection:** AeroTech M1315 is closest to target with safe acceleration.

Method 2: Impulse-to-Weight Ratio
----------------------------------

Quick Calculation
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Motor specifications
   total_impulse_ns = 4392  # N·s
   propellant_mass_kg = 2.8  # kg
   
   # Rocket
   dry_mass_kg = 8.5
   total_mass = dry_mass_kg + propellant_mass_kg
   
   # Calculate I/W ratio
   iw_ratio = total_impulse_ns / total_mass
   
   print(f"I/W Ratio: {iw_ratio:.1f} N·s/kg")
   # Output: I/W Ratio: 388.7 N·s/kg

**I/W Ratio Guidelines:**

.. list-table::
   :header-rows: 1
   :widths: 30 30 40
   
   * - I/W Ratio
     - Flight Type
     - Typical Apogee
   * - 50-80 N·s/kg
     - Low altitude
     - 300-800 m
   * - 80-120 N·s/kg
     - Sport flight
     - 800-1500 m
   * - 120-180 N·s/kg
     - High altitude
     - 1500-3000 m
   * - 180-300 N·s/kg
     - Very high
     - 3000-6000 m
   * - > 300 N·s/kg
     - Extreme
     - > 6000 m

Motor Selection Constraints
----------------------------

Physical Constraints
~~~~~~~~~~~~~~~~~~~~

1. **Diameter**: Motor must fit motor mount

   .. code-block:: yaml
   
      # Check motor diameter vs. rocket diameter
      rocket_diameter: 127 mm
      motor_diameter: 98 mm  # Fits with centering rings

2. **Length**: Motor must fit airframe

   .. code-block:: text
   
      Motor length: 548 mm
      Available space: 600 mm  ✓

3. **Mass**: Total mass must be reasonable

   .. code-block:: python
   
      loaded_mass = dry_mass + motor_propellant
      # Should be < 25 kg for amateur flights

Performance Constraints
~~~~~~~~~~~~~~~~~~~~~~~

1. **Acceleration limits**:

   - Electronics: < 30g
   - Airframe: < 40g
   - Comfortable: < 15g

2. **Velocity limits**:

   - Subsonic: < 300 m/s (Mach 0.88)
   - Transonic: Avoid unless designed for it

3. **Stability throughout burn**:

   - Check CoM shift as propellant burns
   - Ensure stability margin stays > 1.0

Cost Optimization
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Compare cost per meter of altitude
   
   motors = [
       {'name': 'M1315', 'cost': 180, 'apogee': 2485},
       {'name': 'M1670', 'cost': 220, 'apogee': 2605},
       {'name': 'M2020', 'cost': 250, 'apogee': 2680},
   ]
   
   for m in motors:
       cost_per_m = m['cost'] / m['apogee']
       print(f"{m['name']}: €{cost_per_m:.3f}/meter")
   
   # Output:
   # M1315: €0.072/meter  ← Most efficient
   # M1670: €0.084/meter
   # M2020: €0.093/meter

Motor Comparison Script
-----------------------

Create ``scripts/compare_motors.py``:

.. code-block:: python

   #!/usr/bin/env python3
   """Compare multiple motors for target apogee."""
   
   import sys
   import json
   from pathlib import Path
   import subprocess
   
   def simulate_motor(base_config, motor_file, motor_name):
       """Simulate rocket with specific motor."""
       
       # Create temp config
       import yaml
       with open(base_config) as f:
           config = yaml.safe_load(f)
       
       config['motor']['thrust_source'] = motor_file
       
       temp_config = f'/tmp/test_{motor_name}.yaml'
       with open(temp_config, 'w') as f:
           yaml.dump(config, f)
       
       # Run simulation
       output_name = f'motor_test_{motor_name}'
       cmd = [
           'python', 'scripts/run_single_simulation.py',
           '--config', temp_config,
           '--name', output_name
       ]
       
       subprocess.run(cmd, capture_output=True)
       
       # Load results
       summary_file = Path(f'outputs/{output_name}/trajectory/{output_name}_summary.json')
       with open(summary_file) as f:
           return json.load(f)
   
   def compare_motors(base_config, motors, target_apogee):
       """Compare list of motors."""
       
       results = []
       
       for motor_name, motor_file in motors.items():
           print(f"Simulating {motor_name}...")
           data = simulate_motor(base_config, motor_file, motor_name)
           
           flight = data['flight_results']
           
           results.append({
               'name': motor_name,
               'apogee': flight['apogee_m'],
               'apogee_error': abs(flight['apogee_m'] - target_apogee),
               'max_velocity': flight['max_velocity_ms'],
               'max_accel': flight['max_acceleration_ms2'],
               'flight_time': flight['flight_time_s']
           })
       
       # Sort by apogee error (closest to target)
       results.sort(key=lambda x: x['apogee_error'])
       
       # Print comparison
       print("\n" + "="*80)
       print(f"MOTOR COMPARISON (Target: {target_apogee:.0f} m)")
       print("="*80)
       print(f"{'Motor':<15} {'Apogee':>10} {'Error':>10} {'Max V':>10} {'Max A':>10}")
       print(f"{'':15} {'(m)':>10} {'(m)':>10} {'(m/s)':>10} {'(g)':>10}")
       print("-"*80)
       
       for r in results:
           accel_g = r['max_accel'] / 9.81
           error_str = f"+{r['apogee_error']:.0f}" if r['apogee'] > target_apogee else f"{r['apogee_error']:.0f}"
           print(f"{r['name']:<15} {r['apogee']:>10.0f} {error_str:>10} {r['max_velocity']:>10.1f} {accel_g:>10.1f}")
       
       print("="*80)
       print(f"RECOMMENDED: {results[0]['name']} (closest to target)")
       print("="*80)
   
   if __name__ == "__main__":
       motors = {
           'M1315': 'data/motors/AeroTech_M1315.eng',
           'M1670': 'data/motors/Cesaroni_M1670.eng',
           'M2020': 'data/motors/Loki_M2020.eng',
       }
       
       compare_motors('configs/my_rocket.yaml', motors, target_apogee=2500)

**Usage:**

.. code-block:: bash

   python scripts/compare_motors.py

Motor Safety Checks
-------------------

Before Final Selection
~~~~~~~~~~~~~~~~~~~~~~

1. **Verify certification**:

   - Check motor is certified for your organization (NAR/TRA)
   - Verify you have appropriate certification level

2. **Check availability**:

   - Motor in stock at vendors
   - Shipping restrictions to your location

3. **Structural analysis**:

   .. code-block:: python
   
      # Check max thrust vs. airframe strength
      max_thrust_n = 2200  # From motor specs
      airframe_area_m2 = 0.0127  # π × (0.0635)²
      
      thrust_stress_pa = max_thrust_n / airframe_area_m2
      
      # Compare to material strength
      # Fiberglass: ~300 MPa (300,000,000 Pa)
      safety_factor = 300_000_000 / thrust_stress_pa
      
      print(f"Safety factor: {safety_factor:.1f}")
      # Should be > 5 for amateur rocketry

4. **Thermal analysis**:

   - Check motor ejection charge won't damage recovery system
   - Verify motor mount can handle heat

Common Motor Selection Mistakes
--------------------------------

Mistake 1: Choosing Too Powerful
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** M2500 motor in 5 kg rocket → 50g acceleration → electronics failure

**Solution:** Calculate max acceptable acceleration BEFORE selecting motor

.. code-block:: python

   max_safe_accel_g = 20  # For your electronics
   rocket_mass_kg = 10
   
   max_thrust_n = max_safe_accel_g * 9.81 * rocket_mass_kg
   print(f"Max thrust: {max_thrust_n:.0f} N")
   # Don't exceed this thrust!

Mistake 2: Ignoring Burn Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Very short burn (< 1s) → all acceleration near pad → unstable

**Solution:** Prefer moderate thrust, longer burn (1.5-3s typical)

Mistake 3: Not Accounting for Wind
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** High apogee + long descent = 2 km drift

**Solution:** Consider dual-deploy or choose motor for lower apogee on windy days

Quick Reference Chart
---------------------

**Rocket Mass vs. Motor Class:**

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25
   
   * - Rocket Mass
     - Low Flight (500m)
     - Sport (1500m)
     - High (3000m)
   * - 0.5 kg
     - F-G
     - H-I
     - J-K
   * - 2.0 kg
     - H-I
     - J-K
     - L-M
   * - 5.0 kg
     - I-J
     - K-L
     - M-N
   * - 10.0 kg
     - J-K
     - L-M
     - N-O

.. seealso::

   - `ThrustCurve.org Motor Search <https://www.thrustcurve.org/motorsearch.jsp>`_
   - :ref:`tutorial_custom_motor` - Using motor data files
   - :ref:`howto_validate_design` - Verify your selection
