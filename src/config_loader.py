"""Configuration loader for rocket simulation parameters.

This module provides dataclasses for configuration and utilities to load
and validate YAML configuration files.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class InertiaConfig:
    """Rocket inertia tensor configuration."""

    ixx_kg_m2: float
    iyy_kg_m2: float
    izz_kg_m2: float

    def to_tuple(self) -> Tuple[float, float, float]:
        """Return inertia as tuple for RocketPy API."""
        return (self.ixx_kg_m2, self.iyy_kg_m2, self.izz_kg_m2)


@dataclass
class GeometryConfig:
    """Rocket geometry configuration."""

    caliber_m: float
    length_m: float


@dataclass
class FinConfig:
    """Fin configuration."""

    count: int
    root_chord_m: float
    tip_chord_m: float
    span_m: float
    thickness_m: float
    position_m: float = 0.0
    cant_angle_deg: float = 0.0
    airfoil: Optional[str] = None


@dataclass
class NoseConeConfig:
    """Nose cone configuration."""

    length_m: float
    kind: str = "vonKarman"  # Options: vonKarman, conical, ogive, elliptical
    position_m: float = 0.0


@dataclass
class ParachuteConfig:
    """Parachute configuration."""

    enabled: bool = True
    name: str = "Main"
    cd_s: float = 10.0  # Drag coefficient × area
    trigger: Union[str, float] = "apogee"  # "apogee" or altitude in meters
    sampling_rate_hz: float = 105.0
    lag_s: float = 1.5
    noise_std: Tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass
class AirBrakesConfig:
    """Air brakes configuration for active drag control."""

    enabled: bool = True
    drag_coefficient: float = 1.5  # Drag coefficient when deployed
    reference_area_m2: float = 0.01  # Reference area in m²
    position_m: float = -0.5  # Position from nose (m)
    deployment_level: float = 1.0  # Deployment level (0.0-1.0, 1.0=fully deployed)
    override_cd_s: Optional[float] = None  # Override for cd_s calculation


@dataclass
class RocketConfig:
    """Complete rocket configuration."""

    name: str
    dry_mass_kg: float
    inertia: InertiaConfig
    geometry: GeometryConfig
    cg_location_m: float  # From nose
    cp_location_m: Optional[float] = None  # From nose, can be computed
    nose_cone: Optional[NoseConeConfig] = None
    fins: Optional[FinConfig] = None
    parachute: Optional[ParachuteConfig] = None
    air_brakes: Optional[AirBrakesConfig] = None  # Air brakes for apogee targeting
    power_off_drag: Optional[str] = None  # Path to drag curve file
    power_on_drag: Optional[str] = None  # Path to drag curve file
    coordinate_system: str = "tail_to_nose"

    @property
    def radius_m(self) -> float:
        """Return rocket radius in meters."""
        return self.geometry.caliber_m / 2.0

    @property
    def static_margin_calibers(self) -> Optional[float]:
        """Calculate static margin in calibers."""
        if self.cp_location_m is None:
            return None
        return (self.cp_location_m - self.cg_location_m) / self.geometry.caliber_m


@dataclass
class MotorConfig:
    """Motor configuration."""

    type: str = "SolidMotor"  # SolidMotor, LiquidMotor, HybridMotor
    thrust_source: str = ""  # Path to thrust curve file (.eng, .csv)
    dry_mass_kg: float = 1.5
    dry_inertia: Tuple[float, float, float] = (0.125, 0.125, 0.002)
    nozzle_radius_m: float = 0.033
    grain_number: int = 5
    grain_density_kg_m3: float = 1815.0
    grain_outer_radius_m: float = 0.033
    grain_initial_inner_radius_m: float = 0.015
    grain_initial_height_m: float = 0.120
    grain_separation_m: float = 0.005
    grains_center_of_mass_position_m: float = -0.85
    center_of_dry_mass_position_m: float = 0.317
    nozzle_position_m: float = 0.0
    burn_time_s: Optional[float] = None
    throat_radius_m: float = 0.011
    position_m: float = -1.373  # Position on rocket


@dataclass
class WindConfig:
    """Wind configuration."""

    model: str = "constant"  # constant, function, custom
    velocity_ms: float = 0.0
    direction_deg: float = 0.0  # Meteorological convention (0=North, 90=East)


@dataclass
class EnvironmentConfig:
    """Environment configuration."""

    latitude_deg: float
    longitude_deg: float
    elevation_m: float = 0.0
    atmospheric_model: str = "standard_atmosphere"  # standard_atmosphere, custom, wyoming
    atmospheric_model_file: Optional[str] = None
    date: Optional[Tuple[int, int, int, int]] = None  # (year, month, day, hour_utc)
    wind: WindConfig = field(default_factory=WindConfig)
    gravity_ms2: float = 9.80665
    max_expected_height_m: float = 10000.0


@dataclass
class RailConfig:
    """Launch rail configuration."""

    length_m: float = 5.2
    inclination_deg: float = 85.0  # Degrees from vertical
    heading_deg: float = 0.0  # Degrees from North


@dataclass
class SimulationConfig:
    """Simulation parameters configuration."""

    max_time_s: float = 600.0
    max_time_step_s: float = float('inf')
    min_time_step_s: float = 0.0
    rtol: float = 1e-6
    atol: float = 1e-6
    terminate_on_apogee: bool = False
    verbose: bool = False
    rail: RailConfig = field(default_factory=RailConfig)


class ConfigLoader:
    """Load and validate configuration from YAML files."""

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """Initialize ConfigLoader.

        Args:
            config_path: Path to main configuration file (YAML).
        """
        self.config_path = Path(config_path) if config_path else None
        self.config_data: Dict[str, Any] = {}

    def load_yaml(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load YAML file.

        Args:
            file_path: Path to YAML file.

        Returns:
            Dictionary with configuration data.

        Raises:
            FileNotFoundError: If file does not exist.
            yaml.YAMLError: If YAML parsing fails.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        logger.info(f"Loading configuration from {path}")

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return data or {}

    def merge_configs(self, *config_dicts: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries.

        Args:
            *config_dicts: Variable number of configuration dictionaries.

        Returns:
            Merged configuration dictionary.
        """
        merged = {}
        for config in config_dicts:
            self._deep_merge(merged, config)
        return merged

    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge update dict into base dict (in-place).

        Args:
            base: Base dictionary to merge into.
            update: Dictionary with updates.
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def load_from_yaml(self, config_path: Union[str, Path]) -> None:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration YAML file.
        """
        self.config_path = Path(config_path)
        self.config_data = self.load_yaml(config_path)

    def get_rocket_config(self) -> RocketConfig:
        """Parse and return RocketConfig from loaded data.

        Returns:
            RocketConfig object.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If configuration is invalid.
        """
        if "rocket" not in self.config_data:
            raise KeyError("'rocket' section not found in configuration")

        rocket_data = self.config_data["rocket"]

        # Parse inertia
        inertia_data = rocket_data.get("inertia", {})
        inertia = InertiaConfig(
            ixx_kg_m2=inertia_data.get("ixx_kg_m2", 0.1),
            iyy_kg_m2=inertia_data.get("iyy_kg_m2", 0.1),
            izz_kg_m2=inertia_data.get("izz_kg_m2", 0.05),
        )

        # Parse geometry
        geometry_data = rocket_data.get("geometry", {})
        geometry = GeometryConfig(
            caliber_m=geometry_data.get("caliber_m", 0.1),
            length_m=geometry_data.get("length_m", 2.0),
        )

        # Parse fins
        fins = None
        if "fins" in rocket_data:
            fins_data = rocket_data["fins"]
            fins = FinConfig(
                count=fins_data.get("count", 4),
                root_chord_m=fins_data.get("root_chord_m", 0.1),
                tip_chord_m=fins_data.get("tip_chord_m", 0.05),
                span_m=fins_data.get("span_m", 0.1),
                thickness_m=fins_data.get("thickness_m", 0.003),
                position_m=fins_data.get("position_m", 0.0),
                cant_angle_deg=fins_data.get("cant_angle_deg", 0.0),
                airfoil=fins_data.get("airfoil"),
            )

        # Parse nose cone
        nose_cone = None
        if "nose_cone" in rocket_data:
            nose_data = rocket_data["nose_cone"]
            nose_cone = NoseConeConfig(
                length_m=nose_data.get("length_m", 0.5),
                kind=nose_data.get("kind", "vonKarman"),
                position_m=nose_data.get("position_m", 0.0),
            )

        # Parse parachute
        parachute = None
        if "parachute" in rocket_data:
            para_data = rocket_data["parachute"]
            parachute = ParachuteConfig(
                enabled=para_data.get("enabled", True),
                name=para_data.get("name", "Main"),
                cd_s=para_data.get("cd_s", 10.0),
                trigger=para_data.get("trigger", "apogee"),
                sampling_rate_hz=para_data.get("sampling_rate_hz", 105.0),
                lag_s=para_data.get("lag_s", 1.5),
                noise_std=tuple(para_data.get("noise_std", [0.0, 0.0, 0.0])),
            )

        # Parse air brakes
        air_brakes = None
        if "air_brakes" in rocket_data:
            ab_data = rocket_data["air_brakes"]
            air_brakes = AirBrakesConfig(
                enabled=ab_data.get("enabled", True),
                drag_coefficient=ab_data.get("drag_coefficient", 1.5),
                reference_area_m2=ab_data.get("reference_area_m2", 0.01),
                position_m=ab_data.get("position_m", -0.5),
                deployment_level=ab_data.get("deployment_level", 1.0),
                override_cd_s=ab_data.get("override_cd_s"),
            )

        return RocketConfig(
            name=rocket_data.get("name", "Rocket"),
            dry_mass_kg=rocket_data.get("dry_mass_kg", 10.0),
            inertia=inertia,
            geometry=geometry,
            cg_location_m=rocket_data.get("cg_location_m", 1.0),
            cp_location_m=rocket_data.get("cp_location_m"),
            nose_cone=nose_cone,
            fins=fins,
            parachute=parachute,
            air_brakes=air_brakes,
            power_off_drag=rocket_data.get("power_off_drag"),
            power_on_drag=rocket_data.get("power_on_drag"),
            coordinate_system=rocket_data.get("coordinate_system", "tail_to_nose"),
        )

    def get_motor_config(self) -> MotorConfig:
        """Parse and return MotorConfig from loaded data.

        Returns:
            MotorConfig object.

        Raises:
            KeyError: If required fields are missing.
        """
        if "motor" not in self.config_data:
            raise KeyError("'motor' section not found in configuration")

        motor_data = self.config_data["motor"]

        return MotorConfig(
            type=motor_data.get("type", "SolidMotor"),
            thrust_source=motor_data.get("thrust_source", ""),
            dry_mass_kg=motor_data.get("dry_mass_kg", 1.5),
            dry_inertia=tuple(motor_data.get("dry_inertia", [0.125, 0.125, 0.002])),
            nozzle_radius_m=motor_data.get("nozzle_radius_m", 0.033),
            grain_number=motor_data.get("grain_number", 5),
            grain_density_kg_m3=motor_data.get("grain_density_kg_m3", 1815.0),
            grain_outer_radius_m=motor_data.get("grain_outer_radius_m", 0.033),
            grain_initial_inner_radius_m=motor_data.get("grain_initial_inner_radius_m", 0.015),
            grain_initial_height_m=motor_data.get("grain_initial_height_m", 0.120),
            grain_separation_m=motor_data.get("grain_separation_m", 0.005),
            grains_center_of_mass_position_m=motor_data.get("grains_center_of_mass_position_m", -0.85),
            center_of_dry_mass_position_m=motor_data.get("center_of_dry_mass_position_m", 0.317),
            nozzle_position_m=motor_data.get("nozzle_position_m", 0.0),
            burn_time_s=motor_data.get("burn_time_s"),
            throat_radius_m=motor_data.get("throat_radius_m", 0.011),
            position_m=motor_data.get("position_m", -1.373),
        )

    def get_environment_config(self) -> EnvironmentConfig:
        """Parse and return EnvironmentConfig from loaded data.

        Returns:
            EnvironmentConfig object.

        Raises:
            KeyError: If required fields are missing.
        """
        if "environment" not in self.config_data:
            raise KeyError("'environment' section not found in configuration")

        env_data = self.config_data["environment"]

        # Parse wind configuration
        wind_data = env_data.get("wind", {})
        wind = WindConfig(
            model=wind_data.get("model", "constant"),
            velocity_ms=wind_data.get("velocity_ms", 0.0),
            direction_deg=wind_data.get("direction_deg", 0.0),
        )

        # Parse date if provided
        date = None
        if "date" in env_data:
            date_data = env_data["date"]
            if isinstance(date_data, (list, tuple)) and len(date_data) == 4:
                date = tuple(date_data)

        return EnvironmentConfig(
            latitude_deg=env_data.get("latitude_deg", 0.0),
            longitude_deg=env_data.get("longitude_deg", 0.0),
            elevation_m=env_data.get("elevation_m", 0.0),
            atmospheric_model=env_data.get("atmospheric_model", "standard_atmosphere"),
            atmospheric_model_file=env_data.get("atmospheric_model_file"),
            date=date,
            wind=wind,
            gravity_ms2=env_data.get("gravity_ms2", 9.80665),
            max_expected_height_m=env_data.get("max_expected_height_m", 10000.0),
        )

    def get_simulation_config(self) -> SimulationConfig:
        """Parse and return SimulationConfig from loaded data.

        Returns:
            SimulationConfig object.
        """
        sim_data = self.config_data.get("simulation", {})

        # Parse rail configuration
        rail_data = sim_data.get("rail", {})
        rail = RailConfig(
            length_m=rail_data.get("length_m", 5.2),
            inclination_deg=rail_data.get("inclination_deg", 85.0),
            heading_deg=rail_data.get("heading_deg", 0.0),
        )

        return SimulationConfig(
            max_time_s=sim_data.get("max_time_s", 600.0),
            max_time_step_s=sim_data.get("max_time_step_s", float('inf')),
            min_time_step_s=sim_data.get("min_time_step_s", 0.0),
            rtol=sim_data.get("rtol", 1e-6),
            atol=sim_data.get("atol", 1e-6),
            terminate_on_apogee=sim_data.get("terminate_on_apogee", False),
            verbose=sim_data.get("verbose", False),
            rail=rail,
        )

    def load_complete_config(
        self,
        config_path: Union[str, Path],
    ) -> Tuple[RocketConfig, MotorConfig, EnvironmentConfig, SimulationConfig]:
        """Load all configurations from a single YAML file.

        Args:
            config_path: Path to complete configuration YAML file.

        Returns:
            Tuple of (RocketConfig, MotorConfig, EnvironmentConfig, SimulationConfig).
        """
        self.load_from_yaml(config_path)
        return (
            self.get_rocket_config(),
            self.get_motor_config(),
            self.get_environment_config(),
            self.get_simulation_config(),
        )
