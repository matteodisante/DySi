Rocket Simulation Framework Documentation
==========================================

Welcome to the Rocket Simulation Framework documentation!

This framework provides a comprehensive toolkit for rocket flight simulation, Monte Carlo analysis, sensitivity studies, and active control systems, built on top of RocketPy.

.. grid:: 2
    :gutter: 3

    .. grid-item-card:: 🚀 Quick Start
        :link: user_guide/quickstart
        :link-type: doc

        Get started with your first simulation in minutes

    .. grid-item-card:: 📚 User Guide
        :link: user_guide/installation
        :link-type: doc

        Complete guide to using the framework

    .. grid-item-card:: 💡 Examples
        :link: examples/index
        :link-type: doc

        Practical examples and tutorials

    .. grid-item-card:: 🛠️ Development
        :link: development/index
        :link-type: doc

        Contributing and extending the framework

What's New
----------

**Latest Features:**

- ✅ **Bug Fixes**: Motor position validation, controller state reset, sensitivity analysis
- 🌤️ **Weather Integration**: Support for Wyoming soundings, GFS forecasts, ERA5 reanalysis
- 🎯 **Air Brakes Control**: PID, bang-bang, and model-predictive controllers
- 📊 **Monte Carlo Analysis**: Parallel uncertainty quantification with auto-parallelization
- 🔍 **Sensitivity Analysis**: Sobol indices and LAE methods

Key Features
------------

**Configuration Management**
   Type-safe YAML-based configuration with Python dataclasses

**RocketPy Integration**
   Native RocketPy API usage with full feature access

**Monte Carlo Analysis**
   Parallel uncertainty quantification with parameter distributions

**Sensitivity Analysis**
   Variance-based methods for parameter importance ranking

**Air Brakes Control**
   Active control system for precise apogee targeting

**Weather Integration**
   Real weather data from multiple sources

Quick Example
-------------

.. code-block:: yaml

    # configs/my_rocket.yaml
    motor:
      thrust_source: "Cesaroni_M1670.eng"
      position_m: -1.255
      # ... other params

    rocket:
      mass_kg: 19.197
      # ... other params

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/my_rocket.yaml \
        --plots \
        --output results/

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/installation
   user_guide/quickstart
   user_guide/key_concepts
   user_guide/configuration
   user_guide/documentation_index
   user_guide/configuration_reference
   user_guide/plots_and_output_reference

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/index

.. toctree::
   :maxdepth: 2
   :caption: Development

   development/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
