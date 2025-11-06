"""Flight simulator for executing rocket trajectory simulations.

This module provides the FlightSimulator class for running single flight
simulations and extracting key flight metrics.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    from rocketpy import Flight, Rocket, Environment
except ImportError:
    Flight = None
    Rocket = None
    Environment = None

from src.config_loader import SimulationConfig

logger = logging.getLogger(__name__)


class FlightSimulator:
    """Simulator for rocket flight trajectories.

    This class executes single flight simulations using RocketPy's Flight
    class and provides methods to extract key metrics and export data.

    Attributes:
        rocket: Rocket instance for simulation.
        environment: Environment instance for simulation.
        config: SimulationConfig with simulation parameters.
        flight: Flight instance (after run()).

    Example:
        >>> simulator = FlightSimulator(rocket, environment, sim_config)
        >>> flight = simulator.run()
        >>> metrics = simulator.get_summary()
        >>> print(f"Apogee: {metrics['apogee_m']:.0f} m")
    """

    def __init__(
        self,
        rocket: "Rocket",
        environment: "Environment",
        config: SimulationConfig,
    ):
        """Initialize FlightSimulator.

        Args:
            rocket: Configured Rocket instance.
            environment: Configured Environment instance.
            config: SimulationConfig with simulation parameters.

        Raises:
            ImportError: If RocketPy is not installed.
        """
        if Flight is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        self.rocket = rocket
        self.environment = environment
        self.config = config
        self.flight: Optional[Flight] = None

    def run(self) -> "Flight":
        """Execute flight simulation.

        Returns:
            Flight instance with simulation results.

        Raises:
            RuntimeError: If simulation fails.

        Example:
            >>> simulator = FlightSimulator(rocket, env, sim_config)
            >>> flight = simulator.run()
            >>> print(f"Apogee: {flight.apogee} m")
        """
        logger.info("Starting flight simulation...")

        try:
            # Create Flight instance and run simulation
            self.flight = Flight(
                rocket=self.rocket,
                environment=self.environment,
                rail_length=self.config.rail.length_m,
                inclination=self.config.rail.inclination_deg,
                heading=self.config.rail.heading_deg,
                terminate_on_apogee=self.config.terminate_on_apogee,
                max_time=self.config.max_time_s,
                max_time_step=self.config.max_time_step_s,
                min_time_step=self.config.min_time_step_s,
                rtol=self.config.rtol,
                atol=self.config.atol,
                verbose=self.config.verbose,
            )

            logger.info(
                f"Simulation complete: Apogee = {self.flight.apogee:.0f} m, "
                f"Flight time = {self.flight.t_final:.1f} s"
            )

            return self.flight

        except Exception as e:
            logger.error(f"Simulation failed: {e}", exc_info=True)
            raise RuntimeError(f"Flight simulation failed: {e}") from e

    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive flight summary.

        Returns:
            Dictionary with key flight metrics.

        Raises:
            RuntimeError: If simulation has not been run yet.

        Example:
            >>> summary = simulator.get_summary()
            >>> print(f"Max velocity: {summary['max_velocity_ms']:.1f} m/s")
        """
        if self.flight is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        return {
            # Altitude metrics
            "apogee_m": float(self.flight.apogee),
            "apogee_time_s": float(self.flight.apogee_time),
            "apogee_x_m": float(self.flight.apogee_x),
            "apogee_y_m": float(self.flight.apogee_y),

            # Velocity metrics
            "max_velocity_ms": float(self.flight.max_speed),
            "max_velocity_time_s": float(self.flight.max_speed_time),
            "out_of_rail_velocity_ms": float(self.flight.out_of_rail_velocity),
            "impact_velocity_ms": float(self.flight.impact_velocity),

            # Mach and dynamic pressure
            "max_mach_number": float(self.flight.max_mach_number),
            "max_mach_number_time_s": float(self.flight.max_mach_number_time),

            # Impact metrics
            "x_impact_m": float(self.flight.x_impact),
            "y_impact_m": float(self.flight.y_impact),
            "impact_velocity_ms": float(self.flight.impact_velocity),
            "t_final_s": float(self.flight.t_final),

            # Launch rail metrics
            "out_of_rail_time_s": float(self.flight.out_of_rail_time),
            "out_of_rail_velocity_ms": float(self.flight.out_of_rail_velocity),

            # Stability
            "initial_stability_margin_calibers": float(
                self.flight.initial_stability_margin
            ),
            "out_of_rail_stability_margin_calibers": float(
                self.flight.out_of_rail_stability_margin
            ),

            # Drift distance
            "lateral_distance_m": float(
                (self.flight.x_impact**2 + self.flight.y_impact**2)**0.5
            ),
        }

    def get_trajectory_data(self) -> Dict[str, Any]:
        """Get complete trajectory data as arrays.

        Returns:
            Dictionary with time-series trajectory data.

        Raises:
            RuntimeError: If simulation has not been run yet.

        Example:
            >>> data = simulator.get_trajectory_data()
            >>> import matplotlib.pyplot as plt
            >>> plt.plot(data['time_s'], data['altitude_m'])
        """
        if self.flight is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        # Get time array
        time_array = self.flight.time

        return {
            "time_s": time_array,
            "altitude_m": [float(self.flight.z(t)) for t in time_array],
            "x_m": [float(self.flight.x(t)) for t in time_array],
            "y_m": [float(self.flight.y(t)) for t in time_array],
            "vx_ms": [float(self.flight.vx(t)) for t in time_array],
            "vy_ms": [float(self.flight.vy(t)) for t in time_array],
            "vz_ms": [float(self.flight.vz(t)) for t in time_array],
            "ax_ms2": [float(self.flight.ax(t)) for t in time_array],
            "ay_ms2": [float(self.flight.ay(t)) for t in time_array],
            "az_ms2": [float(self.flight.az(t)) for t in time_array],
        }

    def export_summary_to_dict(self) -> Dict[str, Any]:
        """Export complete simulation summary including configuration.

        Returns:
            Dictionary with configuration and results.

        Raises:
            RuntimeError: If simulation has not been run yet.

        Example:
            >>> summary = simulator.export_summary_to_dict()
            >>> import json
            >>> with open('results.json', 'w') as f:
            ...     json.dump(summary, f, indent=2)
        """
        if self.flight is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        flight_summary = self.get_summary()

        return {
            "simulation_config": {
                "rail_length_m": self.config.rail.length_m,
                "rail_inclination_deg": self.config.rail.inclination_deg,
                "rail_heading_deg": self.config.rail.heading_deg,
                "max_time_s": self.config.max_time_s,
                "rtol": self.config.rtol,
                "atol": self.config.atol,
            },
            "environment": {
                "latitude_deg": self.environment.latitude,
                "longitude_deg": self.environment.longitude,
                "elevation_m": self.environment.elevation,
            },
            "rocket": {
                "mass_kg": float(self.rocket.mass),
                "radius_m": float(self.rocket.radius),
            },
            "flight_results": flight_summary,
        }

    def print_summary(self) -> None:
        """Print formatted flight summary to console.

        Raises:
            RuntimeError: If simulation has not been run yet.

        Example:
            >>> simulator.run()
            >>> simulator.print_summary()
        """
        if self.flight is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        summary = self.get_summary()

        print("\n" + "="*60)
        print("FLIGHT SIMULATION SUMMARY")
        print("="*60)

        print("\n--- ALTITUDE METRICS ---")
        print(f"  Apogee:                {summary['apogee_m']:.2f} m")
        print(f"  Apogee Time:           {summary['apogee_time_s']:.2f} s")
        print(f"  Apogee Location:       ({summary['apogee_x_m']:.1f}, {summary['apogee_y_m']:.1f}) m")

        print("\n--- VELOCITY METRICS ---")
        print(f"  Max Velocity:          {summary['max_velocity_ms']:.2f} m/s")
        print(f"  Max Mach Number:       {summary['max_mach_number']:.3f}")
        print(f"  Off-Rail Velocity:     {summary['out_of_rail_velocity_ms']:.2f} m/s")
        print(f"  Impact Velocity:       {summary['impact_velocity_ms']:.2f} m/s")

        print("\n--- IMPACT METRICS ---")
        print(f"  Impact Location:       ({summary['x_impact_m']:.1f}, {summary['y_impact_m']:.1f}) m")
        print(f"  Lateral Distance:      {summary['lateral_distance_m']:.1f} m")
        print(f"  Flight Duration:       {summary['t_final_s']:.2f} s")

        print("\n--- STABILITY ---")
        print(f"  Initial Margin:        {summary['initial_stability_margin_calibers']:.2f} calibers")
        print(f"  Off-Rail Margin:       {summary['out_of_rail_stability_margin_calibers']:.2f} calibers")

        print("="*60 + "\n")

    @staticmethod
    def quick_simulation(
        rocket: "Rocket",
        environment: "Environment",
        rail_length_m: float = 5.2,
        inclination_deg: float = 85.0,
        heading_deg: float = 0.0,
    ) -> "Flight":
        """Quick flight simulation with default parameters.

        This is a convenience method for running simulations without
        creating a full SimulationConfig.

        Args:
            rocket: Configured Rocket instance.
            environment: Configured Environment instance.
            rail_length_m: Launch rail length in meters.
            inclination_deg: Rail inclination from vertical.
            heading_deg: Launch heading from North.

        Returns:
            Flight instance with results.

        Example:
            >>> flight = FlightSimulator.quick_simulation(rocket, env)
            >>> print(f"Apogee: {flight.apogee:.0f} m")
        """
        if Flight is None:
            raise ImportError(
                "RocketPy is not installed. Install with: pip install rocketpy"
            )

        logger.info("Running quick simulation with default parameters...")

        flight = Flight(
            rocket=rocket,
            environment=environment,
            rail_length=rail_length_m,
            inclination=inclination_deg,
            heading=heading_deg,
        )

        logger.info(f"Simulation complete: Apogee = {flight.apogee:.0f} m")

        return flight

    def compare_with(self, other_flight: "Flight") -> Dict[str, Any]:
        """Compare this flight with another flight.

        Args:
            other_flight: Another Flight instance to compare with.

        Returns:
            Dictionary with comparison metrics.

        Raises:
            RuntimeError: If simulation has not been run yet.

        Example:
            >>> flight1 = simulator1.run()
            >>> flight2 = simulator2.run()
            >>> comparison = simulator1.compare_with(flight2)
            >>> print(f"Apogee difference: {comparison['apogee_diff_m']:.1f} m")
        """
        if self.flight is None:
            raise RuntimeError("Simulation not run yet. Call run() first.")

        return {
            "apogee_diff_m": float(self.flight.apogee - other_flight.apogee),
            "apogee_diff_percent": float(
                100 * (self.flight.apogee - other_flight.apogee) / other_flight.apogee
            ),
            "max_velocity_diff_ms": float(
                self.flight.max_speed - other_flight.max_speed
            ),
            "impact_distance_diff_m": float(
                self.flight.x_impact - other_flight.x_impact
            ),
            "flight_time_diff_s": float(
                self.flight.t_final - other_flight.t_final
            ),
        }
