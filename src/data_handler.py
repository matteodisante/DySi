"""Data handler for exporting flight simulation results.

This module provides utilities for exporting trajectory data and simulation
results to various formats (CSV, JSON, KML).
"""

from pathlib import Path
from typing import Dict, Any, Optional
import json
import csv
import logging

from src.utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class DataHandler:
    """Handler for exporting flight simulation data.

    This class provides methods to export trajectory data and simulation
    results to various file formats.

    Example:
        >>> handler = DataHandler()
        >>> handler.export_trajectory_csv(trajectory_data, "outputs/results/flight.csv")
        >>> handler.export_summary_json(summary_data, "outputs/results/summary.json")
    """

    def __init__(self, output_dir: str = "outputs/results"):
        """Initialize DataHandler.

        Args:
            output_dir: Default output directory for exports.
        """
        self.output_dir = Path(output_dir)
        ensure_directory_exists(str(self.output_dir))
        logger.debug(f"DataHandler initialized with output_dir: {self.output_dir}")

    def export_trajectory_csv(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "trajectory.csv",
    ) -> Path:
        """Export trajectory data to CSV file.

        Args:
            trajectory_data: Dictionary with time-series data (from get_trajectory_data()).
            output_path: Optional custom output path. If None, uses output_dir.
            filename: Filename for CSV file.

        Returns:
            Path to created CSV file.

        Example:
            >>> data = simulator.get_trajectory_data()
            >>> path = handler.export_trajectory_csv(data)
            >>> print(f"Exported to {path}")
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting trajectory data to {output_path}")

        # Get column names and ensure time is first
        columns = list(trajectory_data.keys())
        if "time_s" in columns:
            columns.remove("time_s")
            columns = ["time_s"] + columns

        # Write CSV file
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(columns)

            # Write data rows
            num_rows = len(trajectory_data[columns[0]])
            for i in range(num_rows):
                row = [trajectory_data[col][i] for col in columns]
                writer.writerow(row)

        logger.info(f"Exported {num_rows} data points to {output_path}")
        return output_path

    def export_summary_json(
        self,
        summary_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "summary.json",
        indent: int = 2,
    ) -> Path:
        """Export flight summary to JSON file.

        Args:
            summary_data: Dictionary with summary data (from get_summary()).
            output_path: Optional custom output path. If None, uses output_dir.
            filename: Filename for JSON file.
            indent: JSON indentation level.

        Returns:
            Path to created JSON file.

        Example:
            >>> summary = simulator.get_summary()
            >>> path = handler.export_summary_json(summary)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting summary data to {output_path}")

        with open(output_path, "w") as f:
            json.dump(summary_data, f, indent=indent)

        logger.info(f"Exported summary to {output_path}")
        return output_path

    def export_complete_dataset(
        self,
        trajectory_data: Dict[str, Any],
        summary_data: Dict[str, Any],
        base_filename: str = "flight",
        export_formats: tuple = ("csv", "json"),
    ) -> Dict[str, Path]:
        """Export complete dataset in multiple formats.

        Args:
            trajectory_data: Trajectory time-series data.
            summary_data: Flight summary data.
            base_filename: Base name for output files.
            export_formats: Tuple of formats to export ("csv", "json").

        Returns:
            Dictionary mapping format to output path.

        Example:
            >>> paths = handler.export_complete_dataset(
            ...     trajectory_data, summary_data, "my_flight"
            ... )
            >>> print(paths["csv"])  # outputs/results/my_flight_trajectory.csv
        """
        paths = {}

        if "csv" in export_formats:
            csv_path = self.export_trajectory_csv(
                trajectory_data,
                filename=f"{base_filename}_trajectory.csv",
            )
            paths["csv"] = csv_path

        if "json" in export_formats:
            json_path = self.export_summary_json(
                summary_data,
                filename=f"{base_filename}_summary.json",
            )
            paths["json"] = json_path

        logger.info(f"Exported complete dataset with base name: {base_filename}")
        return paths

    def export_kml(
        self,
        trajectory_data: Dict[str, Any],
        output_path: Optional[str] = None,
        filename: str = "trajectory.kml",
        rocket_name: str = "Rocket Flight",
    ) -> Path:
        """Export trajectory to KML file for Google Earth.

        Args:
            trajectory_data: Trajectory data with x, y, altitude.
            output_path: Optional custom output path.
            filename: Filename for KML file.
            rocket_name: Name for the flight path in KML.

        Returns:
            Path to created KML file.

        Raises:
            ImportError: If simplekml is not installed.

        Example:
            >>> data = simulator.get_trajectory_data()
            >>> path = handler.export_kml(data, rocket_name="Calisto Flight 1")
        """
        try:
            import simplekml
        except ImportError:
            raise ImportError(
                "simplekml is required for KML export. "
                "Install with: pip install simplekml"
            )

        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting KML trajectory to {output_path}")

        # Create KML object
        kml = simplekml.Kml()

        # Create line string for trajectory
        # Note: KML uses (longitude, latitude, altitude)
        # We need to convert x, y to lat/lon if environment data is available
        # For now, we'll create a simplified version using x, y as offsets

        # Add a placeholder implementation
        # In a full implementation, you would convert x, y to actual lat/lon
        logger.warning(
            "KML export is simplified. For accurate geo-coordinates, "
            "environment location data should be used."
        )

        # Create a line showing the trajectory path
        line = kml.newlinestring(name=rocket_name)
        line.altitudemode = simplekml.AltitudeMode.relativetoground
        line.extrude = 1

        # Use x, y as simple offsets (this is a simplified approach)
        coords = []
        for i in range(len(trajectory_data["time_s"])):
            # Simplified: use x, y directly (not accurate geo-coordinates)
            lon = trajectory_data["x_m"][i] / 111000  # Rough conversion
            lat = trajectory_data["y_m"][i] / 111000
            alt = trajectory_data["altitude_m"][i]
            coords.append((lon, lat, alt))

        line.coords = coords

        # Save KML file
        kml.save(str(output_path))

        logger.info(f"Exported KML trajectory to {output_path}")
        return output_path

    def load_trajectory_csv(self, csv_path: str) -> Dict[str, Any]:
        """Load trajectory data from CSV file.

        Args:
            csv_path: Path to CSV file.

        Returns:
            Dictionary with trajectory data.

        Raises:
            FileNotFoundError: If CSV file does not exist.

        Example:
            >>> data = handler.load_trajectory_csv("outputs/results/flight.csv")
            >>> print(data.keys())
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Loading trajectory data from {csv_path}")

        trajectory_data = {}

        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)

            # Initialize lists for each column
            for fieldname in reader.fieldnames:
                trajectory_data[fieldname] = []

            # Read all rows
            for row in reader:
                for fieldname in reader.fieldnames:
                    trajectory_data[fieldname].append(float(row[fieldname]))

        num_points = len(trajectory_data[reader.fieldnames[0]])
        logger.info(f"Loaded {num_points} data points from {csv_path}")

        return trajectory_data

    def load_summary_json(self, json_path: str) -> Dict[str, Any]:
        """Load flight summary from JSON file.

        Args:
            json_path: Path to JSON file.

        Returns:
            Dictionary with summary data.

        Raises:
            FileNotFoundError: If JSON file does not exist.

        Example:
            >>> summary = handler.load_summary_json("outputs/results/summary.json")
            >>> print(f"Apogee: {summary['apogee_m']} m")
        """
        json_path = Path(json_path)
        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        logger.info(f"Loading summary data from {json_path}")

        with open(json_path, "r") as f:
            summary_data = json.load(f)

        logger.info(f"Loaded summary from {json_path}")
        return summary_data

    def create_comparison_report(
        self,
        flight_summaries: Dict[str, Dict[str, Any]],
        output_path: Optional[str] = None,
        filename: str = "comparison.csv",
    ) -> Path:
        """Create comparison report for multiple flights.

        Args:
            flight_summaries: Dictionary mapping flight names to summary dicts.
            output_path: Optional custom output path.
            filename: Filename for comparison CSV.

        Returns:
            Path to created comparison file.

        Example:
            >>> summaries = {
            ...     "Flight 1": simulator1.get_summary(),
            ...     "Flight 2": simulator2.get_summary(),
            ... }
            >>> path = handler.create_comparison_report(summaries)
        """
        if output_path is None:
            output_path = self.output_dir / filename
        else:
            output_path = Path(output_path)

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating comparison report at {output_path}")

        # Get all metrics from first flight
        first_flight = list(flight_summaries.values())[0]
        metrics = list(first_flight.keys())

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Write header
            writer.writerow(["Flight Name"] + metrics)

            # Write data for each flight
            for flight_name, summary in flight_summaries.items():
                row = [flight_name] + [summary.get(metric, "N/A") for metric in metrics]
                writer.writerow(row)

        logger.info(
            f"Created comparison report for {len(flight_summaries)} flights"
        )
        return output_path

    @staticmethod
    def format_summary_text(summary: Dict[str, Any]) -> str:
        """Format flight summary as readable text.

        Args:
            summary: Flight summary dictionary.

        Returns:
            Formatted text string.

        Example:
            >>> summary = simulator.get_summary()
            >>> text = DataHandler.format_summary_text(summary)
            >>> print(text)
        """
        lines = []
        lines.append("=" * 60)
        lines.append("FLIGHT SUMMARY")
        lines.append("=" * 60)

        # Group metrics by category
        altitude_metrics = [k for k in summary.keys() if "apogee" in k.lower()]
        velocity_metrics = [k for k in summary.keys() if "velocity" in k.lower() or "mach" in k.lower()]
        impact_metrics = [k for k in summary.keys() if "impact" in k.lower() or "final" in k.lower()]
        stability_metrics = [k for k in summary.keys() if "stability" in k.lower() or "margin" in k.lower()]

        if altitude_metrics:
            lines.append("\n--- ALTITUDE METRICS ---")
            for key in altitude_metrics:
                lines.append(f"  {key:30s}: {summary[key]}")

        if velocity_metrics:
            lines.append("\n--- VELOCITY METRICS ---")
            for key in velocity_metrics:
                lines.append(f"  {key:30s}: {summary[key]}")

        if impact_metrics:
            lines.append("\n--- IMPACT METRICS ---")
            for key in impact_metrics:
                lines.append(f"  {key:30s}: {summary[key]}")

        if stability_metrics:
            lines.append("\n--- STABILITY ---")
            for key in stability_metrics:
                lines.append(f"  {key:30s}: {summary[key]}")

        lines.append("=" * 60)

        return "\n".join(lines)
