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

        # Plot all motor curves (organized in motor/ subdirectory)
        if self.motor:
            motor_paths = self.plot_all_motor_curves(output_dir)
            paths.update(motor_paths)

        # Plot rocket drag curves (organized in rocket/ subdirectory)
        rocket_dir = output_dir / "rocket"
        rocket_dir.mkdir(parents=True, exist_ok=True)
        
        if hasattr(self.rocket, 'power_off_drag'):
            drag_off_path = self.plot_drag_curve(
                self.rocket.power_off_drag,
                "Power-Off Drag Coefficient",
                rocket_dir / "power_off_drag.png"
            )
            if drag_off_path:
                paths['rocket_power_off_drag'] = drag_off_path

        if hasattr(self.rocket, 'power_on_drag'):
            drag_on_path = self.plot_drag_curve(
                self.rocket.power_on_drag,
                "Power-On Drag Coefficient",
                rocket_dir / "power_on_drag.png"
            )
            if drag_on_path:
                paths['rocket_power_on_drag'] = drag_on_path

        # Plot environment profiles (organized in environment/ subdirectory)
        env_dir = output_dir / "environment"
        env_dir.mkdir(parents=True, exist_ok=True)
        
        if hasattr(self.environment, 'wind_velocity_x') and hasattr(self.environment, 'wind_velocity_y'):
            wind_path = self.plot_wind_profile(env_dir)
            if wind_path:
                paths['environment_wind_profile'] = wind_path

        if hasattr(self.environment, 'pressure') and hasattr(self.environment, 'temperature'):
            atm_path = self.plot_atmospheric_profile(env_dir)
            if atm_path:
                paths['environment_atmospheric_profile'] = atm_path

        logger.info(f"Generated {len(paths)} curve plots")
        return paths

    def plot_all_motor_curves(self, output_dir: Path) -> dict:
        """Generate all motor curve plots.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            Dictionary mapping curve name to file path
        """
        motor_dir = output_dir / "motor"
        motor_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        
        logger.info(f"Generating motor curve plots in {motor_dir}")
        
        # 1. Thrust curve
        if hasattr(self.motor, 'thrust'):
            path = self.plot_thrust_curve(motor_dir)
            if path:
                paths['motor_thrust'] = path
        
        # 2. Mass evolution (total_mass + propellant_mass combined)
        if hasattr(self.motor, 'total_mass') and hasattr(self.motor, 'propellant_mass'):
            path = self.plot_mass_evolution(motor_dir)
            if path:
                paths['motor_mass_evolution'] = path
        
        # 3. Mass flow rate
        if hasattr(self.motor, 'total_mass_flow_rate'):
            path = self.plot_single_function(
                self.motor.total_mass_flow_rate,
                "Mass Flow Rate vs Time",
                "Time (s)",
                "Mass Flow Rate (kg/s)",
                motor_dir / "mass_flow_rate.png"
            )
            if path:
                paths['motor_mass_flow_rate'] = path
        
        # 4. Center of mass (motor COM + propellant COM combined)
        if hasattr(self.motor, 'center_of_mass') and hasattr(self.motor, 'center_of_propellant_mass'):
            path = self.plot_center_of_mass(motor_dir)
            if path:
                paths['motor_center_of_mass'] = path
        
        # 5. Exhaust velocity
        if hasattr(self.motor, 'exhaust_velocity'):
            path = self.plot_single_function(
                self.motor.exhaust_velocity,
                "Exhaust Velocity vs Time",
                "Time (s)",
                "Exhaust Velocity (m/s)",
                motor_dir / "exhaust_velocity.png"
            )
            if path:
                paths['motor_exhaust_velocity'] = path
        
        # 6. Grain geometry (inner_radius + height on dual y-axes)
        if hasattr(self.motor, 'grain_inner_radius') and hasattr(self.motor, 'grain_height'):
            path = self.plot_grain_geometry(motor_dir)
            if path:
                paths['motor_grain_geometry'] = path
        
        # 7. Grain volume
        if hasattr(self.motor, 'grain_volume'):
            path = self.plot_single_function(
                self.motor.grain_volume,
                "Grain Volume vs Time",
                "Time (s)",
                "Volume (m³)",
                motor_dir / "grain_volume.png"
            )
            if path:
                paths['motor_grain_volume'] = path
        
        # 8. Burn characteristics (burn_area + burn_rate on dual y-axes)
        if hasattr(self.motor, 'burn_area') and hasattr(self.motor, 'burn_rate'):
            path = self.plot_burn_characteristics(motor_dir)
            if path:
                paths['motor_burn_characteristics'] = path
        
        # 9. Kn curve
        if hasattr(self.motor, 'Kn'):
            path = self.plot_single_function(
                self.motor.Kn,
                "Kn (Burn Area / Throat Area) vs Time",
                "Time (s)",
                "Kn (dimensionless)",
                motor_dir / "kn_curve.png"
            )
            if path:
                paths['motor_kn_curve'] = path
        
        # 10. Motor inertia tensor evolution
        if hasattr(self.motor, 'I_11') and hasattr(self.motor, 'I_22') and hasattr(self.motor, 'I_33'):
            path = self.plot_inertia_tensor(motor_dir)
            if path:
                paths['motor_inertia_tensor'] = path
        
        # 11. Propellant inertia tensor evolution
        if hasattr(self.motor, 'propellant_I_11') and hasattr(self.motor, 'propellant_I_22') and hasattr(self.motor, 'propellant_I_33'):
            path = self.plot_propellant_inertia_tensor(motor_dir)
            if path:
                paths['motor_propellant_inertia_tensor'] = path
        
        logger.info(f"Generated {len(paths)} motor curve plots")
        return paths

    def plot_thrust_curve(self, output_dir: Path) -> Optional[Path]:
        """Plot motor thrust curve.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        return self.plot_single_function(
            self.motor.thrust,
            "Motor Thrust Curve",
            "Time (s)",
            "Thrust (N)",
            output_dir / "thrust.png"
        )

    def plot_single_function(
        self,
        func,
        title: str,
        xlabel: str,
        ylabel: str,
        output_path: Path
    ) -> Optional[Path]:
        """Generic function plotter for single curve.

        Args:
            func: RocketPy Function object
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            output_path: Output file path

        Returns:
            Path to created plot or None if failed
        """
        try:
            # Get function data
            if hasattr(func, 'get_source'):
                try:
                    data = func.get_source()
                except:
                    # Sample the function
                    data = self._sample_function(func)
            else:
                # Sample the function
                data = self._sample_function(func)

            if data is None or len(data) == 0:
                logger.warning(f"No data available for {title}")
                return None

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2)
            ax.set_xlabel(xlabel, fontsize=12)
            ax.set_ylabel(ylabel, fontsize=12)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(left=0)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot {title}: {e}")
            return None

    def _sample_function(self, func, num_points: int = 200):
        """Sample a RocketPy Function object.

        Args:
            func: RocketPy Function to sample
            num_points: Number of sample points

        Returns:
            Numpy array with shape (n, 2) of [time, value] pairs
        """
        try:
            # Try to get time range from motor burn time
            if hasattr(self.motor, 'burn_out_time'):
                t_max = float(self.motor.burn_out_time)
            elif hasattr(self.motor, 'burn_time'):
                burn_time = self.motor.burn_time
                if isinstance(burn_time, tuple):
                    t_max = burn_time[1]
                else:
                    t_max = float(burn_time)
            else:
                t_max = 5.0  # Default

            t_array = np.linspace(0, t_max, num_points)
            values = np.array([func(t) for t in t_array])
            
            return np.column_stack([t_array, values])
        except Exception as e:
            logger.warning(f"Could not sample function: {e}")
            return None

    def plot_mass_evolution(self, output_dir: Path) -> Optional[Path]:
        """Plot total mass and propellant mass on same axes.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "mass_evolution.png"

            # Sample both functions
            total_mass_data = self._sample_function(self.motor.total_mass)
            propellant_mass_data = self._sample_function(self.motor.propellant_mass)

            if total_mass_data is None or propellant_mass_data is None:
                return None

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(total_mass_data[:, 0], total_mass_data[:, 1], 'b-', linewidth=2, label='Total Mass')
            ax.plot(propellant_mass_data[:, 0], propellant_mass_data[:, 1], 'r-', linewidth=2, label='Propellant Mass')
            ax.set_xlabel('Time (s)', fontsize=12)
            ax.set_ylabel('Mass (kg)', fontsize=12)
            ax.set_title('Motor Mass Evolution', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Mass evolution plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot mass evolution: {e}")
            return None

    def plot_center_of_mass(self, output_dir: Path) -> Optional[Path]:
        """Plot motor COM and propellant COM on same axes.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "center_of_mass.png"

            # Sample both functions
            motor_com_data = self._sample_function(self.motor.center_of_mass)
            propellant_com_data = self._sample_function(self.motor.center_of_propellant_mass)

            if motor_com_data is None or propellant_com_data is None:
                return None

            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(motor_com_data[:, 0], motor_com_data[:, 1], 'b-', linewidth=2, label='Motor COM')
            ax.plot(propellant_com_data[:, 0], propellant_com_data[:, 1], 'r-', linewidth=2, label='Propellant COM')
            ax.set_xlabel('Time (s)', fontsize=12)
            ax.set_ylabel('Position (m)', fontsize=12)
            ax.set_title('Center of Mass Evolution', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=10)
            ax.set_xlim(left=0)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Center of mass plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot center of mass: {e}")
            return None

    def plot_grain_geometry(self, output_dir: Path) -> Optional[Path]:
        """Plot grain inner radius and height on dual y-axes.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "grain_geometry.png"

            # Sample both functions
            radius_data = self._sample_function(self.motor.grain_inner_radius)
            height_data = self._sample_function(self.motor.grain_height)

            if radius_data is None or height_data is None:
                return None

            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot inner radius on left y-axis
            color = 'tab:blue'
            ax1.set_xlabel('Time (s)', fontsize=12)
            ax1.set_ylabel('Inner Radius (m)', color=color, fontsize=12)
            ax1.plot(radius_data[:, 0], radius_data[:, 1], color=color, linewidth=2, label='Inner Radius')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_xlim(left=0)
            ax1.grid(True, alpha=0.3)

            # Plot height on right y-axis
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Height (m)', color=color, fontsize=12)
            ax2.plot(height_data[:, 0], height_data[:, 1], color=color, linewidth=2, label='Height')
            ax2.tick_params(axis='y', labelcolor=color)

            # Title
            ax1.set_title('Grain Geometry Evolution', fontsize=14, fontweight='bold')

            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Grain geometry plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot grain geometry: {e}")
            return None

    def plot_burn_characteristics(self, output_dir: Path) -> Optional[Path]:
        """Plot burn area and burn rate on dual y-axes.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "burn_characteristics.png"

            # Sample both functions
            area_data = self._sample_function(self.motor.burn_area)
            rate_data = self._sample_function(self.motor.burn_rate)

            if area_data is None or rate_data is None:
                return None

            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot burn area on left y-axis
            color = 'tab:blue'
            ax1.set_xlabel('Time (s)', fontsize=12)
            ax1.set_ylabel('Burn Area (m²)', color=color, fontsize=12)
            ax1.plot(area_data[:, 0], area_data[:, 1], color=color, linewidth=2, label='Burn Area')
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.set_xlim(left=0)
            ax1.grid(True, alpha=0.3)

            # Plot burn rate on right y-axis
            ax2 = ax1.twinx()
            color = 'tab:red'
            ax2.set_ylabel('Burn Rate (m/s)', color=color, fontsize=12)
            ax2.plot(rate_data[:, 0], rate_data[:, 1], color=color, linewidth=2, label='Burn Rate')
            ax2.tick_params(axis='y', labelcolor=color)

            # Title
            ax1.set_title('Burn Characteristics', fontsize=14, fontweight='bold')

            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Burn characteristics plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot burn characteristics: {e}")
            return None

    def plot_inertia_tensor(self, output_dir: Path) -> Optional[Path]:
        """Plot motor inertia tensor components (I_11, I_22, I_33).
        
        Uses dual y-axis if I_33 is significantly different from I_11/I_22.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "inertia_tensor.png"

            # Sample inertia components
            I_11_data = self._sample_function(self.motor.I_11)
            I_22_data = self._sample_function(self.motor.I_22)
            I_33_data = self._sample_function(self.motor.I_33)

            if I_11_data is None or I_22_data is None or I_33_data is None:
                return None

            # Check if we need dual y-axis (I_33 typically much smaller than I_11/I_22)
            max_I_11 = np.max(np.abs(I_11_data[:, 1]))
            max_I_33 = np.max(np.abs(I_33_data[:, 1]))
            
            use_dual_axis = (max_I_11 / max_I_33 > 10) if max_I_33 > 0 else False

            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot I_11 and I_22 on left y-axis
            ax1.set_xlabel('Time (s)', fontsize=12)
            ax1.set_ylabel('Inertia I_11, I_22 (kg·m²)', fontsize=12)
            ax1.plot(I_11_data[:, 0], I_11_data[:, 1], 'b-', linewidth=2, label='I_11')
            ax1.plot(I_22_data[:, 0], I_22_data[:, 1], 'b--', linewidth=2, label='I_22', alpha=0.7)
            ax1.set_xlim(left=0)
            ax1.grid(True, alpha=0.3)

            if use_dual_axis:
                # Plot I_33 on right y-axis
                ax2 = ax1.twinx()
                color = 'tab:red'
                ax2.set_ylabel('Inertia I_33 (kg·m²)', color=color, fontsize=12)
                ax2.plot(I_33_data[:, 0], I_33_data[:, 1], color=color, linewidth=2, label='I_33')
                ax2.tick_params(axis='y', labelcolor=color)

                # Combine legends
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)
            else:
                # Plot I_33 on same axis
                ax1.plot(I_33_data[:, 0], I_33_data[:, 1], 'r-', linewidth=2, label='I_33')
                ax1.legend(loc='best', fontsize=10)

            ax1.set_title('Motor Inertia Tensor Evolution', fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Inertia tensor plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot inertia tensor: {e}")
            return None

    def plot_propellant_inertia_tensor(self, output_dir: Path) -> Optional[Path]:
        """Plot propellant inertia tensor components (I_11, I_22, I_33).
        
        Uses dual y-axis if I_33 is significantly different from I_11/I_22.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "propellant_inertia_tensor.png"

            # Sample propellant inertia components
            I_11_data = self._sample_function(self.motor.propellant_I_11)
            I_22_data = self._sample_function(self.motor.propellant_I_22)
            I_33_data = self._sample_function(self.motor.propellant_I_33)

            if I_11_data is None or I_22_data is None or I_33_data is None:
                return None

            # Check if we need dual y-axis
            max_I_11 = np.max(np.abs(I_11_data[:, 1]))
            max_I_33 = np.max(np.abs(I_33_data[:, 1]))
            
            use_dual_axis = (max_I_11 / max_I_33 > 10) if max_I_33 > 0 else False

            fig, ax1 = plt.subplots(figsize=(10, 6))

            # Plot I_11 and I_22 on left y-axis
            ax1.set_xlabel('Time (s)', fontsize=12)
            ax1.set_ylabel('Propellant I_11, I_22 (kg·m²)', fontsize=12)
            ax1.plot(I_11_data[:, 0], I_11_data[:, 1], 'b-', linewidth=2, label='I_11')
            ax1.plot(I_22_data[:, 0], I_22_data[:, 1], 'b--', linewidth=2, label='I_22', alpha=0.7)
            ax1.set_xlim(left=0)
            ax1.grid(True, alpha=0.3)

            if use_dual_axis:
                # Plot I_33 on right y-axis
                ax2 = ax1.twinx()
                color = 'tab:red'
                ax2.set_ylabel('Propellant I_33 (kg·m²)', color=color, fontsize=12)
                ax2.plot(I_33_data[:, 0], I_33_data[:, 1], color=color, linewidth=2, label='I_33')
                ax2.tick_params(axis='y', labelcolor=color)

                # Combine legends
                lines1, labels1 = ax1.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=10)
            else:
                # Plot I_33 on same axis
                ax1.plot(I_33_data[:, 0], I_33_data[:, 1], 'r-', linewidth=2, label='I_33')
                ax1.legend(loc='best', fontsize=10)

            ax1.set_title('Propellant Inertia Tensor Evolution', fontsize=14, fontweight='bold')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Propellant inertia tensor plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot propellant inertia tensor: {e}")
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
