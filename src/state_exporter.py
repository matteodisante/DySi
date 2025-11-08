"""State exporter for capturing complete simulation parameters.

This module provides utilities for exporting all simulation input parameters
and output summaries (NOT time series arrays) in JSON/YAML format.

Time series arrays (x, y, z trajectories) are handled separately by DataHandler.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import logging
from datetime import datetime

import numpy as np
import yaml

from src.curve_plotter import CurvePlotter

logger = logging.getLogger(__name__)


class StateExporter:
    """Export complete simulation state before and after flight.

    This class captures ALL parameters used in a simulation:
    - User-defined parameters from YAML config
    - Default values set by rocket-sim code
    - Internal RocketPy object states
    - Computed/derived values

    Separates concerns:
    - initial_state.json: All INPUT parameters before simulation
    - final_state.json: INPUT + OUTPUT summary statistics
    - trajectory.csv: OUTPUT time series arrays (handled by DataHandler)

    Example:
        >>> exporter = StateExporter(motor, rocket, environment, sim_config)
        >>> exporter.export_initial_state("outputs/flight_001/initial_state.json")
        >>> # ... run simulation ...
        >>> exporter.export_final_state(flight, "outputs/flight_001/final_state.json")
    """

    def __init__(
        self,
        motor,
        rocket,
        environment,
        sim_config: Dict[str, Any],
        original_config: Optional[Dict[str, Any]] = None
    ):
        """Initialize StateExporter with simulation objects.

        Args:
            motor: RocketPy Motor object (SolidMotor, LiquidMotor, etc.)
            rocket: RocketPy Rocket object
            environment: RocketPy Environment object
            sim_config: Dictionary with simulation configuration (rail, tolerances, etc.)
            original_config: Optional original YAML configuration dict
        """
        self.motor = motor
        self.rocket = rocket
        self.environment = environment
        self.sim_config = sim_config
        self.original_config = original_config or {}

        logger.debug("StateExporter initialized")

    def export_initial_state(
        self,
        output_path: str,
        format: str = "json"
    ) -> Path:
        """Export all input parameters before simulation starts.

        Captures complete state of motor, rocket, environment, and simulation
        configuration BEFORE calling flight.simulate().

        Args:
            output_path: Path for output file
            format: "json" or "yaml"

        Returns:
            Path to created file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting initial state to {output_path}")

        # Build complete state dictionary
        state = {
            "metadata": self._create_metadata(),
            "motor": self._extract_motor_state(),
            "rocket": self._extract_rocket_state(),
            "environment": self._extract_environment_state(),
            "simulation_config": self._extract_simulation_config(),
        }

        # Save in requested format
        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(state, f, indent=2, cls=_NumpyEncoder)
        elif format == "yaml":
            with open(output_path, 'w') as f:
                yaml.dump(state, f, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Initial state exported to {output_path}")
        return output_path

    def export_final_state(
        self,
        flight,
        output_path: str,
        format: str = "json"
    ) -> Path:
        """Export input parameters + output summary after simulation.

        Includes all initial state PLUS flight results summary.
        Does NOT include time series arrays (those go in trajectory.csv).

        Args:
            flight: RocketPy Flight object (after simulation)
            output_path: Path for output file
            format: "json" or "yaml"

        Returns:
            Path to created file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting final state to {output_path}")

        # Build complete state (initial + results)
        state = {
            "metadata": self._create_metadata(include_flight=True),
            "motor": self._extract_motor_state(),
            "rocket": self._extract_rocket_state(),
            "environment": self._extract_environment_state(),
            "simulation_config": self._extract_simulation_config(),
            "flight_results": self._extract_flight_summary(flight),
        }

        # Save in requested format
        if format == "json":
            with open(output_path, 'w') as f:
                json.dump(state, f, indent=2, cls=_NumpyEncoder)
        elif format == "yaml":
            with open(output_path, 'w') as f:
                yaml.dump(state, f, default_flow_style=False, sort_keys=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Final state exported to {output_path}")
        return output_path

    def export_complete(
        self,
        flight,
        output_dir: str,
        formats: List[str] = ["json", "yaml"],
        include_plots: bool = True
    ) -> Dict[str, Path]:
        """Export both initial and final states in multiple formats.

        Args:
            flight: RocketPy Flight object (after simulation)
            output_dir: Directory for output files
            formats: List of formats to export ("json", "yaml")
            include_plots: If True, also generate curve plots

        Returns:
            Dictionary mapping file type to path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        paths = {}

        for fmt in formats:
            # Export initial state
            initial_path = output_dir / f"initial_state.{fmt}"
            self.export_initial_state(str(initial_path), format=fmt)
            paths[f"initial_{fmt}"] = initial_path

            # Export final state
            final_path = output_dir / f"final_state.{fmt}"
            self.export_final_state(flight, str(final_path), format=fmt)
            paths[f"final_{fmt}"] = final_path

        # Generate curve plots if requested
        if include_plots and self.motor:
            curves_dir = output_dir / "curves"
            curve_paths = self.export_curves_plots(str(curves_dir))
            paths.update(curve_paths)

        logger.info(f"Complete state exported to {output_dir}")
        return paths

    def export_curves_plots(self, output_dir: str) -> Dict[str, Path]:
        """Generate and save plots of all curves (thrust, drag, wind, etc.).

        Args:
            output_dir: Directory for plot PNG files

        Returns:
            Dictionary mapping plot name to path
        """
        plotter = CurvePlotter(self.motor, self.rocket, self.environment)
        return plotter.plot_all_curves(output_dir)

    def _create_metadata(self, include_flight: bool = False) -> Dict[str, Any]:
        """Create metadata section for export.

        Args:
            include_flight: Whether this is for final state (post-flight)

        Returns:
            Metadata dictionary
        """
        try:
            import rocketpy
            rocketpy_version = rocketpy.__version__
        except:
            rocketpy_version = "unknown"

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "rocketpy_version": rocketpy_version,
            "export_type": "final_state" if include_flight else "initial_state",
        }

        # Include original config file reference if available
        if self.original_config:
            metadata["config_source"] = self.original_config.get("_config_file", "unknown")

        return metadata

    def _extract_motor_state(self) -> Dict[str, Any]:
        """Extract complete motor parameters using comprehensive introspection.

        Returns:
            Dictionary with ALL motor parameters
        """
        motor_state = {
            "_class_type": type(self.motor).__name__,
        }

        # Use RocketPy's to_dict() as base (provides well-structured data)
        try:
            motor_dict = self.motor.to_dict(
                include_outputs=False,
                discretize=True,
                allow_pickle=False
            )
            motor_state.update(motor_dict)
        except Exception as e:
            logger.warning(f"Could not use motor.to_dict(): {e}")

        # Now add ALL remaining attributes via introspection
        motor_state.update(self._introspect_all_attributes(
            self.motor,
            exclude_prefixes=['_'],
            exclude_names=['plots', 'prints']  # Exclude plotting/printing utilities
        ))

        return motor_state

    def _extract_motor_manual(self) -> Dict[str, Any]:
        """Manually extract motor parameters (fallback method).

        Returns:
            Dictionary with motor parameters
        """
        params = {}

        # Common motor attributes
        attrs = [
            'dry_mass', 'dry_I_11', 'dry_I_22', 'dry_I_33',
            'dry_I_12', 'dry_I_13', 'dry_I_23',
            'nozzle_position', 'nozzle_radius',
        ]

        for attr in attrs:
            if hasattr(self.motor, attr):
                value = getattr(self.motor, attr)
                params[attr] = float(value) if isinstance(value, (int, float, np.number)) else value

        # Thrust curve
        if hasattr(self.motor, 'thrust'):
            params['thrust_curve'] = self._serialize_function(
                self.motor.thrust,
                name="thrust"
            )

        # Solid motor specific
        if hasattr(self.motor, 'grain_number'):
            solid_attrs = [
                'grain_number', 'grain_density', 'grain_outer_radius',
                'grain_initial_inner_radius', 'grain_initial_height',
                'grain_separation', 'grains_center_of_mass_position',
                'throat_radius'
            ]
            for attr in solid_attrs:
                if hasattr(self.motor, attr):
                    value = getattr(self.motor, attr)
                    params[attr] = float(value) if isinstance(value, (int, float, np.number)) else value

        return params

    def _extract_rocket_state(self) -> Dict[str, Any]:
        """Extract complete rocket parameters using comprehensive introspection.

        Returns:
            Dictionary with ALL rocket parameters
        """
        rocket_state = {
            "_class_type": type(self.rocket).__name__,
        }

        # Use RocketPy's to_dict() as base (provides well-structured data)
        try:
            rocket_dict = self.rocket.to_dict(
                include_outputs=False,
                discretize=True,
                allow_pickle=False
            )
            rocket_state.update(rocket_dict)
        except Exception as e:
            logger.warning(f"Could not use rocket.to_dict(): {e}")

        # Add ALL remaining attributes via introspection
        rocket_state.update(self._introspect_all_attributes(
            self.rocket,
            exclude_prefixes=['_'],
            exclude_names=['plots', 'prints', 'motor']  # Motor is extracted separately
        ))

        return rocket_state

    def _extract_rocket_manual(self) -> Dict[str, Any]:
        """Manually extract rocket parameters (fallback method).

        Returns:
            Dictionary with rocket parameters
        """
        params = {}

        # Basic properties
        attrs = [
            'radius', 'mass', 'motor_position',
            'center_of_mass_without_motor',
            'I_11_without_motor', 'I_22_without_motor', 'I_33_without_motor',
            'I_12_without_motor', 'I_13_without_motor', 'I_23_without_motor',
        ]

        for attr in attrs:
            if hasattr(self.rocket, attr):
                value = getattr(self.rocket, attr)
                params[attr] = float(value) if isinstance(value, (int, float, np.number)) else value

        # Drag curves
        if hasattr(self.rocket, 'power_off_drag'):
            params['power_off_drag'] = self._serialize_function(
                self.rocket.power_off_drag,
                name="power_off_drag"
            )

        if hasattr(self.rocket, 'power_on_drag'):
            params['power_on_drag'] = self._serialize_function(
                self.rocket.power_on_drag,
                name="power_on_drag"
            )

        # Aerodynamic surfaces
        if hasattr(self.rocket, 'aerodynamic_surfaces'):
            params['aerodynamic_surfaces'] = []
            for surface, position in self.rocket.aerodynamic_surfaces:
                surface_data = {
                    "type": type(surface).__name__,
                    "position": position if isinstance(position, (list, tuple)) else [position],
                }
                # Try to extract surface parameters
                try:
                    if hasattr(surface, 'to_dict'):
                        surface_data['parameters'] = surface.to_dict()
                    else:
                        # Manual extraction
                        surface_data['parameters'] = self._extract_surface_params(surface)
                except Exception as e:
                    logger.warning(f"Could not extract surface parameters: {e}")

                params['aerodynamic_surfaces'].append(surface_data)

        # Parachutes
        if hasattr(self.rocket, 'parachutes'):
            params['parachutes'] = []
            for para in self.rocket.parachutes:
                try:
                    if hasattr(para, 'to_dict'):
                        params['parachutes'].append(para.to_dict())
                    else:
                        params['parachutes'].append(self._extract_parachute_params(para))
                except Exception as e:
                    logger.warning(f"Could not extract parachute parameters: {e}")

        return params

    def _extract_surface_params(self, surface) -> Dict[str, Any]:
        """Extract parameters from an aerodynamic surface.

        Args:
            surface: Aerodynamic surface object (NoseCone, Fins, etc.)

        Returns:
            Dictionary with surface parameters
        """
        params = {}

        # Common attributes to try
        attrs = [
            'length', 'kind', 'base_radius', 'bluffness',  # NoseCone
            'n', 'root_chord', 'tip_chord', 'span', 'sweep_length',  # Fins
            'cant_angle', 'airfoil',
        ]

        for attr in attrs:
            if hasattr(surface, attr):
                value = getattr(surface, attr)
                if value is not None:
                    params[attr] = float(value) if isinstance(value, (int, float, np.number)) else value

        return params

    def _extract_parachute_params(self, parachute) -> Dict[str, Any]:
        """Extract parameters from a parachute.

        Args:
            parachute: Parachute object

        Returns:
            Dictionary with parachute parameters
        """
        params = {}

        attrs = [
            'name', 'cd_s', 'trigger', 'sampling_rate',
            'lag', 'noise',
        ]

        for attr in attrs:
            if hasattr(parachute, attr):
                value = getattr(parachute, attr)
                if value is not None:
                    params[attr] = value if isinstance(value, (str, int, float, list, tuple)) else str(value)

        return params

    def _extract_environment_state(self) -> Dict[str, Any]:
        """Extract complete environment parameters using comprehensive introspection.

        Returns:
            Dictionary with ALL environment parameters
        """
        env_state = {
            "_class_type": type(self.environment).__name__,
        }

        # Use RocketPy's to_dict() as base (provides well-structured data)
        try:
            env_dict = self.environment.to_dict(
                include_outputs=False,
                discretize=True
            )
            env_state.update(env_dict)
        except Exception as e:
            logger.warning(f"Could not use environment.to_dict(): {e}")

        # Add ALL remaining attributes via introspection
        env_state.update(self._introspect_all_attributes(
            self.environment,
            exclude_prefixes=['_'],
            exclude_names=['plots', 'prints']
        ))

        return env_state

    def _extract_environment_manual(self) -> Dict[str, Any]:
        """Manually extract environment parameters (fallback method).

        Returns:
            Dictionary with environment parameters
        """
        params = {}

        # Location and basic properties
        attrs = [
            'latitude', 'longitude', 'elevation',
            'datum', 'timezone', 'max_expected_height',
        ]

        for attr in attrs:
            if hasattr(self.environment, attr):
                value = getattr(self.environment, attr)
                params[attr] = value if isinstance(value, (str, int, float, list, tuple)) else str(value)

        # Date
        if hasattr(self.environment, 'date'):
            params['date'] = list(self.environment.date) if isinstance(self.environment.date, tuple) else self.environment.date

        # Atmospheric model type
        if hasattr(self.environment, 'atmospheric_model_type'):
            params['atmospheric_model_type'] = self.environment.atmospheric_model_type

        # Wind
        if hasattr(self.environment, 'wind_velocity_x'):
            params['wind'] = {
                'wind_velocity_x': self._serialize_function(self.environment.wind_velocity_x, "wind_x"),
                'wind_velocity_y': self._serialize_function(self.environment.wind_velocity_y, "wind_y"),
            }

        return params

    def _extract_simulation_config(self) -> Dict[str, Any]:
        """Extract simulation configuration parameters.

        Returns:
            Dictionary with simulation configuration
        """
        config = dict(self.sim_config)  # Copy

        # Ensure all values are serializable
        for key, value in config.items():
            if isinstance(value, (int, float, str, bool, type(None))):
                continue
            elif isinstance(value, (list, tuple)):
                config[key] = list(value)
            elif isinstance(value, dict):
                config[key] = dict(value)
            else:
                config[key] = str(value)

        return config

    def _extract_flight_summary(self, flight) -> Dict[str, Any]:
        """Extract flight results summary (NO time series arrays).

        Args:
            flight: RocketPy Flight object

        Returns:
            Dictionary with summary statistics only
        """
        summary = {}

        # Apogee
        if hasattr(flight, 'apogee'):
            summary['apogee'] = {
                'altitude_m': float(flight.apogee),
                'time_s': float(flight.apogee_time) if hasattr(flight, 'apogee_time') else None,
                'x_m': float(flight.apogee_x) if hasattr(flight, 'apogee_x') else None,
                'y_m': float(flight.apogee_y) if hasattr(flight, 'apogee_y') else None,
            }

        # Max values
        summary['max_values'] = {}
        if hasattr(flight, 'max_speed'):
            summary['max_values']['velocity_ms'] = float(flight.max_speed)
        if hasattr(flight, 'max_mach_number'):
            summary['max_values']['mach_number'] = float(flight.max_mach_number)
        if hasattr(flight, 'max_acceleration'):
            summary['max_values']['acceleration_ms2'] = float(flight.max_acceleration)

        # Rail exit
        if hasattr(flight, 'out_of_rail_velocity'):
            summary['rail_exit'] = {
                'velocity_ms': float(flight.out_of_rail_velocity),
                'time_s': float(flight.out_of_rail_time) if hasattr(flight, 'out_of_rail_time') else None,
            }

        # Impact
        summary['impact'] = {}
        if hasattr(flight, 'impact_velocity'):
            summary['impact']['velocity_ms'] = float(flight.impact_velocity)
        if hasattr(flight, 'x_impact'):
            summary['impact']['x_m'] = float(flight.x_impact)
        if hasattr(flight, 'y_impact'):
            summary['impact']['y_m'] = float(flight.y_impact)

        # Flight duration
        if hasattr(flight, 't_final'):
            summary['flight_time_s'] = float(flight.t_final)

        # Events (parachute deployments, motor burnout, etc.)
        if hasattr(flight, 'parachute_events'):
            summary['events'] = []
            for event in flight.parachute_events:
                event_data = {
                    'name': event[0] if isinstance(event, tuple) else str(event),
                    'time_s': float(event[1]) if isinstance(event, tuple) and len(event) > 1 else None,
                }
                summary['events'].append(event_data)

        return summary

    def _introspect_all_attributes(
        self,
        obj,
        exclude_prefixes: List[str] = None,
        exclude_names: List[str] = None
    ) -> Dict[str, Any]:
        """Extract ALL non-callable attributes from an object via introspection.

        This function performs comprehensive attribute extraction to ensure
        that EVERY parameter is captured, not just those in to_dict().

        Args:
            obj: Object to introspect
            exclude_prefixes: List of attribute name prefixes to exclude (e.g., ['_'])
            exclude_names: List of specific attribute names to exclude

        Returns:
            Dictionary with all extracted attributes
        """
        exclude_prefixes = exclude_prefixes or []
        exclude_names = exclude_names or []

        attributes = {}

        for name in dir(obj):
            # Skip excluded prefixes (e.g., private attributes)
            if any(name.startswith(prefix) for prefix in exclude_prefixes):
                continue

            # Skip excluded names
            if name in exclude_names:
                continue

            try:
                attr = getattr(obj, name)

                # Skip callable methods (functions)
                if callable(attr):
                    continue

                # Serialize the attribute value
                serialized_value = self._serialize_attribute_value(attr, name)

                # Only add if serialization was successful and not None
                if serialized_value is not None:
                    attributes[name] = serialized_value

            except Exception as e:
                # Some attributes might fail to access - log but continue
                logger.debug(f"Could not extract attribute '{name}': {e}")
                continue

        return attributes

    def _serialize_attribute_value(self, value, name: str = "unknown"):
        """Serialize a single attribute value to JSON-compatible format.

        Args:
            value: The attribute value to serialize
            name: Name of the attribute (for logging)

        Returns:
            Serialized value or None if not serializable
        """
        # Handle None
        if value is None:
            return None

        # Handle basic types (int, float, str, bool)
        if isinstance(value, (bool, int, float, str)):
            return value

        # Handle numpy types
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        if isinstance(value, np.bool_):
            return bool(value)
        if isinstance(value, np.ndarray):
            # Small arrays: convert to list
            if value.size < 1000:
                return value.tolist()
            else:
                # Large arrays: just store metadata
                return {
                    '_type': 'ndarray',
                    '_shape': value.shape,
                    '_dtype': str(value.dtype),
                    '_note': 'Large array - not serialized (>1000 elements)'
                }

        # Handle tuples and lists
        if isinstance(value, (tuple, list)):
            try:
                serialized_list = [self._serialize_attribute_value(item, f"{name}[{i}]") for i, item in enumerate(value)]
                return serialized_list if isinstance(value, list) else tuple(serialized_list)
            except:
                return {
                    '_type': type(value).__name__,
                    '_length': len(value),
                    '_note': 'Complex sequence - could not serialize'
                }

        # Handle dictionaries
        if isinstance(value, dict):
            try:
                serialized_dict = {}
                for k, v in value.items():
                    # Convert keys to strings (YAML doesn't support object keys)
                    if isinstance(k, (str, int, float, bool)):
                        key_str = k
                    else:
                        # Convert complex keys to string representation
                        key_str = f"{type(k).__name__}_{id(k)}"  # e.g., "TrapezoidalFins_140234567890"

                    serialized_dict[key_str] = self._serialize_attribute_value(v, f"{name}.{key_str}")
                return serialized_dict
            except Exception as e:
                logger.debug(f"Could not serialize dict '{name}': {e}")
                return {
                    '_type': 'dict',
                    '_keys': [str(k) for k in list(value.keys())[:20]] if len(value.keys()) < 20 else f"{len(value)} keys",
                    '_note': 'Complex dict - could not serialize'
                }

        # Handle RocketPy Function objects
        if hasattr(value, '__class__') and value.__class__.__name__ == 'Function':
            return self._serialize_function(value, name)

        # Handle RocketPy Components (list of surfaces, etc.)
        if hasattr(value, '__class__') and value.__class__.__name__ == 'Components':
            try:
                # Components is iterable
                components_list = []
                for i, component in enumerate(value):
                    comp_data = {
                        '_type': type(component).__name__,
                        '_index': i
                    }
                    # Try to get basic info from component
                    if hasattr(component, 'name'):
                        comp_data['name'] = str(component.name)
                    if hasattr(component, 'to_dict'):
                        try:
                            comp_data.update(component.to_dict(include_outputs=False, discretize=True, allow_pickle=False))
                        except:
                            pass
                    components_list.append(comp_data)
                return components_list
            except:
                return {
                    '_type': 'Components',
                    '_note': 'Components object - could not serialize contents'
                }

        # Handle other RocketPy objects (Motor, Rocket, Environment, etc.)
        if hasattr(value, 'to_dict'):
            try:
                return value.to_dict(include_outputs=False, discretize=True, allow_pickle=False)
            except:
                pass

        # Handle generic objects with __dict__
        if hasattr(value, '__dict__'):
            return {
                '_type': type(value).__name__,
                '_note': f'{type(value).__name__} object - see separate section or use string representation',
                '_str': str(value) if len(str(value)) < 200 else str(value)[:200] + '...'
            }

        # Last resort: string representation
        try:
            str_value = str(value)
            if len(str_value) < 200:
                return str_value
            else:
                return {
                    '_type': type(value).__name__,
                    '_str_preview': str_value[:200] + '...'
                }
        except:
            return {
                '_type': type(value).__name__,
                '_note': 'Could not serialize'
            }

    def _serialize_function(self, func_obj, name: str = "function") -> Dict[str, Any]:
        """Serialize a RocketPy Function object to dictionary.

        Args:
            func_obj: RocketPy Function object
            name: Name for the function

        Returns:
            Dictionary with function metadata and discretized points
        """
        func_data = {
            "name": name,
            "type": "Function",
        }

        try:
            # Try to get source information
            if hasattr(func_obj, 'source'):
                source = func_obj.source
                if isinstance(source, str):
                    # File path
                    func_data['source_file'] = source
                    func_data['source_type'] = 'file'
                elif callable(source):
                    func_data['source_type'] = 'callable'
                elif isinstance(source, (list, np.ndarray)):
                    func_data['source_type'] = 'array'
                else:
                    func_data['source_type'] = type(source).__name__

            # Get interpolation/extrapolation methods
            if hasattr(func_obj, '__interpolation__'):
                func_data['interpolation'] = func_obj.__interpolation__
            if hasattr(func_obj, '__extrapolation__'):
                func_data['extrapolation'] = func_obj.__extrapolation__

            # Discretize function for plotting/analysis
            # Get reasonable range and sample points
            if hasattr(func_obj, 'get_source'):
                try:
                    source_array = func_obj.get_source()
                    if isinstance(source_array, np.ndarray) and len(source_array) > 0:
                        # Take up to 200 points
                        step = max(1, len(source_array) // 200)
                        sampled = source_array[::step]
                        func_data['discretized_points'] = sampled.tolist()
                except:
                    pass

        except Exception as e:
            logger.warning(f"Could not fully serialize function {name}: {e}")
            func_data['error'] = str(e)

        return func_data


class _NumpyEncoder(json.JSONEncoder):
    """JSON encoder that handles numpy types and complex objects."""

    def default(self, obj):
        # Handle numpy types
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)

        # Try to use to_dict() if available (RocketPy objects)
        if hasattr(obj, 'to_dict'):
            try:
                return obj.to_dict(include_outputs=False, discretize=True, allow_pickle=False)
            except:
                pass

        # Try to convert to dict using __dict__
        if hasattr(obj, '__dict__'):
            try:
                class_name = obj.__class__.__name__
                return {
                    '_type': class_name,
                    '_note': f'{class_name} object - complex type simplified for export'
                }
            except:
                pass

        # Last resort: string representation
        try:
            return str(obj)
        except:
            return f"<non-serializable: {type(obj).__name__}>"
