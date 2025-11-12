Next Steps
==========

Congratulations on completing the Getting Started guide! You now have a solid foundation
in rocket-sim. This page will help you decide where to go next based on your goals.

Choose Your Path
----------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🎓 I'm Learning Rocket Simulation
      :link: #path-learning
      :link-type: ref

      New to rocketry or trajectory simulation

   .. grid-item-card:: 🏆 I'm Building a Competition Rocket
      :link: #path-competition
      :link-type: ref

      Need to design and validate for competition

   .. grid-item-card:: 🔬 I'm Doing Research
      :link: #path-research
      :link-type: ref

      Advanced analysis and custom modifications

   .. grid-item-card:: 💻 I'm Contributing Code
      :link: #path-development
      :link-type: ref

      Want to extend or improve rocket-sim

.. _path-learning:

Path 1: Learning Rocket Simulation
-----------------------------------

**Your Goal**: Understand how rocket simulations work and learn best practices.

Recommended Learning Path
~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Complete the Tutorials** (TODO)
   
   Follow step-by-step tutorials building from simple to complex:
   
   * :doc:`/user/tutorials/01_basic_flight` - Minimal rocket
   * :doc:`/user/tutorials/02_adding_fins` - Aerodynamic surfaces
   * :doc:`/user/tutorials/03_custom_motor` - Use your own motor data
   * :doc:`/user/tutorials/04_parachute_recovery` - Recovery system
   * :doc:`/user/tutorials/05_weather_data` - Real atmospheric conditions

2. **Study Example Rockets**
   
   Analyze pre-configured rockets in ``data/rockets/``:
   
   .. code-block:: bash

      # Explore example configurations
      ls data/rockets/
      # calisto, prometheus, valetudo, etc.
   
   Each includes complete YAML config and explanation.

3. **Understand the Physics** (TODO)
   
   Read background theory:
   
   * :doc:`/background/rocket_physics` - Forces and motion
   * :doc:`/background/aerodynamics` - Drag and stability
   * :doc:`/background/simulation_theory` - Numerical methods

4. **Experiment with Parameters**
   
   Create ``configs/learning/experiments.yaml`` and try:
   
   * Varying launch angles (60°, 75°, 85°, 90°)
   * Different motor sizes (impulse classes H, I, J, K, L, M)
   * Fin configurations (3 vs 4 fins, different spans)
   * Mass variations (simulate payload changes)

5. **Master the Tools**
   
   Learn advanced features:
   
   * :doc:`/user/how_to_guides/custom_plots` - Visualization (TODO)
   * :doc:`/user/how_to_guides/data_analysis` - Processing results (TODO)
   * :doc:`/user/how_to_guides/parameter_study` - Sensitivity analysis (TODO)

**Estimated Time**: 2-3 weeks of occasional practice

.. _path-competition:

Path 2: Building a Competition Rocket
--------------------------------------

**Your Goal**: Design, simulate, and validate a rocket for competition (IREC, EuRoC, etc.).

Competition Workflow
~~~~~~~~~~~~~~~~~~~~

1. **Start with Similar Rocket** (TODO)
   
   Find a similar competition rocket as baseline:
   
   .. code-block:: bash

      # Copy competition template
      cp configs/templates/competition_rocket.yaml configs/my_team_rocket.yaml
   
   Study examples:
   
   * ``data/rockets/prometheus/`` - EuRoC 9km category
   * ``data/rockets/valetudo/`` - IREC 10k SRAD

2. **Input Your Design Parameters** (TODO)
   
   Follow the guide:
   
   * :doc:`/user/how_to_guides/measure_rocket_params` - How to measure your actual rocket (TODO)
   * :doc:`/user/how_to_guides/motor_selection` - Choose optimal motor (TODO)
   * :doc:`/user/configuration/index` - Complete parameter reference (TODO)

3. **Validate Design**
   
   Check critical parameters:
   
   * **Static margin** ≥ 2.0 calibers (validator enforces this)
   * **Apogee** within competition requirements ± 10%
   * **Max velocity** < Mach 0.8 (unless designed for transonic)
   * **Landing impact** < 10 m/s (safe recovery)

4. **Optimize with Parameter Sweeps** (TODO)
   
   Find optimal configuration:
   
   .. code-block:: bash

      python scripts/parameter_sweep.py \
          --config configs/my_team_rocket.yaml \
          --vary "simulation.inclination" --range 80 90 \
          --vary "rocket.mass" --range 14 16 \
          --target-apogee 3000
   
   See :doc:`/user/how_to_guides/optimization` (TODO)

