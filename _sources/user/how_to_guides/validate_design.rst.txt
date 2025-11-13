.. _howto_validate_design:

Validate Your Rocket Design
============================

This guide shows you how to verify that your rocket design is stable, safe, and ready to fly.

.. admonition:: Quick Answer
   :class: tip
   
   Run your simulation and check the stability margin is between 1.0 and 3.0 calibers.

Prerequisites
-------------

- Configuration file created
- Basic understanding of stability (see :ref:`tutorial_adding_fins`)

Validation Checklist
--------------------

Step 1: Check Stability Margin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run your simulation:

.. code-block:: bash

   python scripts/run_single_simulation.py --config configs/my_rocket.yaml --name validation_test

Check the results:

.. code-block:: bash

   grep "Stability" outputs/validation_test/final_state_READABLE.txt

**Expected output:**

.. code-block:: text

   Initial Stability Margin: 1.8 calibers  ✓
   Out-of-rail Stability: 1.9 calibers    ✓

**Stability criteria:**

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Stability Margin
     - Status
     - Action Required
   * - < 0.5 calibers
     - ❌ **UNSAFE**
     - Rocket will tumble - DO NOT FLY
   * - 0.5 - 1.0 calibers
     - ⚠️ **MARGINAL**
     - Increase fin size or add nose weight
   * - 1.0 - 2.5 calibers
     - ✅ **GOOD**
     - Ready to fly
   * - 2.5 - 3.5 calibers
     - ✅ **STABLE**
     - Good, may weathercock in wind
   * - > 3.5 calibers
     - ⚠️ **OVER-STABLE**
     - Consider reducing fin size

**If unstable (< 1.0):**

1. Increase fin span by 20%
2. Move fins closer to tail
3. Add weight to nose cone
4. Reduce motor size (lighter = CoM forward)

Step 2: Check Rail Exit Velocity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Find rail exit velocity:

.. code-block:: bash

   grep "Rail Exit" outputs/validation_test/final_state_READABLE.txt

**Expected:**

.. code-block:: text

   Rail Exit:
     Velocity:                    18.2 m/s  ✓

**Velocity criteria:**

- **< 15 m/s**: ❌ Too slow - fins not effective yet
- **15-20 m/s**: ⚠️ Marginal - increase rail length or motor
- **20-30 m/s**: ✅ Good - safe flight
- **> 30 m/s**: ✅ Excellent - very stable launch

**If too slow:**

1. Increase rail length (try 5m → 7m)
2. Use more powerful motor
3. Reduce rocket mass

Step 3: Validate Mass Distribution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check center of mass vs. center of pressure:

.. code-block:: bash

   grep -A 3 "Center of Mass" outputs/validation_test/final_state_READABLE.txt
   grep -A 3 "Center of Pressure" outputs/validation_test/final_state_READABLE.txt

**Expected pattern:**

.. code-block:: text

   Center of Mass (dry): 1.30 m from tail
   Center of Pressure:   2.10 m from tail
   
   Distance (CP - CoM):  0.80 m = 6.3 calibers ✓

CP must be **aft** (toward tail) of CoM!

Step 4: Check Landing Velocity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   grep "Impact" outputs/validation_test/final_state_READABLE.txt

**Expected:**

.. code-block:: text

   Impact:
     Velocity:                    -5.4 m/s  ✓

**Landing velocity criteria:**

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Landing Velocity
     - Status
     - Assessment
   * - < 5 m/s
     - ✅ **SAFE**
     - Minimal risk of damage
   * - 5-8 m/s
     - ✅ **ACCEPTABLE**
     - Safe with proper padding
   * - 8-12 m/s
     - ⚠️ **RISKY**
     - Risk of damage, increase chute size
   * - > 12 m/s
     - ❌ **UNSAFE**
     - Likely damage - increase parachute

**If too fast:**

1. Increase parachute Cd×S by 30%
2. Add second parachute
3. Check deployment altitude

Step 5: Verify Motor Performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check motor classification matches expectations:

.. code-block:: bash

   grep -A 10 "Performance:" outputs/validation_test/final_state_READABLE.txt

**Verify:**

- Total impulse matches motor designation
- Burn time is reasonable (not too short/long)
- Max thrust within structural limits

Quick Validation Script
-----------------------

Create ``scripts/quick_validate.py``:

