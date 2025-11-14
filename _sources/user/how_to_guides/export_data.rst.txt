.. _howto_export_data:

Export Simulation Data
=======================

This guide shows you how to export simulation results in various formats for analysis, reporting, and sharing.

.. admonition:: Quick Answer
   :class: tip
   
   Simulation data is automatically exported to ``outputs/<rocket_name>/`` in multiple formats (CSV, JSON, plots).

Available Export Formats
------------------------

Automatic Exports
~~~~~~~~~~~~~~~~~

Every simulation automatically creates:

1. **JSON Summary** - ``trajectory/<name>_summary.json``
2. **CSV Trajectory** - ``trajectory/<name>_trajectory.csv``
3. **Readable State** - ``final_state_READABLE.txt``
4. **Binary State** - ``final_state`` (Python pickle)
5. **PNG Plots** - ``plots/<name>_*.png``

Export Locations
----------------

Default Structure
~~~~~~~~~~~~~~~~~

.. code-block:: text

   outputs/
   └── my_rocket/
       ├── final_state                           # Binary (pickle)
       ├── final_state_READABLE.txt              # Human-readable
       ├── initial_state
       ├── initial_state_READABLE.txt
       ├── my_rocket_log                         # Log file (if --log-file)
       ├── curves/                               # Motor/rocket curves
       ├── plots/                                # Visualization
       │   ├── my_rocket_altitude.png
       │   ├── my_rocket_velocity.png
       │   ├── my_rocket_acceleration.png
       │   ├── my_rocket_trajectory_2d.png
       │   └── my_rocket_trajectory_3d.png
       └── trajectory/                           # Numerical data
           ├── my_rocket_summary.json
           └── my_rocket_trajectory.csv

Exporting Specific Data
------------------------

Method 1: Use JSON Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best for:** Reports, dashboards, quick analysis

.. code-block:: python

   import json
   
   # Load summary
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json') as f:
       data = json.load(f)
   
   # Extract specific results
   apogee = data['flight_results']['apogee_m']
   max_velocity = data['flight_results']['max_velocity_ms']
   
   print(f"Apogee: {apogee:.1f} m")
   print(f"Max velocity: {max_velocity:.1f} m/s")

**Available fields:**

.. code-block:: python

   # Simulation configuration
   data['simulation_config']  # Rail, integration params
   data['environment']         # Launch site
   data['rocket']              # Basic rocket info
   
   # Flight results
   results = data['flight_results']
   results['apogee_m']
   results['apogee_time_s']
   results['max_velocity_ms']
   results['max_acceleration_ms2']
   results['flight_time_s']
   results['x_impact_m']
   results['y_impact_m']
   results['lateral_distance_m']
   # ... and more

Method 2: Use CSV Trajectory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best for:** Detailed analysis, custom plots, spreadsheets

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Load trajectory
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Available columns:
   # time_s, altitude_m, x_m, y_m,
   # vx_ms, vy_ms, vz_ms,
   # ax_ms2, ay_ms2, az_ms2
   
   # Plot altitude vs. time
   plt.figure(figsize=(10, 6))
   plt.plot(df['time_s'], df['altitude_m'])
   plt.xlabel('Time (s)')
   plt.ylabel('Altitude (m)')
   plt.title('Rocket Trajectory')
   plt.grid(True)
   plt.savefig('my_custom_plot.png', dpi=300)

Method 3: Parse Readable State
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Best for:** Human review, reports

.. code-block:: bash

   # Extract specific sections
   grep -A 20 "FLIGHT RESULTS" outputs/my_rocket/final_state_READABLE.txt > flight_summary.txt
   
   # Get apogee info
   grep "Apogee:" outputs/my_rocket/final_state_READABLE.txt
   
   # Get motor performance
   grep -A 10 "Performance:" outputs/my_rocket/final_state_READABLE.txt

Custom Export Formats
---------------------

Export to Excel
~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   
   # Load trajectory
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Calculate additional fields
   df['velocity_mag'] = (df['vx_ms']**2 + df['vy_ms']**2 + df['vz_ms']**2)**0.5
   df['acceleration_mag'] = (df['ax_ms2']**2 + df['ay_ms2']**2 + df['az_ms2']**2)**0.5
   
   # Export to Excel
   with pd.ExcelWriter('trajectory_analysis.xlsx') as writer:
       df.to_excel(writer, sheet_name='Trajectory', index=False)
       
       # Add summary sheet
       summary = {
           'Metric': ['Apogee (m)', 'Max Velocity (m/s)', 'Flight Time (s)'],
           'Value': [df['altitude_m'].max(), df['velocity_mag'].max(), df['time_s'].max()]
       }
       pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)