5. **Account for Uncertainty** (TODO - Monte Carlo)
   
   Run Monte Carlo analysis to quantify uncertainty:
   
   * Manufacturing tolerances (mass ± 2%, CP ± 5mm)
   * Weather variations (wind, temperature, pressure)
   * Motor performance (thrust ± 5%)
   
   See :doc:`/user/how_to_guides/monte_carlo` (TODO)

6. **Use Real Launch Site Weather** (TODO)
   
   Get atmospheric data for your competition:
   
   .. code-block:: yaml

      environment:
        latitude: 32.9406      # Spaceport America Cup
        longitude: -106.9195
        elevation: 1400
        atmospheric_model_type: "Forecast"
        atmospheric_model_file: "GFS"
        date: [2025, 6, 21, 10]  # Competition date
   
   See :doc:`/user/how_to_guides/weather_integration` (TODO)

7. **Generate Competition Report** (TODO)
   
   Create professional documentation:
   
   .. code-block:: bash

      python scripts/generate_report.py \
          --config configs/my_team_rocket.yaml \
          --output reports/competition_submission.pdf \
          --include trajectory plots stability analysis
   
   See :doc:`/user/how_to_guides/generate_reports` (TODO)

**Estimated Time**: 1-2 weeks for complete design iteration

.. _path-research:

Path 3: Research and Advanced Analysis
---------------------------------------

**Your Goal**: Publish-quality analysis, custom modifications, advanced simulations.

Research Workflow
~~~~~~~~~~~~~~~~~

1. **Master the API** (TODO)
   
   Go beyond YAML configs and use Python API directly:
   
   .. code-block:: python

      from src.config_loader import load_config
      from src.flight_simulator import FlightSimulator
      
      config = load_config("configs/research_vehicle.yaml")
      simulator = FlightSimulator(config)
      flight = simulator.run()
      
      # Custom analysis
      import numpy as np
      max_q = np.max(flight.dynamic_pressure)  # Maximum dynamic pressure
   
   See :doc:`/reference/api/index` (TODO)

2. **Custom Atmospheric Models** (TODO)
   
   Implement your own atmosphere:
   
   .. code-block:: python

      from rocketpy import Environment
      
      env = Environment(latitude=X, longitude=Y)
      
      # Custom pressure profile from your measurements
      env.set_atmospheric_model(
          type="custom_atmosphere",
          pressure=my_pressure_data,
          temperature=my_temperature_data,
          wind_u=my_wind_u_data,
          wind_v=my_wind_v_data
      )
   
   See :doc:`/user/advanced/custom_atmosphere` (TODO)

3. **Advanced Control Systems** (TODO)
   
   Implement custom air brakes controllers:
   
   * Model Predictive Control (MPC)
   * Adaptive control
   * Machine learning-based control
   
   See :doc:`/user/advanced/custom_controllers` (TODO)

4. **Sensitivity Analysis** (TODO)
   
   Understand parameter influence:
   
   .. code-block:: python

      from src.sensitivity import SensitivityAnalyzer
      
      analyzer = SensitivityAnalyzer(config)
      results = analyzer.run_sobol_analysis(
          parameters=['rocket.mass', 'motor.thrust_scale', 'environment.wind_speed'],
          n_samples=1000
      )
      analyzer.plot_sensitivity_indices()
   
   See :doc:`/user/advanced/sensitivity_analysis` (TODO)

