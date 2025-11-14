.. _quick-plot-guide:

Quick Plot Reference Card
==========================

A compact reference for interpreting DySi output plots. For detailed explanations,
see :doc:`technical/plot_interpretation`.

.. note::
   
   All plots are in ``outputs/<simulation_name>/curves/`` organized by category.

----

🚀 Critical Plots to Check First
---------------------------------

1. **stability_envelope.png** (stability/)
   
   ✅ Entire curve in **green zones** (> 1.5 cal)
   
   ⚠️ Yellow zones = marginal (1.0-1.5 cal)
   
   ❌ Red zones = unstable (< 1.0 cal) - **DO NOT FLY**

2. **thrust_curve.png** (motor/)
   
   ✅ Matches motor specifications
   
   ✅ Smooth curve without irregularities
   
   📊 Total impulse = area under curve

3. **aerodynamic_forces.png** (flight/)
   
   ✅ Peak forces at Max-Q
   
   ⚠️ Check bending moments for structural safety

----

📊 Plot Categories
------------------

Motor Plots (motor/)
~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - ``thrust_curve.png``
     - Thrust vs time with performance metrics
   * - ``mass_evolution.png``
     - Total/propellant mass decrease
   * - ``kn_curve.png``
     - Burn area to throat area ratio
   * - ``center_of_mass.png``
     - Motor COM position evolution

Rocket Plots (rocket/)
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - ``drag_coefficient.png``
     - Cd vs Mach (peaks at M≈1.0)
   * - ``cp_position_vs_mach.png``
     - CP movement in transonic region

Stability Plots (stability/)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - ``stability_envelope.png``
     - **MOST IMPORTANT** - Safety zones + critical events
   * - ``stability_margin_surface.png``
     - 3D: Margin vs Mach vs Time
   * - ``stability_cp_travel.png``
     - CP position vs Mach with regime zones

Flight Plots (flight/)
~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - ``trajectory_3d.png``
     - 3D flight path with XY/XZ/YZ projections
   * - ``position_data.png``
     - Position components (X, Y, Z) vs time
   * - ``linear_kinematics_data.png``
     - Velocities (Vx,Vy,Vz) and accelerations (Ax,Ay,Az)
   * - ``flight_path_angle_data.png``
     - Flight path vs attitude angle, lateral angle
   * - ``attitude_data.png``
     - Euler angles (ψ, θ, φ)
   * - ``angular_kinematics_data.png``
     - Angular velocities (ω) and accelerations (α)
   * - ``aerodynamic_forces.png``
     - Lift, drag, bending moment, spin moment
   * - ``rail_buttons_forces.png``
     - Rail button normal/shear forces (if applicable)
   * - ``energy_data.png``
     - Kinetic, potential, thrust/drag power
   * - ``fluid_mechanics_data.png``
     - Mach, Reynolds, pressures, AoA
   * - ``stability_and_control_data.png``
     - Stability margin + frequency response

Environment Plots (environment/)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 30 70
   :header-rows: 0

   * - ``wind_profile.png``
     - Wind speed and direction vs altitude
   * - ``atmospheric_profile.png``
     - Temperature, pressure, density vs altitude

----

⚡ Quick Interpretation Guide
-----------------------------

Stability Margin Values
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Range
     - Status
     - Action
   * - < 1.0 cal
     - ❌ Unstable
     - DO NOT FLY - Redesign required
   * - 1.0-1.5 cal
     - ⚠️ Marginal
     - Risky - subsonic only, consider improving
   * - 1.5-2.0 cal
     - ✅ Safe
     - Acceptable for flight
   * - 2.0-2.5 cal
     - ✅✅ Optimal
     - Excellent design target
   * - > 2.5 cal
     - 🔹 Overstable
     - Very stable (may reduce maneuverability)

Flight Regime Indicators
~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Mach Range
     - Description
   * - M < 0.8
     - **Subsonic** - Normal aerodynamics
   * - M = 0.8-1.2
     - **Transonic** - Critical region, peak drag, CP shifts
   * - M > 1.2
     - **Supersonic** - Stabilized aerodynamics

