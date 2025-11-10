"""Utility functions for rocket simulation.

This module provides common utility functions for unit conversions,
coordinate transformations, and other helper functions.
"""

import logging
from typing import Tuple
import numpy as np

logger = logging.getLogger(__name__)


# Unit conversion constants
DEG_TO_RAD = np.pi / 180.0
RAD_TO_DEG = 180.0 / np.pi
FT_TO_M = 0.3048
M_TO_FT = 1.0 / FT_TO_M
LBF_TO_N = 4.44822
N_TO_LBF = 1.0 / LBF_TO_N
LBM_TO_KG = 0.453592
KG_TO_LBM = 1.0 / LBM_TO_KG
IN_TO_M = 0.0254
M_TO_IN = 1.0 / IN_TO_M


def deg_to_rad(degrees: float) -> float:
    """Convert degrees to radians.

    Args:
        degrees: Angle in degrees.

    Returns:
        Angle in radians.
    """
    return degrees * DEG_TO_RAD


def rad_to_deg(radians: float) -> float:
    """Convert radians to degrees.

    Args:
        radians: Angle in radians.

    Returns:
        Angle in degrees.
    """
    return radians * RAD_TO_DEG


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters.

    Args:
        feet: Length in feet.

    Returns:
        Length in meters.
    """
    return feet * FT_TO_M


def meters_to_feet(meters: float) -> float:
    """Convert meters to feet.

    Args:
        meters: Length in meters.

    Returns:
        Length in feet.
    """
    return meters * M_TO_FT


def lbf_to_newtons(lbf: float) -> float:
    """Convert pounds-force to Newtons.

    Args:
        lbf: Force in pounds-force.

    Returns:
        Force in Newtons.
    """
    return lbf * LBF_TO_N


def newtons_to_lbf(newtons: float) -> float:
    """Convert Newtons to pounds-force.

    Args:
        newtons: Force in Newtons.

    Returns:
        Force in pounds-force.
    """
    return newtons * N_TO_LBF


def lbm_to_kg(lbm: float) -> float:
    """Convert pounds-mass to kilograms.

    Args:
        lbm: Mass in pounds-mass.

    Returns:
        Mass in kilograms.
    """
    return lbm * LBM_TO_KG


def kg_to_lbm(kg: float) -> float:
    """Convert kilograms to pounds-mass.

    Args:
        kg: Mass in kilograms.

    Returns:
        Mass in pounds-mass.
    """
    return kg * KG_TO_LBM


def inches_to_meters(inches: float) -> float:
    """Convert inches to meters.

    Args:
        inches: Length in inches.

    Returns:
        Length in meters.
    """
    return inches * IN_TO_M


def meters_to_inches(meters: float) -> float:
    """Convert meters to inches.

    Args:
        meters: Length in meters.

    Returns:
        Length in inches.
    """
    return meters * M_TO_IN


def calculate_static_margin(
    cp_location_m: float,
    cg_location_m: float,
    caliber_m: float,
) -> float:
    """Calculate static margin in calibers.

    Static margin is the distance between center of pressure (CP)
    and center of gravity (CG), expressed in rocket diameters (calibers).
    Positive margin indicates stable rocket (CP behind CG).

    Args:
        cp_location_m: Center of pressure location (m).
        cg_location_m: Center of gravity location (m).
        caliber_m: Rocket diameter/caliber (m).

    Returns:
        Static margin in calibers.

    Example:
        >>> calculate_static_margin(1.5, 1.0, 0.1)
        5.0  # CP is 5 calibers behind CG
    """
    return (cp_location_m - cg_location_m) / caliber_m


def wind_to_components(
    velocity_ms: float,
    direction_deg: float,
) -> Tuple[float, float]:
    """Convert wind velocity and direction to x-y components.

    Uses meteorological convention: direction is where wind comes FROM.
    - 0° = North
    - 90° = East
    - 180° = South
    - 270° = West

    Args:
        velocity_ms: Wind speed (m/s).
        direction_deg: Wind direction (degrees, meteorological convention).

    Returns:
        Tuple of (wind_x, wind_y) components in m/s.
        wind_x: East component
        wind_y: North component

    Example:
        >>> wind_to_components(10.0, 0.0)  # Wind from North
        (0.0, -10.0)  # Blowing toward South
        >>> wind_to_components(10.0, 90.0)  # Wind from East
        (-10.0, 0.0)  # Blowing toward West
    """
    # Convert to radians
    direction_rad = deg_to_rad(direction_deg)

    # Calculate components (negative because wind direction is where it comes FROM)
    wind_x = -velocity_ms * np.sin(direction_rad)  # East component
    wind_y = -velocity_ms * np.cos(direction_rad)  # North component

    return (wind_x, wind_y)


def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """Setup logging configuration.

    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR").
        log_file: Optional log file path. If None, logs to console only.

    Example:
        >>> setup_logging(level="DEBUG", log_file="simulation.log")
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to allow reconfiguration
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(numeric_level)
        root_logger.addHandler(file_handler)

    # Silence verbose third-party libraries
    # These libraries produce excessive DEBUG messages that clutter logs
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    logger.info(f"Logging configured with level={level}")


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: Path to directory.

    Example:
        >>> ensure_directory_exists("outputs/results")
    """
    from pathlib import Path

    path = Path(directory_path)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory_path}")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted string (e.g., "2m 30s" or "1h 5m 23s").

    Example:
        >>> format_duration(150)
        '2m 30s'
        >>> format_duration(3723)
        '1h 2m 3s'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix.

    Args:
        text: String to truncate.
        max_length: Maximum length.
        suffix: Suffix to append if truncated.

    Returns:
        Truncated string.

    Example:
        >>> truncate_string("Very long rocket name here", max_length=15)
        'Very long ro...'
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
