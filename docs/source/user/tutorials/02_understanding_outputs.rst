.. _tutorial_understanding_outputs:

Understanding Simulation Outputs
=================================

After running a simulation, ``rocket-sim`` generates comprehensive output files organized in the ``outputs/<rocket_name>/`` directory. This tutorial explains the structure and contents of these outputs, helping you analyze your simulation results effectively.

.. note::
   
   This tutorial assumes you've already run your first simulation following :ref:`tutorial_basic_flight`. If not, run:
   
   .. code-block:: bash
   
      python scripts/run_single_simulation.py --config configs/templates/tutorial_rocket.yaml --name my_first_rocket

Output Directory Structure
---------------------------

After a successful simulation, you'll find the following structure:

.. code-block:: text

   outputs/
   └── my_first_rocket/              # Named after your rocket
       ├── initial_state              # Binary state file (Python pickle)
       ├── initial_state_READABLE.txt # Human-readable initial parameters
       ├── final_state                # Binary state file (Python pickle)
       ├── final_state_READABLE.txt   # Human-readable final results
       ├── my_first_rocket_log        # Simulation log (if --log-file used)
       ├── curves/                    # Motor and rocket curves
       │   └── (curve data files)
       ├── plots/                     # Visualization plots
       │   ├── my_first_rocket_altitude.png
       │   ├── my_first_rocket_velocity.png
       │   ├── my_first_rocket_acceleration.png
       │   ├── my_first_rocket_trajectory_2d.png
       │   └── my_first_rocket_trajectory_3d.png
       └── trajectory/                # Trajectory data
           ├── my_first_rocket_summary.json
           └── my_first_rocket_trajectory.csv

.. tip::
   
   The ``--name`` argument in the run command determines the output directory name. Use descriptive names like ``artemis``, ``test_flight_v3``, or ``nominal_flight`` to organize multiple simulations.

State Files
-----------

Initial and Final State (Binary)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Files:** ``initial_state`` and ``final_state``

These are Python pickle files containing the complete serialized state of your rocket, motor, and environment objects. They're primarily used for:

- Reloading simulation results without re-running
- Programmatic access to all simulation data
- Advanced post-processing with custom scripts

.. code-block:: python

   import pickle
   
   # Load the final state
   with open('outputs/my_first_rocket/final_state', 'rb') as f:
       rocket_state = pickle.load(f)
   
   # Access flight results
   flight = rocket_state['flight']
   print(f"Apogee: {flight.apogee:.2f} m")

.. warning::
   
   Binary state files are Python version-specific and may not work across different RocketPy versions. For long-term storage and sharing, use the READABLE.txt or JSON files instead.

Readable State Files
~~~~~~~~~~~~~~~~~~~~

**Files:** ``initial_state_READABLE.txt`` and ``final_state_READABLE.txt``

These comprehensive text files document all input parameters and simulation results in human-readable format. They're perfect for:

- Quick review of simulation setup and results
- Including in reports and documentation
- Verifying input parameters
- Sharing results with team members

The ``final_state_READABLE.txt`` file is organized into sections:

**1. Motor Parameters**
   - Basic properties (type, coordinate system, dry mass)
   - Grain geometry (for solid motors)
   - Performance metrics (total impulse, average/max thrust, burn duration)
   - Inertia tensor

**2. Rocket Parameters**
   - Basic properties (radius, mass, coordinate system)
   - Center of mass positions (static and with motor)
   - Inertia tensor (with and without motor)
   - Aerodynamic surfaces (nose cone, fins, air brakes)
   - Parachute configurations
   - Stability margins

**3. Environment Parameters**
   - Launch location (latitude, longitude, elevation)
   - Atmospheric model configuration
   - Wind conditions

**4. Simulation Configuration**
   - Launch rail settings (length, inclination, heading)
   - Numerical integration parameters (rtol, atol, max time)

**5. Flight Results** ⭐
   - **Apogee:** Altitude, time, and position at highest point
   - **Maximum values:** Peak velocity, Mach number, and acceleration
   - **Rail exit:** Velocity and time when leaving the launch rail
   - **Impact:** Landing velocity, position, and distance from launch
   - **Flight duration:** Total time from launch to landing
   - **Events:** Parachute deployments and other flight events

Example excerpt:

.. code-block:: text

   FLIGHT RESULTS
   ================================================================================
   
   Apogee:
   ----------------------------------------
     Altitude:                    2299.94 m (7545.74 ft)
     Time:                        20.77 s
     Position X:                  -2.71 m
     Position Y:                  373.64 m
   
   Maximum Values:
   ----------------------------------------
     Velocity:                    240.72 m/s
     Mach Number:                 0.711
     Acceleration:                121.42 m/s² (12.38 g)
   
   Rail Exit:
   ----------------------------------------
     Velocity:                    18.20 m/s
     Time:                        0.18 s

