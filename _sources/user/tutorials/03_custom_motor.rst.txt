.. _tutorial_custom_motor:

Using Custom Motor Data
========================

While ``rocket-sim`` includes some motor thrust curves, you'll often need to use motors specific to your rocket. This tutorial teaches you how to import custom motor thrust curves from various sources and validate the data for accurate simulations.

.. note::
   
   This tutorial assumes you've completed :ref:`tutorial_basic_flight`. We'll build upon the basic configuration to use a custom motor.

Motor Data Formats
------------------

``rocket-sim`` (via RocketPy) supports two primary thrust curve formats:

1. **RASP .eng files** - Industry standard format from ThrustCurve.org
2. **CSV files** - Custom thrust data in simple text format

RASP .eng Format
~~~~~~~~~~~~~~~~

The RASP .eng format is the most common thrust curve format, used by thousands of commercially available motors. It's supported by:

- `ThrustCurve.org <https://www.thrustcurve.org/>`_ - Database of commercial motors
- Motor manufacturers (Cesaroni, AeroTech, etc.)
- Test stand software (many data loggers export to .eng)

**File structure:**

.. code-block:: text

   ; Motor Name and Metadata
   MotorName Diameter Length Propellant TotalWeight PropellantWeight Manufacturer
      time1 thrust1
      time2 thrust2
      ...
      timeN thrustN

**Example** (``Cesaroni_7579M1520-P.eng``):

.. code-block:: text

   ; Pro98-3G 7579M1520-BS P
   M1520-BS 98 548 P 3.737 6.718 CTI
      0.04 1427.795
      0.082 1706.389
      0.176 1620.489
      0.748 1734.249
      1.652 1827.113
      2.676 1715.676
      3.89 1423.152
      4.399 1404.579
      4.616 661.661
      4.877 69.649
      4.897 0.0

**Header fields:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65
   
   * - Field
     - Units
     - Description
   * - MotorName
     - —
     - Designation (e.g., M1520-BS)
   * - Diameter
     - mm
     - Motor case outer diameter
   * - Length
     - mm
     - Motor case length
   * - Propellant
     - —
     - Propellant type code
   * - TotalWeight
     - kg
     - Loaded motor weight
   * - PropellantWeight
     - kg
     - Propellant mass only
   * - Manufacturer
     - —
     - Manufacturer code (CTI, AT, etc.)

**Data columns:**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60
   
   * - Column
     - Units
     - Description
   * - Time
     - seconds
     - Time from ignition
   * - Thrust
     - Newtons
     - Thrust force at this time point

.. tip::
   
   **Where to find .eng files:**
   
   1. **ThrustCurve.org** - Search by motor designation, download .eng file
   2. **Manufacturer websites** - Often provide thrust curves for their motors
   3. **Motor testing** - Export from your own static test stand data

CSV Format
~~~~~~~~~~

For custom motors or test stand data, you can use CSV format with time-thrust pairs:

**Simple format** (time, thrust):

.. code-block:: csv

   # Custom Motor Thrust Curve
   # Time (s), Thrust (N)
   0.0, 0.0
   0.1, 450.5
   0.5, 1200.8
   1.5, 1450.2
   2.5, 1380.6
   3.0, 890.3
   3.5, 120.7
   3.6, 0.0

**Rules for CSV files:**

- First column: time in seconds
- Second column: thrust in Newtons
- Lines starting with ``#`` are comments (optional)
- Must start at t=0 and end when thrust reaches zero
- Data points should be evenly spaced for best interpolation

Tutorial: Using a ThrustCurve.org Motor
---------------------------------------

Let's download and use a real motor from ThrustCurve.org.

Step 1: Find Your Motor
~~~~~~~~~~~~~~~~~~~~~~~~

1. Visit `thrustcurve.org/simfilesearch.jsp <https://www.thrustcurve.org/simfilesearch.jsp>`_
2. Search for your motor (e.g., "Cesaroni M1520")
3. Click on your motor in the results
4. Click "Download RASAero (.eng)" button
5. Save the ``.eng`` file to ``data/motors/`` in your project

.. image:: /_static/images/thrustcurve_download.png
   :alt: Downloading motor file from ThrustCurve.org
   :width: 600px
   :align: center

.. note::
   
   If the image is not available, simply:
   
   1. Search for your motor on ThrustCurve.org
   2. Look for the "Download" or "Simfiles" section
   3. Download the .eng format file

Step 2: Inspect the File
~~~~~~~~~~~~~~~~~~~~~~~~~

Before using the motor, verify the file contents:

.. code-block:: bash

   cat data/motors/Cesaroni_7579M1520-P.eng

Check that:

✅ File has header line with motor name and parameters

✅ Thrust data starts at time = 0

✅ Thrust data ends at approximately zero thrust

✅ No negative thrust values

✅ No missing data points or corrupted lines

