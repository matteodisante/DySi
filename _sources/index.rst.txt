Rocket Simulation Framework
============================

A production-ready rocket trajectory simulation framework built on `RocketPy <https://github.com/RocketPy-Team/RocketPy>`_.

**New to rocket-sim?** Start with :doc:`getting_started/index` ⚡

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: ⚡ Getting Started
      :link: getting_started/index
      :link-type: doc

      New user? Start here for installation, quickstart, and core concepts.

   .. grid-item-card:: 📚 User Guide
      :link: user/index
      :link-type: doc

      Tutorials, how-to guides, and configuration reference.

   .. grid-item-card:: 🔍 API Reference
      :link: api/index
      :link-type: doc

      Complete technical reference for all modules and functions.

   .. grid-item-card:: 💻 Developer Guide
      :link: developer/index
      :link-type: doc

      Contributing, architecture, and extending rocket-sim.

----

What is rocket-sim?
-------------------

rocket-sim is a **YAML-based simulation framework** that makes rocket trajectory analysis accessible and reproducible.

**Key Features:**

✅ **No coding required** - Configure simulations with YAML files

✅ **Automatic validation** - Physical plausibility and stability checks

✅ **Professional outputs** - Publication-quality plots and data exports

✅ **Weather integration** - Real atmospheric data from multiple sources

✅ **Advanced control** - Air brakes with PID, bang-bang, or MPC controllers

**Built for:**

* Student rocketry teams (IREC, EuRoC, SA Cup)
* Aerospace engineering education
* Research and development
* High-power rocketry enthusiasts

Quick Example
-------------

Create a configuration file ``my_rocket.yaml``:

.. code-block:: yaml

   rocket:
     name: "My Rocket"
     mass: 10.0          # kg (dry mass)
     radius: 0.05        # m
     # ... more parameters
   
   motor:
     thrust_source: "motors/AeroTech_J450.eng"
     # ... motor parameters
   
   environment:
     latitude: 39.39     # Launch site coordinates
     longitude: -8.29
   
   simulation:
     inclination: 85     # Launch angle (degrees)
     heading: 90         # Launch direction (East)

Run the simulation:

.. code-block:: bash

   python scripts/run_single_simulation.py \
       --config my_rocket.yaml \
       --name my_flight \
       --plots

Get comprehensive results in ``outputs/my_flight/``:

* 3D trajectory visualization
* Altitude, velocity, acceleration plots
* CSV data export for custom analysis
* KML file for Google Earth
* Complete motor and rocket state

Installation
------------

.. code-block:: bash

   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt

Verify:

.. code-block:: bash

   python -c "import rocketpy; print('✓ Ready to simulate!')"

See :doc:`getting_started/installation` for detailed instructions.

First Simulation in 5 Minutes
------------------------------

Follow the :doc:`getting_started/quickstart` to:

1. Run a pre-configured example rocket
2. Understand the configuration structure
3. Generate plots and export data
4. Customize parameters for your rocket

Documentation Structure
-----------------------

This documentation is organized into four main sections:

**Getting Started** - *Start here if you're new*
   Installation, quickstart tutorial, key concepts, and next steps.
   
   :doc:`getting_started/index`

**User Guide** - *How to use rocket-sim*
   Step-by-step tutorials, how-to guides, configuration reference, and examples.
   
   :doc:`user/index`

**API Reference** - *Technical details*
   Complete reference for all modules, classes, and functions.
   
   :doc:`api/index`

**Developer Guide** - *Contributing and extending*
   Architecture, coding standards, testing, and contribution guidelines.
   
   :doc:`developer/index`

.. tip::
   **Not sure where to look?**
   
   * **"How do I...?"** → User Guide
   * **"What does this parameter do?"** → API Reference
   * **"I want to understand the code"** → Developer Guide

Project Status
--------------

.. list-table::
   :widths: 40 60
   :header-rows: 0

   * - **Current Version**
     - 1.0.0
   * - **Python Version**
     - 3.8+
   * - **RocketPy Version**
     - 1.x
   * - **License**
     - MIT
   * - **Status**
     - Production Ready

**Production Features:**

* ✅ Single flight simulations with comprehensive validation
* ✅ Motor state export (35+ attributes, 11 curve plots)
* ✅ Air brakes control (PID, bang-bang, MPC)
* ✅ Weather data integration (Wyoming, GFS, ERA5)
* ✅ Publication-quality visualization
* ✅ Complete test suite

**Planned Features:**

* 🚧 Monte Carlo uncertainty quantification
* 🚧 Multi-stage rocket support
* 🚧 Advanced reporting system

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   getting_started/index
   user/index
   api/index
   developer/index

.. toctree::
   :maxdepth: 1
   :caption: Additional Resources

   changelog
   bibliography
   glossary

Getting Help
------------

**Documentation:** You're reading it! Use the search function (top right) to find specific topics.

**Examples:** Check ``examples/`` and ``configs/`` directories for working code.

**Issues:** Report bugs or request features on `GitHub Issues <https://github.com/matteodisante/rocket-sim/issues>`_.

**Community:** Join discussions on `GitHub Discussions <https://github.com/matteodisante/rocket-sim/discussions>`_.

Acknowledgments
---------------

rocket-sim is built on the excellent `RocketPy <https://github.com/RocketPy-Team/RocketPy>`_ library
developed by the RocketPy Team at UFRJ.

Developed for the **STARPI** student rocketry team.

Indices and Tables
==================

* :ref:`genindex` - All functions, classes, and terms
* :ref:`modindex` - All modules
* :ref:`search` - Search the documentation