Typical Values
~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Parameter
     - Normal Range
     - Warning Signs
   * - Attitude Angle
     - < 5°
     - > 10° may indicate instability
   * - Angle of Attack
     - < 3° (after rail)
     - > 10° excessive weathercocking
   * - Drag Coefficient
     - 0.3-0.5 (subsonic)
     - Spikes > 1.0 unusual
   * - Angular Velocity
     - Small (< 1 rad/s)
     - Growing oscillations
   * - Stability Margin
     - 1.5-2.5 cal
     - < 1.5 marginal, < 1.0 unsafe

----

🔍 Common Patterns
------------------

Normal Flight Indicators
~~~~~~~~~~~~~~~~~~~~~~~~

✅ Stability margin minimum at burnout, increases in transonic

✅ Drag coefficient peaks around M = 1.0

✅ CP shifts aft (negative) in transonic → improves stability

✅ Attitude angle stays small (< 5°)

✅ Energy transfers smoothly from kinetic to potential

✅ Thrust curve matches motor specs

Warning Signs
~~~~~~~~~~~~~

⚠️ Stability dips into yellow zone (< 1.5 cal)

⚠️ Large attitude oscillations (> 10°)

⚠️ High angle of attack (> 10°)

⚠️ Irregular thrust profile

⚠️ Growing angular velocity oscillations

Critical Issues
~~~~~~~~~~~~~~~

❌ Stability margin in red zone (< 1.0 cal) - **STOP**

❌ Extreme bending moments - structural failure risk

❌ AoA > 20° - complete instability

❌ Negative stability margin anywhere

----

📋 Analysis Checklist
---------------------

Before Flight Approval
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ☐ Stability envelope shows margin > 1.5 cal throughout flight
   ☐ Thrust curve matches motor specifications
   ☐ Max-Q and bending moments within structural limits
   ☐ Attitude angle stays small (< 5°)
   ☐ No critical warnings in any plot
   ☐ Drag coefficient reasonable (< 0.8 peak)
   ☐ CP travel understood and accounted for
   ☐ Energy conservation holds (smooth decrease)

Performance Validation
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   ☐ Max Mach number as expected
   ☐ Apogee altitude matches predictions
   ☐ Burnout time matches motor specs
   ☐ Max-Q occurs at reasonable altitude
   ☐ Flight attitude stable throughout
   ☐ Angular kinematics show damped oscillations

----

🔗 Related Documentation
------------------------

**Detailed Guides:**

- :doc:`technical/plot_interpretation` - Full interpretation guide
- :doc:`technical/stability_analysis` - Stability theory
- :doc:`how_to_guides/validate_design` - Design validation workflow

**Tutorials:**

- :doc:`tutorials/02_understanding_outputs` - Output tutorial
- :doc:`tutorials/01_basic_flight` - First simulation walkthrough

**Configuration:**

- :doc:`configuration/index` - All configuration parameters

----

💡 Quick Tips
-------------

.. tip::
   **New to plot interpretation?**
   
   Start with these three plots in order:
   
   1. ``stability/stability_envelope.png`` - Is it safe?
   2. ``motor/thrust_curve.png`` - Does motor work correctly?
   3. ``flight/fluid_mechanics_data.png`` - How did flight perform?

.. tip::
   **Seeing unexpected results?**
   
   Check these common issues:
   
   - Wrong coordinate system in rocket definition
   - CP position reference point confusion
   - Motor thrust curve interpolation errors
   - Atmospheric model not loaded correctly

.. tip::
   **Preparing for competition?**
   
   Generate a complete analysis package:
   
   .. code-block:: bash
   
      python scripts/run_single_simulation.py \
          --config my_rocket.yaml \
          --name competition_analysis \
          --plots \
          --export-all

   All plots will be in ``outputs/competition_analysis/curves/``