Step 3: Configure Your Motor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create or modify your YAML configuration file (``configs/my_custom_motor.yaml``):

.. code-block:: yaml

   # Motor configuration with custom thrust curve
   motor:
     type: "SolidMotor"
     
     # Path to your custom thrust curve
     thrust_source: "data/motors/Cesaroni_7579M1520-P.eng"
     
     # Coordinate system (see below for explanation)
     coordinate_system_orientation: "nozzle_to_combustion_chamber"
     
     # Dry mass (motor hardware without propellant)
     dry_mass_kg: 1.815
     
     # Nozzle dimensions
     nozzle_radius_m: 0.033
     throat_radius_m: 0.011
     
     # Grain geometry (5 cylindrical grains)
     grain_number: 5
     grain_density_kg_m3: 1815
     grain_outer_radius_m: 0.033
     grain_initial_inner_radius_m: 0.015
     grain_initial_height_m: 0.120
     grain_separation_m: 0.005
     
     # Positions (in motor coordinate system)
     nozzle_position_m: 0.0
     grains_center_of_mass_position_m: 0.317
     center_of_dry_mass_position_m: 0.317

.. important::
   
   **Key parameters to verify:**
   
   - ``thrust_source`` - Path must be correct (relative to project root)
   - ``dry_mass_kg`` - Motor case mass WITHOUT propellant
   - ``grain_density_kg_m3`` - Propellant density (typically 1600-1850 kg/m³)
   - Grain dimensions must match your actual motor

Understanding Coordinate Systems
---------------------------------

RocketPy motors use a local coordinate system for positioning components. Understanding this is crucial for correct simulation.

Motor Coordinate System Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option 1: ``nozzle_to_combustion_chamber`` (RECOMMENDED)**

Origin at the nozzle exit, positive direction toward combustion chamber:

.. code-block:: text

   Nozzle Exit                           Combustion Chamber
        |                                        |
        |<-------- Motor Length ---------------->|
        0         Grains CoM              Dry CoM
        |             |                      |
        +-------------+----------------------+
        
   Position values are POSITIVE, measured from nozzle

**Option 2: ``combustion_chamber_to_nozzle``**

Origin at combustion chamber end, positive direction toward nozzle:

.. code-block:: text

   Combustion Chamber                     Nozzle Exit
        |                                        |
        |<-------- Motor Length ---------------->|
     Dry CoM      Grains CoM                     0
        |             |                          |
        +-------------+-------------------------+
        
   Position values are POSITIVE, measured from chamber

**Which to use?**

- Use ``nozzle_to_combustion_chamber`` for consistency with most motor documentation
- Ensures positive position values (easier to verify)
- Matches typical motor diagrams

Position Parameters Explained
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 35 65
   
   * - Parameter
     - Description
   * - ``nozzle_position_m``
     - Position of nozzle exit (typically 0.0)
   * - ``grains_center_of_mass_position_m``
     - Distance from nozzle to grains CoM
   * - ``center_of_dry_mass_position_m``
     - Distance from nozzle to dry mass CoM (empty motor)

**How to determine positions:**

1. **Nozzle position**: Almost always 0.0 (reference point)
2. **Grains CoM**: Measure from nozzle to center of propellant stack
3. **Dry mass CoM**: Often approximately at motor case center

.. tip::
   
   If you don't have exact CoM measurements:
   
   - **Grains CoM**: Assume at geometric center of grain stack
   - **Dry mass CoM**: Assume at geometric center of motor case
   
   These approximations are usually sufficient for preliminary designs.

Tutorial: Creating CSV Thrust Curve
------------------------------------

For custom motors or test stand data, you can create CSV thrust curves.

Step 1: Collect Thrust Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sources of thrust data:

- **Static test stand** - Measured from your motor firing
- **Simulation software** - ProPep, MotorSim, etc.
- **Manufacturer data** - Sometimes provided as tables
- **Literature** - Research papers on propellant formulations

Step 2: Format as CSV
~~~~~~~~~~~~~~~~~~~~~~

Create ``data/motors/custom_motor.csv``:

.. code-block:: csv

   # Custom K-class motor thrust curve
   # Static test: 2025-10-15
   # Propellant: KNDX
   # Total impulse: ~1500 N·s
   #
   # Time (s), Thrust (N)
   0.0, 0.0
   0.05, 180.5
   0.10, 520.3
   0.20, 850.7
   0.50, 950.2
   1.00, 940.8
   1.50, 920.4
   2.00, 880.6
   2.50, 820.3
   3.00, 720.8
   3.50, 580.2
   4.00, 380.5
   4.50, 150.3
   4.80, 50.2
   5.00, 0.0

.. warning::
   
   **Critical CSV requirements:**
   
   - ✅ First point must be at t=0
   - ✅ Last point must have thrust ≈ 0
   - ✅ Time must be monotonically increasing
   - ✅ No negative thrust values
   - ✅ Units: seconds and Newtons (not milliseconds, not pounds)

