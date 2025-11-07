=============
API Reference
=============

This section contains detailed documentation for all modules, classes, and functions
in the Rocket Simulation Framework.

Overview
========

The framework is organized into several main modules:

* **Configuration**: YAML loading and dataclass configs (:mod:`src.config_loader`)
* **Builders**: Component construction (:mod:`src.motor_builder`, :mod:`src.rocket_builder`, :mod:`src.environment_setup`)
* **Simulators**: Flight simulation (:mod:`src.flight_simulator`)
* **Analyzers**: Monte Carlo and sensitivity analysis (:mod:`src.monte_carlo_runner`, :mod:`src.sensitivity_analyzer`)
* **Controllers**: Air brakes control (:mod:`src.air_brakes_controller`)
* **Utilities**: Validation, visualization, data handling

Module Index
============

Configuration
-------------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.config_loader

Builders
--------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.motor_builder
   src.rocket_builder
   src.environment_setup

Simulators
----------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.flight_simulator

Analyzers
---------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.monte_carlo_runner
   src.sensitivity_analyzer

Controllers
-----------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.air_brakes_controller

Weather
-------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.weather_fetcher

Utilities
---------

.. autosummary::
   :toctree: generated/
   :template: module.rst

   src.validators
   src.visualizer
   src.data_handler
   src.utils

Detailed Documentation
======================

Configuration Module
--------------------

.. automodule:: src.config_loader
   :members:
   :undoc-members:
   :show-inheritance:

Motor Builder
-------------

.. automodule:: src.motor_builder
   :members:
   :undoc-members:
   :show-inheritance:

Rocket Builder
--------------

.. automodule:: src.rocket_builder
   :members:
   :undoc-members:
   :show-inheritance:

Environment Setup
-----------------

.. automodule:: src.environment_setup
   :members:
   :undoc-members:
   :show-inheritance:

Flight Simulator
----------------

.. automodule:: src.flight_simulator
   :members:
   :undoc-members:
   :show-inheritance:

Monte Carlo Runner
------------------

.. automodule:: src.monte_carlo_runner
   :members:
   :undoc-members:
   :show-inheritance:

Sensitivity Analyzer
--------------------

.. automodule:: src.sensitivity_analyzer
   :members:
   :undoc-members:
   :show-inheritance:

Air Brakes Controller
---------------------

.. automodule:: src.air_brakes_controller
   :members:
   :undoc-members:
   :show-inheritance:

Weather Fetcher
---------------

.. automodule:: src.weather_fetcher
   :members:
   :undoc-members:
   :show-inheritance:

Validators
----------

.. automodule:: src.validators
   :members:
   :undoc-members:
   :show-inheritance:

Visualizer
----------

.. automodule:: src.visualizer
   :members:
   :undoc-members:
   :show-inheritance:

Data Handler
------------

.. automodule:: src.data_handler
   :members:
   :undoc-members:
   :show-inheritance:

Utilities
---------

.. automodule:: src.utils
   :members:
   :undoc-members:
   :show-inheritance:
