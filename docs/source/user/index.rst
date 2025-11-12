User Guide
==========

.. toctree::
   :maxdepth: 2
   
   installation
   quickstart
   configuration
   outputs

Installation
------------

Prerequisites
^^^^^^^^^^^^^

* Python 3.8 or higher
* pip package manager

Setup
^^^^^

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim

2. Create virtual environment:

.. code-block:: bash

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate

3. Install dependencies:

.. code-block:: bash

   pip install -r requirements.txt

Quick Start
-----------

Run a basic simulation:

.. code-block:: bash

   python scripts/run_single_simulation.py \\
       --config configs/single_sim/01_minimal.yaml \\
       --name test_flight \\
       --plots

Configuration
-------------

See the `Configuration Reference <../user/CONFIGURATION_REFERENCE.md>`_ for detailed YAML configuration options.

Outputs
-------

See the `Plots and Output Reference <../user/PLOTS_AND_OUTPUT_REFERENCE.md>`_ for understanding simulation outputs.

Additional Resources
--------------------

* `Motor State Export Guide <../user/MOTOR_STATE_EXPORT_GUIDE.md>`_
* `Troubleshooting <../user/TROUBLESHOOTING.md>`_
