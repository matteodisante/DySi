Monte Carlo Analysis
====================

This example demonstrates uncertainty quantification using Monte Carlo simulation.

What is Monte Carlo Analysis?
------------------------------

Monte Carlo analysis quantifies uncertainty by:

1. Defining probability distributions for uncertain parameters
2. Randomly sampling from these distributions
3. Running many simulations with different parameter combinations
4. Analyzing the statistical distribution of results

This helps answer questions like:

- What is the expected apogee with 95% confidence?
- How much does wind affect the landing zone?
- Which parameters contribute most to uncertainty?

Configuration File
------------------

Extend your base configuration with parameter variations:

.. code-block:: yaml

    # Base configuration (motor, rocket, environment, simulation)
    motor:
      thrust_source: "Cesaroni_M1670.eng"
      # ... other motor parameters ...
      position_m: -1.255

    rocket:
      # ... rocket parameters ...
      mass_kg: 19.197

    environment:
      # ... environment parameters ...
      latitude_deg: 39.3897
      longitude_deg: -8.2889

    simulation:
      # ... simulation parameters ...
      rail_length_m: 5.2

    # Monte Carlo specific configuration
    parameter_variations:
      # Motor thrust uncertainty (±3.3%)
      motor.thrust_source:
        type: "normal"
        mean: 1.0
        std: 0.033

      # Rocket mass uncertainty (±0.5 kg)
      rocket.mass_kg:
        type: "normal"
        mean: 19.197
        std: 0.5

      # Wind speed variation (0-10 m/s uniform)
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

      # Wind direction (0-360° uniform)
      environment.wind_direction_deg:
        type: "uniform"
        min: 0
        max: 360

      # Rail inclination uncertainty (±0.5°)
      simulation.inclination_deg:
        type: "normal"
        mean: 84.7
        std: 0.5

Distribution Types
------------------

Normal Distribution
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parameter_variations:
      rocket.mass_kg:
        type: "normal"
        mean: 19.197
        std: 0.5

Use when:

- Measurement uncertainties
- Manufacturing tolerances
- Most natural variations

Uniform Distribution
~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parameter_variations:
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

Use when:

- No prior knowledge of distribution
- Bounded but equally likely values
- Conservative worst-case analysis

Truncated Normal
~~~~~~~~~~~~~~~~

.. code-block:: yaml

    parameter_variations:
      rocket.mass_kg:
        type: "truncated_normal"
        mean: 19.197
        std: 0.5
        min: 18.0
        max: 20.0

Use when:

- Normal distribution but with physical bounds
- Prevents unrealistic values

Running Monte Carlo Analysis
-----------------------------

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    python scripts/run_monte_carlo.py \
        --config configs/monte_carlo_example.yaml \
        --n-sims 1000 \
        --plots \
        --output monte_carlo_results/

Python Script
~~~~~~~~~~~~~

.. code-block:: python

    from src.monte_carlo_runner import MonteCarloRunner

    # Initialize runner
    runner = MonteCarloRunner(
        config_path="configs/monte_carlo_example.yaml",
        n_simulations=1000,
        output_dir="monte_carlo_results"
    )

    # Run Monte Carlo analysis
    results = runner.run()

    # Access results
    apogees = [r["apogee_m"] for r in results]
    print(f"Mean apogee: {np.mean(apogees):.2f} m")
    print(f"Std dev: {np.std(apogees):.2f} m")
    print(f"95% CI: [{np.percentile(apogees, 2.5):.2f}, {np.percentile(apogees, 97.5):.2f}] m")

Expected Output
---------------

.. code-block:: text

    🚀 Monte Carlo Simulation
    ├─ Configuration: configs/monte_carlo_example.yaml
    ├─ Simulations: 1000
    └─ Output: monte_carlo_results/

    Running simulations: 100%|████████████| 1000/1000 [02:15<00:00, 7.38it/s]

    📊 Results Summary:

    Apogee (m):
    ├─ Mean: 2541.32 ± 156.78
    ├─ Median: 2538.91
    ├─ 95% CI: [2235.67, 2847.23]
    ├─ Min: 2089.45
    └─ Max: 2976.34

    Max Velocity (m/s):
    ├─ Mean: 289.67 ± 12.34
    ├─ Median: 289.45
    └─ 95% CI: [266.12, 313.89]

    Landing Dispersion:
    ├─ Mean distance: 845.32 m
    ├─ Max distance: 2134.56 m
    └─ 95% ellipse: 1654.23 m

    💾 Results saved to: monte_carlo_results/monte_carlo_*.json

Generated Plots
---------------

The Monte Carlo analysis generates:

1. **Apogee Distribution**: Histogram with statistics
2. **Velocity Distribution**: Maximum velocity histogram
3. **Landing Dispersion**: 2D scatter plot of impact points
4. **Parameter Correlation**: Correlation matrix heatmap
5. **Time Series**: Trajectory envelopes
6. **Sensitivity Tornado**: Parameter importance ranking

Interpreting Results
--------------------

Mean vs Median
~~~~~~~~~~~~~~

