Installation
============

This guide will help you install rocket-sim and verify your setup.

.. admonition:: Prerequisites
   :class: note

   * Python 3.8 or higher
   * pip package manager
   * 500 MB free disk space (for dependencies)

Installation Methods
--------------------

Method 1: Standard Installation (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the recommended method for most users.

**Step 1: Clone the Repository**

.. code-block:: bash

   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim

**Step 2: Create Virtual Environment** (Recommended)

Using a virtual environment prevents conflicts with other Python projects:

.. tab-set::

   .. tab-item:: macOS/Linux

      .. code-block:: bash

         python3 -m venv venv
         source venv/bin/activate

   .. tab-item:: Windows

      .. code-block:: batch

         python -m venv venv
         venv\Scripts\activate

**Step 3: Install Dependencies**

.. code-block:: bash

   pip install -r requirements.txt

**Step 4: Verify Installation**

.. code-block:: bash

   python -c "import rocketpy; print(f'✓ RocketPy {rocketpy.__version__} installed successfully')"

Expected output:

.. code-block:: text

   ✓ RocketPy 1.x.x installed successfully

Method 2: Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you plan to contribute or modify the code:

.. code-block:: bash

   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim
   pip install -r requirements.txt
   pip install -r requirements-docs.txt  # For documentation building

Verify Your Setup
-----------------

Run the verification script to ensure everything is working:

.. code-block:: bash

   python -c "
   import sys
   import rocketpy
   import yaml
   import numpy
   import matplotlib
   
   print('✓ Python:', sys.version.split()[0])
   print('✓ RocketPy:', rocketpy.__version__)
   print('✓ NumPy:', numpy.__version__)
   print('✓ Matplotlib:', matplotlib.__version__)
   print('✓ PyYAML:', yaml.__version__)
   print()
   print('🚀 All dependencies installed correctly!')
   "

Expected output:

.. code-block:: text

   ✓ Python: 3.x.x
   ✓ RocketPy: 1.x.x
   ✓ NumPy: 1.x.x
   ✓ Matplotlib: 3.x.x
   ✓ PyYAML: 6.x
   
   🚀 All dependencies installed correctly!

Project Structure
-----------------

After installation, your directory should look like this:

.. code-block:: text

   rocket-sim/
   ├── configs/              # Configuration files
   │   ├── single_sim/       # Single flight configs
   │   └── templates/        # Configuration templates
   ├── data/                 # Motor files, drag curves
   ├── docs/                 # Documentation (you're here!)
   ├── examples/             # Example Python scripts
   ├── scripts/              # CLI tools
   ├── src/                  # Core simulation code
   └── outputs/              # Results (created automatically)

Troubleshooting
---------------

ImportError: No module named 'rocketpy'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: RocketPy is not installed or virtual environment is not activated.

**Solution**:

.. code-block:: bash

   # Ensure virtual environment is activated (you should see (venv) in prompt)
   source venv/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate     # Windows
   
   # Reinstall dependencies
   pip install -r requirements.txt

ModuleNotFoundError: No module named 'yaml'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: PyYAML is missing.

**Solution**:

.. code-block:: bash

   pip install pyyaml

Permission Denied
~~~~~~~~~~~~~~~~~

**Problem**: Insufficient permissions to install packages.

**Solution**: Use virtual environment (recommended) or install with ``--user`` flag:

.. code-block:: bash

   pip install --user -r requirements.txt

Python Version Too Old
~~~~~~~~~~~~~~~~~~~~~~

**Problem**: You have Python 3.7 or older.

**Solution**: Install Python 3.8+ from `python.org <https://www.python.org/downloads/>`_ and retry.

Verify with:

.. code-block:: bash

   python --version
   # Should show: Python 3.8.x or higher

macOS SSL Certificate Error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: ``[SSL: CERTIFICATE_VERIFY_FAILED]`` when downloading packages.

**Solution**: Install certificates:

.. code-block:: bash

   # macOS specific fix
   /Applications/Python\ 3.x/Install\ Certificates.command

Windows Long Path Issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Errors related to path length on Windows.

**Solution**: Enable long paths in Windows or install in a shorter path:

.. code-block:: batch

   # Install in shorter path
   cd C:\
   git clone https://github.com/matteodisante/rocket-sim.git
   cd rocket-sim

Next Steps
----------

✅ Installation complete! 

Now you're ready to:

* :doc:`quickstart` - Run your first simulation in 5 minutes
* :doc:`key_concepts` - Learn the core concepts
* Browse example configurations in ``configs/single_sim/``

.. seealso::

   * `RocketPy Installation Guide <https://docs.rocketpy.org/en/latest/user/installation.html>`_
   * `Python Virtual Environments Tutorial <https://docs.python.org/3/tutorial/venv.html>`_

Getting Help
------------

If you encounter issues not covered here:

1. Check the :doc:`/user/troubleshooting` guide (TODO)
2. Search existing `GitHub Issues <https://github.com/matteodisante/rocket-sim/issues>`_
3. Open a new issue with:
   
   * Your Python version (``python --version``)
   * Your operating system
   * Complete error message
   * Steps to reproduce

.. tip::
   Include output of ``pip list`` to show all installed packages when reporting issues.
