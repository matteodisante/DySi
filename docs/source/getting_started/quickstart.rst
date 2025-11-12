Quickstart: Your First Simulation
==================================

.. admonition:: What You'll Learn
   :class: tip

   By the end of this 5-minute tutorial, you will:
   
   * Run a complete rocket flight simulation
   * Understand the basic configuration structure
   * Generate trajectory plots and export data
   * Know where to customize parameters

Prerequisites
-------------

* Completed :doc:`installation`
* 5 minutes of time
* Basic familiarity with YAML (optional)

.. note::
   This tutorial uses the pre-configured minimal example. No code writing required!

Step 1: Navigate to Project Directory
--------------------------------------

Open a terminal and navigate to the rocket-sim directory:

.. code-block:: bash

   cd /path/to/rocket-sim

Activate your virtual environment if you created one:

.. tab-set::

   .. tab-item:: macOS/Linux

      .. code-block:: bash

         source venv/bin/activate

   .. tab-item:: Windows

      .. code-block:: batch

         venv\Scripts\activate

Step 2: Examine the Configuration File
---------------------------------------

Let's look at the minimal configuration file that defines our rocket:

.. code-block:: bash

   cat configs/single_sim/01_minimal.yaml

You'll see a YAML file with four main sections:

.. code-block:: yaml

   # Rocket physical parameters
   rocket:
     name: "Calisto"
     mass: 14.426        # kg (without motor)
     radius: 0.0635      # m
     # ... more parameters
   
   # Motor thrust curve and properties
   motor:
     thrust_source: "data/motors/Cesaroni_M1670.eng"
     dry_mass: 1.815     # kg
     # ... more parameters
   
   # Launch site and atmospheric conditions
   environment:
     latitude: 39.3897   # Spaceport America
     longitude: -8.2889
     elevation: 1400     # m
   
   # Launch angle and simulation settings
   simulation:
     inclination: 85     # degrees from horizontal
     heading: 90         # degrees (East)

.. tip::
   Don't worry about understanding every parameter yet. We'll cover them in :doc:`key_concepts`.

Step 3: Run Your First Simulation
----------------------------------

Execute the simulation with plotting enabled:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config configs/single_sim/01_minimal.yaml \
       --name my_first_rocket \
       --plots

**What's happening:**

* ``--config`` specifies which configuration file to use
* ``--name`` sets the output directory name (results go to ``outputs/my_first_rocket/``)
* ``--plots`` generates trajectory visualizations

Expected output:

.. code-block:: text

   ════════════════════════════════════════════════════════════════
                     ROCKET SIMULATION FRAMEWORK
   ════════════════════════════════════════════════════════════════
   
   [CONFIG] Loading configuration from: configs/single_sim/01_minimal.yaml
   [VALID] Configuration validation: PASSED
   
   [BUILD] Building Motor...
   [BUILD] Motor built successfully
   
   [BUILD] Building Environment...
   [BUILD] Environment built successfully
   
   [BUILD] Building Rocket...
   [BUILD] Rocket built successfully
   
   [SIM] Running flight simulation...
   [SIM] Simulation completed in 2.3s
   
   ┌─────────────────────────────────────────────────────────────┐
   │                    FLIGHT SUMMARY                           │
   ├─────────────────────────────────────────────────────────────┤
   │ Apogee Altitude:        3290.5 m                            │
   │ Apogee Time:            20.4 s                              │
   │ Max Velocity:           287.3 m/s                           │
   │ Max Acceleration:       89.2 m/s²                           │
   │ Impact Velocity:        5.2 m/s                             │
   │ Flight Time:            134.7 s                             │
   │ Ground Hit:             (420m, -1850m)                      │
   └─────────────────────────────────────────────────────────────┘
   
   [EXPORT] Exporting results to: outputs/my_first_rocket/
   [PLOT] Generating plots...
   [PLOT] Saved: trajectory_3d.png
   [PLOT] Saved: altitude_vs_time.png
   [PLOT] Saved: velocity_vs_time.png
   
   ✓ Simulation completed successfully!

Step 4: Explore the Results
----------------------------

Navigate to the output directory:

.. code-block:: bash

   cd outputs/my_first_rocket/
   ls -la

You'll find:

.. code-block:: text

   my_first_rocket/
   ├── plots/                          # Visualizations
   │   ├── trajectory_3d.png           # 3D flight path
   │   ├── altitude_vs_time.png        # Altitude profile
   │   ├── velocity_vs_time.png        # Velocity profile
   │   └── acceleration_vs_time.png    # Acceleration profile
   ├── trajectory/                     # Raw data
   │   ├── trajectory.csv              # Full trajectory data
   │   └── trajectory.kml              # Google Earth format
   ├── motor/                          # Motor state
   │   ├── motor_attributes.txt        # 35+ motor parameters
   │   └── curves/                     # Motor curve plots
   ├── rocket/                         # Rocket state
   │   └── rocket_attributes.txt       # Rocket configuration
   ├── final_state                     # Simulation end state
   └── initial_state                   # Simulation start state

