.. _howto_create_config:

Create Configuration Files
===========================

This guide shows you how to create simulation configuration files from scratch or templates.

.. admonition:: Quick Start
   :class: tip
   
   Copy a template and customize it:
   
   .. code-block:: bash
   
      cp configs/templates/single_sim_template.yaml configs/single_sim/my_rocket.yaml
      # Edit my_rocket.yaml with your parameters

Configuration Structure
-----------------------

All configuration files are YAML format with these main sections:

.. code-block:: yaml

   # Simulation metadata
   name: my_rocket
   description: "Short description"
   
   # Launch site and conditions
   environment:
     # Location, weather, etc.
   
   # Rocket physical properties
   rocket:
     # Mass, dimensions, etc.
   
   # Motor specification
   motor:
     # Thrust curve, mass, etc.
   
   # Aerodynamic surfaces
   fins:
     # Geometry
   
   nose_cone:
     # Shape, length
   
   # Recovery system
   parachutes:
     # Deployment, Cd*S
   
   # Launch hardware
   rail:
     # Length, inclination
   
   # Numerical parameters
   integration:
     # Time step, tolerances

Method 1: Use Templates
-----------------------

Available Templates
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   configs/templates/
   ├── single_sim_template.yaml      # Single flight simulation
   ├── monte_carlo_template.yaml     # Uncertainty analysis
   └── optimization_template.yaml    # Design optimization

Create from Single Sim Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Copy template
   cp configs/templates/single_sim_template.yaml configs/single_sim/artemis.yaml
   
   # Edit in your preferred editor
   code configs/single_sim/artemis.yaml  # VS Code
   # or
   nano configs/single_sim/artemis.yaml  # Terminal

**Required customizations:**

.. code-block:: yaml

   # 1. Set rocket name (used for outputs)
   name: artemis
   
   # 2. Update launch location
   environment:
     latitude_deg: 44.5  # Your launch site
     longitude_deg: 11.3
     elevation_m: 50
   
   # 3. Specify motor file
   motor:
     motor_path: ../../data/motors/cesaroni_l1395.eng  # Path from config file
   
   # 4. Set rocket mass and dimensions
   rocket:
     mass_without_motor_kg: 5.2
     radius_m: 0.04  # 80mm diameter
     length_m: 1.5

Create from Monte Carlo Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cp configs/templates/monte_carlo_template.yaml configs/monte_carlo/artemis_mc.yaml

**Key differences:**

.. code-block:: yaml

   # Monte Carlo adds uncertainty to parameters
   
   # Single value (deterministic)
   mass_without_motor_kg: 5.2
   
   # Distribution (stochastic)
   mass_without_motor_kg:
     distribution: normal
     mean: 5.2
     std_dev: 0.1  # ±1.9% uncertainty
   
   # Ensemble parameters
   ensemble:
     num_simulations: 100
     seed: 42  # For reproducibility

Method 2: Build from Scratch
-----------------------------

Minimal Configuration
~~~~~~~~~~~~~~~~~~~~~

Start with absolute minimum required fields:

.. code-block:: yaml

   # minimal_rocket.yaml
   
   name: minimal
   
   environment:
     latitude_deg: 0.0
     longitude_deg: 0.0
     elevation_m: 0
   
   rocket:
     radius_m: 0.0635
     mass_without_motor_kg: 5.0
     length_m: 1.4
   
   motor:
     motor_path: data/motors/cesaroni_l1395.eng
     burn_time_s: 3.0
     dry_mass_kg: 0.5
     position_m: -0.6
   
   fins:
     number: 3
     root_chord_m: 0.15
     tip_chord_m: 0.05
     span_m: 0.12
     position_m: -1.2
   
   nose_cone:
     length_m: 0.3
     kind: vonkarman
     position_m: 1.1
   
   rail:
     length_m: 3.0

.. warning::

   This minimal config uses many defaults. For real flights, specify all relevant parameters explicitly.

Add Recommended Fields
~~~~~~~~~~~~~~~~~~~~~~~

Expand minimal config with important parameters:

