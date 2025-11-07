Sensitivity Analysis
====================

Sensitivity analysis identifies which parameters most affect simulation outcomes.

Overview
--------

While Monte Carlo tells you "what happens" with uncertainty, sensitivity analysis tells you "why it happens" by ranking parameter importance.

**Key Questions Answered:**

- Which parameter should we measure most carefully?
- Where should we focus quality control?
- Which uncertainties drive outcome variability?

Methods
-------

Sobol Indices
~~~~~~~~~~~~~

Variance-based global sensitivity analysis:

- **First-order (S1)**: Direct effect of parameter
- **Total-order (ST)**: Total effect including interactions

.. code-block:: yaml

    sensitivity_analysis:
      method: "sobol"
      n_samples: 2000
      target_variable: "apogee_m"
      parameters:
        - "motor.thrust_source"
        - "rocket.mass_kg"
        - "environment.wind_speed_mps"

Local Average Effect (LAE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Measures local parameter importance:

.. code-block:: yaml

    sensitivity_analysis:
      method: "lae"
      n_samples: 1000
      target_variable: "apogee_m"
      parameters:
        - "motor.thrust_source"
        - "rocket.mass_kg"

Running Analysis
----------------

.. code-block:: bash

    python scripts/run_sensitivity_analysis.py \
        --config configs/sensitivity_example.yaml \
        --method sobol \
        --n-samples 2000 \
        --output sensitivity_results/

Example Results
---------------

.. code-block:: text

    📊 Sensitivity Analysis Results (Sobol Indices)
    Target: apogee_m

    Parameter Importance Ranking:
    1. motor.thrust_source    S1: 0.673  ST: 0.701  ████████████████
    2. rocket.mass_kg         S1: 0.189  ST: 0.215  ████
    3. environment.wind_speed S1: 0.042  ST: 0.068  █
    4. simulation.inclination S1: 0.015  ST: 0.024

    Interpretation:
    - Motor thrust accounts for ~67% of apogee variance
    - Rocket mass contributes ~19%
    - Wind and inclination have minor effects (<5%)

Interpretation Guide
--------------------

Sobol Indices
~~~~~~~~~~~~~

- **S1 > 0.1**: Important parameter (direct effect)
- **ST - S1 > 0.05**: Strong interactions with other parameters
- **ST < 0.01**: Negligible effect

Focus On
~~~~~~~~

1. **High S1**: Direct effect - control this parameter carefully
2. **High (ST - S1)**: Strong interactions - consider coupled effects
3. **Low ST**: Negligible - can use nominal value

Next Steps
----------

- :doc:`monte_carlo` - Run uncertainty quantification
- :doc:`../user_guide/configuration` - Configuration options