**View the plots:**

.. tab-set::

   .. tab-item:: macOS

      .. code-block:: bash

         open plots/trajectory_3d.png

   .. tab-item:: Linux

      .. code-block:: bash

         xdg-open plots/trajectory_3d.png

   .. tab-item:: Windows

      .. code-block:: batch

         start plots\trajectory_3d.png

What You're Seeing
~~~~~~~~~~~~~~~~~~

The 3D trajectory plot shows:

* **Blue line**: Powered ascent (motor burning)
* **Red line**: Ballistic coast to apogee
* **Green line**: Parachute descent
* **Launch point**: Origin (0, 0, 0)
* **Impact point**: Where rocket lands

Step 5: Examine the Data
-------------------------

Let's look at the detailed trajectory data:

.. code-block:: bash

   head -20 trajectory/trajectory.csv

The CSV contains time-series data with columns:

.. code-block:: text

   time,x,y,z,vx,vy,vz,ax,ay,az,altitude,velocity,acceleration,...
   0.0,0.0,0.0,1400.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,...
   0.1,0.09,0.02,1400.5,0.87,0.15,4.9,8.7,1.5,49.1,0.5,5.0,50.2,...
   ...

You can import this into:

* **Excel/Google Sheets** for custom analysis
* **Python/MATLAB** for advanced processing
* **Plotting tools** for custom visualizations

Step 6: Customize Your Simulation
----------------------------------

Now let's modify some parameters. Open the configuration file:

.. code-block:: bash

   # Make a copy to experiment with
   cp configs/single_sim/01_minimal.yaml configs/my_custom_rocket.yaml
   
   # Edit with your preferred editor
   nano configs/my_custom_rocket.yaml  # or vim, code, etc.

**Try changing:**

* ``simulation.inclination: 80`` → Launch at different angle
* ``simulation.heading: 45`` → Launch northeast instead of east
* ``rocket.mass: 12.0`` → Make rocket lighter
* ``environment.elevation: 0`` → Launch from sea level

Run with your custom config:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config configs/my_custom_rocket.yaml \
       --name custom_test \
       --plots

.. warning::
   Some parameter changes may cause validation errors. Don't worry! The validator
   will tell you exactly what's wrong and suggest fixes.

What You've Learned
-------------------

Congratulations! You've successfully:

✅ Run a complete 6-DOF rocket trajectory simulation

✅ Generated publication-quality plots and data exports

✅ Understood the basic configuration structure

✅ Customized simulation parameters

Next Steps
----------

Now you're ready to:

1. **Understand the concepts** → :doc:`key_concepts`
   
   Learn what each configuration parameter actually means

2. **Explore complete configuration** → ``configs/single_sim/02_complete.yaml``
   
   See all available features (air brakes, weather data, custom drag curves)

3. **Build your own rocket** → :doc:`/user/tutorials/index` (TODO)
   
   Step-by-step guide to simulate your actual rocket design

4. **Advanced features** → :doc:`/user/how_to_guides/index` (TODO)
   
   Weather integration, air brakes control, Monte Carlo analysis

Common Next Questions
---------------------

.. dropdown:: How do I simulate my own rocket design?
   :color: info

   1. Copy ``configs/templates/template_complete_documented.yaml``
   2. Fill in your rocket's actual parameters (mass, dimensions, etc.)
   3. Use your motor's thrust curve file (``.eng`` format)
   4. Run simulation and iterate

   See :doc:`/user/tutorials/custom_rocket` (TODO) for step-by-step guide.

.. dropdown:: Where can I get motor thrust curve files?
   :color: info

   * `ThrustCurve.org <http://www.thrustcurve.org/>`_ - Database of commercial motors
   * Test data from your own static fire tests
   * Motor manufacturer websites (Cesaroni, AeroTech, etc.)
   
   Files should be in RASP ``.eng`` format.

.. dropdown:: Can I use real weather data?
   :color: info

   Yes! rocket-sim supports:
   
   * Wyoming atmospheric soundings
   * GFS forecast data
   * ERA5 reanalysis data
   
   See :doc:`/user/how_to_guides/weather_integration` (TODO)

.. dropdown:: What if the simulation fails or gives weird results?
   :color: info

   1. Check the validation messages - they often point to the issue
   2. Verify your rocket is statically stable (static margin > 2 calibers)
   3. Ensure motor thrust curve is reasonable
   4. See :doc:`/user/troubleshooting` (TODO) for common issues

Getting Help
------------

If you're stuck:

* **Documentation**: Browse :doc:`/user/index` (TODO)
* **Examples**: Check ``examples/`` directory for working code
* **Issues**: `GitHub Issues <https://github.com/matteodisante/rocket-sim/issues>`_

.. seealso::

   * :doc:`key_concepts` - Understand the simulation components
   * :doc:`/user/configuration_reference` (TODO) - Every parameter explained
   * `RocketPy Documentation <https://docs.rocketpy.org/>`_ - Underlying library