.. code-block:: yaml

   name: recommended
   description: "Rocket with key parameters specified"
   
   environment:
     latitude_deg: 44.5
     longitude_deg: 11.3
     elevation_m: 50
     datum: SRTM  # Elevation model
   
   rocket:
     radius_m: 0.0635
     mass_without_motor_kg: 5.0
     length_m: 1.4
     
     # Inertia (Ixx, Iyy, Izz) in kg·m²
     inertia:
       ixx: 6.0
       iyy: 6.0
       izz: 0.03
     
     # Center of mass position
     center_of_mass_without_motor_m: 0.5
     
     # Drag coefficients
     power_off_drag_coefficient: 0.5
     power_on_drag_coefficient: 0.5
   
   motor:
     motor_path: data/motors/cesaroni_l1395.eng
     burn_time_s: 3.0
     dry_mass_kg: 0.5
     position_m: -0.6
     
     # Motor grain geometry (for Solid motors)
     nozzle_radius_m: 0.033
     grain_number: 5
     grain_separation_m: 0.005
     grain_density_kgm3: 1815
     grain_outer_radius_m: 0.033
     grain_initial_inner_radius_m: 0.015
     grain_initial_height_m: 0.12
   
   fins:
     number: 3
     root_chord_m: 0.15
     tip_chord_m: 0.05
     span_m: 0.12
     position_m: -1.2
     cant_angle_deg: 0.0  # For spin stabilization if needed
     airfoil: null  # Use flat plate, or specify airfoil file
   
   nose_cone:
     length_m: 0.3
     kind: vonkarman  # Options: vonkarman, conical, elliptical, ogive, lvhaack, tangent, parabolic, powerseries
     position_m: 1.1
     base_radius_m: null  # Optional: nose cone base radius (m). If null, uses rocket radius
     bluffness: null  # Optional: tip bluffness ratio (0-1). null = sharp tip
   
   parachutes:
     drogue:
       name: drogue
       cd_s: 0.5
       trigger: apogee
       sampling_rate_hz: 100
       lag_s: 1.5
       noise_std_dev: 0.0
     
     main:
       name: main
       cd_s: 10.0
       trigger: altitude
       trigger_value: 300
       sampling_rate_hz: 100
       lag_s: 1.5
       noise_std_dev: 0.0
   
   rail:
     length_m: 3.0
     inclination_deg: 85  # Slightly off-vertical
     heading_deg: 90  # East
   
   integration:
     max_time_s: 300
     max_time_step_s: 0.1
     min_time_step_s: 0.001
     rtol: 1e-6
     atol: 1e-9

Method 3: Interactive Builder
------------------------------

Use Interactive Script
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # scripts/create_config_interactive.py
   
   import yaml
   from pathlib import Path
   
   def create_config_interactive():
       """Interactive configuration builder."""
       
       print("=== Rocket Configuration Builder ===\n")
       
       # Basic info
       name = input("Rocket name: ").strip()
       description = input("Description (optional): ").strip()
       
       # Environment
       print("\n--- Launch Site ---")
       lat = float(input("Latitude (deg): "))
       lon = float(input("Longitude (deg): "))
       elev = float(input("Elevation (m ASL): "))
       
       # Rocket
       print("\n--- Rocket Dimensions ---")
       diameter_mm = float(input("Diameter (mm): "))
       length_m = float(input("Length (m): "))
       mass_kg = float(input("Mass without motor (kg): "))
       
       # Motor
       print("\n--- Motor ---")
       motor_file = input("Motor file path (from data/motors/): ").strip()
       burn_time = float(input("Burn time (s): "))
       dry_mass = float(input("Motor dry mass (kg): "))
       motor_pos = float(input("Motor position from nose (m, negative): "))
       
       # Fins
       print("\n--- Fins ---")
       n_fins = int(input("Number of fins: "))
       root_chord = float(input("Root chord (m): "))
       tip_chord = float(input("Tip chord (m): "))
       span = float(input("Span (m): "))
       fin_pos = float(input("Fin position from nose (m, negative): "))
       
       # Nose cone
       print("\n--- Nose Cone ---")
       nc_length = float(input("Nose cone length (m): "))
       print("Shapes: vonkarman, conical, ogive, elliptical")
       nc_kind = input("Shape [vonkarman]: ").strip() or "vonkarman"
       
       # Parachutes
       print("\n--- Parachutes ---")
       has_drogue = input("Include drogue parachute? [y/n]: ").lower() == 'y'
       has_main = input("Include main parachute? [y/n]: ").lower() == 'y'
       
       parachutes = {}
       
       if has_drogue:
           drogue_cds = float(input("Drogue Cd*S (m²): "))
           parachutes['drogue'] = {
               'name': 'drogue',
               'cd_s': drogue_cds,
               'trigger': 'apogee',
               'sampling_rate_hz': 100,
               'lag_s': 1.5,
               'noise_std_dev': 0.0
           }
       
       if has_main:
           main_cds = float(input("Main Cd*S (m²): "))
           main_alt = float(input("Main deployment altitude (m AGL): "))
           parachutes['main'] = {
               'name': 'main',
               'cd_s': main_cds,
               'trigger': 'altitude',
               'trigger_value': main_alt,
               'sampling_rate_hz': 100,
               'lag_s': 1.5,
               'noise_std_dev': 0.0
           }
       
       # Rail
       print("\n--- Launch Rail ---")
       rail_length = float(input("Rail length (m) [3.0]: ") or "3.0")
       
       # Build config dictionary
       config = {
           'name': name,
           'description': description,
           'environment': {
               'latitude_deg': lat,
               'longitude_deg': lon,
               'elevation_m': elev,
               'datum': 'SRTM'
           },
           'rocket': {
               'radius_m': diameter_mm / 2000,  # Convert mm to m
               'mass_without_motor_kg': mass_kg,
               'length_m': length_m,
               'inertia': {
                   'ixx': mass_kg * (3 * (diameter_mm/2000)**2 + length_m**2) / 12,
                   'iyy': mass_kg * (3 * (diameter_mm/2000)**2 + length_m**2) / 12,
                   'izz': mass_kg * (diameter_mm/2000)**2 / 2
               },
               'center_of_mass_without_motor_m': length_m * 0.5,
               'power_off_drag_coefficient': 0.5,
               'power_on_drag_coefficient': 0.5
           },
           'motor': {
               'motor_path': f'../../data/motors/{motor_file}',
               'burn_time_s': burn_time,
               'dry_mass_kg': dry_mass,
               'position_m': motor_pos,
               'nozzle_radius_m': 0.033,
               'grain_number': 5,
               'grain_separation_m': 0.005,
               'grain_density_kgm3': 1815,
               'grain_outer_radius_m': 0.033,
               'grain_initial_inner_radius_m': 0.015,
               'grain_initial_height_m': 0.12
           },
           'fins': {
               'number': n_fins,
               'root_chord_m': root_chord,
               'tip_chord_m': tip_chord,
               'span_m': span,
               'position_m': fin_pos,
               'cant_angle_deg': 0.0,
               'airfoil': None
           },
           'nose_cone': {
               'length_m': nc_length,
               'kind': nc_kind,
               'position_m': length_m - nc_length,
               'base_radius_m': None,
               'bluffness': None
           },
           'parachutes': parachutes,
           'rail': {
               'length_m': rail_length,
               'inclination_deg': 90,
               'heading_deg': 0
           },
           'integration': {
               'max_time_s': 300,
               'max_time_step_s': 0.1,
               'min_time_step_s': 0.001,
               'rtol': 1e-6,
               'atol': 1e-9
           }
       }
       
       # Save config
       output_path = Path('configs/single_sim') / f'{name}.yaml'
       output_path.parent.mkdir(parents=True, exist_ok=True)
       
       with open(output_path, 'w') as f:
           yaml.dump(config, f, default_flow_style=False, sort_keys=False)
       
       print(f"\n✓ Configuration saved to {output_path}")
       print(f"\nRun simulation with:")
       print(f"  python scripts/run_single_simulation.py {output_path}")
   
   if __name__ == '__main__':
       create_config_interactive()

