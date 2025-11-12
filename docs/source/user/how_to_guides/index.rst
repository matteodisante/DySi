How-To Guides
=============

These task-focused guides show you how to solve specific problems with rocket-sim.
Unlike tutorials, these assume you understand the basics and jump straight to solutions.

.. admonition:: When to use How-To Guides
   :class: tip

   * You know **what** you want to accomplish
   * You need **practical steps** to do it
   * You want **quick answers** without lengthy explanations

Choose Your Task
----------------

Configuration and Setup
~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 📝 Create a Configuration File
      :link: create_config
      :link-type: doc

      Build a config from scratch or template

   .. grid-item-card:: 📏 Measure Your Rocket
      :link: measure_rocket
      :link-type: doc

      How to measure physical parameters

   .. grid-item-card:: ✅ Validate Your Design
      :link: validate_design
      :link-type: doc

      Check stability and plausibility

   .. grid-item-card:: 🔧 Fix Validation Errors
      :link: troubleshooting_validation
      :link-type: doc

      Common errors and solutions

Motor and Propulsion
~~~~~~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 🔥 Import Motor Data
      :link: motor_data
      :link-type: doc

      Use .eng files or custom curves

   .. grid-item-card:: 🎯 Select Optimal Motor
      :link: motor_selection
      :link-type: doc

      Choose motor for target apogee

   .. grid-item-card:: ⚖️ Compare Motors
      :link: compare_motors
      :link-type: doc

      Evaluate multiple motor options

Environment and Weather
~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 🌤️ Use Real Weather Data
      :link: weather_data
      :link-type: doc

      Wyoming, GFS, ERA5 integration

   .. grid-item-card:: 💨 Configure Wind Profiles
      :link: wind_profiles
      :link-type: doc

      Altitude-dependent wind

   .. grid-item-card:: 🌍 Custom Atmospheric Models
      :link: custom_atmosphere
      :link-type: doc

      Import your own atmosphere data

Aerodynamics and Control
~~~~~~~~~~~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 📊 Import Drag Curves
      :link: custom_drag
      :link-type: doc

      Use wind tunnel data

   .. grid-item-card:: 🎮 Configure Air Brakes
      :link: air_brakes
      :link-type: doc

      Active apogee control

   .. grid-item-card:: ⚙️ Tune PID Controller
      :link: pid_tuning
      :link-type: doc

      Optimize controller parameters

Output and Analysis
~~~~~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 💾 Export Data
      :link: export_data
      :link-type: doc

      CSV, JSON, KML formats

   .. grid-item-card:: 📈 Create Custom Plots
      :link: custom_plots
      :link-type: doc

      Visualize specific metrics

   .. grid-item-card:: 📄 Generate Reports
      :link: generate_reports
      :link-type: doc

      Professional documentation

   .. grid-item-card:: 🔍 Analyze Trajectory
      :link: data_analysis
      :link-type: doc

      Post-process simulation data

Advanced Topics
~~~~~~~~~~~~~~~

.. grid:: 1 2 2 2
   :gutter: 2

   .. grid-item-card:: 🔬 Parameter Sensitivity
      :link: parameter_study
      :link-type: doc

      Understand parameter effects

   .. grid-item-card:: 🎲 Monte Carlo Analysis
      :link: monte_carlo
      :link-type: doc

      Uncertainty quantification

   .. grid-item-card:: 🔄 Batch Simulations
      :link: batch_processing
      :link-type: doc

      Run multiple configurations

   .. grid-item-card:: 🚀 Optimize Design
      :link: optimization
      :link-type: doc

      Find optimal parameters

Quick Reference
---------------

**Most Common Tasks:**

1. :doc:`measure_rocket` - Measure your rocket's parameters
2. :doc:`create_config` - Create configuration file
3. :doc:`validate_design` - Verify stability
4. :doc:`weather_data` - Add real atmospheric data
5. :doc:`export_data` - Export results

**Troubleshooting:**

* :doc:`troubleshooting_validation` - Fix validation errors
* :doc:`troubleshooting_simulation` - Debug simulation issues
* :doc:`troubleshooting_output` - Resolve output problems

Available Guides
----------------

.. toctree::
   :maxdepth: 1
   :caption: Configuration

   create_config
   measure_rocket
   validate_design
   troubleshooting_validation

.. toctree::
   :maxdepth: 1
   :caption: Motors

   motor_data
   motor_selection
   compare_motors

.. toctree::
   :maxdepth: 1
   :caption: Environment

   weather_data
   wind_profiles
   custom_atmosphere

.. toctree::
   :maxdepth: 1
   :caption: Aerodynamics

   custom_drag
   air_brakes
   pid_tuning

.. toctree::
   :maxdepth: 1
   :caption: Output

   export_data
   custom_plots
   generate_reports
   data_analysis

.. toctree::
   :maxdepth: 1
   :caption: Advanced

   parameter_study
   monte_carlo
   batch_processing
   optimization

.. toctree::
   :maxdepth: 1
   :caption: Troubleshooting

   troubleshooting_simulation
   troubleshooting_output

How-To vs Tutorial
------------------

**Use a Tutorial when:**

* You're learning rocket-sim for the first time
* You want step-by-step explanations
* You're building knowledge systematically

**Use a How-To Guide when:**

* You have a specific task to accomplish
* You already understand the basics
* You want quick, practical solutions

.. seealso::

   * :doc:`/user/tutorials/index` - Learning-oriented tutorials
   * :doc:`/user/configuration/index` - Parameter reference
   * :doc:`/user/examples/index` - Complete examples

Getting Help
------------

If a how-to guide doesn't solve your problem:

1. Check :doc:`/user/configuration/index` for parameter details
2. Search documentation (search box at top right)
3. Ask on `GitHub Discussions <https://github.com/matteodisante/rocket-sim/discussions>`_
4. Report bugs on `GitHub Issues <https://github.com/matteodisante/rocket-sim/issues>`_

Contributing
------------

Have a useful how-to guide to share?

1. Fork the repository
2. Write your guide following the :doc:`template </developer/howto_template>`
3. Submit a pull request

See :doc:`/developer/contributing` for details.
