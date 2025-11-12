Tutorials
=========

These step-by-step tutorials will teach you how to use rocket-sim effectively.
Each tutorial builds on previous knowledge, so we recommend following them in order.

.. admonition:: Prerequisites
   :class: note

   Before starting, ensure you've completed :doc:`/getting_started/quickstart`.

Tutorial Path
-------------

.. grid:: 1 2 2 3
   :gutter: 2

   .. grid-item-card:: 1️⃣ Basic Flight
      :link: 01_basic_flight
      :link-type: doc
      :class-header: bg-light

      Create your first simulation from scratch
      
      **Time**: 15 minutes  
      **Level**: Beginner

   .. grid-item-card:: 2️⃣ Understanding Outputs ✅
      :link: 02_understanding_outputs
      :link-type: doc
      :class-header: bg-light

      Interpret trajectory data and plots
      
      **Time**: 20 minutes  
      **Level**: Beginner

   .. grid-item-card:: 3️⃣ Custom Motor Data ✅
      :link: 03_custom_motor
      :link-type: doc
      :class-header: bg-light

      Import your own thrust curves
      
      **Time**: 25 minutes  
      **Level**: Beginner

   .. grid-item-card:: 4️⃣ Adding Fins ✅
      :link: 04_adding_fins
      :link-type: doc
      :class-header: bg-light

      Design fin configurations
      
      **Time**: 30 minutes  
      **Level**: Intermediate

   .. grid-item-card:: 5️⃣ Recovery System
      :link: 05_recovery_system
      :link-type: doc
      :class-header: bg-light

      Configure parachutes and deployment
      
      **Time**: 20 minutes  
      **Level**: Intermediate

   .. grid-item-card:: 6️⃣ Weather Integration
      :link: 06_weather_integration
      :link-type: doc
      :class-header: bg-light

      Use real atmospheric data
      
      **Time**: 30 minutes  
      **Level**: Intermediate

   .. grid-item-card:: 7️⃣ Air Brakes Control
      :link: 07_air_brakes
      :link-type: doc
      :class-header: bg-light

      Active apogee control with PID
      
      **Time**: 35 minutes  
      **Level**: Advanced

   .. grid-item-card:: 8️⃣ Custom Aerodynamics
      :link: 08_custom_aero
      :link-type: doc
      :class-header: bg-light

      Import wind tunnel drag curves
      
      **Time**: 25 minutes  
      **Level**: Advanced

Learning Paths
--------------

Choose the path that fits your needs:

**Quick Start Path** (Total: ~50 minutes)
   For users who want to get productive quickly:
   
   1. :doc:`01_basic_flight` - Essential basics
   2. :doc:`02_understanding_outputs` - Interpret results
   3. :doc:`03_custom_motor` - Use your own motor

**Competition Path** (Total: ~2 hours)
   For student rocketry teams preparing for competitions:
   
   1. :doc:`01_basic_flight` - Fundamentals
   2. :doc:`04_adding_fins` - Aerodynamic design
   3. :doc:`05_recovery_system` - Safe landing
   4. :doc:`06_weather_integration` - Launch site conditions
   5. :doc:`07_air_brakes` - Active control (optional)

**Complete Path** (Total: ~3 hours)
   Master all features of rocket-sim:
   
   All tutorials 1-8 in order

Tutorial Contents
-----------------

.. toctree::
   :maxdepth: 1
   :caption: Available Tutorials

   01_basic_flight
   02_understanding_outputs
   03_custom_motor
   04_adding_fins
   05_recovery_system
   06_weather_integration
   07_air_brakes
   08_custom_aero

What You'll Learn
-----------------

By completing these tutorials, you will be able to:

✅ Create rocket configurations from scratch

✅ Import and validate motor thrust curves

✅ Design stable fin configurations

✅ Configure recovery systems with deployment logic

✅ Use real atmospheric data from multiple sources

✅ Implement active control systems (air brakes)

✅ Import custom aerodynamic data

✅ Validate and troubleshoot configurations

✅ Interpret simulation results and plots

✅ Export data in multiple formats

Next Steps
----------

After completing the tutorials:

* **Apply to your rocket**: Use :doc:`/how_to_guides/index` for specific tasks
* **Deep dive into parameters**: See :doc:`/configuration/index` for all options
* **Study examples**: Browse :doc:`/examples/index` for real rockets
* **Contribute**: Read :doc:`/developer/index` to extend rocket-sim

Tips for Learning
-----------------

.. tip::
   **Work through examples**: Type the code yourself rather than copy-pasting.
   This helps build muscle memory and understanding.

.. tip::
   **Experiment**: After each tutorial, try modifying parameters to see how
   results change. This is the best way to build intuition.

.. tip::
   **Use version control**: Keep your configurations in git so you can
   track changes and revert if needed.

.. note::
   All tutorial examples are available in ``examples/tutorials/`` directory.
   You can run them directly to verify expected behavior.

Getting Help
------------

If you get stuck:

1. Check the tutorial's "Common Issues" section
2. Review :doc:`/getting_started/key_concepts` for fundamentals
3. Search the documentation
4. Ask on `GitHub Discussions <https://github.com/matteodisante/rocket-sim/discussions>`_
