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

    def __init__(self, motor, rocket, environment, max_mach: float = 2.0, flight=None):
        """Initialize CurvePlotter.

        Args:
            motor: RocketPy Motor object
            rocket: RocketPy Rocket object
            environment: RocketPy Environment object
            max_mach: Maximum Mach number reached during flight (default 2.0)
            flight: RocketPy Flight object (optional, for simulation data)
        """
        self.motor = motor
        self.rocket = rocket
        self.environment = environment
        self.max_mach = max_mach
        self.flight = flight
        
        logger.info(f"🚀 CurvePlotter initialized with max_mach={max_mach:.3f}, flight={'provided' if flight else 'None'}")
        
        # Extract critical flight events if flight object available
        self.burnout_time = None
        self.max_q_time = None
        self.apogee_time = None
        self.parachute_deploy_time = None
        
        if self.flight is not None:
            try:
                self.burnout_time = float(self.flight.rocket.motor.burn_out_time)
            except:
                pass
            try:
                self.max_q_time = float(self.flight.max_dynamic_pressure_time)
                self.max_q_pressure = float(self.flight.max_dynamic_pressure)  # Pa
            except:
                self.max_q_pressure = None
            try:
                self.apogee_time = float(self.flight.apogee_time)
            except:
                pass
            try:
                # Calculate parachute deployment time (apogee + lag for first parachute)
                if hasattr(self.flight.rocket, 'parachutes') and len(self.flight.rocket.parachutes) > 0:
                    first_parachute = self.flight.rocket.parachutes[0]
                    # Check if trigger is apogee
                    if hasattr(first_parachute, 'trigger') and first_parachute.trigger == 'apogee':
                        lag = float(first_parachute.lag) if hasattr(first_parachute, 'lag') else 0
                        if self.apogee_time is not None:
                            self.parachute_deploy_time = self.apogee_time + lag
                            logger.info(f"📍 Parachute deployment detected: {self.parachute_deploy_time:.2f}s (apogee {self.apogee_time:.2f}s + lag {lag:.2f}s)")
            except Exception as e:
                logger.debug(f"Could not extract parachute deployment time: {e}")
                pass

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

        # Plot all stability curves (organized in stability/ subdirectory)
        if self.rocket:
            stability_paths = self.plot_all_stability_curves(output_dir)
            paths.update(stability_paths)

        # Plot all flight data curves (organized in flight/ subdirectory)
        if self.flight:
            flight_paths = self.plot_all_flight_curves(output_dir)
            paths.update(flight_paths)

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
        """Sample a RocketPy Function object (time-based).

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

    def _sample_mach_function(self, func, num_points: int = 300):
        """Sample a RocketPy Function object that depends on Mach number.

        Uses actual maximum Mach number reached during flight with small margin.
        For subsonic flights (< M=1.0), shows up to max_mach + 5%.
        For transonic/supersonic, shows up to max_mach + 10%.

        Args:
            func: RocketPy Function to sample (must accept Mach as input)
            num_points: Number of sample points

        Returns:
            Numpy array with shape (n, 2) of [mach, value] pairs
        """
        try:
            # Use smaller margin for subsonic, larger for supersonic
            if self.max_mach < 1.0:
                # Subsonic: show only +5% beyond actual flight
                mach_max = self.max_mach * 1.05
                logger.debug(f"Subsonic flight: max_mach={self.max_mach:.3f}, plotting to {mach_max:.3f}")
            else:
                # Transonic/Supersonic: show +10% for safety analysis
                mach_max = self.max_mach * 1.1
                logger.debug(f"Supersonic flight: max_mach={self.max_mach:.3f}, plotting to {mach_max:.3f}")
            
            mach_array = np.linspace(0, mach_max, num_points)
            values = np.array([func(m) for m in mach_array])
            
            return np.column_stack([mach_array, values])
        except Exception as e:
            logger.warning(f"Could not sample Mach function: {e}")
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
        
        # 13. Lift coefficient derivative vs Mach (skip - not plottable as-is)
        # The total_lift_coeff_der is a function object that requires special handling
        # Uncomment if RocketPy provides a plottable version in future releases

        # === PERFORMANCE (1 plot) ===
        
        # 16. Thrust-to-weight ratio vs time (skip - not plottable as-is)
        # The thrust_to_weight is a function object that requires special handling
        # Uncomment if RocketPy provides a plottable version in future releases
        
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
            
            data = self._sample_mach_function(self.rocket.cp_position)
            if data is None or len(data) == 0:
                logger.warning("No center of pressure data available")
                return None
            
            fig, ax = plt.subplots(figsize=(12, 7))
            
            # Distinguish simulated vs theoretical data
            simulated_mask = data[:, 0] <= self.max_mach
            theoretical_mask = data[:, 0] >= self.max_mach
            
            ax.plot(data[simulated_mask, 0], data[simulated_mask, 1], 
                   'b-', linewidth=3, label='CP (Simulated)', zorder=5)
            if np.any(theoretical_mask):
                ax.plot(data[theoretical_mask, 0], data[theoretical_mask, 1], 
                       'b--', linewidth=2, alpha=0.6, label='CP (Theoretical)', zorder=4)
            
            # Mark max Mach
            ax.axvline(x=self.max_mach, color='darkblue', linestyle='-.', linewidth=2,
                      alpha=0.7, label=f'Max Mach: {self.max_mach:.3f}', zorder=6)
            
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
        Mach number and time during flight. This uses rocket.stability_margin(mach, time)
        which accounts for CP movement with Mach number.
        
        Note: This is different from static_margin which assumes Mach=0 (CP fixed).
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "stability_margin_surface.png"
            
            # Sample the stability_margin function over Mach and time grid
            # Use adaptive margin: +5% for subsonic, +10% for supersonic
            mach_max = self.max_mach * 1.05 if self.max_mach < 1.0 else self.max_mach * 1.1
            mach_range = np.linspace(0, mach_max, 50)
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
            ax.set_title("Stability Margin (function of Mach & Time)", fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Stability margin surface plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot stability margin surface: {e}")
            return None

    def plot_static_margin_enhanced(self, output_dir: Path) -> Optional[Path]:
        """Plot actual stability margin vs time with aerospace guideline thresholds.

        Enhanced version showing REAL stability margin (accounting for CP movement with Mach):
        - Uses rocket.stability_margin(mach, time) for accurate flight behavior
        - Critical threshold at 1.0 caliber (minimum safety)
        - Recommended threshold at 1.5 calibers (subsonic)
        - Design target zone at 2.0-2.5 calibers
        - Critical flight events markers
        - Parachute deployment marker

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "stability_margin_enhanced.png"

            # Calculate actual stability margin using real Mach number at each time
            if self.flight is None:
                logger.warning("Flight object required for stability margin - falling back to static margin")
                data = self._sample_function(self.rocket.static_margin)
                using_static = True
            else:
                # Determine time range: extend to shortly after parachute deployment
                t_max = self.flight.t_final
                if self.parachute_deploy_time is not None and self.parachute_deploy_time < self.flight.t_final:
                    t_max = min(self.parachute_deploy_time + 10, self.parachute_deploy_time * 1.2, self.flight.t_final)
                
                # Sample time points
                time_points = np.linspace(0, t_max, 200)
                stability_values = []
                
                for t in time_points:
                    try:
                        # Get Mach number at this time from flight data
                        mach = float(self.flight.mach_number(t))
                        # Calculate stability margin at this Mach and time
                        sm = float(self.rocket.stability_margin(mach, t))
                        stability_values.append([t, sm])
                    except Exception as e:
                        if len(stability_values) == 0:
                            logger.warning(f"Failed to compute stability margin at t={t:.2f}s: {e}")
                        pass
                
                if len(stability_values) == 0:
                    logger.warning("Could not compute stability margin data - falling back to static margin")
                    data = self._sample_function(self.rocket.static_margin)
                    using_static = True
                else:
                    data = np.array(stability_values)
                    using_static = False
            
            if data is None or len(data) == 0:
                logger.warning("No stability margin data available")
                return None

            fig, ax = plt.subplots(figsize=(14, 8))

            # Plot stability margin
            margin_label = 'Static Margin (at Mach=0)' if using_static else 'Stability Margin (actual flight)'
            ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=3, label=margin_label, zorder=5)

            # Add threshold lines and zones
            ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2,
                      alpha=0.7, label='Minimum Safety (1.0 cal)', zorder=3)
            ax.axhline(y=1.5, color='orange', linestyle='--', linewidth=2,
                      alpha=0.7, label='Recommended Subsonic (1.5 cal)', zorder=3)

            # Design target zone (2.0-2.5 calibers)
            ax.axhspan(2.0, 2.5, alpha=0.15, color='green',
                      label='Design Target Zone (2.0-2.5 cal)', zorder=1)

            # Unsafe zone (below 1.0)
            ax.axhspan(ax.get_ylim()[0], 1.0, alpha=0.1, color='red', zorder=1)

            # Marginal zone (1.0-1.5)
            ax.axhspan(1.0, 1.5, alpha=0.1, color='yellow', zorder=1)

            # Mark critical flight events
            events_marked = []
            
            # Burnout
            if self.burnout_time is not None and self.burnout_time < data[-1, 0]:
                burn_out = self.burnout_time
                ax.axvline(x=burn_out, color='purple', linestyle=':', linewidth=2,
                          alpha=0.7, label=f'Burn Out ({burn_out:.2f}s)', zorder=4)
                
                # Get stability margin at burnout (use actual if available)
                if not using_static and self.flight is not None:
                    mach_bo = float(self.flight.mach_number(burn_out))
                    sm_at_burnout = float(self.rocket.stability_margin(mach_bo, burn_out))
                else:
                    sm_at_burnout = self.rocket.static_margin(burn_out)
                    
                ax.plot(burn_out, sm_at_burnout, 'mo', markersize=12, zorder=6)
                ax.annotate(f'SM @ Burnout\n{sm_at_burnout:.2f} cal',
                           xy=(burn_out, sm_at_burnout),
                           xytext=(burn_out * 1.15, sm_at_burnout),
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='mediumpurple', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color='purple', lw=1.5))
                events_marked.append('burnout')
            
            # Max dynamic pressure
            if self.max_q_time is not None and self.max_q_time < data[-1, 0]:
                max_q_t = self.max_q_time
                # Format pressure value
                max_q_label = f'Max-Q ({max_q_t:.2f}s)'
                if self.max_q_pressure is not None:
                    max_q_kpa = self.max_q_pressure / 1000.0  # Convert Pa to kPa
                    max_q_label = f'Max-Q ({max_q_t:.2f}s, {max_q_kpa:.1f} kPa)'
                
                ax.axvline(x=max_q_t, color='orange', linestyle=':', linewidth=2,
                          alpha=0.7, label=max_q_label, zorder=4)
                
                # Get stability margin at Max-Q (use actual if available)
                if not using_static and self.flight is not None:
                    mach_mq = float(self.flight.mach_number(max_q_t))
                    sm_at_maxq = float(self.rocket.stability_margin(mach_mq, max_q_t))
                else:
                    sm_at_maxq = self.rocket.static_margin(max_q_t)
                    
                ax.plot(max_q_t, sm_at_maxq, 'o', color='orange', markersize=12, zorder=6)
                
                # Annotation with SM and pressure
                annotation_text = f'SM @ Max-Q\n{sm_at_maxq:.2f} cal'
                if self.max_q_pressure is not None:
                    max_q_kpa = self.max_q_pressure / 1000.0
                    annotation_text = f'SM @ Max-Q\n{sm_at_maxq:.2f} cal\nQ = {max_q_kpa:.1f} kPa'
                
                ax.annotate(annotation_text,
                           xy=(max_q_t, sm_at_maxq),
                           xytext=(max_q_t * 1.15, sm_at_maxq - 0.2),
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='orange', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color='orange', lw=1.5))
                events_marked.append('max_q')
            
            # Apogee
            if self.apogee_time is not None and self.apogee_time < data[-1, 0]:
                apogee_t = self.apogee_time
                ax.axvline(x=apogee_t, color='green', linestyle=':', linewidth=2,
                          alpha=0.7, label=f'Apogee ({apogee_t:.2f}s)', zorder=4)
                
                # Get stability margin at apogee (use actual if available)
                if not using_static and self.flight is not None:
                    mach_ap = float(self.flight.mach_number(apogee_t))
                    sm_at_apogee = float(self.rocket.stability_margin(mach_ap, apogee_t))
                else:
                    sm_at_apogee = self.rocket.static_margin(apogee_t)
                    
                ax.plot(apogee_t, sm_at_apogee, 'go', markersize=12, zorder=6)
                ax.annotate(f'SM @ Apogee\n{sm_at_apogee:.2f} cal',
                           xy=(apogee_t, sm_at_apogee),
                           xytext=(apogee_t * 0.85, sm_at_apogee + 0.2),
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7),
                           arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
                events_marked.append('apogee')
            
            # Parachute deployment
            if self.parachute_deploy_time is not None and self.parachute_deploy_time < data[-1, 0]:
                chute_t = self.parachute_deploy_time
                ax.axvline(x=chute_t, color='cyan', linestyle=':', linewidth=2.5,
                          alpha=0.7, label=f'Parachute Deploy ({chute_t:.2f}s)', zorder=4)
                events_marked.append('parachute')

            # Find and annotate minimum static margin
            min_idx = np.argmin(data[:, 1])
            min_time = data[min_idx, 0]
            min_sm = data[min_idx, 1]
            ax.plot(min_time, min_sm, 'ro', markersize=12, zorder=6)
            ax.annotate(f'Minimum: {min_sm:.2f} cal @ {min_time:.2f}s',
                       xy=(min_time, min_sm),
                       xytext=(min_time, min_sm - 0.5),
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='red'))

            ax.set_xlabel("Time (s)", fontsize=13, fontweight='bold')
            ax.set_ylabel("Stability Margin (calibers)", fontsize=13, fontweight='bold')
            
            # Set title based on what data we're using
            if using_static:
                title = "Static Margin vs Time (at Mach=0 - Aerospace Guidelines)"
            else:
                title = "Stability Margin vs Time (Actual Flight - CP varies with Mach)"
            ax.set_title(title, fontsize=15, fontweight='bold')
            ax.legend(loc='best', fontsize=10, framealpha=0.9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlim(left=0)

            # Add text box with verdict
            verdict = "SAFE" if min_sm >= 1.5 else ("MARGINAL" if min_sm >= 1.0 else "UNSAFE")
            verdict_color = 'green' if min_sm >= 1.5 else ('orange' if min_sm >= 1.0 else 'red')
            textstr = f'Verdict: {verdict}\nMin SM: {min_sm:.2f} cal'
            props = dict(boxstyle='round', facecolor=verdict_color, alpha=0.3, linewidth=2, edgecolor='black')
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=12, fontweight='bold',
                   verticalalignment='top', bbox=props)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Enhanced stability margin plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot enhanced static margin: {e}")
            return None

    def plot_cp_travel_analysis(self, output_dir: Path) -> Optional[Path]:
        """Plot center of pressure travel vs Mach with transonic region analysis.

        Highlights:
        - CP position variation with Mach number
        - Transonic region (0.8-1.2 Mach) where CP shifts occur
        - CP travel range
        - Subsonic/Transonic/Supersonic regions

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "cp_travel_analysis.png"

            # Sample CP position vs Mach (adaptive margin based on flight regime)
            mach_max = self.max_mach * 1.05 if self.max_mach < 1.0 else self.max_mach * 1.1
            mach_array = np.linspace(0, mach_max, 300)
            cp_values = [self.rocket.cp_position(m) for m in mach_array]

            fig, ax = plt.subplots(figsize=(14, 8))

            # Split data into simulated and theoretical regions
            simulated_mask = mach_array <= self.max_mach
            theoretical_mask = mach_array >= self.max_mach
            
            # Plot simulated region (solid line)
            ax.plot(mach_array[simulated_mask], np.array(cp_values)[simulated_mask], 
                   'b-', linewidth=3.5, label='CP (Simulated Flight Envelope)', zorder=5)
            
            # Plot theoretical extension (dashed line)
            if np.any(theoretical_mask):
                ax.plot(mach_array[theoretical_mask], np.array(cp_values)[theoretical_mask], 
                       'b--', linewidth=2, alpha=0.6, label='CP (Theoretical Extension)', zorder=4)
            
            # Mark maximum Mach reached
            cp_at_max_mach = self.rocket.cp_position(self.max_mach)
            ax.axvline(x=self.max_mach, color='darkblue', linestyle='-.', linewidth=2.5,
                      alpha=0.8, label=f'Max Mach Reached: {self.max_mach:.3f}', zorder=6)
            ax.plot(self.max_mach, cp_at_max_mach, 'o', color='darkblue', 
                   markersize=12, zorder=7, markeredgewidth=2, markeredgecolor='white')

            # Only show transonic/supersonic regions if relevant to flight
            # Subsonic region (always shown)
            subsonic_end = min(0.8, mach_max)
            ax.axvspan(0, subsonic_end, alpha=0.1, color='green', label='Subsonic (<0.8)', zorder=1)
            
            # Transonic region (only if max_mach >= 0.8)
            if self.max_mach >= 0.8:
                transonic_end = min(1.2, mach_max)
                ax.axvspan(0.8, transonic_end, alpha=0.2, color='orange',
                          label='Transonic Region (0.8-1.2 Mach)', zorder=1)
                
                # Mark Mach 1 (only if we plot that far)
                if mach_max >= 1.0:
                    ax.axvline(x=1.0, color='red', linestyle='--', linewidth=2,
                              alpha=0.7, label='Sonic (M=1.0)', zorder=3)
            
            # Supersonic region (only if max_mach > 1.2)
            if mach_max > 1.2:
                ax.axvspan(1.2, mach_max, alpha=0.1, color='blue',
                          label='Supersonic (>1.2)', zorder=1)

            # Calculate and annotate CP travel in transonic region (only if relevant)
            if self.max_mach >= 0.8:
                cp_at_08 = self.rocket.cp_position(0.8)
                eval_mach_high = min(1.2, self.max_mach)  # Don't go beyond actual flight
                cp_at_high = self.rocket.cp_position(eval_mach_high)
                cp_shift = abs(cp_at_high - cp_at_08)

                ax.plot([0.8, eval_mach_high], [cp_at_08, cp_at_high], 'ro-', linewidth=2, markersize=8, zorder=6)
                
                # Position annotation intelligently
                annot_x = min(1.0, self.max_mach * 0.95)
                annot_text_x = min(annot_x * 1.1, mach_max * 0.95)  # Keep annotation within plot
                ax.annotate(f'CP Shift:\n{cp_shift:.4f} m\n({cp_shift*100:.2f} cm)',
                           xy=(annot_x, (cp_at_08 + cp_at_high)/2),
                           xytext=(annot_text_x, (cp_at_08 + cp_at_high)/2),
                           fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.8),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3', color='red', lw=2))

            # Calculate total CP travel range
            cp_min = min(cp_values)
            cp_max = max(cp_values)
            cp_range = cp_max - cp_min

            ax.axhline(y=cp_min, color='gray', linestyle=':', linewidth=1, alpha=0.5)
            ax.axhline(y=cp_max, color='gray', linestyle=':', linewidth=1, alpha=0.5)

            # Add CoM reference line if available
            if hasattr(self.rocket, 'center_of_mass_without_motor'):
                com = float(self.rocket.center_of_mass_without_motor)
                ax.axhline(y=com, color='green', linestyle='--', linewidth=2.5,
                          label=f'CoM (without motor) = {com:.3f} m', zorder=4)

            ax.set_xlabel("Mach Number", fontsize=13, fontweight='bold')
            ax.set_ylabel("CP Position (m)", fontsize=13, fontweight='bold')
            ax.set_title("Center of Pressure Travel Analysis vs Mach", fontsize=15, fontweight='bold')
            ax.legend(loc='best', fontsize=10, framealpha=0.9)
            ax.grid(True, alpha=0.3, linestyle='--')
            ax.set_xlim(left=0, right=mach_max)  # Force X-axis to match actual plot range

            # Add text box with CP travel statistics
            textstr = f'CP Travel Range: {cp_range:.4f} m ({cp_range*100:.2f} cm)\n'
            textstr += f'CP Min: {cp_min:.4f} m\nCP Max: {cp_max:.4f} m'
            props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8, linewidth=2, edgecolor='black')
            ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=10, fontweight='bold',
                   verticalalignment='bottom', bbox=props)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"CP travel analysis plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot CP travel analysis: {e}")
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

    def plot_cp_com_evolution_complete(self, output_dir: Path) -> Optional[Path]:
        """Plot comprehensive CP and CoM evolution during flight.
        
        Shows:
        - CP position varying with Mach (real flight data)
        - CoM position varying with time (propellant consumption)
        - Stability margin evolution
        - All on same time axis for direct comparison
        
        Args:
            output_dir: Output directory
            
        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "cp_com_complete_evolution.png"
            
            if self.flight is None:
                logger.warning("Flight object required for complete CP/CoM evolution plot")
                return None
            
            # Determine time range (up to parachute deployment + buffer)
            t_max = self.flight.t_final
            if self.parachute_deploy_time is not None and self.parachute_deploy_time < self.flight.t_final:
                t_max = min(self.parachute_deploy_time + 10, self.parachute_deploy_time * 1.2, self.flight.t_final)
            
            time_points = np.linspace(0, t_max, 300)
            
            # Get CoM evolution (changes as propellant burns)
            com_values = [float(self.rocket.center_of_mass(t)) for t in time_points]
            
            # Get CP evolution (varies with Mach during flight)
            cp_values = []
            mach_values = []
            for t in time_points:
                try:
                    mach = float(self.flight.mach_number(t))
                    cp = float(self.rocket.cp_position(mach))
                    cp_values.append(cp)
                    mach_values.append(mach)
                except:
                    cp_values.append(np.nan)
                    mach_values.append(np.nan)
            
            # Calculate stability margin in calibers
            rocket_radius = float(self.rocket.radius)
            stability_margin_values = [(cp - com) / (2 * rocket_radius) for cp, com in zip(cp_values, com_values)]
            
            # Create figure with 3 subplots
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 12), sharex=True)
            
            # --- SUBPLOT 1: CP and CoM positions ---
            ax1.plot(time_points, com_values, 'b-', linewidth=3, label='Center of Mass (CoM)', zorder=5)
            ax1.plot(time_points, cp_values, 'r-', linewidth=3, label='Center of Pressure (CP - varies with Mach)', zorder=5)
            
            # Fill area between
            ax1.fill_between(time_points, com_values, cp_values, alpha=0.2, color='green',
                            label='CP-CoM Distance', zorder=1)
            
            # Mark critical events
            if self.burnout_time is not None and self.burnout_time < t_max:
                ax1.axvline(x=self.burnout_time, color='purple', linestyle=':', linewidth=2,
                          alpha=0.7, label=f'Burnout ({self.burnout_time:.2f}s)', zorder=4)
            if self.max_q_time is not None and self.max_q_time < t_max:
                ax1.axvline(x=self.max_q_time, color='orange', linestyle=':', linewidth=2,
                          alpha=0.7, label=f'Max-Q ({self.max_q_time:.2f}s)', zorder=4)
            if self.apogee_time is not None and self.apogee_time < t_max:
                ax1.axvline(x=self.apogee_time, color='green', linestyle=':', linewidth=2,
                          alpha=0.7, label=f'Apogee ({self.apogee_time:.2f}s)', zorder=4)
            if self.parachute_deploy_time is not None and self.parachute_deploy_time < t_max:
                ax1.axvline(x=self.parachute_deploy_time, color='cyan', linestyle=':', linewidth=2.5,
                          alpha=0.7, label=f'Parachute ({self.parachute_deploy_time:.2f}s)', zorder=4)
            
            ax1.set_ylabel("Position from Tail (m)", fontsize=13, fontweight='bold')
            ax1.set_title("CP and CoM Evolution During Flight (CP varies with actual Mach)", fontsize=15, fontweight='bold')
            ax1.legend(loc='best', fontsize=10, framealpha=0.9)
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # --- SUBPLOT 2: Mach number evolution ---
            ax2.plot(time_points, mach_values, 'darkblue', linewidth=3, label='Mach Number', zorder=5)
            ax2.axhline(y=0.8, color='orange', linestyle='--', linewidth=1.5, alpha=0.6, label='Transonic Start (M=0.8)')
            ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5, alpha=0.6, label='Sonic (M=1.0)')
            
            # Shade transonic region
            ax2.axhspan(0.8, 1.2, alpha=0.1, color='orange', label='Transonic Region')
            
            # Mark max Mach
            max_mach_idx = np.argmax(mach_values)
            ax2.plot(time_points[max_mach_idx], mach_values[max_mach_idx], 'ro', markersize=12, zorder=6,
                    label=f'Max Mach: {mach_values[max_mach_idx]:.3f}')
            
            ax2.set_ylabel("Mach Number", fontsize=13, fontweight='bold')
            ax2.set_title("Mach Number Evolution", fontsize=14, fontweight='bold')
            ax2.legend(loc='best', fontsize=10, framealpha=0.9)
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.set_ylim(bottom=0)
            
            # --- SUBPLOT 3: Stability margin ---
            ax3.plot(time_points, stability_margin_values, 'g-', linewidth=3, label='Stability Margin (actual)', zorder=5)
            
            # Add threshold lines
            ax3.axhline(y=1.0, color='red', linestyle='--', linewidth=2,
                       alpha=0.7, label='Minimum (1.0 cal)', zorder=3)
            ax3.axhline(y=1.5, color='orange', linestyle='--', linewidth=2,
                       alpha=0.7, label='Recommended (1.5 cal)', zorder=3)
            ax3.axhspan(2.0, 2.5, alpha=0.15, color='green', label='Design Target', zorder=1)
            
            # Shade unsafe zone
            ax3.axhspan(ax3.get_ylim()[0], 1.0, alpha=0.1, color='red', zorder=1)
            
            # Mark minimum
            min_idx = np.argmin(stability_margin_values)
            ax3.plot(time_points[min_idx], stability_margin_values[min_idx], 'ro', markersize=12, zorder=6)
            ax3.annotate(f'Min: {stability_margin_values[min_idx]:.2f} cal @ {time_points[min_idx]:.1f}s',
                        xy=(time_points[min_idx], stability_margin_values[min_idx]),
                        xytext=(time_points[min_idx] * 1.1, stability_margin_values[min_idx] - 0.3),
                        fontsize=10, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.4', facecolor='orange', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
            
            ax3.set_xlabel("Time (s)", fontsize=13, fontweight='bold')
            ax3.set_ylabel("Stability Margin (calibers)", fontsize=13, fontweight='bold')
            ax3.set_title("Stability Margin (accounting for CP movement with Mach)", fontsize=14, fontweight='bold')
            ax3.legend(loc='best', fontsize=10, framealpha=0.9)
            ax3.grid(True, alpha=0.3, linestyle='--')
            ax3.set_xlim(left=0, right=t_max)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.debug(f"Complete CP/CoM evolution plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot complete CP/CoM evolution: {e}")
            return None

    def plot_all_stability_curves(self, output_dir: Path) -> dict:
        """Generate all comprehensive stability analysis plots.

        Creates a dedicated stability/ subdirectory with all stability plots
        following aerospace engineering best practices.

        Args:
            output_dir: Base output directory

        Returns:
            Dictionary mapping plot name to file path
        """
        stability_dir = output_dir / "stability"
        stability_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating comprehensive stability analysis plots in {stability_dir}")

        paths = {}

        # 1. Stability envelope - BEST: actual stability margin + safety zones + critical events + parachute
        path = self.plot_stability_envelope(stability_dir)
        if path:
            paths['stability_envelope'] = path

        # 2. Stability margin surface (3D: Mach vs Time) - shows relationship between Mach, Time, and Stability
        if hasattr(self.rocket, 'stability_margin'):
            path = self.plot_stability_margin_surface(stability_dir)
            if path:
                paths['stability_margin_surface'] = path

        # 3. CP travel analysis - shows CP movement vs Mach with flight regime regions
        path = self.plot_cp_travel_analysis(stability_dir)
        if path:
            paths['stability_cp_travel'] = path

        # 4. CP and CoM evolution - comprehensive view of how both change during flight
        path = self.plot_cp_com_evolution_complete(stability_dir)
        if path:
            paths['stability_cp_com_evolution'] = path

        # 5. Stability margin enhanced - RECOMMENDED: uses actual flight stability margin
        # Accounts for CP movement with Mach (more accurate than static margin for transonic flights)
        path = self.plot_static_margin_enhanced(stability_dir)
        if path:
            paths['stability_margin_enhanced'] = path

        # 5. Generate comprehensive text report
        path = self.generate_stability_report(stability_dir)
        if path:
            paths['stability_report'] = path

        logger.info(f"Generated {len(paths)} stability analysis plots and reports")
        return paths

    def plot_com_vs_cop_comparison(self, output_dir: Path) -> Optional[Path]:
        """Plot CoM and CoP evolution comparison over time.

        Shows how center of mass and center of pressure change during flight,
        and the distance between them (which determines stability margin).

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "com_vs_cop_evolution.png"

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

            # Get burn out time for x-axis limit
            burn_out = 10.0
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                if hasattr(self.rocket.motor, 'burn_out_time'):
                    burn_out = float(self.rocket.motor.burn_out_time)

            time_array = np.linspace(0, burn_out, 200)

            # Get CoM evolution
            com_values = [self.rocket.center_of_mass(t) for t in time_array]

            # Get CoP at Mach 0 (static)
            cp_value = self.rocket.cp_position(0)

            # Plot 1: CoM and CoP positions
            ax1.plot(time_array, com_values, 'b-', linewidth=3, label='Center of Mass (CoM)', zorder=5)
            ax1.axhline(y=cp_value, color='red', linestyle='--', linewidth=3,
                       label=f'Center of Pressure (CoP @ M=0) = {cp_value:.3f} m', zorder=4)

            # Fill area between CoM and CoP
            ax1.fill_between(time_array, com_values, cp_value, alpha=0.2, color='green',
                            label='CP-CM Distance', zorder=1)

            ax1.set_ylabel("Position (m)", fontsize=13, fontweight='bold')
            ax1.set_title("Center of Mass and Center of Pressure Evolution", fontsize=15, fontweight='bold')
            ax1.legend(loc='best', fontsize=11, framealpha=0.9)
            ax1.grid(True, alpha=0.3, linestyle='--')

            # Mark burn out
            ax1.axvline(x=burn_out, color='purple', linestyle=':', linewidth=2,
                       alpha=0.7, label=f'Burn Out ({burn_out:.2f}s)', zorder=4)

            # Plot 2: CP-CM distance (stability indicator)
            cp_cm_distance = [cp_value - com for com in com_values]
            rocket_radius = float(self.rocket.radius) if hasattr(self.rocket, 'radius') else 0.1
            stability_calibers = [dist / (2 * rocket_radius) for dist in cp_cm_distance]

            ax2.plot(time_array, stability_calibers, 'g-', linewidth=3, label='Static Margin (at Mach=0)', zorder=5)

            # Add threshold lines
            ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2,
                       alpha=0.7, label='Minimum (1.0 cal)', zorder=3)
            ax2.axhline(y=1.5, color='orange', linestyle='--', linewidth=2,
                       alpha=0.7, label='Recommended (1.5 cal)', zorder=3)
            ax2.axhspan(2.0, 2.5, alpha=0.15, color='green', label='Design Target', zorder=1)

            # Mark burn out
            ax2.axvline(x=burn_out, color='purple', linestyle=':', linewidth=2,
                       alpha=0.7, zorder=4)

            ax2.set_xlabel("Time (s)", fontsize=13, fontweight='bold')
            ax2.set_ylabel("Static Margin (calibers)", fontsize=13, fontweight='bold')
            ax2.set_title("Static Margin (at Mach=0) Derived from CP-CM Distance", fontsize=15, fontweight='bold')
            ax2.legend(loc='best', fontsize=11, framealpha=0.9)
            ax2.grid(True, alpha=0.3, linestyle='--')
            ax2.set_xlim(left=0, right=burn_out * 1.1)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"CoM vs CoP comparison plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot CoM vs CoP comparison: {e}")
            return None

    def plot_stability_envelope(self, output_dir: Path) -> Optional[Path]:
        """Plot stability envelope showing safe/marginal/unsafe zones.

        Creates a diagram showing the actual stability margin throughout the flight
        accounting for CP movement with Mach number. This uses rocket.stability_margin(mach, time)
        which is more accurate than static_margin for transonic/supersonic flights.

        Args:
            output_dir: Output directory

        Returns:
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "stability_envelope.png"

            # Calculate actual stability margin using real Mach number at each time
            if self.flight is None:
                logger.warning("Flight object required for stability envelope - falling back to static margin")
                data = self._sample_function(self.rocket.static_margin)
            else:
                # Determine time range: extend to shortly after parachute deployment
                t_max = self.flight.t_final
                if self.parachute_deploy_time is not None and self.parachute_deploy_time < self.flight.t_final:
                    # Extend to 10s after deployment or 20% beyond, whichever is less
                    t_max = min(self.parachute_deploy_time + 10, self.parachute_deploy_time * 1.2, self.flight.t_final)
                
                # Sample time points
                time_points = np.linspace(0, t_max, 200)
                stability_values = []
                
                for t in time_points:
                    try:
                        # Get Mach number at this time from flight data
                        mach = float(self.flight.mach_number(t))
                        # Calculate stability margin at this Mach and time
                        # Note: stability_margin is a Function object, call it directly
                        sm = float(self.rocket.stability_margin(mach, t))
                        stability_values.append([t, sm])
                    except Exception as e:
                        # Log first error for debugging
                        if len(stability_values) == 0:
                            logger.warning(f"Failed to compute stability margin at t={t:.2f}s, mach={mach if 'mach' in locals() else 'N/A'}: {e}")
                        pass
                
                if len(stability_values) == 0:
                    logger.warning("Could not compute stability margin data for envelope plot")
                    return None
                
                data = np.array(stability_values)
            
            if data is None or len(data) == 0:
                logger.warning("No stability margin data available for envelope plot")
                return None

            fig, ax = plt.subplots(figsize=(14, 8))

            # Define stability zones
            zones = [
                {'ymin': -np.inf, 'ymax': 0, 'color': 'darkred', 'alpha': 0.3, 'label': 'UNSTABLE (SM<0)'},
                {'ymin': 0, 'ymax': 1.0, 'color': 'red', 'alpha': 0.2, 'label': 'UNSAFE (0<SM<1.0)'},
                {'ymin': 1.0, 'ymax': 1.5, 'color': 'yellow', 'alpha': 0.2, 'label': 'MARGINAL (1.0<SM<1.5)'},
                {'ymin': 1.5, 'ymax': 2.0, 'color': 'lightgreen', 'alpha': 0.2, 'label': 'ACCEPTABLE (1.5<SM<2.0)'},
                {'ymin': 2.0, 'ymax': 2.5, 'color': 'green', 'alpha': 0.3, 'label': 'DESIGN TARGET (2.0<SM<2.5)'},
                {'ymin': 2.5, 'ymax': np.inf, 'color': 'lightblue', 'alpha': 0.15, 'label': 'VERY STABLE (SM>2.5)'},
            ]

            # Get y-axis limits based on data
            y_min = min(data[:, 1])
            y_max = max(data[:, 1])
            y_range = y_max - y_min
            y_plot_min = y_min - 0.2 * y_range
            y_plot_max = y_max + 0.2 * y_range

            # Plot zones
            for zone in zones:
                ymin = max(zone['ymin'], y_plot_min)
                ymax = min(zone['ymax'], y_plot_max)
                if ymin < ymax:
                    ax.axhspan(ymin, ymax, alpha=zone['alpha'], color=zone['color'],
                              label=zone['label'], zorder=1)

            # Plot stability margin trajectory
            ax.plot(data[:, 0], data[:, 1], 'b-', linewidth=3.5,
                   label='Flight Stability Margin', zorder=5, marker='o', markersize=4, markevery=10)

            # Add zone boundary lines
            for threshold in [0, 1.0, 1.5, 2.0, 2.5]:
                if y_plot_min <= threshold <= y_plot_max:
                    ax.axhline(y=threshold, color='black', linestyle='--',
                              linewidth=1, alpha=0.5, zorder=2)

            # Mark critical points
            min_idx = np.argmin(data[:, 1])
            max_idx = np.argmax(data[:, 1])
            ax.plot(data[min_idx, 0], data[min_idx, 1], 'ro',
                   markersize=15, zorder=6, label=f'Minimum: {data[min_idx, 1]:.2f} cal @ {data[min_idx, 0]:.1f}s')
            ax.plot(data[max_idx, 0], data[max_idx, 1], 'go',
                   markersize=15, zorder=6, label=f'Maximum: {data[max_idx, 1]:.2f} cal @ {data[max_idx, 0]:.1f}s')
            
            # Mark critical flight events
            if self.burnout_time is not None:
                ax.axvline(x=self.burnout_time, color='purple', linestyle=':', 
                          linewidth=2, alpha=0.6, label=f'Burnout ({self.burnout_time:.1f}s)', zorder=4)
            if self.max_q_time is not None:
                ax.axvline(x=self.max_q_time, color='orange', linestyle=':', 
                          linewidth=2, alpha=0.6, label=f'Max-Q ({self.max_q_time:.1f}s)', zorder=4)
            if self.apogee_time is not None and self.apogee_time < data[-1, 0]:
                ax.axvline(x=self.apogee_time, color='green', linestyle=':', 
                          linewidth=2, alpha=0.6, label=f'Apogee ({self.apogee_time:.1f}s)', zorder=4)
            if self.parachute_deploy_time is not None and self.parachute_deploy_time < data[-1, 0]:
                ax.axvline(x=self.parachute_deploy_time, color='cyan', linestyle=':', 
                          linewidth=2.5, alpha=0.7, label=f'Parachute Deploy ({self.parachute_deploy_time:.1f}s)', zorder=4)

            ax.set_xlabel("Time (s)", fontsize=13, fontweight='bold')
            ax.set_ylabel("Stability Margin (calibers)", fontsize=13, fontweight='bold')
            ax.set_title("Stability Envelope - Actual Flight Stability (function of Mach & Time)", fontsize=15, fontweight='bold')
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10, framealpha=0.95)
            ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
            ax.set_xlim(left=0)
            ax.set_ylim(y_plot_min, y_plot_max)

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

            logger.debug(f"Stability envelope plot saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not plot stability envelope: {e}")
            return None

    def generate_stability_report(self, output_dir: Path) -> Optional[Path]:
        """Generate comprehensive stability analysis text report.

        Creates a detailed text report following aerospace engineering guidelines
        for rocket stability analysis.

        Args:
            output_dir: Output directory

        Returns:
            Path to created report or None if failed
        """
        try:
            output_path = output_dir / "STABILITY_REPORT.txt"

            # Sample static margin data
            data = self._sample_function(self.rocket.static_margin)
            if data is None or len(data) == 0:
                logger.warning("No static margin data available for stability report")
                return None

            # Calculate key metrics
            min_idx = np.argmin(data[:, 1])
            max_idx = np.argmax(data[:, 1])
            min_sm = data[min_idx, 1]
            min_sm_time = data[min_idx, 0]
            max_sm = data[max_idx, 1]
            max_sm_time = data[max_idx, 0]
            initial_sm = data[0, 1]

            # Get burn out time and SM at burnout
            burn_out = None
            sm_at_burnout = None
            if hasattr(self.rocket, 'motor') and self.rocket.motor:
                if hasattr(self.rocket.motor, 'burn_out_time'):
                    burn_out = float(self.rocket.motor.burn_out_time)
                    sm_at_burnout = self.rocket.static_margin(burn_out)

            # Calculate CP travel in transonic region
            cp_at_08 = self.rocket.cp_position(0.8)
            cp_at_12 = self.rocket.cp_position(1.2)
            cp_shift_transonic = abs(cp_at_12 - cp_at_08)

            # Determine stability verdict
            if min_sm < 0:
                verdict = "UNSTABLE - FLIGHT NOT RECOMMENDED"
                verdict_color = "CRITICAL"
            elif min_sm < 1.0:
                verdict = "UNSAFE - HIGH RISK OF INSTABILITY"
                verdict_color = "DANGER"
            elif min_sm < 1.5:
                verdict = "MARGINAL - Acceptable only for subsonic flight"
                verdict_color = "WARNING"
            elif min_sm < 2.0:
                verdict = "ACCEPTABLE - Good for most applications"
                verdict_color = "ACCEPTABLE"
            else:
                verdict = "SAFE - Excellent stability margin"
                verdict_color = "SAFE"

            # Write report
            with open(output_path, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("COMPREHENSIVE ROCKET STABILITY ANALYSIS REPORT\n")
                f.write("=" * 80 + "\n\n")

                f.write("EXECUTIVE SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(f"Overall Stability Verdict: {verdict}\n")
                f.write(f"Assessment Level: [{verdict_color}]\n")
                f.write(f"Minimum Stability Margin: {min_sm:.3f} calibers @ t={min_sm_time:.2f}s\n\n")

                f.write("=" * 80 + "\n")
                f.write("1. STABILITY MARGIN ANALYSIS\n")
                f.write("=" * 80 + "\n\n")

                f.write("1.1 Key Stability Metrics:\n")
                f.write("-" * 40 + "\n")
                f.write(f"  Initial Stability Margin (t=0):        {initial_sm:.3f} calibers\n")
                f.write(f"  Minimum Stability Margin:              {min_sm:.3f} calibers @ t={min_sm_time:.2f}s\n")
                f.write(f"  Maximum Stability Margin:              {max_sm:.3f} calibers @ t={max_sm_time:.2f}s\n")
                if burn_out is not None and sm_at_burnout is not None:
                    f.write(f"  Stability Margin at Burnout:           {sm_at_burnout:.3f} calibers @ t={burn_out:.2f}s\n")
                f.write(f"  Stability Margin Variation:            {max_sm - min_sm:.3f} calibers\n\n")

                f.write("1.2 Aerospace Engineering Guidelines:\n")
                f.write("-" * 40 + "\n")
                f.write("  Minimum Safety Threshold:              1.0 calibers\n")
                f.write("  Recommended for Subsonic Flight:       1.5 calibers\n")
                f.write("  Design Target Range:                   2.0 - 2.5 calibers\n\n")

                f.write("1.3 Compliance Assessment:\n")
                f.write("-" * 40 + "\n")
                f.write(f"  Above 1.0 caliber (minimum):          {'YES' if min_sm >= 1.0 else 'NO [CRITICAL]'}\n")
                f.write(f"  Above 1.5 calibers (recommended):     {'YES' if min_sm >= 1.5 else 'NO'}\n")
                f.write(f"  In design target (2.0-2.5):           {'YES' if 2.0 <= min_sm <= 2.5 else 'NO'}\n\n")

                f.write("=" * 80 + "\n")
                f.write("2. CENTER OF PRESSURE ANALYSIS\n")
                f.write("=" * 80 + "\n\n")

                f.write("2.1 CP Travel in Transonic Region (M=0.8 to M=1.2):\n")
                f.write("-" * 40 + "\n")
                f.write(f"  CP Position at M=0.8:                  {cp_at_08:.4f} m\n")
                f.write(f"  CP Position at M=1.2:                  {cp_at_12:.4f} m\n")
                f.write(f"  CP Shift (transonic):                  {cp_shift_transonic:.4f} m ({cp_shift_transonic*100:.2f} cm)\n\n")

                f.write("2.2 Transonic Stability Considerations:\n")
                f.write("-" * 40 + "\n")
                if cp_shift_transonic > 0.01:  # 1 cm
                    f.write(f"  WARNING: Significant CP shift detected ({cp_shift_transonic*100:.2f} cm)\n")
                    f.write("  This can reduce stability margin by 0.5-1.0 calibers in transonic region.\n")
                    f.write("  Static margin alone is INADEQUATE for supersonic flight analysis.\n")
                    f.write("  Review stability margin surface plot (Mach vs Time) carefully.\n")
                else:
                    f.write("  Minimal CP travel detected in transonic region.\n")
                    f.write("  Static margin analysis is likely sufficient.\n")
                f.write("\n")

                f.write("=" * 80 + "\n")
                f.write("3. RECOMMENDATIONS & ACTION ITEMS\n")
                f.write("=" * 80 + "\n\n")

                if min_sm < 0:
                    f.write("  CRITICAL ACTIONS REQUIRED:\n")
                    f.write("  - DO NOT FLY - Rocket is aerodynamically unstable\n")
                    f.write("  - Increase fin size significantly (area and/or span)\n")
                    f.write("  - Move fins further aft on the rocket body\n")
                    f.write("  - Reduce nose weight or move CG forward\n")
                    f.write("  - Re-run analysis after design changes\n\n")
                elif min_sm < 1.0:
                    f.write("  HIGH PRIORITY ACTIONS:\n")
                    f.write("  - Flight is NOT RECOMMENDED with current configuration\n")
                    f.write("  - Increase fin size or adjust fin position to achieve SM >= 1.5 cal\n")
                    f.write("  - Consider adding ballast to move CG forward\n")
                    f.write("  - Re-analyze after modifications\n\n")
                elif min_sm < 1.5:
                    f.write("  RECOMMENDED IMPROVEMENTS:\n")
                    f.write("  - Stability is marginal - increase to >= 1.5 calibers for safety\n")
                    f.write("  - Consider slightly larger fins or move fins aft\n")
                    f.write("  - Acceptable for subsonic flight only\n\n")
                elif min_sm < 2.0:
                    f.write("  OPTIONAL OPTIMIZATIONS:\n")
                    f.write("  - Stability is acceptable for most applications\n")
                    f.write("  - Consider targeting 2.0-2.5 calibers for optimal safety margin\n\n")
                else:
                    f.write("  DESIGN APPROVED:\n")
                    f.write("  - Excellent stability margin\n")
                    f.write("  - Safe for flight\n")
                    f.write("  - Well within aerospace engineering guidelines\n\n")

                f.write("=" * 80 + "\n")
                f.write("END OF REPORT\n")
                f.write("=" * 80 + "\n")

            logger.debug(f"Stability analysis report saved to {output_path}")
            return output_path

        except Exception as e:
            logger.warning(f"Could not generate stability report: {e}")
            return None

    def _get_plot_time_limit(self) -> float:
        """Determine appropriate time limit for flight plots.
        
        Returns time that includes parachute deployment events to show
        dynamics during and after deployment.
        
        Returns
        -------
        float
            Time limit in seconds
        """
        # Default: full flight time
        time_limit = self.flight.t_final
        
        # If we have parachute events, extend beyond first parachute
        if hasattr(self.flight, 'parachute_events') and self.flight.parachute_events:
            # Get time of last parachute deployment
            last_chute_time = max(event[0] for event in self.flight.parachute_events)
            # Add 10% of flight time after last chute or 20 seconds, whichever is less
            extension = min(0.1 * self.flight.t_final, 20.0)
            time_limit = min(last_chute_time + extension, self.flight.t_final)
        # Otherwise use apogee + extension if available
        elif hasattr(self.flight, 'apogee_time') and self.flight.apogee_time > 0:
            # Add 30% of time to apogee or 30 seconds after apogee
            extension = min(0.3 * self.flight.apogee_time, 30.0)
            time_limit = min(self.flight.apogee_time + extension, self.flight.t_final)
        
        return time_limit

    def plot_all_flight_curves(self, output_dir: Path) -> dict:
        """Generate all flight data plots.
        
        Args:
            output_dir: Base output directory
            
        Returns:
            Dictionary mapping curve name to file path
        """
        flight_dir = output_dir / "flight"
        flight_dir.mkdir(parents=True, exist_ok=True)
        
        paths = {}
        
        logger.info(f"Generating flight curve plots in {flight_dir}")
        
        # 1. 3D Trajectory
        path = self.plot_trajectory_3d(flight_dir)
        if path:
            paths['flight_trajectory_3d'] = path
        
        # 2. Position data (x, y, z vs time)
        path = self.plot_position_data(flight_dir)
        if path:
            paths['flight_position_data'] = path
        
        # 3. Linear kinematics (velocities and accelerations)
        path = self.plot_linear_kinematics_data(flight_dir)
        if path:
            paths['flight_linear_kinematics'] = path
        
        # 4. Flight path angle
        path = self.plot_flight_path_angle_data(flight_dir)
        if path:
            paths['flight_path_angle'] = path
        
        # 5. Attitude data (Euler angles)
        path = self.plot_attitude_data(flight_dir)
        if path:
            paths['flight_attitude_data'] = path
        
        # 6. Angular kinematics (angular velocities and accelerations)
        path = self.plot_angular_kinematics_data(flight_dir)
        if path:
            paths['flight_angular_kinematics'] = path
        
        # 7. Aerodynamic forces (lift, drag, moments)
        path = self.plot_aerodynamic_forces(flight_dir)
        if path:
            paths['flight_aerodynamic_forces'] = path
        
        # 8. Rail buttons forces
        path = self.plot_rail_buttons_forces(flight_dir)
        if path:
            paths['flight_rail_buttons_forces'] = path
        
        # 9. Energy data (kinetic, potential, thrust power, drag power)
        path = self.plot_energy_data(flight_dir)
        if path:
            paths['flight_energy_data'] = path
        
        # 10. Fluid mechanics data (Mach, Reynolds, pressures, angles of attack)
        path = self.plot_fluid_mechanics_data(flight_dir)
        if path:
            paths['flight_fluid_mechanics'] = path
        
        # 11. Stability and control data (stability margin, frequency response)
        path = self.plot_stability_and_control_data(flight_dir)
        if path:
            paths['flight_stability_control'] = path
        
        logger.info(f"Generated {len(paths)} flight curve plots")
        return paths

    def plot_position_data(self, output_dir: Path) -> Optional[Path]:
        """Plot position components (x, y, z) vs time.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "position_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 10))
            
            # X position (East)
            ax1.plot(
                self.flight.x[:, 0],
                self.flight.x[:, 1],
                color='#1f77b4',
                linewidth=2,
                label='X - East'
            )
            ax1.set_xlim(0, time_limit)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('X Position (m)')
            ax1.set_title('X - East Component')
            ax1.grid(True, alpha=0.3)
            ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            
            # Y position (North)
            ax2.plot(
                self.flight.y[:, 0],
                self.flight.y[:, 1],
                color='#ff7f0e',
                linewidth=2,
                label='Y - North'
            )
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Y Position (m)')
            ax2.set_title('Y - North Component')
            ax2.grid(True, alpha=0.3)
            ax2.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            
            # Z position (Altitude)
            ax3.plot(
                self.flight.z[:, 0],
                self.flight.z[:, 1],
                color='#2ca02c',
                linewidth=2,
                label='Z - Altitude'
            )
            # Mark apogee
            if hasattr(self.flight, 'apogee') and hasattr(self.flight, 'apogee_time'):
                ax3.scatter(
                    [self.flight.apogee_time],
                    [self.flight.apogee],
                    color='red',
                    s=100,
                    marker='^',
                    label=f'Apogee: {self.flight.apogee:.1f} m',
                    zorder=5
                )
            ax3.set_xlim(0, time_limit)
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Z Position (m)')
            ax3.set_title('Z - Altitude')
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            ax3.axhline(y=0, color='gray', linestyle='--', linewidth=0.8, alpha=0.5)
            
            fig.suptitle('Position Data', fontsize=14, y=0.995)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.debug(f"Position data plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot position data: {e}")
            return None

    def plot_trajectory_3d(self, output_dir: Path) -> Optional[Path]:
        """Plot 3D trajectory with projections on XY, XZ, and YZ planes.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            from mpl_toolkits.mplot3d import Axes3D
            
            output_path = output_dir / "trajectory_3d.png"
            
            # Extract trajectory data
            x = self.flight.x[:, 1]
            y = self.flight.y[:, 1]
            z = self.flight.z[:, 1]
            
            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111, projection='3d')
            
            # Main 3D trajectory
            ax.plot(x, y, z, linewidth=2.5, color='#1f77b4', label='Flight Path')
            
            # Project on XY plane (ground track)
            ax.plot(x, y, np.min(z) * np.ones_like(z), 
                   linewidth=1, color='gray', alpha=0.5, linestyle='--')
            
            # Project on XZ plane
            ax.plot(x, np.max(y) * np.ones_like(y), z,
                   linewidth=1, color='gray', alpha=0.5, linestyle='--')
            
            # Project on YZ plane
            ax.plot(np.min(x) * np.ones_like(x), y, z,
                   linewidth=1, color='gray', alpha=0.5, linestyle='--')
            
            # Mark key points
            ax.scatter([x[0]], [y[0]], [z[0]], 
                      color='green', s=100, marker='o', label='Launch', zorder=5)
            
            # Mark apogee at the maximum altitude point in the trajectory
            apogee_idx = np.argmax(z)
            if hasattr(self.flight, 'apogee') and hasattr(self.flight, 'apogee_time'):
                # Use max point position but show official apogee values in label
                ax.scatter([x[apogee_idx]], [y[apogee_idx]], [z[apogee_idx]],
                          color='red', s=200, marker='^', 
                          label=f'Apogee: {self.flight.apogee:.1f} m @ {self.flight.apogee_time:.1f} s', 
                          zorder=10, edgecolors='darkred', linewidths=2)
            else:
                # Fallback: use max altitude
                ax.scatter([x[apogee_idx]], [y[apogee_idx]], [z[apogee_idx]],
                          color='red', s=200, marker='^', label='Apogee', 
                          zorder=10, edgecolors='darkred', linewidths=2)
            
            # Find landing
            ax.scatter([x[-1]], [y[-1]], [z[-1]],
                      color='orange', s=100, marker='s', label='Landing', zorder=5)
            
            ax.set_xlabel('X (m) - East')
            ax.set_ylabel('Y (m) - North')
            ax.set_zlabel('Z (m) - Altitude')
            ax.set_title('3D Flight Trajectory')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.debug(f"3D trajectory plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot 3D trajectory: {e}")
            return None

    def plot_linear_kinematics_data(self, output_dir: Path) -> Optional[Path]:
        """Plot linear velocities and accelerations (vx, vy, vz, ax, ay, az).

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "linear_kinematics_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            
            # X velocity and acceleration
            ax1 = axes[0, 0]
            ax1_twin = ax1.twinx()
            ax1.plot(self.flight.vx[:, 0], self.flight.vx[:, 1], 
                    color='#1f77b4', linewidth=2, label='Vx')
            ax1_twin.plot(self.flight.ax[:, 0], self.flight.ax[:, 1],
                         color='#ff7f0e', linewidth=2, label='Ax', linestyle='--')
            ax1.set_xlim(0, time_limit)
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Vx (m/s)', color='#1f77b4')
            ax1_twin.set_ylabel('Ax (m/s²)', color='#ff7f0e')
            ax1.set_title('X - East Component')
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='y', labelcolor='#1f77b4')
            ax1_twin.tick_params(axis='y', labelcolor='#ff7f0e')
            
            # Y velocity and acceleration
            ax2 = axes[0, 1]
            ax2_twin = ax2.twinx()
            ax2.plot(self.flight.vy[:, 0], self.flight.vy[:, 1],
                    color='#1f77b4', linewidth=2, label='Vy')
            ax2_twin.plot(self.flight.ay[:, 0], self.flight.ay[:, 1],
                         color='#ff7f0e', linewidth=2, label='Ay', linestyle='--')
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Vy (m/s)', color='#1f77b4')
            ax2_twin.set_ylabel('Ay (m/s²)', color='#ff7f0e')
            ax2.set_title('Y - North Component')
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='y', labelcolor='#1f77b4')
            ax2_twin.tick_params(axis='y', labelcolor='#ff7f0e')
            
            # Z velocity and acceleration
            ax3 = axes[1, 0]
            ax3_twin = ax3.twinx()
            ax3.plot(self.flight.vz[:, 0], self.flight.vz[:, 1],
                    color='#1f77b4', linewidth=2, label='Vz')
            ax3_twin.plot(self.flight.az[:, 0], self.flight.az[:, 1],
                         color='#ff7f0e', linewidth=2, label='Az', linestyle='--')
            ax3.set_xlim(0, time_limit)
            ax3.set_xlabel('Time (s)')
            ax3.set_ylabel('Vz (m/s)', color='#1f77b4')
            ax3_twin.set_ylabel('Az (m/s²)', color='#ff7f0e')
            ax3.set_title('Z - Altitude Component')
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='y', labelcolor='#1f77b4')
            ax3_twin.tick_params(axis='y', labelcolor='#ff7f0e')
            
            # Total speed and acceleration magnitude
            ax4 = axes[1, 1]
            ax4_twin = ax4.twinx()
            ax4.plot(self.flight.speed[:, 0], self.flight.speed[:, 1],
                    color='#1f77b4', linewidth=2, label='Speed')
            ax4_twin.plot(self.flight.acceleration[:, 0], self.flight.acceleration[:, 1],
                         color='#ff7f0e', linewidth=2, label='Acceleration', linestyle='--')
            ax4.set_xlim(0, time_limit)
            ax4.set_xlabel('Time (s)')
            ax4.set_ylabel('Speed (m/s)', color='#1f77b4')
            ax4_twin.set_ylabel('Acceleration (m/s²)', color='#ff7f0e')
            ax4.set_title('Total Magnitude')
            ax4.grid(True, alpha=0.3)
            ax4.tick_params(axis='y', labelcolor='#1f77b4')
            ax4_twin.tick_params(axis='y', labelcolor='#ff7f0e')
            
            fig.suptitle('Linear Kinematics Data', fontsize=14, y=0.995)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.debug(f"Linear kinematics plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot linear kinematics: {e}")
            return None

    def plot_flight_path_angle_data(self, output_dir: Path) -> Optional[Path]:
        """Plot flight path angle vs attitude angle and lateral attitude angle.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "flight_path_angle_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 8))
            
            # Flight path angle vs Attitude angle
            ax1.plot(
                self.flight.attitude_angle[:, 0],
                self.flight.attitude_angle[:, 1],
                label="Attitude Angle",
                color='#1f77b4',
                linewidth=2
            )
            ax1.plot(
                self.flight.path_angle[:, 0],
                self.flight.path_angle[:, 1],
                label="Flight Path Angle",
                color='#ff7f0e',
                linewidth=2,
                linestyle='--'
            )
            ax1.set_xlim(0, time_limit)
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Angle (°)")
            ax1.set_title("Flight Path Angle vs Attitude Angle")
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Lateral attitude angle
            ax2.plot(
                self.flight.lateral_attitude_angle[:, 0],
                self.flight.lateral_attitude_angle[:, 1],
                label="Lateral Attitude Angle",
                color='#2ca02c',
                linewidth=2
            )
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Angle (°)")
            ax2.set_title("Lateral Attitude Angle")
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.debug(f"Flight path angle plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot flight path angle: {e}")
            return None

    def plot_attitude_data(self, output_dir: Path) -> Optional[Path]:
        """Plot Euler angles (psi, theta, phi) vs time.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "attitude_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9, 12))
            
            # Attitude angle (combined)
            ax1.plot(
                self.flight.attitude_angle[:, 0],
                self.flight.attitude_angle[:, 1],
                label="Attitude Angle"
            )
            ax1.set_xlim(0, time_limit)
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Attitude Angle (°)")
            ax1.set_title("Rocket Attitude Angle")
            ax1.grid(True)
            
            # Psi - Precession
            ax2.plot(self.flight.psi[:, 0], self.flight.psi[:, 1], label="ψ - Precession")
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("ψ (°)")
            ax2.set_title("Euler Precession Angle")
            ax2.grid(True)
            
            # Theta - Nutation
            ax3.plot(self.flight.theta[:, 0], self.flight.theta[:, 1], label="θ - Nutation")
            ax3.set_xlim(0, time_limit)
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("θ (°)")
            ax3.set_title("Euler Nutation Angle")
            ax3.grid(True)
            
            # Phi - Spin
            ax4.plot(self.flight.phi[:, 0], self.flight.phi[:, 1], label="φ - Spin")
            ax4.set_xlim(0, time_limit)
            ax4.set_xlabel("Time (s)")
            ax4.set_ylabel("φ (°)")
            ax4.set_title("Euler Spin Angle")
            ax4.grid(True)
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Attitude data plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot attitude data: {e}")
            return None

    def plot_angular_kinematics_data(self, output_dir: Path) -> Optional[Path]:
        """Plot angular velocities and accelerations.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "angular_kinematics_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 9))
            
            # Omega1 and Alpha1
            ax1.plot(self.flight.w1[:, 0], self.flight.w1[:, 1], color="#ff7f0e")
            ax1.set_xlim(0, time_limit)
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel(r"Angular Velocity - ${\omega_1}$ (rad/s)", color="#ff7f0e")
            ax1.set_title(r"Angular Velocity ${\omega_1}$ | Angular Acceleration ${\alpha_1}$")
            ax1.tick_params("y", colors="#ff7f0e")
            ax1.grid(True)
            
            ax1up = ax1.twinx()
            ax1up.plot(self.flight.alpha1[:, 0], self.flight.alpha1[:, 1], color="#1f77b4")
            ax1up.set_ylabel(r"Angular Acceleration - ${\alpha_1}$ (rad/s²)", color="#1f77b4")
            ax1up.tick_params("y", colors="#1f77b4")
            
            # Omega2 and Alpha2
            ax2.plot(self.flight.w2[:, 0], self.flight.w2[:, 1], color="#ff7f0e")
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel(r"Angular Velocity - ${\omega_2}$ (rad/s)", color="#ff7f0e")
            ax2.set_title(r"Angular Velocity ${\omega_2}$ | Angular Acceleration ${\alpha_2}$")
            ax2.tick_params("y", colors="#ff7f0e")
            ax2.grid(True)
            
            ax2up = ax2.twinx()
            ax2up.plot(self.flight.alpha2[:, 0], self.flight.alpha2[:, 1], color="#1f77b4")
            ax2up.set_ylabel(r"Angular Acceleration - ${\alpha_2}$ (rad/s²)", color="#1f77b4")
            ax2up.tick_params("y", colors="#1f77b4")
            
            # Omega3 and Alpha3
            ax3.plot(self.flight.w3[:, 0], self.flight.w3[:, 1], color="#ff7f0e")
            ax3.set_xlim(0, time_limit)
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel(r"Angular Velocity - ${\omega_3}$ (rad/s)", color="#ff7f0e")
            ax3.set_title(r"Angular Velocity ${\omega_3}$ | Angular Acceleration ${\alpha_3}$")
            ax3.tick_params("y", colors="#ff7f0e")
            ax3.grid(True)
            
            ax3up = ax3.twinx()
            ax3up.plot(self.flight.alpha3[:, 0], self.flight.alpha3[:, 1], color="#1f77b4")
            ax3up.set_ylabel(r"Angular Acceleration - ${\alpha_3}$ (rad/s²)", color="#1f77b4")
            ax3up.tick_params("y", colors="#1f77b4")
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Angular kinematics plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot angular kinematics: {e}")
            return None

    def plot_aerodynamic_forces(self, output_dir: Path) -> Optional[Path]:
        """Plot aerodynamic forces and moments.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "aerodynamic_forces.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            time_limit_index = np.searchsorted(self.flight.time[:, 0], time_limit)
            
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9, 12))
            
            # Aerodynamic Lift
            ax1.plot(
                self.flight.aerodynamic_lift[: time_limit_index, 0],
                self.flight.aerodynamic_lift[: time_limit_index, 1],
                label="Resultant"
            )
            ax1.plot(
                self.flight.R1[: time_limit_index, 0],
                self.flight.R1[: time_limit_index, 1],
                label="R1"
            )
            ax1.plot(
                self.flight.R2[: time_limit_index, 0],
                self.flight.R2[: time_limit_index, 1],
                label="R2"
            )
            ax1.set_xlim(0, time_limit)
            ax1.legend()
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Lift Force (N)")
            ax1.set_title("Aerodynamic Lift Resultant Force")
            ax1.grid()
            
            # Aerodynamic Drag
            ax2.plot(
                self.flight.aerodynamic_drag[: time_limit_index, 0],
                self.flight.aerodynamic_drag[: time_limit_index, 1]
            )
            ax2.set_xlim(0, time_limit)
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Drag Force (N)")
            ax2.set_title("Aerodynamic Drag Force")
            ax2.grid()
            
            # Aerodynamic Bending Moment
            ax3.plot(
                self.flight.aerodynamic_bending_moment[: time_limit_index, 0],
                self.flight.aerodynamic_bending_moment[: time_limit_index, 1],
                label="Resultant"
            )
            ax3.plot(
                self.flight.M1[: time_limit_index, 0],
                self.flight.M1[: time_limit_index, 1],
                label="M1"
            )
            ax3.plot(
                self.flight.M2[: time_limit_index, 0],
                self.flight.M2[: time_limit_index, 1],
                label="M2"
            )
            ax3.set_xlim(0, time_limit)
            ax3.legend()
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("Bending Moment (N m)")
            ax3.set_title("Aerodynamic Bending Resultant Moment")
            ax3.grid()
            
            # Aerodynamic Spin Moment
            ax4.plot(
                self.flight.aerodynamic_spin_moment[: time_limit_index, 0],
                self.flight.aerodynamic_spin_moment[: time_limit_index, 1]
            )
            ax4.set_xlim(0, time_limit)
            ax4.set_xlabel("Time (s)")
            ax4.set_ylabel("Spin Moment (N m)")
            ax4.set_title("Aerodynamic Spin Moment")
            ax4.grid()
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Aerodynamic forces plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot aerodynamic forces: {e}")
            return None

    def plot_rail_buttons_forces(self, output_dir: Path) -> Optional[Path]:
        """Plot rail button forces during rail phase.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            # Check if rail buttons exist
            if len(self.flight.rocket.rail_buttons) == 0:
                logger.info("No rail buttons defined - skipping rail button plots")
                return None
            
            # Check if there's a rail phase
            if not hasattr(self.flight, 'out_of_rail_time_index') or self.flight.out_of_rail_time_index == 0:
                logger.info("No rail phase found - skipping rail button plots")
                return None
            
            output_path = output_dir / "rail_buttons_forces.png"
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))
            
            # Normal Forces
            ax1.plot(
                self.flight.rail_button1_normal_force[: self.flight.out_of_rail_time_index, 0],
                self.flight.rail_button1_normal_force[: self.flight.out_of_rail_time_index, 1],
                label="Upper Rail Button"
            )
            ax1.plot(
                self.flight.rail_button2_normal_force[: self.flight.out_of_rail_time_index, 0],
                self.flight.rail_button2_normal_force[: self.flight.out_of_rail_time_index, 1],
                label="Lower Rail Button"
            )
            ax1.set_xlim(
                0,
                self.flight.out_of_rail_time if self.flight.out_of_rail_time > 0 else self.flight.t_final
            )
            ax1.legend()
            ax1.grid(True)
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Normal Force (N)")
            ax1.set_title("Rail Buttons Normal Force")
            
            # Shear Forces
            ax2.plot(
                self.flight.rail_button1_shear_force[: self.flight.out_of_rail_time_index, 0],
                self.flight.rail_button1_shear_force[: self.flight.out_of_rail_time_index, 1],
                label="Upper Rail Button"
            )
            ax2.plot(
                self.flight.rail_button2_shear_force[: self.flight.out_of_rail_time_index, 0],
                self.flight.rail_button2_shear_force[: self.flight.out_of_rail_time_index, 1],
                label="Lower Rail Button"
            )
            ax2.set_xlim(
                0,
                self.flight.out_of_rail_time if self.flight.out_of_rail_time > 0 else self.flight.t_final
            )
            ax2.legend()
            ax2.grid(True)
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Shear Force (N)")
            ax2.set_title("Rail Buttons Shear Force")
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Rail buttons forces plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot rail button forces: {e}")
            return None

    def plot_energy_data(self, output_dir: Path) -> Optional[Path]:
        """Plot energy components and power.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "energy_data.png"
            
            # Determine time limit for energy plots
            apogee_time = self.flight.apogee_time if self.flight.apogee_time > 0 else self.flight.t_final
            
            fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(9, 13))
            
            # Total Mechanical Energy
            ax1.plot(
                self.flight.total_energy[:, 0],
                self.flight.total_energy[:, 1]
            )
            ax1.set_xlim(0, apogee_time)
            ax1.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax1.set_title("Total Mechanical Energy")
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Energy (J)")
            ax1.grid()
            
            # Energy Components
            ax2.plot(
                self.flight.kinetic_energy[:, 0],
                self.flight.kinetic_energy[:, 1],
                label="Kinetic Energy"
            )
            ax2.plot(
                self.flight.potential_energy[:, 0],
                self.flight.potential_energy[:, 1],
                label="Potential Energy"
            )
            ax2.set_xlim(0, apogee_time)
            ax2.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax2.set_title("Total Mechanical Energy Components")
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Energy (J)")
            ax2.legend()
            ax2.grid()
            
            # Thrust Power
            ax3.plot(
                self.flight.thrust_power[:, 0],
                self.flight.thrust_power[:, 1],
                label="|Thrust Power|"
            )
            ax3.set_xlim(0, self.flight.rocket.motor.burn_out_time)
            ax3.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax3.set_title("Thrust Absolute Power")
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("Power (W)")
            ax3.legend()
            ax3.grid()
            
            # Drag Power
            ax4.plot(
                self.flight.drag_power[:, 0],
                -self.flight.drag_power[:, 1],
                label="|Drag Power|"
            )
            ax4.set_xlim(0, apogee_time)
            ax4.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax4.set_title("Drag Absolute Power")
            ax4.set_xlabel("Time (s)")
            ax4.set_ylabel("Power (W)")
            ax4.legend()
            ax4.grid()
            
            plt.subplots_adjust(hspace=1)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Energy data plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot energy data: {e}")
            return None

    def plot_fluid_mechanics_data(self, output_dir: Path) -> Optional[Path]:
        """Plot fluid mechanics parameters (Mach, Reynolds, pressures, AoA).

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "fluid_mechanics_data.png"
            
            # Determine time limit (includes parachute deployment)
            time_limit = self._get_plot_time_limit()
            
            out_of_rail_time = self.flight.out_of_rail_time if hasattr(self.flight, 'out_of_rail_time') else 0
            
            fig = plt.figure(figsize=(9, 16))
            
            # Mach Number
            ax1 = plt.subplot(611)
            ax1.plot(self.flight.mach_number[:, 0], self.flight.mach_number[:, 1])
            ax1.set_xlim(0, self.flight.t_final)
            ax1.set_title("Mach Number")
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Mach Number")
            ax1.grid()
            
            # Reynolds Number
            ax2 = plt.subplot(612)
            ax2.plot(self.flight.reynolds_number[:, 0], self.flight.reynolds_number[:, 1])
            ax2.set_xlim(0, self.flight.t_final)
            ax2.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax2.set_title("Reynolds Number")
            ax2.set_xlabel("Time (s)")
            ax2.set_ylabel("Reynolds Number")
            ax2.grid()
            
            # Pressures
            ax3 = plt.subplot(613)
            ax3.plot(
                self.flight.dynamic_pressure[:, 0],
                self.flight.dynamic_pressure[:, 1],
                label="Dynamic Pressure"
            )
            ax3.plot(
                self.flight.total_pressure[:, 0],
                self.flight.total_pressure[:, 1],
                label="Total Pressure"
            )
            ax3.plot(
                self.flight.pressure[:, 0],
                self.flight.pressure[:, 1],
                label="Static Pressure"
            )
            ax3.set_xlim(0, self.flight.t_final)
            ax3.legend()
            ax3.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
            ax3.set_title("Total and Dynamic Pressure")
            ax3.set_xlabel("Time (s)")
            ax3.set_ylabel("Pressure (Pa)")
            ax3.grid()
            
            # Angle of Attack
            ax4 = plt.subplot(614)
            ax4.plot(self.flight.angle_of_attack[:, 0], self.flight.angle_of_attack[:, 1])
            ax4.set_title("Angle of Attack")
            ax4.set_xlabel("Time (s)")
            ax4.set_ylabel("Angle of Attack (°)")
            ax4.set_xlim(out_of_rail_time, time_limit)
            ax4.grid()
            
            # Stream Velocity
            ax5 = plt.subplot(615)
            ax5.plot(
                self.flight.stream_velocity_x[:, 0],
                self.flight.stream_velocity_x[:, 1],
                label="Stream Velocity X"
            )
            ax5.plot(
                self.flight.stream_velocity_y[:, 0],
                self.flight.stream_velocity_y[:, 1],
                label="Stream Velocity Y"
            )
            ax5.plot(
                self.flight.stream_velocity_z[:, 0],
                self.flight.stream_velocity_z[:, 1],
                label="Stream Velocity Z"
            )
            ax5.set_title("Stream Velocity Components")
            ax5.set_xlabel("Time (s)")
            ax5.set_ylabel("Stream Velocity (m/s)")
            ax5.set_xlim(out_of_rail_time, time_limit)
            ax5.legend()
            ax5.grid()
            
            # Angle of Sideslip
            ax6 = plt.subplot(616)
            ax6.plot(
                self.flight.angle_of_sideslip[:, 0],
                self.flight.angle_of_sideslip[:, 1]
            )
            ax6.set_title("Angle of Sideslip")
            ax6.set_xlabel("Time (s)")
            ax6.set_ylabel("Angle of Sideslip (°)")
            ax6.set_xlim(out_of_rail_time, time_limit)
            ax6.grid()
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Fluid mechanics plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot fluid mechanics data: {e}")
            return None

    def plot_stability_and_control_data(self, output_dir: Path) -> Optional[Path]:
        """Plot stability margin and attitude frequency response.

        Parameters
        ----------
        output_dir : Path
            Output directory for the plot

        Returns
        -------
        Optional[Path]
            Path to created plot or None if failed
        """
        try:
            output_path = output_dir / "stability_and_control_data.png"
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6))
            
            # Stability Margin
            ax1.plot(self.flight.stability_margin[:, 0], self.flight.stability_margin[:, 1])
            ax1.set_xlim(0, self.flight.stability_margin[:, 0][-1])
            ax1.set_title("Stability Margin")
            ax1.set_xlabel("Time (s)")
            ax1.set_ylabel("Stability Margin (c)")
            
            # Add critical event markers
            ax1.axvline(
                x=self.flight.out_of_rail_time,
                color="r",
                linestyle="--",
                label="Out of Rail Time"
            )
            ax1.axvline(
                x=self.flight.rocket.motor.burn_out_time,
                color="g",
                linestyle="--",
                label="Burn Out Time"
            )
            ax1.axvline(
                x=self.flight.apogee_time,
                color="m",
                linestyle="--",
                label="Apogee Time"
            )
            ax1.legend()
            ax1.grid()
            
            # Attitude Frequency Response
            x_axis = np.arange(0, 5, 0.01)
            max_attitude = self.flight.attitude_frequency_response.max
            max_attitude = max_attitude if max_attitude != 0 else 1
            ax2.plot(
                x_axis,
                self.flight.attitude_frequency_response(x_axis) / max_attitude,
                label="Attitude Angle"
            )
            
            # Omega Frequency Response
            max_omega = self.flight.omega1_frequency_response.max
            max_omega = max_omega if max_omega != 0 else 1
            ax2.plot(
                x_axis,
                self.flight.omega1_frequency_response(x_axis) / max_omega,
                label="Omega 1"
            )
            
            max_omega = self.flight.omega2_frequency_response.max
            max_omega = max_omega if max_omega != 0 else 1
            ax2.plot(
                x_axis,
                self.flight.omega2_frequency_response(x_axis) / max_omega,
                label="Omega 2"
            )
            
            max_omega = self.flight.omega3_frequency_response.max
            max_omega = max_omega if max_omega != 0 else 1
            ax2.plot(
                x_axis,
                self.flight.omega3_frequency_response(x_axis) / max_omega,
                label="Omega 3"
            )
            
            ax2.set_title("Frequency Response")
            ax2.set_xlabel("Frequency (Hz)")
            ax2.set_ylabel("Amplitude Magnitude Normalized")
            ax2.set_xlim(0, 5)
            ax2.legend()
            ax2.grid()
            
            plt.subplots_adjust(hspace=0.5)
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            logger.info(f"Stability and control plot saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.warning(f"Could not plot stability and control data: {e}")
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

