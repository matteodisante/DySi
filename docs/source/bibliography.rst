Bibliography
============

Key References
--------------

Rocket Propulsion
~~~~~~~~~~~~~~~~~

.. [Sutton2016] Sutton, G. P., & Biblarz, O. (2016). 
   *Rocket Propulsion Elements* (9th ed.). Wiley.
   
   The definitive reference on rocket motor theory, thermodynamics, 
   and performance analysis.

.. [Turner2009] Turner, M. J. L. (2009).
   *Rocket and Spacecraft Propulsion: Principles, Practice and New Developments* (3rd ed.). Springer.
   
   Comprehensive coverage of propulsion systems for all rocket types.

Rocket Stability and Aerodynamics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. [Barrowman1967] Barrowman, J. S. (1967).
   *The Theoretical Prediction of the Center of Pressure*.
   NARAM-9 Report.
   
   Classic work on predicting CP location for fin-stabilized rockets.

.. [Niskanen2009] Niskanen, S. (2009).
   *Development of an Open Source Model Rocket Simulation Software*.
   Master's Thesis, Helsinki University of Technology.
   
   Theoretical foundation for OpenRocket simulator, includes excellent
   aerodynamics and stability analysis.

.. [Box1999] Box, S., Bishop, C. M., & Hunt, H. (1999).
   *Stochastic Six-Degree-of-Freedom Flight Simulator for Passively Controlled High-Power Rockets*.
   Journal of Guidance, Control, and Dynamics, 22(5), 715-722.

Atmospheric Models
~~~~~~~~~~~~~~~~~~

.. [ISA1976] U.S. Standard Atmosphere (1976).
   *U.S. Standard Atmosphere, 1976*.
   NOAA/NASA/USAF.
   
   Standard atmospheric model used worldwide for aerospace applications.

.. [Hersbach2020] Hersbach, H., et al. (2020).
   *The ERA5 global reanalysis*.
   Quarterly Journal of the Royal Meteorological Society, 146(730), 1999-2049.
   
   Describes ERA5 reanalysis data used for historical weather simulations.

Numerical Methods
~~~~~~~~~~~~~~~~~

.. [Dormand1980] Dormand, J. R., & Prince, P. J. (1980).
   *A family of embedded Runge-Kutta formulae*.
   Journal of Computational and Applied Mathematics, 6(1), 19-26.
   
   Describes RK45 method used for trajectory integration in RocketPy.

Software and Tools
~~~~~~~~~~~~~~~~~~

.. [RocketPy] RocketPy Team. (2024).
   *RocketPy: Trajectory Simulation for High-Power Rocketry*.
   https://github.com/RocketPy-Team/RocketPy
   
   The underlying simulation library for rocket-sim.

.. [OpenRocket] OpenRocket Development Team.
   *OpenRocket Technical Documentation*.
   https://wiki.openrocket.info/
   
   Open source rocket design and simulation software.

Online Resources
----------------

Motor Data
~~~~~~~~~~

* **ThrustCurve.org** - Database of commercial rocket motors with certified thrust curves
  https://www.thrustcurve.org/

* **Cesaroni Technology** - High-power hybrid and solid motors
  https://www.cesaroni.net/

* **AeroTech** - High-power solid rocket motors
  http://www.aerotech-rocketry.com/

Atmospheric Data
~~~~~~~~~~~~~~~~

* **Wyoming Weather Soundings** - Upper air observations
  http://weather.uwyo.edu/upperair/sounding.html

* **NOAA GFS Forecasts** - Global Forecast System
  https://www.ncei.noaa.gov/products/weather-climate-models/global-forecast

* **Copernicus ERA5** - ECMWF Reanalysis data
  https://cds.climate.copernicus.eu/

Standards and Regulations
~~~~~~~~~~~~~~~~~~~~~~~~~~

* **NAR High Power Rocketry Safety Code**
  https://www.nar.org/safety-information/high-power-rocket-safety-code/

* **Tripoli Rocketry Association Safety Code**
  https://www.tripoli.org/Safety

* **FAA Regulations** - Title 14 CFR Part 101 (Moored Balloons, Kites, Amateur Rockets)
  https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-101

Further Reading
---------------

For deeper understanding of specific topics:

* **Rocket Physics**: Start with [Sutton2016]_ and [Turner2009]_
* **Stability Analysis**: Read [Barrowman1967]_ and [Niskanen2009]_
* **Simulation Theory**: Study [Box1999]_ and [Dormand1980]_
* **RocketPy Details**: See [RocketPy]_ documentation and source code

Academic Citations
------------------

If you use rocket-sim in academic work, please cite:

.. code-block:: bibtex

   @software{rocketsim2025,
     title = {rocket-sim: Production-Ready Rocket Trajectory Simulation Framework},
     author = {STARPI Team},
     year = {2025},
     url = {https://github.com/matteodisante/rocket-sim},
     note = {Built on RocketPy}
   }

   @software{rocketpy2024,
     title = {RocketPy: Trajectory Simulation for High-Power Rocketry},
     author = {RocketPy Team},
     year = {2024},
     url = {https://github.com/RocketPy-Team/RocketPy}
   }