- **Mean**: Average value (sensitive to outliers)
- **Median**: Middle value (robust to outliers)

If mean ≠ median, the distribution is skewed.

Confidence Intervals
~~~~~~~~~~~~~~~~~~~~

**95% CI [2235, 2847]** means:

- 95% of flights will reach between 2235m and 2847m
- 2.5% will be lower, 2.5% will be higher

Landing Dispersion
~~~~~~~~~~~~~~~~~~

The 2D scatter plot shows where the rocket will land:

- Each point = one simulation
- Ellipse = 95% confidence region
- Useful for safety analysis and recovery planning

Correlation Analysis
~~~~~~~~~~~~~~~~~~~~

The correlation matrix shows which parameters vary together:

- **+1**: Perfect positive correlation
- **0**: No correlation
- **-1**: Perfect negative correlation

Example: Wind speed and landing distance typically correlate positively.

Advanced Features
-----------------

Parallel Execution
~~~~~~~~~~~~~~~~~~

Monte Carlo simulations automatically use all CPU cores:

.. code-block:: python

    # Automatic parallelization
    runner = MonteCarloRunner(
        config_path="configs/example.yaml",
        n_simulations=10000  # Will use all cores
    )

Progress Monitoring
~~~~~~~~~~~~~~~~~~~

Track progress in real-time:

.. code-block:: python

    runner = MonteCarloRunner(
        config_path="configs/example.yaml",
        n_simulations=1000,
        verbose=True  # Enable progress bar
    )

Error Handling
~~~~~~~~~~~~~~

The framework handles simulation failures gracefully:

- Failed simulations are logged but don't stop the analysis
- Results include only successful simulations
- Summary reports failure rate

Export Results
~~~~~~~~~~~~~~

Export for external analysis:

.. code-block:: python

    # Export to CSV
    runner.export_results_csv("results.csv")

    # Export for sensitivity analysis
    runner.export_for_sensitivity("sensitivity_data.json")

    # Export raw data
    runner.export_full_results("full_results.json")

Best Practices
--------------

Sample Size
~~~~~~~~~~~

- **100-500**: Quick exploratory analysis
- **1000-5000**: Production analysis
- **10000+**: High-precision analysis or sensitivity studies

Typical convergence: ~1000 simulations for 1% precision on mean.

Parameter Selection
~~~~~~~~~~~~~~~~~~~

Focus on parameters with:

1. **High uncertainty**: Wide distribution
2. **High sensitivity**: Strong effect on outputs
3. **Physical importance**: Safety-critical parameters

Common parameters to vary:

- Motor thrust (manufacturing tolerance)
- Rocket mass (measurement uncertainty)
- Wind speed/direction (weather variability)
- Drag coefficient (aerodynamic uncertainty)
- Parachute deployment (timing/reliability)

Validation
~~~~~~~~~~

Verify your Monte Carlo setup:

1. **Sanity check**: Do results make physical sense?
2. **Convergence**: Does increasing N change results?
3. **Extreme cases**: Are min/max values realistic?
4. **Correlations**: Do correlated parameters make sense?

Example: Complete Monte Carlo Study
------------------------------------

.. code-block:: yaml

    motor:
      thrust_source: "Cesaroni_M1670.eng"
      burn_out_time_s: 3.9
      dry_mass_kg: 1.815
      # ... other motor params ...
      position_m: -1.255

    rocket:
      radius_m: 0.0635
      mass_kg: 19.197
      # ... other rocket params ...

    environment:
      latitude_deg: 39.3897
      longitude_deg: -8.2889
      elevation_m: 0

    simulation:
      rail_length_m: 5.2
      inclination_deg: 84.7
      heading_deg: 90

    parameter_variations:
      # Motor uncertainties
      motor.thrust_source:
        type: "normal"
        mean: 1.0
        std: 0.033

      motor.dry_mass_kg:
        type: "normal"
        mean: 1.815
        std: 0.05

      # Rocket uncertainties
      rocket.mass_kg:
        type: "normal"
        mean: 19.197
        std: 0.5

      rocket.radius_m:
        type: "normal"
        mean: 0.0635
        std: 0.001

      # Environment uncertainties
      environment.wind_speed_mps:
        type: "uniform"
        min: 0
        max: 10

      environment.wind_direction_deg:
        type: "uniform"
        min: 0
        max: 360

      # Launch uncertainties
      simulation.rail_length_m:
        type: "normal"
        mean: 5.2
        std: 0.1

      simulation.inclination_deg:
        type: "normal"
        mean: 84.7
        std: 0.5

      simulation.heading_deg:
        type: "uniform"
        min: 85
        max: 95

Run with:

.. code-block:: bash

    python scripts/run_monte_carlo.py \
        --config configs/complete_monte_carlo.yaml \
        --n-sims 5000 \
        --plots \
        --output mc_results/

Next Steps
----------

- :doc:`sensitivity_analysis` - Identify critical parameters
- :doc:`weather_integration` - Add realistic weather variations
- :doc:`../user_guide/configuration` - All configuration options