Run interactive builder:

.. code-block:: bash

   python scripts/create_config_interactive.py

Method 4: From Existing Rocket
-------------------------------

Convert OpenRocket Design
~~~~~~~~~~~~~~~~~~~~~~~~~

If you have an OpenRocket (.ork) file:

.. code-block:: python

   # scripts/convert_openrocket.py
   
   import zipfile
   import xml.etree.ElementTree as ET
   import yaml
   
   def parse_openrocket(ork_file):
       """Extract parameters from OpenRocket file."""
       
       # ORK files are ZIP archives containing XML
       with zipfile.ZipFile(ork_file, 'r') as z:
           with z.open('rocket.ork') as f:
               tree = ET.parse(f)
       
       root = tree.getroot()
       rocket = root.find('.//rocket')
       
       # Extract basic dimensions
       nosecone = rocket.find('.//nosecone')
       bodytube = rocket.find('.//bodytube')
       finset = rocket.find('.//finset')
       motor = rocket.find('.//motor')
       
       config = {
           'name': rocket.get('name', 'converted'),
           'rocket': {
               'length_m': float(bodytube.find('length').text),
               'radius_m': float(bodytube.find('radius').text),
               # Add more conversions...
           },
           # Continue extracting...
       }
       
       return config
   
   # Usage
   config = parse_openrocket('my_rocket.ork')
   
   with open('configs/single_sim/converted.yaml', 'w') as f:
       yaml.dump(config, f)

Copy from Previous Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Copy and rename
   cp configs/single_sim/artemis.yaml configs/single_sim/artemis_v2.yaml
   
   # Update name
   sed -i '' 's/name: artemis/name: artemis_v2/' configs/single_sim/artemis_v2.yaml

Configuration Best Practices
-----------------------------

Naming Conventions
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good - descriptive, version-aware
   name: artemis_l1395_3fin
   
   # Good - includes date for testing
   name: artemis_test_2024_01_15
   
   # Bad - generic
   name: rocket1
   
   # Bad - spaces (breaks file paths)
   name: "my rocket"