Trajectory Data
---------------

Summary JSON
~~~~~~~~~~~~

**File:** ``trajectory/<rocket_name>_summary.json``

This JSON file contains key simulation results in a machine-readable format, ideal for:

- Automated analysis and comparison
- Integration with other software
- Creating custom dashboards
- Monte Carlo result aggregation

**Structure:**

.. code-block:: json

   {
     "simulation_config": {
       "rail_length_m": 1.5,
       "rail_inclination_deg": 85.0,
       "rail_heading_deg": 0.0,
       "max_time_s": 600.0,
       "rtol": 1e-06,
       "atol": 1e-06
     },
     "environment": {
       "latitude_deg": 39.3897,
       "longitude_deg": -8.2889,
       "elevation_m": 100.0
     },
     "rocket": {
       "mass_kg": 16.426,
       "radius_m": 0.0635
     },
     "flight_results": {
       "apogee_m": 2299.94,
       "apogee_time_s": 20.77,
       "max_velocity_ms": 240.72,
       "max_acceleration_ms2": 121.42,
       "flight_time_s": 404.52,
       "x_impact_m": -2.85,
       "y_impact_m": 405.26,
       "lateral_distance_m": 405.27
     }
   }

**Key fields:**

.. list-table::
   :header-rows: 1
   :widths: 25 15 60
   
   * - Field
     - Units
     - Description
   * - ``apogee_m``
     - meters
     - Maximum altitude above launch site elevation
   * - ``apogee_time_s``
     - seconds
     - Time from launch to apogee
   * - ``max_velocity_ms``
     - m/s
     - Peak velocity magnitude during flight
   * - ``max_acceleration_ms2``
     - m/s²
     - Peak acceleration (typically during motor burn)
   * - ``max_mach_number``
     - —
     - Peak Mach number (velocity/speed of sound)
   * - ``out_of_rail_velocity_ms``
     - m/s
     - Velocity when rocket leaves launch rail
   * - ``flight_time_s``
     - seconds
     - Total flight duration from launch to landing
   * - ``lateral_distance_m``
     - meters
     - Horizontal distance from launch point to landing
   * - ``x_impact_m``, ``y_impact_m``
     - meters
     - Landing coordinates (x=East, y=North)
   * - ``initial_stability_margin_calibers``
     - calibers
     - Static margin at launch (CoP - CoM distance)

Trajectory CSV
~~~~~~~~~~~~~~

**File:** ``trajectory/<rocket_name>_trajectory.csv``

This CSV file contains the complete time-series trajectory data at each integration step. Perfect for:

- Custom analysis with spreadsheet software (Excel, Google Sheets)
- Creating custom plots with Python, MATLAB, or R
- Detailed flight phase analysis
- Verifying simulation behavior

**Column structure:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65
   
   * - Column
     - Units
     - Description
   * - ``time_s``
     - seconds
     - Time from launch
   * - ``altitude_m``
     - meters
     - Altitude above sea level
   * - ``x_m``
     - meters
     - East position (positive = east)
   * - ``y_m``
     - meters
     - North position (positive = north)
   * - ``vx_ms``
     - m/s
     - East velocity component
   * - ``vy_ms``
     - m/s
     - North velocity component
   * - ``vz_ms``
     - m/s
     - Vertical velocity component (positive = up)
   * - ``ax_ms2``
     - m/s²
     - East acceleration component
   * - ``ay_ms2``
     - m/s²
     - North acceleration component
   * - ``az_ms2``
     - m/s²
     - Vertical acceleration component

**Example rows:**

.. code-block:: csv

   time_s,altitude_m,x_m,y_m,vx_ms,vy_ms,vz_ms,ax_ms2,ay_ms2,az_ms2
   0.0,100.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0
   0.175,100.0,0.0,0.36,0.0,0.07,0.8,9.6,9.6,109.7
   2.357,208.7,0.14,42.8,0.5,15.2,173.9,-0.6,-1.5,59.9
   20.77,2399.9,-2.7,373.6,-0.1,0.0,0.0,-0.01,-0.01,-9.8

