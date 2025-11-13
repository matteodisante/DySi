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
