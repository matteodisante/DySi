#!/usr/bin/env python3
"""Command-line script for running Monte Carlo ensemble simulations.

Usage:
    python scripts/run_monte_carlo.py --config configs/simple_rocket.yaml --samples 100
"""

import argparse
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config_loader import ConfigLoader
from src.monte_carlo_runner import MonteCarloRunner
from src.utils import setup_logging


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Run Monte Carlo ensemble simulation",
    )

    parser.add_argument("--config", "-c", type=str, required=True, help="Configuration file")
    parser.add_argument("--samples", "-n", type=int, default=100, help="Number of simulations")
    parser.add_argument("--output-dir", "-o", type=str, default="outputs/monte_carlo", help="Output directory")
    parser.add_argument("--parallel", "-p", action="store_true", help="Run in parallel")
    parser.add_argument("--workers", "-w", type=int, default=None, help="Number of parallel workers")
    parser.add_argument("--seed", "-s", type=int, default=None, help="Random seed")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()

    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)

    logger = logging.getLogger(__name__)

    logger.info("="*60)
    logger.info("MONTE CARLO SIMULATION")
    logger.info("="*60)

    try:
        # Load configuration
        loader = ConfigLoader()
        rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(args.config)

        # Create Monte Carlo runner
        mc_runner = MonteCarloRunner(
            rocket_cfg, motor_cfg, env_cfg, sim_cfg,
            num_simulations=args.samples,
            random_seed=args.seed
        )

        # Add parameter variations (example - user should customize)
        mc_runner.add_parameter_variation("rocket.dry_mass_kg",
                                         mean=rocket_cfg.dry_mass_kg, std=0.5)
        mc_runner.add_parameter_variation("environment.wind.velocity_ms",
                                         mean=env_cfg.wind.velocity_ms, std=2.0)

        # Run simulations
        results = mc_runner.run(parallel=args.parallel, max_workers=args.workers)

        # Print statistics
        mc_runner.print_statistics_summary()

        # Export results
        paths = mc_runner.export_results(args.output_dir)
        logger.info(f"\nResults exported to: {args.output_dir}/")

        return 0

    except Exception as e:
        logger.error(f"Monte Carlo simulation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
