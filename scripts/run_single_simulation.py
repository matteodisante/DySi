#!/usr/bin/env python3
"""Command-line script for running single rocket flight simulations.

This script loads configuration files, builds rocket components, executes
a single flight simulation, and exports results with visualizations.

Usage:
    python scripts/run_single_simulation.py --config configs/complete_example.yaml
    python scripts/run_single_simulation.py --config configs/simple_rocket.yaml --output-dir my_results
"""

import argparse
import sys
from pathlib import Path
import logging

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import ConfigLoader
from src.validators import validate_all_configs
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator
from src.data_handler import DataHandler
from src.visualizer import Visualizer
from src.utils import setup_logging


def parse_arguments():
    """Parse command-line arguments.

    Returns:
        Namespace with parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Run single rocket flight simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run simulation with default configuration
  python scripts/run_single_simulation.py --config configs/complete_example.yaml

  # Run with custom output directory
  python scripts/run_single_simulation.py --config configs/simple_rocket.yaml --output-dir my_results

  # Run without plots (faster)
  python scripts/run_single_simulation.py --config configs/simple_rocket.yaml --no-plots

  # Run with verbose logging
  python scripts/run_single_simulation.py --config configs/simple_rocket.yaml --verbose
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=str,
        required=True,
        help="Path to configuration YAML file",
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="outputs",
        help="Output directory for results (default: outputs)",
    )

    parser.add_argument(
        "--name",
        "-n",
        type=str,
        default=None,
        help="Name for this simulation (used in output filenames)",
    )

    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip plot generation (faster execution)",
    )

    parser.add_argument(
        "--no-export",
        action="store_true",
        help="Skip data export (only print summary)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log file path (default: no file logging)",
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level, log_file=args.log_file)

    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("ROCKET FLIGHT SIMULATION")
    logger.info("=" * 60)
    logger.info(f"Configuration file: {args.config}")
    logger.info(f"Output directory: {args.output_dir}")

    try:
        # 1. Load configurations
        logger.info("\n--- LOADING CONFIGURATION ---")
        loader = ConfigLoader()
        rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(
            args.config
        )
        logger.info(f"Loaded configuration for rocket: {rocket_cfg.name}")

        # 2. Validate configurations
        logger.info("\n--- VALIDATING CONFIGURATION ---")
        warnings = validate_all_configs(rocket_cfg, motor_cfg, env_cfg, sim_cfg)

        if warnings:
            logger.warning(f"Found {len(warnings)} validation warnings:")
            for warning in warnings:
                logger.warning(f"  {warning}")
        else:
            logger.info("All validations passed without warnings")

        # 3. Build components
        logger.info("\n--- BUILDING COMPONENTS ---")

        # Build motor
        logger.info("Building motor...")
        try:
            motor_builder = MotorBuilder(motor_cfg)
            motor = motor_builder.build()
            motor_summary = motor_builder.get_summary()
            logger.info(
                f"Motor: {motor_summary['total_impulse_ns']:.0f} N·s, "
                f"{motor_summary['burn_time_s']:.1f} s burn time"
            )
        except FileNotFoundError as e:
            logger.error(f"Motor build failed: {e}")
            logger.error("Simulation cannot continue without motor. Exiting.")
            sys.exit(1)

        # Build environment
        logger.info("Building environment...")
        env_builder = EnvironmentBuilder(env_cfg)
        env = env_builder.build()
        env_summary = env_builder.get_summary()
        logger.info(f"Environment: {env_summary['location']}")

        # Build rocket
        logger.info("Building rocket...")
        rocket_builder = RocketBuilder(rocket_cfg, motor=motor)
        rocket = rocket_builder.build()
        rocket_summary = rocket_builder.get_summary()
        logger.info(
            f"Rocket: {rocket_summary['name']}, "
            f"mass={rocket_summary['total_mass_kg']:.1f} kg, "
            f"static margin={rocket_summary['static_margin_calibers']:.2f} cal"
        )

        # 4. Run simulation
        logger.info("\n--- RUNNING SIMULATION ---")
        simulator = FlightSimulator(rocket, env, sim_cfg)
        flight = simulator.run()

        # 5. Print summary
        logger.info("\n--- SIMULATION RESULTS ---")
        simulator.print_summary()

        # Determine output name
        output_name = args.name if args.name else rocket_cfg.name.replace(" ", "_").lower()

        # 6. Export data (if not disabled)
        if not args.no_export:
            logger.info("\n--- EXPORTING DATA ---")

            # Create data handler
            data_handler = DataHandler(output_dir=f"{args.output_dir}/results")

            # Get data
            trajectory_data = simulator.get_trajectory_data()
            summary_data = simulator.export_summary_to_dict()

            # Export
            export_paths = data_handler.export_complete_dataset(
                trajectory_data,
                summary_data,
                base_filename=output_name,
            )

            logger.info("Exported data files:")
            for format_type, path in export_paths.items():
                logger.info(f"  {format_type}: {path}")

        # 7. Create plots (if not disabled)
        if not args.no_plots:
            logger.info("\n--- CREATING PLOTS ---")

            try:
                # Create visualizer
                visualizer = Visualizer(output_dir=f"{args.output_dir}/plots")

                # Create standard plots
                trajectory_data = simulator.get_trajectory_data()
                plot_paths = visualizer.create_standard_plots(
                    trajectory_data,
                    base_filename=output_name,
                )

                logger.info("Created plot files:")
                for plot_type, path in plot_paths.items():
                    logger.info(f"  {plot_type}: {path}")

            except ImportError as e:
                logger.warning(f"Plotting skipped: {e}")

        # 8. Success message
        logger.info("\n" + "=" * 60)
        logger.info("SIMULATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"\nResults saved to: {args.output_dir}/")

        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1

    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