.. tip::
   
   **Analyzing trajectory data with Python:**
   
   .. code-block:: python
   
      import pandas as pd
      import matplotlib.pyplot as plt
      
      # Load trajectory
      df = pd.read_csv('outputs/my_first_rocket/trajectory/my_first_rocket_trajectory.csv')
      
      # Calculate total velocity
      df['velocity_ms'] = (df['vx_ms']**2 + df['vy_ms']**2 + df['vz_ms']**2)**0.5
      
      # Plot velocity over time
      plt.figure(figsize=(10, 6))
      plt.plot(df['time_s'], df['velocity_ms'])
      plt.xlabel('Time (s)')
      plt.ylabel('Velocity (m/s)')
      plt.title('Rocket Velocity Profile')
      plt.grid(True)
      plt.show()

Visualization Plots
-------------------

The ``plots/`` directory contains automatically generated visualization plots:

Altitude Plot
~~~~~~~~~~~~~

**File:** ``<rocket_name>_altitude.png``

Shows altitude versus time with key events marked:

- Launch (t=0)
- Motor burnout
- Apogee
- Parachute deployment(s)
- Landing

This plot helps you quickly assess:

- Maximum altitude achieved
- Coasting phase duration
- Descent rate characteristics

Velocity Plot
~~~~~~~~~~~~~

**File:** ``<rocket_name>_velocity.png``

Displays velocity magnitude over time, showing:

- Rapid acceleration during motor burn
- Peak velocity (typically at burnout)
- Deceleration during coast
- Terminal velocity during descent

**Key observations:**

- **Rail exit velocity** should typically be >15 m/s for stable flight
- **Peak velocity** occurs near motor burnout
- **Descent velocity** should be <6-8 m/s for safe recovery

Acceleration Plot
~~~~~~~~~~~~~~~~~

**File:** ``<rocket_name>_acceleration.png``

Shows acceleration magnitude over time:

- **Motor burn phase:** High positive acceleration (may exceed 10g)
- **Coast phase:** Negative acceleration due to drag (typically -1 to -2g)
- **Descent phase:** Oscillates around zero as rocket reaches terminal velocity

.. warning::
   
   High accelerations (>15-20g) can damage electronics and payloads. If your simulation shows excessive acceleration, consider:
   
   - Using a motor with lower thrust
   - Increasing rocket mass
   - Redesigning for better weight distribution

2D Trajectory Plot
~~~~~~~~~~~~~~~~~~

**File:** ``<rocket_name>_trajectory_2d.png``

Top-down view showing horizontal displacement from launch point:

- X-axis: East-West displacement
- Y-axis: North-South displacement
- Markers indicate key events (apogee, landing)

Useful for:

- Assessing wind drift effects
- Planning recovery operations
- Understanding horizontal dispersion

3D Trajectory Plot
~~~~~~~~~~~~~~~~~~

**File:** ``<rocket_name>_trajectory_3d.png``

Complete 3D visualization with:

- X-axis: East-West position
- Y-axis: North-South position
- Z-axis: Altitude

This plot provides the most complete picture of the flight path, showing the combined effects of launch angle, wind drift, and gravity.

Practical Analysis Examples
----------------------------

Example 1: Quick Result Check
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After running a simulation, quickly check results:

.. code-block:: bash

   # Run simulation
   python scripts/run_single_simulation.py --config configs/single_sim/02_complete.yaml --name test_flight
   
   # View key results
   grep -A 10 "FLIGHT RESULTS" outputs/test_flight/final_state_READABLE.txt
   
   # Check apogee
   grep "Apogee:" outputs/test_flight/final_state_READABLE.txt

Example 2: Extract Data for Report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   
   # Load summary
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json', 'r') as f:
       results = json.load(f)
   
   # Extract for report
   flight = results['flight_results']
   
   print(f"""
   Flight Performance Summary
   ==========================
   Apogee:           {flight['apogee_m']:.1f} m ({flight['apogee_m']*3.28084:.0f} ft)
   Max Velocity:     {flight['max_velocity_ms']:.1f} m/s (Mach {flight['max_mach_number']:.3f})
   Max Acceleration: {flight['max_acceleration_ms2']:.1f} m/s² ({flight['max_acceleration_ms2']/9.81:.1f} g)
   Flight Time:      {flight['flight_time_s']:.1f} s ({flight['flight_time_s']/60:.1f} min)
   Landing Distance: {flight['lateral_distance_m']:.1f} m
   """)

