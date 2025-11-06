"""Monte Carlo simulation runner for uncertainty quantification.

This module provides the MonteCarloRunner class for executing ensemble
simulations with parameter variations and statistical analysis.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Tuple
import logging
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed
import json

from src.config_loader import RocketConfig, MotorConfig, EnvironmentConfig, SimulationConfig
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator

logger = logging.getLogger(__name__)


class MonteCarloRunner:
    """Monte Carlo simulation runner.

    This class executes ensemble simulations with parameter variations
    for uncertainty quantification and statistical analysis.

    Example:
        >>> mc_runner = MonteCarloRunner(
        ...     rocket_cfg, motor_cfg, env_cfg, sim_cfg,
        ...     num_simulations=100
        ... )
        >>> mc_runner.add_parameter_variation("rocket.dry_mass_kg", mean=10.0, std=0.5)
        >>> mc_runner.add_parameter_variation("environment.wind.velocity_ms", mean=5.0, std=2.0)
        >>> results = mc_runner.run()
        >>> stats = mc_runner.get_statistics()
    """

    def __init__(
        self,
        base_rocket_config: RocketConfig,
        base_motor_config: MotorConfig,
        base_environment_config: EnvironmentConfig,
        base_simulation_config: SimulationConfig,
        num_simulations: int = 100,
        random_seed: Optional[int] = None,
    ):
        """Initialize Monte Carlo runner.

        Args:
            base_rocket_config: Base rocket configuration.
            base_motor_config: Base motor configuration.
            base_environment_config: Base environment configuration.
            base_simulation_config: Base simulation configuration.
            num_simulations: Number of Monte Carlo samples.
            random_seed: Random seed for reproducibility.
        """
        self.base_rocket_config = base_rocket_config
        self.base_motor_config = base_motor_config
        self.base_environment_config = base_environment_config
        self.base_simulation_config = base_simulation_config
        self.num_simulations = num_simulations
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

        self.parameter_variations: Dict[str, Dict[str, Any]] = {}
        self.results: List[Dict[str, Any]] = []
        self.failed_simulations: List[int] = []

        logger.info(
            f"MonteCarloRunner initialized with {num_simulations} simulations"
        )

    def add_parameter_variation(
        self,
        parameter_path: str,
        mean: float,
        std: float,
        distribution: str = "normal",
    ) -> None:
        """Add parameter variation for Monte Carlo sampling.

        Args:
            parameter_path: Dot-separated path to parameter (e.g., "rocket.dry_mass_kg").
            mean: Mean value for distribution.
            std: Standard deviation.
            distribution: Distribution type ("normal", "uniform").

        Example:
            >>> mc_runner.add_parameter_variation("rocket.dry_mass_kg", 10.0, 0.5)
            >>> mc_runner.add_parameter_variation("environment.wind.velocity_ms", 5.0, 2.0)
        """
        self.parameter_variations[parameter_path] = {
            "mean": mean,
            "std": std,
            "distribution": distribution,
        }
        logger.debug(
            f"Added parameter variation: {parameter_path} ~ {distribution}({mean}, {std})"
        )

    def _sample_parameter(self, variation_spec: Dict[str, Any]) -> float:
        """Sample parameter from specified distribution.

        Args:
            variation_spec: Dictionary with mean, std, distribution.

        Returns:
            Sampled parameter value.
        """
        if variation_spec["distribution"] == "normal":
            return np.random.normal(variation_spec["mean"], variation_spec["std"])
        elif variation_spec["distribution"] == "uniform":
            # For uniform, use mean ± std as bounds
            lower = variation_spec["mean"] - variation_spec["std"]
            upper = variation_spec["mean"] + variation_spec["std"]
            return np.random.uniform(lower, upper)
        else:
            logger.warning(
                f"Unknown distribution {variation_spec['distribution']}, using normal"
            )
            return np.random.normal(variation_spec["mean"], variation_spec["std"])

    def _apply_variations(
        self, simulation_index: int
    ) -> Tuple[RocketConfig, MotorConfig, EnvironmentConfig, SimulationConfig]:
        """Apply parameter variations for a single simulation.

        Args:
            simulation_index: Index of current simulation.

        Returns:
            Tuple of modified configurations.
        """
        # Create copies of base configurations
        import copy
        rocket_cfg = copy.deepcopy(self.base_rocket_config)
        motor_cfg = copy.deepcopy(self.base_motor_config)
        env_cfg = copy.deepcopy(self.base_environment_config)
        sim_cfg = copy.deepcopy(self.base_simulation_config)

        # Apply each parameter variation
        configs = {
            "rocket": rocket_cfg,
            "motor": motor_cfg,
            "environment": env_cfg,
            "simulation": sim_cfg,
        }

        for param_path, variation_spec in self.parameter_variations.items():
            parts = param_path.split(".")
            config_name = parts[0]
            attr_path = parts[1:]

            # Get the config object
            config_obj = configs[config_name]

            # Navigate to the attribute
            obj = config_obj
            for attr in attr_path[:-1]:
                obj = getattr(obj, attr)

            # Sample and set the new value
            new_value = self._sample_parameter(variation_spec)
            setattr(obj, attr_path[-1], new_value)

        return rocket_cfg, motor_cfg, env_cfg, sim_cfg

    def _extract_parameter_values(
        self,
        rocket_cfg,
        motor_cfg,
        env_cfg,
        sim_cfg
    ) -> Dict[str, float]:
        """Extract actual parameter values from configs for sensitivity analysis.

        Args:
            rocket_cfg: Rocket configuration
            motor_cfg: Motor configuration
            env_cfg: Environment configuration
            sim_cfg: Simulation configuration

        Returns:
            Dictionary mapping parameter paths to their values.
        """
        values = {}
        configs = {
            "rocket": rocket_cfg,
            "motor": motor_cfg,
            "environment": env_cfg,
            "simulation": sim_cfg,
        }

        for param_path in self.parameter_variations.keys():
            parts = param_path.split(".")
            config_name = parts[0]
            attr_path = parts[1:]

            obj = configs[config_name]
            for attr in attr_path:
                obj = getattr(obj, attr)

            # Convert to float for analysis
            values[param_path] = float(obj)

        return values

    def _run_single_simulation(self, simulation_index: int) -> Optional[Dict[str, Any]]:
        """Run a single Monte Carlo simulation.

        Args:
            simulation_index: Index of this simulation.

        Returns:
            Dictionary with simulation results, or None if failed.
        """
        try:
            logger.debug(f"Running simulation {simulation_index + 1}/{self.num_simulations}")

            # Apply parameter variations
            rocket_cfg, motor_cfg, env_cfg, sim_cfg = self._apply_variations(
                simulation_index
            )

            # Extract input parameter values for sensitivity analysis
            input_parameters = self._extract_parameter_values(
                rocket_cfg, motor_cfg, env_cfg, sim_cfg
            )

            # Build components
            motor = MotorBuilder(motor_cfg).build()
            env = EnvironmentBuilder(env_cfg).build()
            rocket = RocketBuilder(rocket_cfg, motor=motor, motor_config=motor_cfg).build()

            # Run simulation
            simulator = FlightSimulator(rocket, env, sim_cfg)
            flight = simulator.run()

            # Get results
            summary = simulator.get_summary()
            summary["simulation_index"] = simulation_index
            summary["parameters"] = input_parameters  # ADD INPUT PARAMETERS

            return summary

        except Exception as e:
            logger.warning(f"Simulation {simulation_index} failed: {e}")
            return None

    def run(self, parallel: bool = False, max_workers: Optional[int] = None) -> List[Dict[str, Any]]:
        """Run Monte Carlo ensemble.

        Args:
            parallel: Whether to run simulations in parallel.
            max_workers: Maximum number of parallel workers (None = CPU count).

        Returns:
            List of simulation results.

        Example:
            >>> results = mc_runner.run(parallel=True, max_workers=4)
            >>> print(f"Completed {len(results)} simulations")
        """
        logger.info(f"Starting Monte Carlo with {self.num_simulations} simulations")

        self.results = []
        self.failed_simulations = []

        if parallel:
            logger.info(f"Running in parallel with max_workers={max_workers}")
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._run_single_simulation, i): i
                    for i in range(self.num_simulations)
                }

                for future in as_completed(futures):
                    result = future.result()
                    if result is not None:
                        self.results.append(result)
                    else:
                        self.failed_simulations.append(futures[future])

        else:
            logger.info("Running sequentially")
            for i in range(self.num_simulations):
                result = self._run_single_simulation(i)
                if result is not None:
                    self.results.append(result)
                else:
                    self.failed_simulations.append(i)

        success_rate = len(self.results) / self.num_simulations * 100
        logger.info(
            f"Monte Carlo complete: {len(self.results)}/{self.num_simulations} "
            f"successful ({success_rate:.1f}%)"
        )

        return self.results

    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics from Monte Carlo results.

        Returns:
            Dictionary with statistics for each metric.

        Example:
            >>> stats = mc_runner.get_statistics()
            >>> print(f"Mean apogee: {stats['apogee_m']['mean']:.1f} m")
            >>> print(f"Std dev: {stats['apogee_m']['std']:.1f} m")
        """
        if not self.results:
            raise RuntimeError("No results available. Run simulations first.")

        logger.info("Calculating statistics...")

        # Get all metrics
        metrics = list(self.results[0].keys())
        metrics.remove("simulation_index")  # Don't analyze index

        statistics = {}

        for metric in metrics:
            values = [result[metric] for result in self.results]
            values = np.array(values)

            statistics[metric] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "median": float(np.median(values)),
                "p05": float(np.percentile(values, 5)),
                "p95": float(np.percentile(values, 95)),
            }

        return statistics

    def export_results(self, output_dir: str, base_filename: str = "monte_carlo") -> Dict[str, Path]:
        """Export Monte Carlo results to files.

        Args:
            output_dir: Output directory for exports.
            base_filename: Base filename for exports.

        Returns:
            Dictionary mapping export type to file path.

        Example:
            >>> paths = mc_runner.export_results("outputs/mc_results")
            >>> print(paths["results"])  # outputs/mc_results/monte_carlo_results.json
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting Monte Carlo results to {output_dir}")

        paths = {}

        # Export raw results
        results_file = output_path / f"{base_filename}_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        paths["results"] = results_file
        logger.info(f"Exported raw results to {results_file}")

        # Export statistics
        stats = self.get_statistics()
        stats_file = output_path / f"{base_filename}_statistics.json"
        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=2)
        paths["statistics"] = stats_file
        logger.info(f"Exported statistics to {stats_file}")

        # Export parameter variations
        variations_file = output_path / f"{base_filename}_parameters.json"
        with open(variations_file, "w") as f:
            json.dump(self.parameter_variations, f, indent=2)
        paths["parameters"] = variations_file
        logger.info(f"Exported parameter variations to {variations_file}")

        return paths

    def print_statistics_summary(self) -> None:
        """Print formatted statistics summary to console."""
        if not self.results:
            logger.error("No results available. Run simulations first.")
            return

        stats = self.get_statistics()

        print("\n" + "=" * 70)
        print("MONTE CARLO SIMULATION STATISTICS")
        print("=" * 70)
        print(f"\nTotal simulations: {self.num_simulations}")
        print(f"Successful: {len(self.results)} ({len(self.results)/self.num_simulations*100:.1f}%)")
        print(f"Failed: {len(self.failed_simulations)}")

        # Key metrics
        key_metrics = [
            "apogee_m",
            "max_velocity_ms",
            "x_impact_m",
            "y_impact_m",
            "lateral_distance_m",
        ]

        for metric in key_metrics:
            if metric in stats:
                s = stats[metric]
                print(f"\n{metric.replace('_', ' ').title()}:")
                print(f"  Mean:     {s['mean']:10.2f}")
                print(f"  Std Dev:  {s['std']:10.2f}")
                print(f"  Min:      {s['min']:10.2f}")
                print(f"  Max:      {s['max']:10.2f}")
                print(f"  Median:   {s['median']:10.2f}")
                print(f"  5th %ile: {s['p05']:10.2f}")
                print(f"  95th %ile:{s['p95']:10.2f}")

        print("=" * 70 + "\n")

    def export_for_sensitivity(
        self,
        parameter_names: Optional[List[str]] = None,
        target_names: Optional[List[str]] = None
    ) -> Tuple["pd.DataFrame", "pd.DataFrame"]:
        """
        Export Monte Carlo results as DataFrames for sensitivity analysis.

        This method prepares data in the format expected by
        VarianceBasedSensitivityAnalyzer, extracting parameter values
        and target variables from simulation results.

        Args:
            parameter_names: List of parameter paths to export (None = all)
            target_names: List of target variable names to export (None = all)

        Returns:
            Tuple of (parameters_df, targets_df)
            - parameters_df: DataFrame with shape (N samples, P parameters)
            - targets_df: DataFrame with shape (N samples, T targets)

        Raises:
            RuntimeError: If no results available
            ValueError: If requested parameters/targets don't exist

        Example:
            >>> params_df, targets_df = mc_runner.export_for_sensitivity(
            ...     parameter_names=["rocket.dry_mass_kg", "motor.thrust_avg"],
            ...     target_names=["apogee_m", "max_velocity_ms"]
            ... )
            >>> # Now use with VarianceBasedSensitivityAnalyzer
            >>> analyzer = VarianceBasedSensitivityAnalyzer(
            ...     parameter_names=list(params_df.columns),
            ...     target_names=list(targets_df.columns)
            ... )
            >>> analyzer.fit(params_df, targets_df)
        """
        import pandas as pd

        if not self.results:
            raise RuntimeError(
                "No results available. Run Monte Carlo simulation first."
            )

        logger.info("Exporting Monte Carlo data for sensitivity analysis")

        # Default to all parameters and common target metrics
        if parameter_names is None:
            parameter_names = list(self.parameter_variations.keys())

        if target_names is None:
            target_names = [
                "apogee_m",
                "apogee_time_s",
                "max_velocity_ms",
                "x_impact_m",
                "y_impact_m",
                "lateral_distance_m",
                "flight_time_s"
            ]

        # Extract parameter values
        param_data = []
        for result in self.results:
            param_row = {}
            for param_name in parameter_names:
                if param_name in result.get("parameters", {}):
                    param_row[param_name] = result["parameters"][param_name]
                else:
                    raise ValueError(
                        f"Parameter '{param_name}' not found in results"
                    )
            param_data.append(param_row)

        parameters_df = pd.DataFrame(param_data)

        # Extract target values
        target_data = []
        for result in self.results:
            target_row = {}
            for target_name in target_names:
                if target_name in result:
                    target_row[target_name] = result[target_name]
                else:
                    # Try to find in nested structure
                    found = False
                    for key, value in result.items():
                        if isinstance(value, dict) and target_name in value:
                            target_row[target_name] = value[target_name]
                            found = True
                            break
                    if not found:
                        logger.warning(
                            f"Target '{target_name}' not found in results, skipping"
                        )
            if target_row:  # Only add if at least one target was found
                target_data.append(target_row)

        targets_df = pd.DataFrame(target_data)

        # Validate dimensions match
        if len(parameters_df) != len(targets_df):
            logger.warning(
                f"Parameter samples ({len(parameters_df)}) don't match "
                f"target samples ({len(targets_df)}). Using intersection."
            )
            min_len = min(len(parameters_df), len(targets_df))
            parameters_df = parameters_df.iloc[:min_len]
            targets_df = targets_df.iloc[:min_len]

        logger.info(
            f"Exported {len(parameters_df)} samples with "
            f"{len(parameters_df.columns)} parameters and "
            f"{len(targets_df.columns)} targets"
        )

        return parameters_df, targets_df

    def save_rocketpy_format(
        self,
        output_dir: str,
        filename_prefix: str = "monte_carlo",
        parameter_names: Optional[List[str]] = None,
        target_names: Optional[List[str]] = None
    ) -> Tuple[Path, Path]:
        """
        Save Monte Carlo results in RocketPy standard format.

        Creates two space-separated text files compatible with RocketPy:
        - {prefix}.inputs.txt: Parameter values for each simulation
        - {prefix}.outputs.txt: Output values for each simulation

        This format is compatible with RocketPy's load_monte_carlo_data()
        and sensitivity analysis tools.

        Args:
            output_dir: Directory to save files
            filename_prefix: Prefix for output filenames
            parameter_names: Parameters to export (None = all)
            target_names: Targets to export (None = common metrics)

        Returns:
            Tuple of (input_file_path, output_file_path)

        Example:
            >>> input_path, output_path = mc_runner.save_rocketpy_format(
            ...     output_dir="outputs/sensitivity_data",
            ...     filename_prefix="calisto_mc"
            ... )
            >>> # Files can now be loaded with sensitivity_utils.load_monte_carlo_data()
        """
        # Get data as DataFrames
        parameters_df, targets_df = self.export_for_sensitivity(
            parameter_names=parameter_names,
            target_names=target_names
        )

        # Save using utility function
        from src.sensitivity_utils import save_monte_carlo_data

        input_path, output_path = save_monte_carlo_data(
            parameters_df=parameters_df,
            targets_df=targets_df,
            output_dir=output_dir,
            filename_prefix=filename_prefix
        )

        logger.info(
            f"Saved Monte Carlo data in RocketPy format:\n"
            f"  - {input_path}\n"
            f"  - {output_path}"
        )

        return input_path, output_path

    def get_parameter_metadata(self) -> Dict[str, Dict[str, float]]:
        """
        Get nominal mean and standard deviation for each varied parameter.

        Returns metadata needed for variance-based sensitivity analysis.

        Returns:
            Dictionary mapping parameter names to {"mean": ..., "std": ...}

        Example:
            >>> metadata = mc_runner.get_parameter_metadata()
            >>> print(metadata["rocket.dry_mass_kg"])
            {'mean': 10.0, 'std': 0.5}
            >>>
            >>> # Use with VarianceBasedSensitivityAnalyzer
            >>> analyzer.set_nominal_parameters(
            ...     means={k: v['mean'] for k, v in metadata.items()},
            ...     stds={k: v['std'] for k, v in metadata.items()}
            ... )
        """
        metadata = {}

        for param_name, param_config in self.parameter_variations.items():
            metadata[param_name] = {
                "mean": param_config["mean"],
                "std": param_config["std"],
                "distribution": param_config.get("distribution", "normal")
            }

        return metadata
