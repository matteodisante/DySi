"""Visualization utilities for flight simulation results.

This module provides plotting functions for trajectory data, flight metrics,
and comparative analysis.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging

try:
    import matplotlib.pyplot as plt
    import matplotlib
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from src.utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class Visualizer:
    """Visualizer for flight simulation data.

    This class provides methods to create plots of trajectory data,
    flight metrics, and comparative analyses.

    Example:
        >>> visualizer = Visualizer()
        >>> visualizer.plot_trajectory_2d(trajectory_data, "outputs/plots/trajectory.png")
        >>> visualizer.plot_altitude_vs_time(trajectory_data, "outputs/plots/altitude.png")
    """

    def __init__(self, output_dir: str = "outputs/plots/trajectory", style: str = "seaborn-v0_8-darkgrid"):
        """Initialize Visualizer.

        Args:
            output_dir: Default output directory for plots.
            style: Matplotlib style to use.

        Raises:
            ImportError: If matplotlib is not installed.
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError(
                "matplotlib is required for visualization. "
                "Install with: pip install matplotlib"
            )

        self.output_dir = Path(output_dir)
        ensure_directory_exists(str(self.output_dir))

        # Set matplotlib style
        try:
            plt.style.use(style)
        except:
            logger.warning(f"Style '{style}' not available, using default")

        logger.debug(f"Visualizer initialized with output_dir: {self.output_dir}")

    def plot_trajectory_2d(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "trajectory_2d.png",
        title: str = "Rocket Trajectory (2D)",
    ) -> Path:
        """Plot 2D ground projection of trajectory.

        Args:
            trajectory_data: Dictionary with trajectory data.
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> data = simulator.get_trajectory_data()
            >>> path = visualizer.plot_trajectory_2d(data)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating 2D trajectory plot: {output_path}")

        fig, ax = plt.subplots(figsize=(10, 8))

        # Plot trajectory
        ax.plot(
            trajectory_data["x_m"],
            trajectory_data["y_m"],
            "b-",
            linewidth=2,
            label="Flight Path",
        )

        # Mark launch and landing
        ax.plot(0, 0, "go", markersize=10, label="Launch")
        ax.plot(
            trajectory_data["x_m"][-1],
            trajectory_data["y_m"][-1],
            "ro",
            markersize=10,
            label="Impact",
        )

        ax.set_xlabel("X Position (m)", fontsize=12)
        ax.set_ylabel("Y Position (m)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axis("equal")

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved 2D trajectory plot to {output_path}")
        return output_path

    def plot_trajectory_3d(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "trajectory_3d.png",
        title: str = "Rocket Trajectory (3D)",
    ) -> Path:
        """Plot 3D trajectory.

        Args:
            trajectory_data: Dictionary with trajectory data.
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> path = visualizer.plot_trajectory_3d(trajectory_data)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating 3D trajectory plot: {output_path}")

        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection="3d")

        # Plot trajectory
        ax.plot(
            trajectory_data["x_m"],
            trajectory_data["y_m"],
            trajectory_data["altitude_m"],
            "b-",
            linewidth=2,
            label="Flight Path",
        )

        # Mark launch and landing
        ax.scatter(0, 0, 0, c="g", marker="o", s=100, label="Launch")
        ax.scatter(
            trajectory_data["x_m"][-1],
            trajectory_data["y_m"][-1],
            trajectory_data["altitude_m"][-1],
            c="r",
            marker="o",
            s=100,
            label="Impact",
        )

        ax.set_xlabel("X Position (m)", fontsize=11)
        ax.set_ylabel("Y Position (m)", fontsize=11)
        ax.set_zlabel("Altitude (m)", fontsize=11)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved 3D trajectory plot to {output_path}")
        return output_path

    def plot_altitude_vs_time(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "altitude_vs_time.png",
        title: str = "Altitude vs Time",
    ) -> Path:
        """Plot altitude vs time.

        Args:
            trajectory_data: Dictionary with trajectory data.
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> path = visualizer.plot_altitude_vs_time(trajectory_data)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating altitude vs time plot: {output_path}")

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(
            trajectory_data["time_s"],
            trajectory_data["altitude_m"],
            "b-",
            linewidth=2,
        )

        # Mark apogee
        max_alt_idx = trajectory_data["altitude_m"].index(
            max(trajectory_data["altitude_m"])
        )
        ax.plot(
            trajectory_data["time_s"][max_alt_idx],
            trajectory_data["altitude_m"][max_alt_idx],
            "ro",
            markersize=10,
            label=f'Apogee: {max(trajectory_data["altitude_m"]):.0f} m',
        )

        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Altitude (m)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved altitude vs time plot to {output_path}")
        return output_path

    def plot_velocity_vs_time(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "velocity_vs_time.png",
        title: str = "Velocity vs Time",
    ) -> Path:
        """Plot velocity components vs time.

        Args:
            trajectory_data: Dictionary with trajectory data.
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> path = visualizer.plot_velocity_vs_time(trajectory_data)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating velocity vs time plot: {output_path}")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate total velocity
        import numpy as np
        v_total = [
            np.sqrt(vx**2 + vy**2 + vz**2)
            for vx, vy, vz in zip(
                trajectory_data["vx_ms"],
                trajectory_data["vy_ms"],
                trajectory_data["vz_ms"],
            )
        ]

        ax.plot(trajectory_data["time_s"], v_total, "b-", linewidth=2, label="Total")
        ax.plot(
            trajectory_data["time_s"],
            trajectory_data["vz_ms"],
            "r--",
            linewidth=1.5,
            label="Vertical (vz)",
            alpha=0.7,
        )

        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Velocity (m/s)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved velocity vs time plot to {output_path}")
        return output_path

    def plot_acceleration_vs_time(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "acceleration_vs_time.png",
        title: str = "Acceleration vs Time",
    ) -> Path:
        """Plot acceleration vs time.

        Args:
            trajectory_data: Dictionary with trajectory data.
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> path = visualizer.plot_acceleration_vs_time(trajectory_data)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating acceleration vs time plot: {output_path}")

        fig, ax = plt.subplots(figsize=(12, 6))

        # Calculate total acceleration
        import numpy as np
        a_total = [
            np.sqrt(ax**2 + ay**2 + az**2)
            for ax, ay, az in zip(
                trajectory_data["ax_ms2"],
                trajectory_data["ay_ms2"],
                trajectory_data["az_ms2"],
            )
        ]

        ax.plot(trajectory_data["time_s"], a_total, "b-", linewidth=2, label="Total")
        ax.plot(
            trajectory_data["time_s"],
            trajectory_data["az_ms2"],
            "r--",
            linewidth=1.5,
            label="Vertical (az)",
            alpha=0.7,
        )

        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Acceleration (m/s²)", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved acceleration vs time plot to {output_path}")
        return output_path

    def create_standard_plots(
        self,
        trajectory_data: Dict[str, Any],
        base_filename: str = "flight",
    ) -> Dict[str, Path]:
        """Create standard set of plots.

        Args:
            trajectory_data: Dictionary with trajectory data.
            base_filename: Base name for plot files.

        Returns:
            Dictionary mapping plot type to file path.

        Example:
            >>> paths = visualizer.create_standard_plots(trajectory_data, "mission1")
            >>> print(paths["trajectory_2d"])
        """
        logger.info(f"Creating standard plot set with base name: {base_filename}")

        paths = {}

        paths["trajectory_2d"] = self.plot_trajectory_2d(
            trajectory_data,
            filename=f"{base_filename}_trajectory_2d.png",
        )

        paths["trajectory_3d"] = self.plot_trajectory_3d(
            trajectory_data,
            filename=f"{base_filename}_trajectory_3d.png",
        )

        paths["altitude"] = self.plot_altitude_vs_time(
            trajectory_data,
            filename=f"{base_filename}_altitude.png",
        )

        paths["velocity"] = self.plot_velocity_vs_time(
            trajectory_data,
            filename=f"{base_filename}_velocity.png",
        )

        paths["acceleration"] = self.plot_acceleration_vs_time(
            trajectory_data,
            filename=f"{base_filename}_acceleration.png",
        )

        logger.info(f"Created {len(paths)} standard plots")
        return paths

    def plot_comparison(
        self,
        trajectory_datasets: Dict[str, Dict[str, Any]],
        metric: str = "altitude_m",
        output_path: Optional[str] = None,
        filename: str = "comparison.png",
        title: Optional[str] = None,
    ) -> Path:
        """Plot comparison of multiple flights.

        Args:
            trajectory_datasets: Dictionary mapping flight names to trajectory data.
            metric: Metric to plot (e.g., "altitude_m", "vz_ms").
            output_path: Optional custom output path.
            filename: Filename for plot.
            title: Plot title (auto-generated if None).

        Returns:
            Path to saved plot.

        Example:
            >>> datasets = {
            ...     "Flight 1": data1,
            ...     "Flight 2": data2,
            ... }
            >>> path = visualizer.plot_comparison(datasets, "altitude_m")
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if title is None:
            title = f"Comparison: {metric.replace('_', ' ').title()}"

        logger.info(f"Creating comparison plot: {output_path}")

        fig, ax = plt.subplots(figsize=(12, 6))

        for flight_name, data in trajectory_datasets.items():
            ax.plot(data["time_s"], data[metric], linewidth=2, label=flight_name)

        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel(metric.replace("_", " ").title(), fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved comparison plot to {output_path}")
        return output_path
