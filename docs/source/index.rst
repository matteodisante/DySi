Rocket Simulation Framework
============================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   user/index
   developer/index
   api/index

Welcome to Rocket Simulation Framework
---------------------------------------

A modular, production-ready rocket dynamics simulation framework built on `RocketPy <https://github.com/RocketPy-Team/RocketPy>`_.

Features
--------

**Core Capabilities:**

* 🚀 Complete Flight Simulation - 6-DOF trajectory analysis
* 📁 YAML Configuration - Type-safe configuration files
* ✅ Validation Layer - Automatic physical plausibility checks
* 📈 Publication-Quality Plots - 3D trajectories, altitude, velocity profiles
* 💾 Multiple Export Formats - CSV, JSON, KML
* 🎯 Complete Motor State Export - 35+ attributes + 11 plots

**Advanced Features:**

* 🎯 Air Brakes Control - PID, bang-bang, MPC controllers
* 🌤️ Weather Integration - Wyoming, GFS, ERA5 data
* 📊 Smart Dual Y-Axis Plots
* 📂 Organized Output Structure

**In Development:**

* 📊 Monte Carlo Analysis *(coming soon)*

Quick Start
-----------

Installation
^^^^^^^^^^^^

.. code-block:: bash

   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim
   pip install -r requirements.txt

Run Your First Simulation
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python scripts/run_single_simulation.py \\
       --config configs/single_sim/01_minimal.yaml \\
       --name my_first_rocket \\
       --plots

Project Status
--------------

✅ **Production Ready**

* Single flight simulations
* Motor state export (35+ attributes, 11 plots)
* Air brakes control
* Weather data integration
* Complete test suite

🚧 **In Development**

* Monte Carlo uncertainty analysis
* Parallel execution framework

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
