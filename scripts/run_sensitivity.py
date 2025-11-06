#!/usr/bin/env python3
"""
Run Sensitivity Analysis on Monte Carlo Results.

This script performs sensitivity analysis on Monte Carlo simulation results
using either variance-based or OAT (One-At-a-Time) methods.

Usage:
    # Variance-based sensitivity (recommended)
    python scripts/run_sensitivity.py \\
        --monte-carlo-dir outputs/mc_results/ \\
        --method variance \\
        --parameters rocket.dry_mass_kg,motor.thrust_avg \\
        --targets apogee_m \\
        --output-dir outputs/sensitivity/ \\
        --plot

    # OAT sensitivity (quick screening)
    python scripts/run_sensitivity.py \\
        --config configs/complete_example.yaml \\
        --method oat \\
        --parameters rocket.dry_mass_kg,environment.wind.velocity_ms \\
        --targets apogee_m \\
        --variation 10 \\
        --output-dir outputs/sensitivity_oat/ \\
        --plot
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.variance_sensitivity import VarianceBasedSensitivityAnalyzer
from src.sensitivity_analyzer import OATSensitivityAnalyzer
from src.sensitivity_utils import (
    load_monte_carlo_data,
    estimate_parameter_statistics,
    export_sensitivity_to_json
)
from src.config_loader import ConfigLoader
from src.utils import setup_logging, ensure_directory_exists


logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run sensitivity analysis on simulation results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Method selection
    parser.add_argument(
        "--method",
        type=str,
        choices=["variance", "oat"],
        default="variance",
        help="Sensitivity analysis method: 'variance' (variance-based, recommended) "
             "or 'oat' (one-at-a-time screening)"
    )

    # For variance-based method
    parser.add_argument(
        "--monte-carlo-dir",
        type=str,
        help="Directory containing Monte Carlo results (.inputs.txt and .outputs.txt files). "
             "Required for variance-based method."
    )

    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to .inputs.txt file (overrides --monte-carlo-dir)"
    )

    parser.add_argument(
        "--output-file",
        type=str,
        help="Path to .outputs.txt file (overrides --monte-carlo-dir)"
    )

    # For OAT method
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration YAML file. Required for OAT method."
    )

    parser.add_argument(
        "--variation",
        type=float,
        default=10.0,
        help="Percentage variation for OAT method (default: 10%%)"
    )

    # Common parameters
    parser.add_argument(
        "--parameters",
        type=str,
        required=True,
        help="Comma-separated list of parameter names to analyze "
             "(e.g., 'rocket.dry_mass_kg,motor.thrust_avg')"
    )

    parser.add_argument(
        "--targets",
        type=str,
        default="apogee_m",
        help="Comma-separated list of target variables (default: 'apogee_m')"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/sensitivity",
        help="Output directory for results (default: outputs/sensitivity)"
    )

    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate sensitivity plots"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def run_variance_based_sensitivity(
    input_file: Path,
    output_file: Path,
    parameter_names: List[str],
    target_names: List[str],
    output_dir: Path,
    generate_plots: bool
) -> None:
    """
    Run variance-based sensitivity analysis.

    Args:
        input_file: Path to .inputs.txt file
        output_file: Path to .outputs.txt file
        parameter_names: List of parameter names to analyze
        target_names: List of target variable names
        output_dir: Output directory for results
        generate_plots: Whether to generate plots
    """
    logger.info("Running variance-based sensitivity analysis...")

    # Load Monte Carlo data
    logger.info(f"Loading Monte Carlo data from {input_file.parent}")
    parameters_df, targets_df = load_monte_carlo_data(
        input_file=input_file,
        output_file=output_file,
        parameter_names=parameter_names,
        target_names=target_names
    )

    logger.info(
        f"Loaded {len(parameters_df)} samples with "
        f"{len(parameter_names)} parameters and {len(target_names)} targets"
    )

    # Estimate parameter statistics from data
    param_stats = estimate_parameter_statistics(parameters_df)

    # Create analyzer
    analyzer = VarianceBasedSensitivityAnalyzer(
        parameter_names=parameter_names,
        target_names=target_names
    )

    # Set nominal parameters
    means = {param: stats["mean"] for param, stats in param_stats.items()}
    stds = {param: stats["std"] for param, stats in param_stats.items()}

    analyzer.set_nominal_parameters(means=means, stds=stds)

    # Fit regression models
    logger.info("Fitting regression models...")
    analyzer.fit(parameters_df, targets_df)

    # Print summary
    print("\n")
    analyzer.print_summary()

    # Export results
    ensure_directory_exists(output_dir)

    # Export to JSON
    json_file = output_dir / "sensitivity_results.json"
    export_sensitivity_to_json(
        sensitivity_coefficients=analyzer.sensitivity_coefficients,
        lae=analyzer.lae,
        nominal_parameters=param_stats,
        output_file=json_file
    )
    logger.info(f"Exported results to {json_file}")

    # Generate plots if requested
    if generate_plots:
        for target_name in target_names:
            plot_file = output_dir / f"sensitivity_bars_{target_name}.png"
            logger.info(f"Generating sensitivity bar plot for {target_name}...")
            analyzer.plot_sensitivity_bars(
                output_path=str(plot_file),
                target_name=target_name
            )

    logger.info("Variance-based sensitivity analysis complete!")


def run_oat_sensitivity(
    config_file: Path,
    parameter_names: List[str],
    target_names: List[str],
    variation_percent: float,
    output_dir: Path,
    generate_plots: bool
) -> None:
    """
    Run OAT (One-At-a-Time) sensitivity analysis.

    Args:
        config_file: Path to configuration YAML file
        parameter_names: List of parameter names to analyze
        target_names: List of target variable names
        variation_percent: Percentage variation for parameters
        output_dir: Output directory for results
        generate_plots: Whether to generate plots
    """
    logger.info("Running OAT sensitivity analysis...")

    # Load configuration
    logger.info(f"Loading configuration from {config_file}")
    config_loader = ConfigLoader()
    config_loader.load_from_yaml(str(config_file))

    rocket_cfg = config_loader.get_rocket_config()
    motor_cfg = config_loader.get_motor_config()
    env_cfg = config_loader.get_environment_config()
    sim_cfg = config_loader.get_simulation_config()

    # Create analyzer
    analyzer = OATSensitivityAnalyzer(
        base_rocket_config=rocket_cfg,
        base_motor_config=motor_cfg,
        base_environment_config=env_cfg,
        base_simulation_config=sim_cfg
    )

    # Add parameters
    for param_name in parameter_names:
        logger.info(f"Adding parameter: {param_name} (±{variation_percent}%)")
        analyzer.add_parameter(
            parameter_path=param_name,
            variation_percent=variation_percent
        )

    # Run analysis for each target
    for target_name in target_names:
        logger.info(f"Analyzing target: {target_name}")
        analyzer.run(output_metric=target_name)

        # Print summary
        print(f"\nResults for {target_name}:")
        analyzer.print_summary()

        # Generate tornado diagram if requested
        if generate_plots:
            ensure_directory_exists(output_dir)
            plot_file = output_dir / f"tornado_{target_name}.png"
            logger.info(f"Generating tornado diagram...")
            analyzer.plot_tornado_diagram(
                output_path=str(plot_file),
                title=f"OAT Sensitivity: {target_name}"
            )

    logger.info("OAT sensitivity analysis complete!")


def main():
    """Main entry point."""
    args = parse_arguments()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)

    logger.info("=" * 70)
    logger.info("SENSITIVITY ANALYSIS")
    logger.info("=" * 70)

    # Parse parameters and targets
    parameter_names = [p.strip() for p in args.parameters.split(",")]
    target_names = [t.strip() for t in args.targets.split(",")]

    output_dir = Path(args.output_dir)

    # Run appropriate method
    if args.method == "variance":
        # Variance-based sensitivity
        if args.monte_carlo_dir is None and (args.input_file is None or args.output_file is None):
            logger.error(
                "For variance-based method, either --monte-carlo-dir or "
                "(--input-file and --output-file) must be specified"
            )
            sys.exit(1)

        # Determine input/output files
        if args.input_file and args.output_file:
            input_file = Path(args.input_file)
            output_file = Path(args.output_file)
        else:
            mc_dir = Path(args.monte_carlo_dir)
            # Find .inputs.txt and .outputs.txt files
            input_files = list(mc_dir.glob("*.inputs.txt"))
            output_files = list(mc_dir.glob("*.outputs.txt"))

            if not input_files or not output_files:
                logger.error(
                    f"Could not find .inputs.txt or .outputs.txt files in {mc_dir}"
                )
                sys.exit(1)

            input_file = input_files[0]
            output_file = output_files[0]
            logger.info(f"Using input file: {input_file.name}")
            logger.info(f"Using output file: {output_file.name}")

        run_variance_based_sensitivity(
            input_file=input_file,
            output_file=output_file,
            parameter_names=parameter_names,
            target_names=target_names,
            output_dir=output_dir,
            generate_plots=args.plot
        )

    elif args.method == "oat":
        # OAT sensitivity
        if args.config is None:
            logger.error("For OAT method, --config must be specified")
            sys.exit(1)

        config_file = Path(args.config)
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            sys.exit(1)

        run_oat_sensitivity(
            config_file=config_file,
            parameter_names=parameter_names,
            target_names=target_names,
            variation_percent=args.variation,
            output_dir=output_dir,
            generate_plots=args.plot
        )

    logger.info("=" * 70)
    logger.info("Analysis complete!")
    logger.info(f"Results saved to: {output_dir}")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
