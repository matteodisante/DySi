Installation
============

This guide will help you install the Rocket Simulation Framework.

Prerequisites
-------------

- Python 3.8 or higher
- pip package manager
- Git (for development)

Required Dependencies
---------------------

The framework requires the following packages:

- RocketPy >= 1.0.0
- NumPy >= 1.20.0
- pandas >= 1.3.0
- PyYAML >= 5.4.0
- matplotlib >= 3.3.0

Installation Steps
------------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    git clone https://github.com/your-org/rocket-sim.git
    cd rocket-sim

2. Create Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install Dependencies
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -r requirements.txt

4. Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    python -c "import rocketpy; print(rocketpy.__version__)"
    python -c "from src.config import load_config; print('Installation successful!')"

Optional Dependencies
---------------------

For development and additional features:

.. code-block:: bash

    pip install -r requirements-dev.txt

This includes:

- pytest (testing)
- black (code formatting)
- flake8 (linting)
- mypy (type checking)
- jupyter (notebooks)

Troubleshooting
---------------

RocketPy Installation Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If RocketPy installation fails:

.. code-block:: bash

    pip install --upgrade pip
    pip install rocketpy --no-cache-dir

Import Errors
~~~~~~~~~~~~~

If you get import errors, ensure the project root is in your Python path:

.. code-block:: bash

    export PYTHONPATH="${PYTHONPATH}:/path/to/rocket-sim"

Or in Python:

.. code-block:: python

    import sys
    sys.path.append('/path/to/rocket-sim')

Development Installation
------------------------

For contributing to the framework:

1. Fork the Repository
~~~~~~~~~~~~~~~~~~~~~~

Fork the repository on GitHub and clone your fork:

.. code-block:: bash

    git clone https://github.com/your-username/rocket-sim.git
    cd rocket-sim

2. Install in Editable Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install -e .

3. Install Pre-commit Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install pre-commit
    pre-commit install

Verifying Your Installation
----------------------------

Run the test suite:

.. code-block:: bash

    pytest tests/

Run a simple simulation:

.. code-block:: bash

    python scripts/run_single_simulation.py \
        --config configs/complete_example.yaml \
        --output test_output/

If both commands complete successfully, your installation is working!

Next Steps
----------

- :doc:`quickstart` - Run your first simulation
- :doc:`key_concepts` - Learn framework concepts
- :doc:`configuration` - Configure your simulations