Step 3: Configure Motor
~~~~~~~~~~~~~~~~~~~~~~~~

In your YAML configuration:

.. code-block:: yaml

   motor:
     type: "SolidMotor"
     thrust_source: "data/motors/custom_motor.csv"
     
     # Note: For CSV, you MUST provide burn_time explicitly
     burn_time_s: 5.0  # Match the last time point in CSV
     
     # ... rest of motor parameters ...

.. important::
   
   When using CSV files, ``burn_time_s`` is **required** because CSV files don't include motor metadata like .eng files do.

Validating Motor Data
----------------------

After configuring your motor, validate it before running full simulations.

Quick Validation Script
~~~~~~~~~~~~~~~~~~~~~~~~

Create ``scripts/validate_motor.py``:

.. code-block:: python

   #!/usr/bin/env python3
   """Quick motor validation script."""
   
   import sys
   from pathlib import Path
   
   sys.path.insert(0, str(Path(__file__).parent.parent))
   
   from src.config_loader import ConfigLoader
   from src.motor_builder import MotorBuilder
   
   # Load configuration
   loader = ConfigLoader()
   loader.load_from_yaml("configs/my_custom_motor.yaml")
   motor_config = loader.get_motor_config()
   
   # Build motor
   builder = MotorBuilder(motor_config)
   motor = builder.build()
   
   # Print summary
   print("\n" + "=" * 60)
   print("MOTOR VALIDATION SUMMARY")
   print("=" * 60)
   
   summary = builder.get_summary()
   
   print(f"\nPerformance:")
   print(f"  Total Impulse:    {summary['total_impulse_ns']:.0f} N·s")
   print(f"  Average Thrust:   {summary['average_thrust_n']:.0f} N")
   print(f"  Max Thrust:       {summary['max_thrust_n']:.0f} N")
   print(f"  Burn Time:        {summary['burn_time_s']:.2f} s")
   
   print(f"\nMass Properties:")
   print(f"  Propellant Mass:  {summary['propellant_mass_kg']:.3f} kg")
   print(f"  Total Mass:       {summary['total_mass_kg']:.3f} kg")
   
   print(f"\nMotor Classification:")
   # Classify motor by total impulse
   impulse = summary['total_impulse_ns']
   if impulse < 160:
       class_letter = "G or lower"
   elif impulse < 320:
       class_letter = "H"
   elif impulse < 640:
       class_letter = "I"
   elif impulse < 1280:
       class_letter = "J"
   elif impulse < 2560:
       class_letter = "K"
   elif impulse < 5120:
       class_letter = "L"
   elif impulse < 10240:
       class_letter = "M"
   elif impulse < 20480:
       class_letter = "N"
   else:
       class_letter = "O or higher"
   
   print(f"  Class:            {class_letter}")
   print(f"  Avg Thrust:       {summary['average_thrust_n']:.0f} N")
   print(f"  Designation:      {class_letter}{int(summary['average_thrust_n'])}")
   
   print("\n✓ Motor validated successfully!\n")

Run validation:

.. code-block:: bash

   python scripts/validate_motor.py

Expected output:

.. code-block:: text

   ============================================================
   MOTOR VALIDATION SUMMARY
   ============================================================
   
   Performance:
     Total Impulse:    5467 N·s
     Average Thrust:   2189 N
     Max Thrust:       2663 N
     Burn Time:        2.50 s
   
   Mass Properties:
     Propellant Mass:  2.956 kg
     Total Mass:       4.771 kg
   
   Motor Classification:
     Class:            M
     Avg Thrust:       2189 N
     Designation:      M2189
   
   ✓ Motor validated successfully!

Visual Validation
~~~~~~~~~~~~~~~~~

RocketPy motors have built-in plotting capabilities. Add to your validation script:

.. code-block:: python

   # Plot thrust curve
   motor.plots.thrust()
   
   # Plot total mass over time
   motor.plots.total_mass()
   
   # Plot center of mass over time
   motor.plots.center_of_mass()

This generates plots showing:

- **Thrust curve** - Verify shape matches expectations
- **Mass over time** - Should decrease smoothly as propellant burns
- **Center of mass** - Should shift as propellant burns

Common Motor Issues and Solutions
----------------------------------

Issue 1: Thrust Curve File Not Found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error:**

.. code-block:: text

   FileNotFoundError: Thrust curve file not found: data/motors/my_motor.eng

**Solutions:**

1. Check file path is correct relative to project root
2. Verify file exists: ``ls -la data/motors/my_motor.eng``
3. Check for typos in filename (case-sensitive on Linux/Mac)
4. Ensure file is in correct directory

Issue 2: Negative Thrust Values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error:**

