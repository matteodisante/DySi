User Guide
==========

Welcome to the rocket-sim User Guide! This section contains everything you need to
effectively use rocket-sim for your rocket trajectory simulations.

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 📖 Tutorials
      :link: tutorials/index
      :link-type: doc

      Step-by-step lessons to learn rocket-sim from basics to advanced

   .. grid-item-card:: 🔧 How-To Guides
      :link: how_to_guides/index
      :link-type: doc

      Task-focused guides for specific problems

   .. grid-item-card:: ⚙️ Configuration Reference
      :link: configuration/index
      :link-type: doc

      Complete parameter documentation

   .. grid-item-card:: 🔬 Technical Deep Dives
      :link: technical/index
      :link-type: doc

      Theory, physics, and advanced concepts

   .. grid-item-card:: 📊 Examples
      :link: examples/index
      :link-type: doc

      Real-world rocket configurations

Documentation Types
-------------------

This user guide follows the `Diátaxis framework <https://diataxis.fr/>`_ and is organized into:

**Tutorials** - *Learning-oriented*
   Progressive lessons that teach you how to use rocket-sim through practical examples.
   Start here if you're new or want to learn systematically.
   
   :doc:`tutorials/index`

**How-To Guides** - *Problem-oriented*
   Recipes and solutions for specific tasks. Use these when you know what you want
   to accomplish but need guidance on how to do it.
   
   :doc:`how_to_guides/index`

**Configuration Reference** - *Information-oriented*
   Complete documentation of every configuration parameter, organized by component.
   Use this when you need detailed information about a specific parameter.
   
   :doc:`configuration/index`

**Technical Deep Dives** - *Understanding-oriented*
   Theoretical background, physics, and detailed explanations of complex concepts.
   Use this when you need to deeply understand how things work.
   
   :doc:`technical/index`

**Examples** - *Practical applications*
   Real-world rocket configurations with complete explanations. Use these as
   starting points for your own rockets.
   
   :doc:`examples/index`

Quick Navigation
----------------

.. dropdown:: I'm new to rocket-sim
   :color: info
   :icon: rocket

   Start with:
   
   1. :doc:`/getting_started/installation` - Set up your environment
   2. :doc:`/getting_started/quickstart` - Run your first simulation (5 min)
   3. :doc:`tutorials/01_basic_flight` - Build from scratch
   4. :doc:`tutorials/02_understanding_outputs` - Interpret results
   5. :doc:`technical/plot_interpretation` - Detailed plot guide

.. dropdown:: I want to simulate my rocket
   :color: success
   :icon: tools

   Follow this path:
   
   1. :doc:`how_to_guides/measure_rocket` - Measure your rocket's parameters
   2. :doc:`how_to_guides/create_config` - Create configuration file
   3. :doc:`how_to_guides/validate_design` - Check stability and plausibility
   4. :doc:`configuration/index` - Reference for all parameters

.. dropdown:: I need to solve a specific problem
   :color: warning
   :icon: question

   Check the how-to guides:
   
   * :doc:`how_to_guides/weather_data` - Use real atmospheric data
   * :doc:`how_to_guides/custom_drag` - Import wind tunnel data
   * :doc:`how_to_guides/air_brakes` - Configure active control
   * :doc:`how_to_guides/export_data` - Export in different formats

.. dropdown:: I want to understand what a parameter does
   :color: primary
   :icon: book

   See the configuration reference:
   
   * :doc:`configuration/rocket_params` - All rocket parameters
   * :doc:`configuration/motor_params` - All motor parameters
   * :doc:`configuration/environment_params` - Environment and weather
   * :doc:`configuration/simulation_params` - Launch and simulation settings

.. dropdown:: I want to understand what's in the output plots
   :color: info
   :icon: graph

   Quick references and detailed guides:
   
   * :doc:`quick_plot_reference` - **Quick reference card** for all plots
   * :doc:`technical/plot_interpretation` - Complete interpretation guide
   * :doc:`tutorials/02_understanding_outputs` - Tutorial walkthrough

.. dropdown:: I need to understand the theory
   :color: secondary
   :icon: mortar-board

   Check the technical documentation:
   
   * :doc:`technical/plot_interpretation` - How to read all output plots
   * :doc:`technical/stability_analysis` - Complete stability theory (CM, CP, margins)
   * More technical topics coming soon

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quick_plot_reference
   tutorials/index
   how_to_guides/index
   configuration/index
   technical/index
   examples/index

Common Questions
----------------

**Where do I start?**
   If you've completed :doc:`/getting_started/quickstart`, continue with :doc:`tutorials/01_basic_flight`.

**I keep getting validation errors**
   See :doc:`how_to_guides/troubleshooting_validation` for common issues and solutions.

**Where can I find motor thrust curves?**
   Check `ThrustCurve.org <http://www.thrustcurve.org/>`_ or see :doc:`how_to_guides/motor_data`.

**How do I use real weather data?**
   See :doc:`how_to_guides/weather_data` for Wyoming soundings, GFS, and ERA5 data.

**Can I simulate multiple stages?**
   Multi-stage support is planned but not yet implemented. Track progress in GitHub issues.

Getting Help
------------

* **Search**: Use the search function (top right) to find specific topics
* **Examples**: Browse ``examples/`` directory for working configurations
* **Community**: Ask on `GitHub Discussions <https://github.com/matteodisante/rocket-sim/discussions>`_
* **Issues**: Report bugs on `GitHub Issues <https://github.com/matteodisante/rocket-sim/issues>`_