5. **Batch Processing and Automation**
   
   Run hundreds of simulations:
   
   .. code-block:: bash

      # Process multiple configurations
      for config in configs/batch/*.yaml; do
          python scripts/run_single_simulation.py --config $config --name $(basename $config .yaml)
      done
   
   See :doc:`/user/how_to_guides/batch_processing` (TODO)

6. **Publication-Quality Figures** (TODO)
   
   Create publication-ready plots:
   
   .. code-block:: python

      from src.visualizer import PublicationPlotter
      
      plotter = PublicationPlotter(style='ieee')
      plotter.plot_trajectory_comparison(
          simulations=[flight1, flight2, flight3],
          labels=['Baseline', 'With Air Brakes', 'Optimized'],
          save='figures/trajectory_comparison.pdf'
      )
   
   See :doc:`/user/advanced/publication_plots` (TODO)

7. **Extend RocketPy** (TODO)
   
   Add custom physics models:
   
   * Non-standard drag models
   * Ablative thermal protection
   * Multi-stage rockets
   * Custom force/moment models
   
   See :doc:`/developer/extending_rocketpy` (TODO)

**Estimated Time**: Ongoing research workflow

.. _path-development:

Path 4: Contributing to rocket-sim
-----------------------------------

**Your Goal**: Improve rocket-sim, add features, fix bugs.

Contribution Workflow
~~~~~~~~~~~~~~~~~~~~~

1. **Read Developer Documentation** (TODO)
   
   Understand the codebase:
   
   * :doc:`/developer/architecture` - System design
   * :doc:`/developer/coding_standards` - Code style (snake_case, NumPy docstrings)
   * :doc:`/developer/testing` - How to write tests
   * :doc:`/developer/contributing` - Contribution guidelines

2. **Set Up Development Environment**
   
   .. code-block:: bash

      git clone https://github.com/matteodisante/rocket-sim.git
      cd rocket-sim
      
      # Install dev dependencies
      pip install -r requirements.txt
      pip install -r requirements-docs.txt
      
      # Install pre-commit hooks (code formatting)
      pre-commit install
      
      # Run tests
      pytest tests/

3. **Find Something to Work On**
   
   Check GitHub Issues for:
   
   * ``good-first-issue`` - Easy entry points
   * ``help-wanted`` - Requested features
   * ``bug`` - Known bugs needing fixes

4. **Follow Development Workflow**
   
   .. code-block:: bash

      # Create feature branch
      git checkout -b feature/my-awesome-feature
      
      # Make changes, write tests
      # ...
      
      # Run tests
      pytest tests/
      
      # Run linters
      ruff check .
      ruff format .
      
      # Commit and push
      git commit -m "Add awesome feature"
      git push origin feature/my-awesome-feature
      
      # Open Pull Request on GitHub

5. **Documentation for New Features**
   
   If you add a feature, document it:
   
   * NumPy-style docstrings in code
   * User guide if it's user-facing
   * Example in ``examples/``
   * Test coverage ≥ 80%

6. **Join the Community**
   
   * GitHub Discussions for questions
   * Code reviews on Pull Requests
   * Share your use cases and feedback

**Estimated Time**: Ongoing contributions

Additional Resources
--------------------

Official Documentation
~~~~~~~~~~~~~~~~~~~~~~

* **RocketPy Docs**: https://docs.rocketpy.org/
* **NumPy Docs**: https://numpy.org/doc/stable/
* **SciPy Docs**: https://docs.scipy.org/

Learning Materials
~~~~~~~~~~~~~~~~~~

* **RocketPy Jupyter Notebooks**: ``docs/notebooks/`` in RocketPy repo
* **rocket-sim Examples**: ``examples/`` directory
* **Motor Database**: http://www.thrustcurve.org/

Books and References
~~~~~~~~~~~~~~~~~~~~

* Sutton & Biblarz - *Rocket Propulsion Elements* (motor theory)
* Niskanen - *Development of an Open Source Model Rocket Simulation Software* (OpenRocket thesis)
* Barrowman - *Theoretical Prediction of Center of Pressure* (stability theory)

Community
~~~~~~~~~

* **GitHub Issues**: Bug reports and feature requests
* **GitHub Discussions**: Questions and community help
* **RocketPy Discord**: General rocketry simulation discussion

Getting Help
------------

Still not sure where to start?

1. **Browse the examples**: ``examples/`` and ``configs/``
2. **Read existing configurations**: Learn from working setups
3. **Ask on GitHub Discussions**: Community can guide you
4. **Check RocketPy docs**: For underlying library details

.. tip::
   **Pro tip**: Start with small, working examples and gradually increase complexity.
   Don't try to simulate your dream rocket on day one!

What's Next?
------------

No matter which path you chose, remember:

* **Start simple** - Master basics before advanced features
* **Validate often** - Check results make physical sense
* **Read docs** - Most questions are answered in documentation
* **Ask questions** - Community is here to help
* **Share results** - Your experience helps others learn

Happy simulating! 🚀

.. seealso::

   * :doc:`/user/index` - Complete user documentation (TODO)
   * :doc:`/reference/index` - API reference (TODO)
   * :doc:`/developer/index` - Developer guides (TODO)
