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

        # Plot all rocket curves (organized in rocket/ subdirectory)
        if self.rocket:
            rocket_paths = self.plot_all_rocket_curves(output_dir)
            paths.update(rocket_paths)

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
        """Plot motor thrust curve with annotations for key performance metrics.
        
        Includes annotations for:
        - Burn start and burn out times
        - Maximum thrust point
        - Average thrust line
        - Total impulse (area under curve)

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            # Get thrust data
            if hasattr(self.motor.thrust, 'get_source'):
                try:
                    data = self.motor.thrust.get_source()
                except:
                    data = self._sample_function(self.motor.thrust)
            else:
                data = self._sample_function(self.motor.thrust)

            if data is None or len(data) == 0:
                logger.warning("No thrust data available")
                return None

            # Extract key performance metrics
            burn_start = float(self.motor.burn_start_time) if hasattr(self.motor, 'burn_start_time') else data[0, 0]
            burn_out = float(self.motor.burn_out_time) if hasattr(self.motor, 'burn_out_time') else data[-1, 0]
            max_thrust = float(self.motor.max_thrust) if hasattr(self.motor, 'max_thrust') else np.max(data[:, 1])
            max_thrust_time = float(self.motor.max_thrust_time) if hasattr(self.motor, 'max_thrust_time') else data[np.argmax(data[:, 1]), 0]
            avg_thrust = float(self.motor.average_thrust) if hasattr(self.motor, 'average_thrust') else np.mean(data[:, 1])
            total_impulse = float(self.motor.total_impulse) if hasattr(self.motor, 'total_impulse') else np.trapz(data[:, 1], data[:, 0])
            burn_duration = burn_out - burn_start

            # Create figure
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Plot thrust curve
            ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='Thrust')
            
            # Fill area under curve (total impulse)
            ax.fill_between(data[:, 0], 0, data[:, 1], alpha=0.1, color='blue', label=f'Total Impulse = {total_impulse:.0f} N·s')
            
            # Plot average thrust line
            ax.axhline(y=avg_thrust, color='green', linestyle='--', linewidth=1.5, alpha=0.7, label=f'Average Thrust = {avg_thrust:.1f} N')
            
            # Annotate burn times
            ax.axvline(x=burn_start, color='orange', linestyle=':', linewidth=1.5, alpha=0.7, label=f'Burn Start = {burn_start:.2f} s')
            ax.axvline(x=burn_out, color='red', linestyle=':', linewidth=1.5, alpha=0.7, label=f'Burn Out = {burn_out:.2f} s')
            
            # Annotate max thrust point
            ax.plot(max_thrust_time, max_thrust, 'ro', markersize=10, label=f'Max Thrust = {max_thrust:.1f} N @ {max_thrust_time:.2f} s')
            ax.annotate(f'Max: {max_thrust:.0f} N',
                       xy=(max_thrust_time, max_thrust),
                       xytext=(max_thrust_time, max_thrust * 1.15),
                       fontsize=10,
                       ha='center',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='red'))
            
            # Labels and title
            ax.set_xlabel('Time (s)', fontsize=13, fontweight='bold')
            ax.set_ylabel('Thrust (N)', fontsize=13, fontweight='bold')
            ax.set_title('Motor Thrust Curve', fontsize=15, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
            ax.set_xlim(left=max(0, burn_start - 0.5), right=burn_out + 0.5)
            ax.set_ylim(bottom=0, top=max_thrust * 1.2)
            
            # Add text box with summary statistics
            textstr = f'Burn Duration: {burn_duration:.2f} s\nImpulse Class: {total_impulse:.0f} N·s'
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
            
            plt.tight_layout()
            
            output_path = output_dir / "thrust_curve.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Thrust curve plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot thrust curve: {e}")
            return None

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

    def plot_all_rocket_curves(self, output_dir: Path) -> dict:
        """Generate all rocket curve plots.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            Dictionary mapping curve name to file path
        """
        rocket_dir = output_dir / "rocket"
        rocket_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        
        logger.info(f"Generating rocket curve plots in {rocket_dir}")
        
        # === MASS PROPERTIES (4 plots) ===
        
        # 1. Total mass vs time
        if hasattr(self.rocket, 'total_mass'):
            path = self.plot_single_function(
                self.rocket.total_mass,
                "Total Rocket Mass vs Time",
                "Time (s)",
                "Total Mass (kg)",
                rocket_dir / "total_mass_vs_time.png"
            )
            if path:
                paths['rocket_total_mass'] = path
        
        # 2. Mass components comparison (bar chart)
        path = self.plot_mass_components_comparison(rocket_dir)
        if path:
            paths['rocket_mass_comparison'] = path
        
        # 3. Mass flow rate vs time
        if hasattr(self.rocket, 'total_mass_flow_rate'):
            path = self.plot_single_function(
                self.rocket.total_mass_flow_rate,
                "Rocket Mass Flow Rate vs Time",
                "Time (s)",
                "Mass Flow Rate (kg/s)",
                rocket_dir / "mass_flow_rate_vs_time.png"
            )
            if path:
                paths['rocket_mass_flow_rate'] = path
        
        # 4. Reduced mass vs time
        if hasattr(self.rocket, 'reduced_mass'):
            path = self.plot_single_function(
                self.rocket.reduced_mass,
                "Reduced Mass vs Time",
                "Time (s)",
                "Reduced Mass (kg)",
                rocket_dir / "reduced_mass_vs_time.png"
            )
            if path:
                paths['rocket_reduced_mass'] = path
        
        # === CENTER OF MASS (2 plots) ===
        
        # 5. Center of mass evolution (all positions on same plot)
        path = self.plot_center_of_mass_evolution(rocket_dir)
        if path:
            paths['rocket_com_evolution'] = path
        
        # 6. CoM to CDM distance vs time
        if hasattr(self.rocket, 'com_to_cdm_function'):
            path = self.plot_single_function(
                self.rocket.com_to_cdm_function,
                "Center of Mass to Center of Dry Mass Distance vs Time",
                "Time (s)",
                "Distance (m)",
                rocket_dir / "com_to_cdm_vs_time.png"
            )
            if path:
                paths['rocket_com_to_cdm'] = path
        
        # === INERTIA (4 plots) ===
        
        # 7. Lateral inertia (I_11, I_22) vs time
        if hasattr(self.rocket, 'I_11') and hasattr(self.rocket, 'I_22'):
            path = self.plot_lateral_inertia(rocket_dir)
            if path:
                paths['rocket_inertia_lateral'] = path
        
        # 8. Axial inertia (I_33) vs time
        if hasattr(self.rocket, 'I_33'):
            path = self.plot_single_function(
                self.rocket.I_33,
                "Axial Moment of Inertia vs Time",
                "Time (s)",
                "I_33 (kg·m²)",
                rocket_dir / "inertia_axial_vs_time.png"
            )
            if path:
                paths['rocket_inertia_axial'] = path
        
        # 9. Inertia products (I_12, I_13, I_23) vs time - only if non-zero
        path = self.plot_inertia_products(rocket_dir)
        if path:
            paths['rocket_inertia_products'] = path
        
        # 10. Inertia comparison (without motor, dry, total at t0 and tf)
        path = self.plot_inertia_comparison(rocket_dir)
        if path:
            paths['rocket_inertia_comparison'] = path
        
        # === AERODYNAMICS (3 plots) ===
        
        # 11. Drag coefficients vs Mach (power-on and power-off)
        path = self.plot_drag_coefficients(rocket_dir)
        if path:
            paths['rocket_drag_coefficients'] = path
        
        # 12. Center of pressure position vs Mach
        if hasattr(self.rocket, 'cp_position'):
            path = self.plot_cp_vs_mach(rocket_dir)
            if path:
                paths['rocket_cp_position'] = path
        
        # 13. Lift coefficient derivative vs Mach
        if hasattr(self.rocket, 'total_lift_coeff_der'):
            path = self.plot_single_function(
                self.rocket.total_lift_coeff_der,
                "Total Lift Coefficient Derivative vs Mach",
                "Mach Number",
                "CLα (1/rad)",
                rocket_dir / "lift_coefficient_derivative_vs_mach.png"
            )
            if path:
                paths['rocket_lift_coefficient'] = path
        
        # === STABILITY (2 plots) ===
        
        # 14. Static margin vs time
        if hasattr(self.rocket, 'static_margin'):
            path = self.plot_single_function(
                self.rocket.static_margin,
                "Static Margin vs Time",
                "Time (s)",
                "Static Margin (calibers)",
                rocket_dir / "static_margin_vs_time.png"
            )
            if path:
                paths['rocket_static_margin'] = path
        
        # 15. Stability margin surface (3D plot: Mach vs Time)
        if hasattr(self.rocket, 'stability_margin'):
            path = self.plot_stability_margin_surface(rocket_dir)
            if path:
                paths['rocket_stability_margin_surface'] = path
        
        # === PERFORMANCE (1 plot) ===
        
        # 16. Thrust-to-weight ratio vs time
        if hasattr(self.rocket, 'thrust_to_weight'):
            path = self.plot_single_function(
                self.rocket.thrust_to_weight,
                "Thrust-to-Weight Ratio vs Time",
                "Time (s)",
                "T/W Ratio",
                rocket_dir / "thrust_to_weight_vs_time.png"
            )
            if path:
                paths['rocket_thrust_to_weight'] = path
        
        # === VISUALIZATION (1 plot) ===
        
        # 17. Rocket schematic using rocket.draw()
        path = self.plot_rocket_schematic(rocket_dir)
        if path:
            paths['rocket_schematic'] = path
        
        logger.info(f"Generated {len(paths)} rocket curve plots")
        return paths

    def plot_mass_components_comparison(self, output_dir: Path) -> Optional[Path]:
        """Plot bar chart comparing different mass components.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "mass_components_comparison.png"
            
            # Collect mass components
            components = {}
            
            if hasattr(self.rocket, 'mass'):
                components['Rocket Structure'] = float(self.rocket.mass)
            
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                motor = self.rocket.motor
                if hasattr(motor, 'dry_mass'):
                    components['Motor (dry)'] = float(motor.dry_mass)
                if hasattr(motor, 'propellant_initial_mass'):
                    components['Propellant (initial)'] = float(motor.propellant_initial_mass)
            
            if hasattr(self.rocket, 'dry_mass'):
                components['Total Dry Mass'] = float(self.rocket.dry_mass)
            
            # Sample total mass at t=0
            if hasattr(self.rocket, 'total_mass'):
                try:
                    total_mass_t0 = float(self.rocket.total_mass(0))
                    components['Total Mass (t=0)'] = total_mass_t0
                except:
                    pass
            
            if not components:
                logger.warning("No mass components available for comparison")
                return None
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            
            names = list(components.keys())
            values = list(components.values())
            colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(names)))
            
            bars = ax.bar(names, values, color=colors, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.2f} kg',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax.set_ylabel("Mass (kg)", fontsize=12, fontweight='bold')
            ax.set_title("Rocket Mass Components Comparison", fontsize=14, fontweight='bold')
            ax.grid(True, axis='y', alpha=0.3, linestyle='--')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Mass components comparison plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot mass components comparison: {e}")
            return None

    def plot_center_of_mass_evolution(self, output_dir: Path) -> Optional[Path]:
        """Plot evolution of different center of mass positions over time.
        
        Plots:
        - Total rocket CoM vs time
        - Motor CoM vs time
        - Propellant CoM vs time
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "center_of_mass_evolution.png"
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            plotted = False
            
            # Plot total rocket CoM
            if hasattr(self.rocket, 'center_of_mass'):
                data = self._sample_function(self.rocket.center_of_mass)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='Total Rocket CoM')
                    plotted = True
            
            # Plot motor CoM
            if hasattr(self.rocket, 'motor_center_of_mass_position'):
                data = self._sample_function(self.rocket.motor_center_of_mass_position)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'r--', linewidth=2, label='Motor CoM')
                    plotted = True
            
            # Plot propellant CoM (if available from motor)
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                if hasattr(self.rocket.motor, 'center_of_propellant_mass'):
                    data = self._sample_function(self.rocket.motor.center_of_propellant_mass)
                    if data is not None and len(data) > 0:
                        ax.plot(data[:, 0], data[:, 1], 'g-.', linewidth=2, label='Propellant CoM')
                        plotted = True
            
            if not plotted:
                logger.warning("No center of mass data available")
                plt.close(fig)
                return None
            
            ax.set_xlabel("Time (s)", fontsize=12, fontweight='bold')
            ax.set_ylabel("Position (m)", fontsize=12, fontweight='bold')
            ax.set_title("Center of Mass Evolution", fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Center of mass evolution plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot center of mass evolution: {e}")
            return None

    def plot_lateral_inertia(self, output_dir: Path) -> Optional[Path]:
        """Plot lateral moments of inertia (I_11 and I_22) vs time.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "inertia_lateral_vs_time.png"
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            plotted = False
            
            # Plot I_11
            if hasattr(self.rocket, 'I_11'):
                data = self._sample_function(self.rocket.I_11)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='I_11 (lateral)')
                    plotted = True
            
            # Plot I_22
            if hasattr(self.rocket, 'I_22'):
                data = self._sample_function(self.rocket.I_22)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'r--', linewidth=2.5, label='I_22 (lateral)')
                    plotted = True
            
            if not plotted:
                logger.warning("No lateral inertia data available")
                plt.close(fig)
                return None
            
            ax.set_xlabel("Time (s)", fontsize=12, fontweight='bold')
            ax.set_ylabel("Moment of Inertia (kg·m²)", fontsize=12, fontweight='bold')
            ax.set_title("Lateral Moments of Inertia vs Time", fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Lateral inertia plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot lateral inertia: {e}")
            return None

    def plot_inertia_products(self, output_dir: Path) -> Optional[Path]:
        """Plot products of inertia (I_12, I_13, I_23) vs time if non-zero.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed or all products are zero
        """
        try:
            output_path = output_dir / "inertia_products_vs_time.png"
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            plotted = False
            
            # Check and plot I_12
            if hasattr(self.rocket, 'I_12'):
                data = self._sample_function(self.rocket.I_12)
                if data is not None and len(data) > 0 and np.any(np.abs(data[:, 1]) > 1e-6):
                    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='I_12')
                    plotted = True
            
            # Check and plot I_13
            if hasattr(self.rocket, 'I_13'):
                data = self._sample_function(self.rocket.I_13)
                if data is not None and len(data) > 0 and np.any(np.abs(data[:, 1]) > 1e-6):
                    ax.plot(data[:, 0], data[:, 1], 'r--', linewidth=2.5, label='I_13')
                    plotted = True
            
            # Check and plot I_23
            if hasattr(self.rocket, 'I_23'):
                data = self._sample_function(self.rocket.I_23)
                if data is not None and len(data) > 0 and np.any(np.abs(data[:, 1]) > 1e-6):
                    ax.plot(data[:, 0], data[:, 1], 'g-.', linewidth=2.5, label='I_23')
                    plotted = True
            
            if not plotted:
                logger.debug("All inertia products are zero or not available - skipping plot")
                plt.close(fig)
                return None
            
            ax.set_xlabel("Time (s)", fontsize=12, fontweight='bold')
            ax.set_ylabel("Product of Inertia (kg·m²)", fontsize=12, fontweight='bold')
            ax.set_title("Products of Inertia vs Time", fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5, alpha=0.3)
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Inertia products plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot inertia products: {e}")
            return None

    def plot_inertia_comparison(self, output_dir: Path) -> Optional[Path]:
        """Plot comparison of inertia tensors: without motor, dry, total at t=0 and t=final.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "inertia_comparison.png"
            
            # Collect inertia values
            inertias = {}
            
            # Without motor inertias
            if hasattr(self.rocket, 'I_11_without_motor'):
                inertias['I_11 (no motor)'] = float(self.rocket.I_11_without_motor)
            if hasattr(self.rocket, 'I_22_without_motor'):
                inertias['I_22 (no motor)'] = float(self.rocket.I_22_without_motor)
            if hasattr(self.rocket, 'I_33_without_motor'):
                inertias['I_33 (no motor)'] = float(self.rocket.I_33_without_motor)
            
            # Dry inertias
            if hasattr(self.rocket, 'dry_I_11'):
                inertias['I_11 (dry)'] = float(self.rocket.dry_I_11)
            if hasattr(self.rocket, 'dry_I_22'):
                inertias['I_22 (dry)'] = float(self.rocket.dry_I_22)
            if hasattr(self.rocket, 'dry_I_33'):
                inertias['I_33 (dry)'] = float(self.rocket.dry_I_33)
            
            # Total inertias at t=0
            if hasattr(self.rocket, 'I_11'):
                try:
                    inertias['I_11 (t=0)'] = float(self.rocket.I_11(0))
                except:
                    pass
            if hasattr(self.rocket, 'I_22'):
                try:
                    inertias['I_22 (t=0)'] = float(self.rocket.I_22(0))
                except:
                    pass
            if hasattr(self.rocket, 'I_33'):
                try:
                    inertias['I_33 (t=0)'] = float(self.rocket.I_33(0))
                except:
                    pass
            
            # Get burn out time for final values
            burn_out_time = 0
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                if hasattr(self.rocket.motor, 'burn_out_time'):
                    burn_out_time = float(self.rocket.motor.burn_out_time)
            
            # Total inertias at t=burn_out
            if burn_out_time > 0:
                if hasattr(self.rocket, 'I_11'):
                    try:
                        inertias[f'I_11 (t={burn_out_time:.1f}s)'] = float(self.rocket.I_11(burn_out_time))
                    except:
                        pass
                if hasattr(self.rocket, 'I_22'):
                    try:
                        inertias[f'I_22 (t={burn_out_time:.1f}s)'] = float(self.rocket.I_22(burn_out_time))
                    except:
                        pass
                if hasattr(self.rocket, 'I_33'):
                    try:
                        inertias[f'I_33 (t={burn_out_time:.1f}s)'] = float(self.rocket.I_33(burn_out_time))
                    except:
                        pass
            
            if not inertias:
                logger.warning("No inertia data available for comparison")
                return None
            
            # Create grouped bar chart
            fig, ax = plt.subplots(figsize=(14, 8))
            
            names = list(inertias.keys())
            values = list(inertias.values())
            
            # Group by I_11, I_22, I_33
            i11_indices = [i for i, name in enumerate(names) if 'I_11' in name]
            i22_indices = [i for i, name in enumerate(names) if 'I_22' in name]
            i33_indices = [i for i, name in enumerate(names) if 'I_33' in name]
            
            x = np.arange(len(names))
            colors = ['#1f77b4' if 'I_11' in name else '#ff7f0e' if 'I_22' in name else '#2ca02c' for name in names]
            
            bars = ax.bar(x, values, color=colors, edgecolor='black', linewidth=1.5)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.2f}',
                       ha='center', va='bottom', fontsize=9)
            
            ax.set_ylabel("Moment of Inertia (kg·m²)", fontsize=12, fontweight='bold')
            ax.set_title("Inertia Tensor Components Comparison", fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(names, rotation=45, ha='right')
            ax.grid(True, axis='y', alpha=0.3, linestyle='--')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#1f77b4', edgecolor='black', label='I_11 (lateral)'),
                Patch(facecolor='#ff7f0e', edgecolor='black', label='I_22 (lateral)'),
                Patch(facecolor='#2ca02c', edgecolor='black', label='I_33 (axial)')
            ]
            ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
            
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Inertia comparison plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot inertia comparison: {e}")
            return None

    def plot_drag_coefficients(self, output_dir: Path) -> Optional[Path]:
        """Plot drag coefficients (power-on and power-off) vs Mach number.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "drag_coefficients_vs_mach.png"
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            plotted = False
            
            # Plot power-off drag
            if hasattr(self.rocket, 'power_off_drag'):
                data = self._sample_function(self.rocket.power_off_drag)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='Power-Off Drag')
                    plotted = True
            
            # Plot power-on drag
            if hasattr(self.rocket, 'power_on_drag'):
                data = self._sample_function(self.rocket.power_on_drag)
                if data is not None and len(data) > 0:
                    ax.plot(data[:, 0], data[:, 1], 'r--', linewidth=2.5, label='Power-On Drag')
                    plotted = True
            
            if not plotted:
                logger.warning("No drag coefficient data available")
                plt.close(fig)
                return None
            
            ax.set_xlabel("Mach Number", fontsize=12, fontweight='bold')
            ax.set_ylabel("Drag Coefficient", fontsize=12, fontweight='bold')
            ax.set_title("Drag Coefficients vs Mach Number", fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Add reference lines for subsonic/transonic/supersonic regions
            ax.axvline(x=0.8, color='orange', linestyle=':', linewidth=1, alpha=0.5, label='Transonic (M=0.8)')
            ax.axvline(x=1.0, color='red', linestyle=':', linewidth=1, alpha=0.5, label='Sonic (M=1.0)')
            ax.axvline(x=1.2, color='purple', linestyle=':', linewidth=1, alpha=0.5, label='Supersonic (M=1.2)')
            
            ax.legend(loc='best', fontsize=9)
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Drag coefficients plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot drag coefficients: {e}")
            return None

    def plot_cp_vs_mach(self, output_dir: Path) -> Optional[Path]:
        """Plot center of pressure position vs Mach number.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "cp_position_vs_mach.png"
            
            data = self._sample_function(self.rocket.cp_position)
            if data is None or len(data) == 0:
                logger.warning("No center of pressure data available")
                return None
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=2.5, label='Center of Pressure')
            
            # Add reference line for center of mass (if constant)
            if hasattr(self.rocket, 'center_of_mass_without_motor'):
                com = float(self.rocket.center_of_mass_without_motor)
                ax.axhline(y=com, color='red', linestyle='--', linewidth=2, label=f'CoM (without motor) = {com:.3f} m')
            
            ax.set_xlabel("Mach Number", fontsize=12, fontweight='bold')
            ax.set_ylabel("Position (m)", fontsize=12, fontweight='bold')
            ax.set_title("Center of Pressure Position vs Mach Number", fontsize=14, fontweight='bold')
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Center of pressure plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot center of pressure: {e}")
            return None

    def plot_stability_margin_surface(self, output_dir: Path) -> Optional[Path]:
        """Plot stability margin as a 2D surface (Mach vs Time).
        
        Creates a contour plot showing how stability margin varies with both
        Mach number and time during flight.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "stability_margin_surface.png"
            
            # Sample the stability_margin function over Mach and time grid
            mach_range = np.linspace(0, 3, 50)
            time_range = np.linspace(0, 10, 50)
            
            # Get burn out time if available
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                if hasattr(self.rocket.motor, 'burn_out_time'):
                    max_time = float(self.rocket.motor.burn_out_time) * 1.2
                    time_range = np.linspace(0, max_time, 50)
            
            Mach, Time = np.meshgrid(mach_range, time_range)
            StabilityMargin = np.zeros_like(Mach)
            
            # Evaluate stability margin at each point
            for i in range(len(time_range)):
                for j in range(len(mach_range)):
                    try:
                        StabilityMargin[i, j] = self.rocket.stability_margin(mach_range[j], time_range[i])
                    except:
                        StabilityMargin[i, j] = np.nan
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create filled contour plot
            levels = np.linspace(np.nanmin(StabilityMargin), np.nanmax(StabilityMargin), 20)
            contour = ax.contourf(Mach, Time, StabilityMargin, levels=levels, cmap='RdYlGn')
            
            # Add contour lines
            contour_lines = ax.contour(Mach, Time, StabilityMargin, levels=10, colors='black', linewidths=0.5, alpha=0.4)
            ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%.2f')
            
            # Add colorbar
            cbar = plt.colorbar(contour, ax=ax)
            cbar.set_label('Stability Margin (calibers)', fontsize=12, fontweight='bold')
            
            ax.set_xlabel("Mach Number", fontsize=12, fontweight='bold')
            ax.set_ylabel("Time (s)", fontsize=12, fontweight='bold')
            ax.set_title("Stability Margin Surface (Mach vs Time)", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Stability margin surface plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot stability margin surface: {e}")
            return None

    def plot_rocket_schematic(self, output_dir: Path) -> Optional[Path]:
        """Save rocket schematic using rocket.draw() method.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed or draw() not available
        """
        try:
            output_path = output_dir / "rocket_schematic.png"
            
            # Check if draw method exists
            if not hasattr(self.rocket, 'draw'):
                logger.debug("Rocket.draw() method not available")
                return None
            
            # Call rocket.draw() which creates a matplotlib figure
            # Save the current figure after draw() is called
            self.rocket.draw()
            
            # Get the current figure
            fig = plt.gcf()
            
            # Save it
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Rocket schematic saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not save rocket schematic: {e}")
            return None

    def plot_motor_schematic(self, output_dir: Path) -> Optional[Path]:
        """Save motor schematic using motor.draw() method if available.
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed or draw() not available
        """
        try:
            output_path = output_dir / "motor_schematic.png"
            
            # Check if motor exists and has draw method
            if not self.motor:
                logger.debug("No motor available")
                return None
                
            if not hasattr(self.motor, 'draw'):
                logger.debug("Motor.draw() method not available")
                return None
            
            # Call motor.draw() which creates a matplotlib figure
            self.motor.draw()
            
            # Get the current figure
            fig = plt.gcf()
            
            # Save it
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Motor schematic saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not save motor schematic: {e}")
            return None

    def save_all_schematics(self, output_dir: str) -> dict:
        """Save all technical drawings (rocket and motor schematics).
        
        Args:
            output_dir: Directory for output PNG files
            
        Returns:
            Dictionary mapping schematic name to file path
        """
        output_dir = Path(output_dir) / "plots"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving technical schematics in {output_dir}")
        
        paths = {}
        
        # Save rocket schematic
        rocket_path = self.plot_rocket_schematic(output_dir)
        if rocket_path:
            paths['rocket_schematic'] = rocket_path
        
        # Save motor schematic
        motor_path = self.plot_motor_schematic(output_dir)
        if motor_path:
            paths['motor_schematic'] = motor_path
        
        logger.info(f"Saved {len(paths)} technical schematics")
        return paths