Parameter Organization
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good - grouped logically with comments
   rocket:
     # Mass properties
     mass_without_motor_kg: 5.2
     center_of_mass_without_motor_m: 0.5
     
     # Dimensions
     radius_m: 0.0635
     length_m: 1.4
     
     # Aerodynamics
     power_off_drag_coefficient: 0.5
     power_on_drag_coefficient: 0.5
   
   # Bad - random order, no comments
   rocket:
     power_on_drag_coefficient: 0.5
     radius_m: 0.0635
     mass_without_motor_kg: 5.2
     length_m: 1.4

Units Documentation
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good - units in parameter names
   mass_without_motor_kg: 5.2
   length_m: 1.4
   inclination_deg: 85
   
   # Bad - ambiguous
   mass: 5.2  # kg? g? lbs?
   length: 1.4  # m? cm? inches?
   inclination: 85  # deg? rad?

Advanced Nose Cone Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The nose cone section supports advanced optional parameters:

.. code-block:: yaml

   nose_cone:
     # Required parameters
     length_m: 0.5
     kind: "vonKarman"  # vonkarman, conical, ogive, elliptical, lvhaack, tangent, parabolic, powerseries
     position_m: 0.0
     
     # Optional parameters
     base_radius_m: null  # If null, uses rocket radius. Set to specific value for transitions
     bluffness: null  # Tip bluffness ratio (0-1). null = sharp tip, 0.2 = slightly rounded

**When to use optional parameters:**

1. **base_radius_m**: When nose cone base diameter differs from body tube diameter (e.g., nose cone transitions)

   .. code-block:: yaml
   
      # Example: Smaller nose cone on larger body tube
      rocket:
        radius_m: 0.075  # Body tube: 150mm diameter
      
      nose_cone:
        base_radius_m: 0.065  # Nose cone base: 130mm diameter
        # Creates a shoulder/transition

2. **bluffness**: For realistic nose cones with rounded tips (reduces stress concentration)

   .. code-block:: yaml
   
      # Sharp tip (default)
      nose_cone:
        kind: "ogive"
        bluffness: null  # or 0
      
      # Rounded tip (more realistic)
      nose_cone:
        kind: "ogive"
        bluffness: 0.15  # 15% of base radius

.. note::

   - **bluffness** is NOT compatible with ``kind: "powerseries"``
   - Setting bluffness may slightly reduce effective nose cone length
   - Typical bluffness values: 0.1-0.3 for realistic designs

Validation After Creation
--------------------------

Validate Syntax
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Check YAML is valid
   python -c "
   import yaml
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   print('✓ Valid YAML')
   "

Validate Parameters
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use built-in validator
   python scripts/run_single_simulation.py configs/single_sim/my_rocket.yaml --validate

Check Against Template
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List parameters in config
   python -c "
   import yaml
   def get_keys(d, prefix=''):
       for k, v in d.items():
           if isinstance(v, dict):
               yield from get_keys(v, prefix + k + '.')
           else:
               yield prefix + k
   
   with open('configs/single_sim/my_rocket.yaml') as f:
       config = yaml.safe_load(f)
   
   for key in sorted(get_keys(config)):
       print(key)
   "
   
   # Compare with template
   # (manually check for missing required fields)

Quick Reference: Required Fields
---------------------------------

Absolute Minimum
~~~~~~~~~~~~~~~~

.. code-block:: yaml

   name: <string>
   environment:
     latitude_deg: <float>
     longitude_deg: <float>
     elevation_m: <float>
   rocket:
     radius_m: <float>
     mass_without_motor_kg: <float>
     length_m: <float>
   motor:
     motor_path: <string>
     burn_time_s: <float>
     dry_mass_kg: <float>
     position_m: <float>
   fins:
     number: <int>
     root_chord_m: <float>
     tip_chord_m: <float>
     span_m: <float>
     position_m: <float>
   nose_cone:
     length_m: <float>
     kind: <string>
     position_m: <float>
     base_radius_m: <float>  # Optional
     bluffness: <float>  # Optional (0-1)
   rail:
     length_m: <float>

Recommended Additional Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   rocket:
     inertia: {ixx, iyy, izz}
     center_of_mass_without_motor_m: <float>
     power_off_drag_coefficient: <float>
     power_on_drag_coefficient: <float>
   
   parachutes:
     <name>:
       cd_s: <float>
       trigger: <apogee|altitude>
       trigger_value: <float>  # if altitude trigger
   
   integration:
     max_time_s: <float>
     max_time_step_s: <float>

.. seealso::

   - :ref:`config_reference` - Complete parameter reference
   - :ref:`tutorial_first_simulation` - Using configurations
   - :ref:`howto_validate_design` - Validate parameters before simulation
