"""One-At-a-Time (OAT) Sensitivity Analysis for parameter screening.

This module provides the OATSensitivityAnalyzer class for performing one-at-a-time
(OAT) sensitivity analysis to identify which parameters most affect key outputs.

OAT Method:
    This is a local sensitivity screening method that varies one parameter at a time
    while keeping others fixed. It's useful for quick parameter screening but does
    not quantify variance contribution like variance-based methods.

When to use OAT:
    - Quick screening of many parameters
    - Identifying which parameters to focus on
    - Understanding directional effects (increase/decrease)
    - Simple, interpretable results

When to use Variance-Based instead:
    - Quantitative uncertainty contribution
    - Statistical rigor for publications
    - Integration with Monte Carlo simulations
    - Validation with Linear Approximation Error (LAE)

See Also:
    variance_sensitivity.py: VarianceBasedSensitivityAnalyzer for rigorous analysis
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import logging
import numpy as np

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from src.config_loader import RocketConfig, MotorConfig, EnvironmentConfig, SimulationConfig
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator
from src.utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class OATSensitivityAnalyzer:
    """One-At-a-Time (OAT) sensitivity analyzer for parameter screening.

    This class performs one-at-a-time (OAT) sensitivity analysis to determine
    which parameters have the most impact on key flight metrics.

    OAT Method Overview:
        1. Run baseline simulation with nominal parameters
        2. For each parameter:
           - Run simulation with +X% variation
           - Run simulation with -X% variation
        3. Calculate sensitivity index from output changes
        4. Rank parameters by sensitivity

    This method is complementary to variance-based sensitivity analysis:
    - OAT: Quick screening, shows directional effects, (2N+1) simulations
    - Variance-Based: Statistical rigor, variance contribution, uses MC data

    Note:
        For rigorous uncertainty quantification with statistical validation,
        consider using VarianceBasedSensitivityAnalyzer instead. That method
        integrates with Monte Carlo simulations and provides variance-based
        sensitivity coefficients with Linear Approximation Error (LAE) validation.

    Example:
        >>> # Quick parameter screening
        >>> analyzer = OATSensitivityAnalyzer(rocket_cfg, motor_cfg, env_cfg, sim_cfg)
        >>> analyzer.add_parameter("rocket.dry_mass_kg", variation_percent=10)
        >>> analyzer.add_parameter("environment.wind.velocity_ms", variation_percent=50)
        >>> results = analyzer.run(output_metric="apogee_m")
        >>> importance = analyzer.get_importance_ranking()
        >>> analyzer.plot_tornado_diagram("outputs/tornado.png")
    """

    def __init__(
        self,
        base_rocket_config: RocketConfig,
        base_motor_config: MotorConfig,
        base_environment_config: EnvironmentConfig,
        base_simulation_config: SimulationConfig,
    ):
        """Initialize OATSensitivityAnalyzer.

        Args:
            base_rocket_config: Base rocket configuration.
            base_motor_config: Base motor configuration.
            base_environment_config: Base environment configuration.
            base_simulation_config: Base simulation configuration.
        """
        self.base_rocket_config = base_rocket_config
        self.base_motor_config = base_motor_config
        self.base_environment_config = base_environment_config
        self.base_simulation_config = base_simulation_config

        self.parameters: Dict[str, float] = {}
        self.sensitivity_results: Dict[str, Dict[str, Any]] = {}
        self.baseline_result: Optional[float] = None

        logger.info("OATSensitivityAnalyzer initialized")

    def add_parameter(
        self,
        parameter_path: str,
        variation_percent: float = 10.0,
    ) -> None:
        """Add parameter for sensitivity analysis.

        Args:
            parameter_path: Dot-separated path to parameter.
            variation_percent: Percentage variation from baseline (±).

        Example:
            >>> analyzer.add_parameter("rocket.dry_mass_kg", variation_percent=10)
        """
        self.parameters[parameter_path] = variation_percent
        logger.debug(f"Added parameter: {parameter_path} (±{variation_percent}%)")

    def run(
        self,
        output_metric: str = "apogee_m",
    ) -> Dict[str, Dict[str, Any]]:
        """Run sensitivity analysis.

        Args:
            output_metric: Output metric to analyze (default: "apogee_m").

        Returns:
            Dictionary with sensitivity results for each parameter.

        Example:
            >>> results = analyzer.run(output_metric="apogee_m")
        """
        logger.info(f"Running sensitivity analysis for {output_metric}")

        # Run baseline simulation
        logger.info("Running baseline simulation...")
        self.baseline_result = self._run_baseline(output_metric)
        logger.info(f"Baseline {output_metric}: {self.baseline_result:.2f}")

        # Analyze each parameter
        for param_path, variation_pct in self.parameters.items():
            logger.info(f"Analyzing parameter: {param_path}")

            # Run with positive variation
            result_high = self._run_with_variation(
                param_path, variation_pct, output_metric
            )

            # Run with negative variation
            result_low = self._run_with_variation(
                param_path, -variation_pct, output_metric
            )

            # Calculate sensitivity metrics
            self.sensitivity_results[param_path] = {
                "baseline": self.baseline_result,
                "variation_percent": variation_pct,
                "result_high": result_high,
                "result_low": result_low,
                "absolute_change": (result_high - result_low) / 2,
                "percent_change": (
                    (result_high - result_low) / 2 / self.baseline_result * 100
                ),
                "sensitivity_index": abs(
                    ((result_high - result_low) / 2 / self.baseline_result) /
                    (variation_pct / 100)
                ),
            }

            logger.info(
                f"  Sensitivity index: {self.sensitivity_results[param_path]['sensitivity_index']:.3f}"
            )

        return self.sensitivity_results

    def _run_baseline(self, output_metric: str) -> float:
        """Run baseline simulation.

        Args:
            output_metric: Metric to extract.

        Returns:
            Baseline metric value.
        """
        motor = MotorBuilder(self.base_motor_config).build()
        env = EnvironmentBuilder(self.base_environment_config).build()
        rocket = RocketBuilder(self.base_rocket_config, motor=motor).build()

        simulator = FlightSimulator(rocket, env, self.base_simulation_config)
        flight = simulator.run()
        summary = simulator.get_summary()

        return summary[output_metric]

    def _run_with_variation(
        self, parameter_path: str, variation_percent: float, output_metric: str
    ) -> float:
        """Run simulation with parameter variation.

        Args:
            parameter_path: Path to parameter.
            variation_percent: Percentage variation.
            output_metric: Metric to extract.

        Returns:
            Metric value with variation.
        """
        import copy

        # Create configuration copies
        rocket_cfg = copy.deepcopy(self.base_rocket_config)
        motor_cfg = copy.deepcopy(self.base_motor_config)
        env_cfg = copy.deepcopy(self.base_environment_config)
        sim_cfg = copy.deepcopy(self.base_simulation_config)

        # Apply variation
        parts = parameter_path.split(".")
        config_name = parts[0]
        attr_path = parts[1:]

        configs = {
            "rocket": rocket_cfg,
            "motor": motor_cfg,
            "environment": env_cfg,
            "simulation": sim_cfg,
        }

        config_obj = configs[config_name]
        obj = config_obj
        for attr in attr_path[:-1]:
            obj = getattr(obj, attr)

        # Get baseline value and apply variation
        baseline_value = getattr(obj, attr_path[-1])
        varied_value = baseline_value * (1 + variation_percent / 100)
        setattr(obj, attr_path[-1], varied_value)

        # Run simulation
        motor = MotorBuilder(motor_cfg).build()
        env = EnvironmentBuilder(env_cfg).build()
        rocket = RocketBuilder(rocket_cfg, motor=motor).build()

        simulator = FlightSimulator(rocket, env, sim_cfg)
        flight = simulator.run()
        summary = simulator.get_summary()

        return summary[output_metric]

    def get_importance_ranking(self) -> List[Tuple[str, float]]:
        """Get parameter importance ranking.

        Returns:
            List of (parameter, sensitivity_index) tuples, sorted by importance.

        Example:
            >>> ranking = analyzer.get_importance_ranking()
            >>> for param, index in ranking:
            ...     print(f"{param}: {index:.3f}")
        """
        if not self.sensitivity_results:
            raise RuntimeError("No results available. Run analysis first.")

        ranking = [
            (param, results["sensitivity_index"])
            for param, results in self.sensitivity_results.items()
        ]

        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def plot_tornado_diagram(
        self,
        output_path: Optional[str] = None,
        title: str = "Parameter Sensitivity Analysis",
    ) -> Path:
        """Create tornado diagram showing parameter sensitivity.

        Args:
            output_path: Output file path.
            title: Plot title.

        Returns:
            Path to saved plot.

        Example:
            >>> path = analyzer.plot_tornado_diagram("outputs/plots/tornado.png")
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib required for tornado diagrams")

        if not self.sensitivity_results:
            raise RuntimeError("No results available. Run analysis first.")

        if output_path is None:
            output_path = Path("outputs/plots/tornado_diagram.png")
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Creating tornado diagram: {output_path}")

        # Get sorted parameters by absolute impact
        params_sorted = sorted(
            self.sensitivity_results.items(),
            key=lambda x: abs(x[1]["percent_change"]),
            reverse=True,
        )

        fig, ax = plt.subplots(figsize=(10, max(6, len(params_sorted) * 0.5)))

        y_positions = np.arange(len(params_sorted))
        param_names = [p[0].split(".")[-1] for p in params_sorted]

        # Calculate bar lengths (low and high variations from baseline)
        low_bars = [
            p[1]["result_low"] - p[1]["baseline"] for p in params_sorted
        ]
        high_bars = [
            p[1]["result_high"] - p[1]["baseline"] for p in params_sorted
        ]

        # Plot horizontal bars
        ax.barh(
            y_positions, high_bars, left=0,
            height=0.8, color='steelblue', label='High (+)'
        )
        ax.barh(
            y_positions, low_bars, left=0,
            height=0.8, color='lightcoral', label='Low (-)'
        )

        ax.set_yticks(y_positions)
        ax.set_yticklabels(param_names, fontsize=10)
        ax.set_xlabel("Change in Output Metric", fontsize=12)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.axvline(x=0, color='black', linewidth=0.8)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        logger.info(f"Saved tornado diagram to {output_path}")
        return output_path

    def print_summary(self) -> None:
        """Print sensitivity analysis summary."""
        if not self.sensitivity_results:
            logger.error("No results available. Run analysis first.")
            return

        ranking = self.get_importance_ranking()

        print("\n" + "=" * 70)
        print("SENSITIVITY ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"\nBaseline value: {self.baseline_result:.2f}")
        print(f"\nParameters analyzed: {len(self.parameters)}")
        print("\nParameter Importance Ranking:")
        print("-" * 70)
        print(f"{'Parameter':<40} {'Sensitivity Index':<20}")
        print("-" * 70)

        for param, sensitivity_index in ranking:
            print(f"{param:<40} {sensitivity_index:>10.3f}")

        print("\nDetailed Results:")
        print("-" * 70)

        for param, sensitivity_index in ranking:
            results = self.sensitivity_results[param]
            print(f"\n{param}:")
            print(f"  Variation: ±{results['variation_percent']:.1f}%")
            print(f"  Low result: {results['result_low']:.2f}")
            print(f"  High result: {results['result_high']:.2f}")
            print(f"  Absolute change: {results['absolute_change']:.2f}")
            print(f"  Percent change: {results['percent_change']:.2f}%")
            print(f"  Sensitivity index: {sensitivity_index:.3f}")

        print("=" * 70 + "\n")


# Backward compatibility alias
# Deprecated: Use OATSensitivityAnalyzer instead
SensitivityAnalyzer = OATSensitivityAnalyzer