.. code-block:: python

   #!/usr/bin/env python3
   """Quick validation of rocket design."""
   
   import sys
   import json
   from pathlib import Path
   
   def validate_rocket(output_dir):
       """Validate rocket from simulation output."""
       
       summary_file = Path(output_dir) / "trajectory" / f"{Path(output_dir).name}_summary.json"
       
       if not summary_file.exists():
           print(f"❌ Summary file not found: {summary_file}")
           return False
       
       with open(summary_file) as f:
           data = json.load(f)
       
       results = data['flight_results']
       
       # Validation checks
       checks = []
       
       # 1. Stability
       stability = results['initial_stability_margin_calibers']
       if stability < 1.0:
           checks.append(('❌', 'STABILITY', f'{stability:.2f} cal - UNSTABLE!'))
       elif stability > 3.5:
           checks.append(('⚠️', 'STABILITY', f'{stability:.2f} cal - Over-stable'))
       else:
           checks.append(('✅', 'STABILITY', f'{stability:.2f} cal - Good'))
       
       # 2. Rail exit velocity
       rail_v = results['out_of_rail_velocity_ms']
       if rail_v < 20:
           checks.append(('⚠️', 'RAIL EXIT', f'{rail_v:.1f} m/s - Low'))
       else:
           checks.append(('✅', 'RAIL EXIT', f'{rail_v:.1f} m/s - Good'))
       
       # 3. Landing velocity
       landing_v = abs(results['impact_velocity_ms'])
       if landing_v > 10:
           checks.append(('❌', 'LANDING', f'{landing_v:.1f} m/s - Too fast!'))
       elif landing_v > 7:
           checks.append(('⚠️', 'LANDING', f'{landing_v:.1f} m/s - Marginal'))
       else:
           checks.append(('✅', 'LANDING', f'{landing_v:.1f} m/s - Safe'))
       
       # 4. Apogee sanity
       apogee = results['apogee_m']
       if apogee < 100:
           checks.append(('⚠️', 'APOGEE', f'{apogee:.0f} m - Very low'))
       elif apogee > 10000:
           checks.append(('⚠️', 'APOGEE', f'{apogee:.0f} m - Very high'))
       else:
           checks.append(('✅', 'APOGEE', f'{apogee:.0f} m - Reasonable'))
       
       # Print results
       print("\n" + "="*60)
       print("ROCKET VALIDATION RESULTS")
       print("="*60)
       
       for icon, category, message in checks:
           print(f"{icon} {category:12} {message}")
       
       print("="*60)
       
       # Overall assessment
       failures = sum(1 for icon, _, _ in checks if icon == '❌')
       warnings = sum(1 for icon, _, _ in checks if icon == '⚠️')
       
       if failures > 0:
           print("❌ DESIGN NOT READY - Fix critical issues!")
           return False
       elif warnings > 0:
           print("⚠️ DESIGN MARGINAL - Review warnings")
           return True
       else:
           print("✅ DESIGN VALIDATED - Ready to fly!")
           return True
   
   if __name__ == "__main__":
       if len(sys.argv) < 2:
           print("Usage: python scripts/quick_validate.py outputs/my_rocket")
           sys.exit(1)
       
       success = validate_rocket(sys.argv[1])
       sys.exit(0 if success else 1)

**Usage:**

.. code-block:: bash

   python scripts/quick_validate.py outputs/my_rocket

Common Validation Failures
---------------------------

Problem: Unstable Rocket
~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Stability margin < 1.0 calibers

**Quick fixes:**

1. **Increase fin span**:

   .. code-block:: yaml
   
      fins:
        span_m: 0.12  # Was 0.10, increased 20%

2. **Move fins aft**:

   .. code-block:: yaml
   
      fins:
        position_m: 0.25  # Was 0.35, moved closer to tail

3. **Add nose weight**:

   .. code-block:: yaml
   
      rocket:
        dry_mass_kg: 9.0  # Was 8.5, added 500g to nose

Problem: Rail Exit Too Slow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Rail exit velocity < 20 m/s

**Quick fixes:**

1. **Longer rail**:

   .. code-block:: yaml
   
      simulation:
        rail:
          length_m: 6.0  # Was 4.0

2. **More powerful motor**:

   .. code-block:: yaml
   
      motor:
        thrust_source: "data/motors/Cesaroni_M1670.eng"  # Bigger motor

Problem: Landing Too Hard
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Impact velocity > 8 m/s

**Quick fix:**

.. code-block:: yaml

   parachute:
     cd_s: 10.0  # Was 6.0, increased by 67%

Best Practices
--------------

1. **Validate early and often** - Don't wait until build is complete
2. **Use conservative margins** - Target 1.5-2.0 caliber stability
3. **Document assumptions** - Note where you estimated parameters
4. **Compare with similar rockets** - Sanity check against proven designs
5. **Test incrementally** - Validate subsystems before full rocket

Pre-Flight Final Checks
------------------------

Before launch day:

.. code-block:: bash

   # 1. Re-validate with actual launch site elevation
   # 2. Check with expected day-of weather
   # 3. Verify all measurements are current
   # 4. Confirm parachute size matches actual chute

✅ **Final validation passed = Ready to build and fly!**

.. seealso::

   - :ref:`tutorial_adding_fins` - Understanding stability
   - :ref:`tutorial_recovery_system` - Parachute sizing
   - :ref:`howto_troubleshooting_simulation` - Debug simulation issues