Export to KML (Google Earth)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import simplekml
   import pandas as pd
   import json
   
   # Load data
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json') as f:
       data = json.load(f)
   
   # Create KML
   kml = simplekml.Kml()
   
   # Launch site
   launch_lat = data['environment']['latitude_deg']
   launch_lon = data['environment']['longitude_deg']
   launch_elev = data['environment']['elevation_m']
   
   kml.newpoint(name="Launch Site", 
                coords=[(launch_lon, launch_lat, launch_elev)])
   
   # Trajectory path (simplified - every 10th point)
   coords = []
   for idx in range(0, len(df), 10):
       row = df.iloc[idx]
       # Convert x,y to lat/lon (approximate)
       lat = launch_lat + (row['y_m'] / 111320)
       lon = launch_lon + (row['x_m'] / (111320 * np.cos(np.radians(launch_lat))))
       alt = row['altitude_m']
       coords.append((lon, lat, alt))
   
   linestring = kml.newlinestring(name="Flight Path")
   linestring.coords = coords
   linestring.altitudemode = simplekml.AltitudeMode.absolute
   linestring.style.linestyle.color = simplekml.Color.red
   linestring.style.linestyle.width = 3
   
   # Apogee marker
   apogee_idx = df['altitude_m'].idxmax()
   apogee_row = df.iloc[apogee_idx]
   apogee_lat = launch_lat + (apogee_row['y_m'] / 111320)
   apogee_lon = launch_lon + (apogee_row['x_m'] / (111320 * np.cos(np.radians(launch_lat))))
   
   pnt = kml.newpoint(name="Apogee", 
                      coords=[(apogee_lon, apogee_lat, apogee_row['altitude_m'])])
   pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/flag.png'
   
   # Save
   kml.save("trajectory.kml")

Export for Reports
~~~~~~~~~~~~~~~~~~

Create publication-quality output:

.. code-block:: python

   import json
   import pandas as pd
   from datetime import datetime
   
   def generate_report(output_dir, report_file='flight_report.md'):
       """Generate Markdown report from simulation."""
       
       # Load data
       summary_file = f'{output_dir}/trajectory/{output_dir.split("/")[-1]}_summary.json'
       with open(summary_file) as f:
           data = json.load(f)
       
       results = data['flight_results']
       
       # Create report
       report = f"""
   # Flight Simulation Report
   
   **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
   
   ## Rocket Configuration
   
   - Mass: {data['rocket']['mass_kg']:.2f} kg
   - Diameter: {data['rocket']['radius_m']*2*1000:.0f} mm
   
   ## Launch Site
   
   - Latitude: {data['environment']['latitude_deg']:.4f}°
   - Longitude: {data['environment']['longitude_deg']:.4f}°
   - Elevation: {data['environment']['elevation_m']:.0f} m ASL
   
   ## Flight Performance
   
   | Metric | Value |
   |--------|-------|
   | **Apogee** | {results['apogee_m']:.1f} m ({results['apogee_m']*3.28084:.0f} ft) |
   | **Apogee Time** | {results['apogee_time_s']:.1f} s |
   | **Max Velocity** | {results['max_velocity_ms']:.1f} m/s (Mach {results['max_mach_number']:.3f}) |
   | **Max Acceleration** | {results['max_acceleration_ms2']:.1f} m/s² ({results['max_acceleration_ms2']/9.81:.1f} g) |
   | **Flight Time** | {results['flight_time_s']:.1f} s ({results['flight_time_s']/60:.1f} min) |
   | **Landing Distance** | {results['lateral_distance_m']:.0f} m |
   
   ## Stability
   
   - Initial Stability Margin: {results['initial_stability_margin_calibers']:.2f} calibers
   - Rail Exit Velocity: {results['out_of_rail_velocity_ms']:.1f} m/s
   
   ## Recovery
   
   - Impact Velocity: {abs(results['impact_velocity_ms']):.1f} m/s
   - Landing Position: ({results['x_impact_m']:.1f}, {results['y_impact_m']:.1f}) m
   
   ---
   
   *Generated by rocket-sim*
   """
       
       with open(report_file, 'w') as f:
           f.write(report)
       
       print(f"Report saved to {report_file}")
   
   # Usage
   generate_report('outputs/my_rocket')

Batch Export
------------

