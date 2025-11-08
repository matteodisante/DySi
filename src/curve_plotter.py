"""Curve plotting utilities for state exporter.

This module provides utilities for plotting motor thrust curves, drag coefficients,
wind profiles, and atmospheric properties.
"""

from pathlib import Path
from typing import Optional
import logging

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


class CurvePlotter:
    """Generate plots of simulation input curves."""

    def __init__(self, motor, rocket, environment):
        """Initialize CurvePlotter.

        Args:
            motor: RocketPy Motor object
            rocket: RocketPy Rocket object
            environment: RocketPy Environment object
        """
        self.motor = motor
        self.rocket = rocket
        self.environment = environment

    def plot_all_curves(self, output_dir: str) -> dict:
        """Generate all available curve plots.

        Args:
            output_dir: Directory for output PNG files

        Returns:
            Dictionary mapping plot name to file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating curve plots in {output_dir}")

        paths = {}

        # Plot thrust curve
        if self.motor and hasattr(self.motor, 'thrust'):
            thrust_path = self.plot_thrust_curve(output_dir)
            if thrust_path:
                paths['thrust_curve'] = thrust_path

        # Plot drag curves
        if hasattr(self.rocket, 'power_off_drag'):
            drag_off_path = self.plot_drag_curve(
                self.rocket.power_off_drag,
                "Power-Off Drag Coefficient",
                output_dir / "power_off_drag.png"
            )
            if drag_off_path:
                paths['power_off_drag'] = drag_off_path

        if hasattr(self.rocket, 'power_on_drag'):
            drag_on_path = self.plot_drag_curve(
                self.rocket.power_on_drag,
                "Power-On Drag Coefficient",
                output_dir / "power_on_drag.png"
            )
            if drag_on_path:
                paths['power_on_drag'] = drag_on_path

        # Plot wind profile
        if hasattr(self.environment, 'wind_velocity_x') and hasattr(self.environment, 'wind_velocity_y'):
            wind_path = self.plot_wind_profile(output_dir)
            if wind_path:
                paths['wind_profile'] = wind_path

        # Plot atmospheric profile
        if hasattr(self.environment, 'pressure') and hasattr(self.environment, 'temperature'):
            atm_path = self.plot_atmospheric_profile(output_dir)
            if atm_path:
                paths['atmospheric_profile'] = atm_path

        logger.info(f"Generated {len(paths)} curve plots")
        return paths

    def plot_thrust_curve(self, output_dir: Path) -> Optional[Path]:
        """Plot motor thrust curve.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "thrust_curve.png"

            # Get thrust data
            if hasattr(self.motor.thrust, 'get_source'):
                try:
                    thrust_data = self.motor.thrust.get_source()
                except:
                    # Sample thrust function
                    t_max = getattr(self.motor, 'burn_time', (0, 5))[1] if hasattr(self.motor, 'burn_time') else 5
                    t_array = np.linspace(0, t_max, 200)
                    thrust_data = np.column_stack([
                        t_array,
                        [self.motor.thrust(t) for t in t_array]
                    ])
            else:
                # Sample thrust function
                t_max = getattr(self.motor, 'burn_time', (0, 5))[1] if hasattr(self.motor, 'burn_time') else 5
                t_array = np.linspace(0, t_max, 200)
                thrust_data = np.column_stack([
                    t_array,
                    [self.motor.thrust(t) for t in t_array]
                ])

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(thrust_data[:, 0], thrust_data[:, 1], 'b-', linewidth=2)
            ax.set_xlabel('Time (s)', fontsize=12)
            ax.set_ylabel('Thrust (N)', fontsize=12)
            ax.set_title('Motor Thrust Curve', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Thrust curve plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot thrust curve: {e}")
            return None

    def plot_drag_curve(
        self,
        drag_func,
        title: str,
        output_path: Path
    ) -> Optional[Path]:
        """Plot drag coefficient vs Mach number.

        Args:
            drag_func: Drag function (Cd vs Mach)
            title: Plot title
            output_path: Output file path

        Returns:
            Path to created plot or None if failed
        """
        try:
            # Sample Mach numbers
            mach_array = np.linspace(0, 2.0, 200)
            cd_values = [drag_func(m) for m in mach_array]

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(mach_array, cd_values, 'r-', linewidth=2)
            ax.set_xlabel('Mach Number', fontsize=12)
            ax.set_ylabel('Drag Coefficient (Cd)', fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(left=0)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Drag curve plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot drag curve: {e}")
            return None

    def plot_wind_profile(self, output_dir: Path) -> Optional[Path]:
        """Plot wind velocity vs altitude.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "wind_profile.png"

            # Sample altitudes
            altitudes = np.array([0, 100, 500, 1000, 2000, 5000, 10000])
            wind_x = [self.environment.wind_velocity_x(h) for h in altitudes]
            wind_y = [self.environment.wind_velocity_y(h) for h in altitudes]
            wind_speed = np.sqrt(np.array(wind_x)**2 + np.array(wind_y)**2)

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # Plot wind components
            ax1.plot(wind_x, altitudes, 'b-', linewidth=2, label='East (X)', marker='o')
            ax1.plot(wind_y, altitudes, 'r-', linewidth=2, label='North (Y)', marker='s')
            ax1.set_xlabel('Wind Velocity (m/s)', fontsize=12)
            ax1.set_ylabel('Altitude (m)', fontsize=12)
            ax1.set_title('Wind Velocity Components', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend()

            # Plot wind speed
            ax2.plot(wind_speed, altitudes, 'g-', linewidth=2, marker='o')
            ax2.set_xlabel('Wind Speed (m/s)', fontsize=12)
            ax2.set_ylabel('Altitude (m)', fontsize=12)
            ax2.set_title('Total Wind Speed', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Wind profile plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot wind profile: {e}")
            return None

    def plot_atmospheric_profile(self, output_dir: Path) -> Optional[Path]:
        """Plot atmospheric properties vs altitude.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "atmospheric_profile.png"

            # Sample altitudes
            altitudes = np.linspace(0, 10000, 200)
            pressure = [self.environment.pressure(h) for h in altitudes]
            temperature = [self.environment.temperature(h) for h in altitudes]
            density = [self.environment.density(h) for h in altitudes]

            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))

            # Temperature
            ax1.plot(temperature, altitudes, 'r-', linewidth=2)
            ax1.set_xlabel('Temperature (K)', fontsize=12)
            ax1.set_ylabel('Altitude (m)', fontsize=12)
            ax1.set_title('Temperature Profile', fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)

            # Pressure
            ax2.plot(pressure, altitudes, 'b-', linewidth=2)
            ax2.set_xlabel('Pressure (Pa)', fontsize=12)
            ax2.set_ylabel('Altitude (m)', fontsize=12)
            ax2.set_title('Pressure Profile', fontsize=14, fontweight='bold')
            ax2.grid(True, alpha=0.3)

            # Density
            ax3.plot(density, altitudes, 'g-', linewidth=2)
            ax3.set_xlabel('Density (kg/m³)', fontsize=12)
            ax3.set_ylabel('Altitude (m)', fontsize=12)
            ax3.set_title('Density Profile', fontsize=14, fontweight='bold')
            ax3.grid(True, alpha=0.3)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Atmospheric profile plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot atmospheric profile: {e}")
            return None