Example 3: Compare Multiple Flights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   import pandas as pd
   
   # List of flight names to compare
   flights = ['baseline', 'heavier_rocket', 'longer_rail']
   
   # Collect results
   comparison = []
   for name in flights:
       with open(f'outputs/{name}/trajectory/{name}_summary.json', 'r') as f:
           data = json.load(f)
       
       comparison.append({
           'Flight': name,
           'Apogee (m)': data['flight_results']['apogee_m'],
           'Max Velocity (m/s)': data['flight_results']['max_velocity_ms'],
           'Rail Exit Velocity (m/s)': data['flight_results']['out_of_rail_velocity_ms'],
           'Flight Time (s)': data['flight_results']['flight_time_s']
       })
   
   # Create comparison table
   df = pd.DataFrame(comparison)
   print(df.to_string(index=False))

**Output:**

.. code-block:: text

             Flight  Apogee (m)  Max Velocity (m/s)  Rail Exit Velocity (m/s)  Flight Time (s)
           baseline     2299.94              240.72                     18.20           404.52
     heavier_rocket     2105.33              228.41                     17.15           387.21
        longer_rail     2301.12              240.81                     19.45           404.78

Example 4: Analyze Trajectory Phases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   
   # Load trajectory
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Calculate velocity magnitude
   df['velocity'] = (df['vx_ms']**2 + df['vy_ms']**2 + df['vz_ms']**2)**0.5
   
   # Identify motor burnout (when acceleration drops significantly)
   df['acceleration'] = (df['ax_ms2']**2 + df['ay_ms2']**2 + df['az_ms2']**2)**0.5
   burnout_idx = df[df['acceleration'] < 20].index[0]
   burnout_time = df.loc[burnout_idx, 'time_s']
   burnout_alt = df.loc[burnout_idx, 'altitude_m']
   
   # Find apogee
   apogee_idx = df['altitude_m'].idxmax()
   apogee_time = df.loc[apogee_idx, 'time_s']
   apogee_alt = df.loc[apogee_idx, 'altitude_m']
   
   print(f"""
   Flight Phase Analysis
   =====================
   Motor Burn Phase:
     Duration:     {burnout_time:.2f} s
     End Altitude: {burnout_alt:.1f} m
     End Velocity: {df.loc[burnout_idx, 'velocity']:.1f} m/s
   
   Coast Phase:
     Duration:     {apogee_time - burnout_time:.2f} s
     Altitude Gain: {apogee_alt - burnout_alt:.1f} m
   """)

Understanding Output Units
---------------------------

All outputs use **SI units** consistently:

.. list-table::
   :header-rows: 1
   :widths: 30 20 50
   
   * - Quantity
     - Unit
     - Notes
   * - Length/Distance/Altitude
     - meters (m)
     - Some READABLE files show feet in parentheses
   * - Velocity
     - meters/second (m/s)
     - 
   * - Acceleration
     - meters/second² (m/s²)
     - g-forces shown in parentheses (1g = 9.81 m/s²)
   * - Time
     - seconds (s)
     - Minutes shown in parentheses for flight duration
   * - Mass
     - kilograms (kg)
     - 
   * - Angles
     - degrees (°)
     - Launch rail angles, fin cant angles
   * - Coordinates (lat/lon)
     - decimal degrees (°)
     - WGS84 datum
   * - Mach Number
     - dimensionless
     - velocity / speed of sound

Common Analysis Tasks
---------------------

Verify Stability
~~~~~~~~~~~~~~~~

Check ``initial_stability_margin_calibers`` in the summary JSON or READABLE file:

- **< 1.0:** Unstable - rocket may tumble
- **1.0-2.0:** Stable - recommended range
- **> 3.0:** Over-stable - may weathercock excessively

Rail Exit Velocity Check
~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure ``out_of_rail_velocity_ms`` is adequate:

- **Minimum:** 15 m/s for small rockets
- **Recommended:** 20-25 m/s for reliable flight
- **If too low:** Increase rail length or use more powerful motor

Landing Velocity Assessment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check ``impact_velocity_ms`` for safe recovery:

- **< 5 m/s:** Very safe landing
- **5-8 m/s:** Safe for most rockets with proper padding
- **> 10 m/s:** Risk of damage - consider larger parachute

Next Steps
----------

Now that you understand the output structure, you can:

1. **Run parameter studies** - Vary design parameters and compare results
2. **Optimize performance** - Use outputs to improve apogee, stability, or safety
3. **Learn Monte Carlo** - Continue to :ref:`tutorial_monte_carlo_basics` to handle uncertainties
4. **Create custom analysis** - Build your own analysis scripts using the CSV and JSON data

.. seealso::
   
   - :ref:`configuration_simulation_params` - Understanding rtol/atol and integration settings
   - :ref:`howto_measure_rocket` - Measuring parameters accurately
   - :ref:`tutorial_monte_carlo_basics` - Handling measurement uncertainties
