Glossary
========

.. glossary::

   Apogee
      The highest point in a rocket's trajectory, where vertical velocity becomes zero
      before descent begins.

   Burn Time
      Duration of motor thrust phase, from ignition to propellant exhaustion.

   Caliber
      One body diameter. Used as unit for static margin (e.g., "2.5 calibers").

   Center of Gravity (CG)
      Point where the rocket's mass is balanced. Also called center of mass.
      Changes during flight as propellant burns.

   Center of Pressure (CP)
      Point where total aerodynamic forces act on the rocket. Depends on 
      angle of attack and Mach number.

   Drag Coefficient
      Dimensionless number quantifying aerodynamic drag. Depends on shape,
      surface roughness, and flow conditions (Reynolds number, Mach number).

   ISA
      International Standard Atmosphere - standardized atmospheric model
      defining pressure, temperature, and density vs altitude.

   Motor Impulse Class
      Classification by total impulse: H (160-320 Ns), I (320-640 Ns), 
      J (640-1280 Ns), K (1280-2560 Ns), L (2560-5120 Ns), M (5120-10240 Ns).

   RASP
      Rocket Altitude Simulation Program - defines standard ``.eng`` format
      for motor thrust curves.

   Static Margin
      Distance from CG to CP, measured in calibers. Must be > 2 for stable flight.
      Formula: (CP - CG) / diameter.

   6-DOF
      Six Degrees of Freedom - simulation tracking 3 translational (x, y, z)
      and 3 rotational (pitch, yaw, roll) movements.

   Thrust Curve
      Graph of motor thrust force vs time, defining propulsion profile.

   Total Impulse
      Integral of thrust over burn time. Measured in newton-seconds (Ns).
      Determines motor impulse class.