.. code-block:: text

   ValueError: Thrust curve contains negative values

**Cause:** Test stand noise or data processing errors

**Solution:**

Clean your CSV data:

.. code-block:: python

   import pandas as pd
   
   # Load data
   df = pd.read_csv('raw_thrust_data.csv', comment='#')
   
   # Remove negative thrust
   df['thrust'] = df['thrust'].clip(lower=0)
   
   # Save cleaned data
   df.to_csv('data/motors/cleaned_motor.csv', index=False)

Issue 3: Unrealistic Total Impulse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom:** Calculated total impulse doesn't match expected motor class

**Check:**

1. Verify thrust units are Newtons (not pounds-force)
2. Verify time units are seconds (not milliseconds)
3. Check grain geometry parameters are realistic
4. Validate propellant density (typically 1600-1850 kg/m³)

**Example conversion** (if data is in pounds-force):

.. code-block:: python

   # Convert lbf to N (1 lbf = 4.448222 N)
   df['thrust_n'] = df['thrust_lbf'] * 4.448222

Issue 4: Motor Class Mismatch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem:** Motor designated as "M1520" but calculations show different impulse

**Explanation:** Motor designations format: ``[Class][AvgThrust]``

- **Class letter** = Total impulse range
- **Number** = Average thrust in Newtons

Your calculations should approximately match the designation. Small differences (5-10%) are normal due to rounding.

Best Practices
--------------

1. **Always validate** motors before full simulations
2. **Keep original files** - Don't overwrite downloaded .eng files
3. **Document sources** - Add comments to CSV files noting data origin
4. **Version control** - Track motor files in git for reproducibility
5. **Test incrementally** - Validate motor → simple flight → full simulation
6. **Compare with manufacturer** - If available, verify calculated impulse matches specs

Advanced: Custom Interpolation
-------------------------------

RocketPy interpolates thrust curves for smooth simulation. You can control interpolation:

.. code-block:: yaml

   motor:
     # ... other parameters ...
     
     # Interpolation method: "linear" or "spline"
     interpolation_method: "linear"  # More conservative, avoids overshoot
     # interpolation_method: "spline"  # Smoother, may overshoot

**When to use linear:**

- Sparse data points (< 20 points)
- Noisy test stand data
- Thrust curves with sharp transitions

**When to use spline:**

- High-resolution data (> 50 points)
- Clean manufacturer data
- Smooth thrust profiles

Next Steps
----------

Now that you can use custom motors:

1. **Design fins** - Continue to :ref:`tutorial_adding_fins` to ensure stability
2. **Add recovery** - See :ref:`tutorial_recovery_system` for safe landings
3. **Compare motors** - Run simulations with different motors to optimize performance
4. **Build motor library** - Collect .eng files for all your available motors

.. seealso::
   
   - :ref:`configuration_motor_params` - Complete motor parameter reference
   - :ref:`howto_measure_rocket` - Measuring motor positions accurately
   - `ThrustCurve.org <https://www.thrustcurve.org/>`_ - Motor database
   - `RocketPy Motor Documentation <https://docs.rocketpy.org/en/latest/user/motors.html>`_ - Advanced motor features

Common Motor Sources
--------------------

Free .eng File Databases
~~~~~~~~~~~~~~~~~~~~~~~~~

- **ThrustCurve.org** - 6000+ commercial motors
- **RASP.org** - Original RASP engine database
- **Manufacturer websites** - Cesaroni, AeroTech, Loki, etc.

Motor Simulation Software
~~~~~~~~~~~~~~~~~~~~~~~~~~

For creating custom motor designs:

- **ProPep 3** - Professional propellant evaluation (free for students)
- **MotorSim** - Open-source solid motor design
- **SRM** - Solid rocket motor design tool

Static Test Stand Data Loggers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export .eng files directly:

- **RocketCertifier** - Commercial test stand software
- **AeroTech RATSv2** - RocketApp Test Stand software
- **DIY Arduino loggers** - Many export CSV that can be converted

Converting Other Formats
~~~~~~~~~~~~~~~~~~~~~~~~~

If you have thrust data in other formats:

**Excel to CSV:**

.. code-block:: python

   import pandas as pd
   
   df = pd.read_excel('motor_data.xlsx', usecols=['Time_s', 'Thrust_N'])
   df.to_csv('data/motors/converted_motor.csv', index=False, header=False)

**RASP to CSV:**

.. code-block:: python

   # Parse .eng file and export as CSV
   with open('motor.eng', 'r') as f:
       lines = f.readlines()
   
   # Skip header, extract time-thrust pairs
   data_lines = [l.strip() for l in lines[1:] if l.strip() and not l.startswith(';')]
   
   with open('motor.csv', 'w') as f:
       f.write('# time_s, thrust_n\n')
       for line in data_lines:
           f.write(line.replace(' ', ',') + '\n')