Export Multiple Simulations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   import pandas as pd
   from pathlib import Path
   
   def batch_export(output_dirs, export_file='comparison.csv'):
       """Export multiple simulation results to CSV."""
       
       results = []
       
       for output_dir in output_dirs:
           # Get simulation name
           name = Path(output_dir).name
           
           # Load summary
           summary_file = Path(output_dir) / 'trajectory' / f'{name}_summary.json'
           
           with open(summary_file) as f:
               data = json.load(f)
           
           flight = data['flight_results']
           
           results.append({
               'Name': name,
               'Apogee (m)': flight['apogee_m'],
               'Max Velocity (m/s)': flight['max_velocity_ms'],
               'Max Accel (g)': flight['max_acceleration_ms2'] / 9.81,
               'Flight Time (s)': flight['flight_time_s'],
               'Landing Distance (m)': flight['lateral_distance_m'],
               'Stability Margin': flight['initial_stability_margin_calibers']
           })
       
       # Create DataFrame
       df = pd.DataFrame(results)
       
       # Export
       df.to_csv(export_file, index=False)
       print(f"Exported {len(results)} simulations to {export_file}")
       
       return df
   
   # Usage
   simulations = [
       'outputs/baseline',
       'outputs/motor_test_1',
       'outputs/motor_test_2',
       'outputs/fin_test_1'
   ]
   
   df = batch_export(simulations)
   print(df)

Export for External Tools
--------------------------

OpenRocket Format
~~~~~~~~~~~~~~~~~

Convert simulation to OpenRocket-compatible CSV:

.. code-block:: python

   import pandas as pd
   
   # Load trajectory
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # OpenRocket format
   openrocket = pd.DataFrame({
       'Time (s)': df['time_s'],
       'Altitude (m)': df['altitude_m'],
       'Vertical velocity (m/s)': df['vz_ms'],
       'Vertical acceleration (m/s²)': df['az_ms2'],
       'Total velocity (m/s)': (df['vx_ms']**2 + df['vy_ms']**2 + df['vz_ms']**2)**0.5,
   })
   
   openrocket.to_csv('openrocket_export.csv', index=False)

MATLAB/Octave Format
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import scipy.io
   import pandas as pd
   import numpy as np
   
   # Load data
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Create MATLAB structure
   matlab_data = {
       'time': df['time_s'].values,
       'altitude': df['altitude_m'].values,
       'velocity': np.column_stack([df['vx_ms'], df['vy_ms'], df['vz_ms']]),
       'acceleration': np.column_stack([df['ax_ms2'], df['ay_ms2'], df['az_ms2']]),
       'position': np.column_stack([df['x_m'], df['y_m'], df['altitude_m']])
   }
   
   # Save as .mat file
   scipy.io.savemat('trajectory.mat', matlab_data)

Common Export Tasks
-------------------

Task 1: Create Quick Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # One-liner summary
   python -c "
   import json
   with open('outputs/my_rocket/trajectory/my_rocket_summary.json') as f:
       r = json.load(f)['flight_results']
   print(f\"Apogee: {r['apogee_m']:.0f}m, Max V: {r['max_velocity_ms']:.0f}m/s, Time: {r['flight_time_s']:.0f}s\")
   "

Task 2: Extract Time at Apogee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   apogee_idx = df['altitude_m'].idxmax()
   apogee_time = df.loc[apogee_idx, 'time_s']
   apogee_alt = df.loc[apogee_idx, 'altitude_m']
   
   print(f"Apogee: {apogee_alt:.1f} m at t={apogee_time:.2f} s")

Task 3: Export Flight Phases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   
   df = pd.read_csv('outputs/my_rocket/trajectory/my_rocket_trajectory.csv')
   
   # Calculate velocity magnitude
   df['v_mag'] = (df['vx_ms']**2 + df['vy_ms']**2 + df['vz_ms']**2)**0.5
   
   # Find phase transitions
   apogee_idx = df['altitude_m'].idxmax()
   
   # Export phases
   phases = {
       'ascent': df.iloc[:apogee_idx],
       'descent': df.iloc[apogee_idx:]
   }
   
   for phase_name, phase_data in phases.items():
       phase_data.to_csv(f'{phase_name}_phase.csv', index=False)
       print(f"Exported {phase_name}: {len(phase_data)} points")

.. seealso::

   - :ref:`tutorial_understanding_outputs` - Understanding output files
   - :ref:`howto_custom_plots` - Creating custom visualizations
   - :ref:`howto_data_analysis` - Advanced data analysis
