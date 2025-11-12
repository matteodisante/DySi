#!/usr/bin/env python3
"""
Monte Carlo Uncertainty Quantification Example

This standalone script demonstrates:
- Loading a Monte Carlo configuration
- Defining parameter uncertainties
- Running ensemble simulations in parallel
- Computing statistics (mean, std, percentiles)
- Analyzing landing dispersion
- Generating distribution plots

Usage:
    python examples/02_monte_carlo_simple.py
    python examples/02_monte_carlo_simple.py --config configs/monte_carlo/01_basic_mc.yaml --samples 100
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.monte_carlo_runner import MonteCarloRunner


def main():
    """Run Monte Carlo uncertainty quantification."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run Monte Carlo ensemble simulation")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/monte_carlo/01_basic_mc.yaml",
        help="Path to configuration YAML file"
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=None,
        help="Number of Monte Carlo samples (overrides config)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/monte_carlo_example",
        help="Directory for output files"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    args = parser.parse_args()

    # Resolve paths
    config_path = project_root / args.config
    output_dir = project_root / args.output_dir

    print("=" * 70)
    print("MONTE CARLO UNCERTAINTY QUANTIFICATION")
    print("=" * 70)

    # Step 1: Load Configuration
    print(f"\n[1/4] Loading configuration from {config_path.name}...")
    if not config_path.exists():
        print(f"ERROR: Configuration file not found: {config_path}")
        sys.exit(1)

    loader = ConfigLoader()
    loader.load_from_yaml(str(config_path))

    rocket_cfg = loader.get_rocket_config()
    motor_cfg = loader.get_motor_config()
    env_cfg = loader.get_environment_config()
    sim_cfg = loader.get_simulation_config()

    print(f"✓ Configuration loaded: {rocket_cfg.name}")

    # Get Monte Carlo config from YAML (if present)
    mc_config = None
    try:
        mc_config = loader.get_monte_carlo_config()
        num_simulations = args.samples if args.samples else mc_config.num_simulations
        print(f"  Monte Carlo config found: {mc_config.num_simulations} samples")
    except AttributeError:
        num_simulations = args.samples if args.samples else 50
        print(f"  No Monte Carlo config in YAML, using {num_simulations} samples")

    # Step 2: Setup Monte Carlo Runner
    print(f"\n[2/4] Setting up Monte Carlo runner...")
    mc_runner = MonteCarloRunner(
        base_rocket_config=rocket_cfg,
        base_motor_config=motor_cfg,
        base_environment_config=env_cfg,
        base_simulation_config=sim_cfg,
        num_simulations=num_simulations,
        random_seed=args.seed
    )

    # Add parameter variations (from config or defaults)
    if mc_config and hasattr(mc_config, 'variations'):
        # Use variations from config
        variations = mc_config.variations
        if hasattr(variations, 'motor_thrust_std_pct'):
            # Note: This is a simplified example - production code would
            # need to map config variations to parameter paths properly
            pass

    # Add default parameter variations
    print("  Adding parameter variations:")

    mc_runner.add_parameter_variation(
        parameter_path="rocket.dry_mass_kg",
        mean=rocket_cfg.dry_mass_kg,
        std=0.3,  # ±0.3 kg uncertainty
        distribution="normal"
    )
    print(f"    • dry_mass_kg: μ={rocket_cfg.dry_mass_kg:.2f}, σ=0.30")

    mc_runner.add_parameter_variation(
        parameter_path="environment.wind.velocity_ms",
        mean=env_cfg.wind.velocity_ms,
        std=1.5,  # ±1.5 m/s wind variation
        distribution="normal"
    )
    print(f"    • wind_velocity_ms: μ={env_cfg.wind.velocity_ms:.2f}, σ=1.50")

    mc_runner.add_parameter_variation(
        parameter_path="rocket.cg_location_m",
        mean=rocket_cfg.cg_location_m,
        std=0.02,  # ±2 cm CG uncertainty
        distribution="normal"
    )
    print(f"    • cg_location_m: μ={rocket_cfg.cg_location_m:.2f}, σ=0.02")

    print(f"\n✓ Monte Carlo runner configured:")
    print(f"  Samples:      {num_simulations}")
    print(f"  Parameters:   {len(mc_runner.parameter_variations)}")
    print(f"  Workers:      {args.workers}")
    print(f"  Seed:         {args.seed}")

    # Step 3: Run Ensemble Simulation
    print(f"\n[3/4] Running {num_simulations} simulations in parallel...")
    print("  This may take several minutes...")

    try:
        results = mc_runner.run(parallel=True, max_workers=args.workers)
        print(f"\n✓ Ensemble complete!")
        print(f"  Successful: {len(results)}/{num_simulations}")
        print(f"  Failed:     {len(mc_runner.failed_simulations)}/{num_simulations}")
    except Exception as e:
        print(f"✗ Monte Carlo simulation failed: {e}")
        sys.exit(1)

    # Step 4: Analyze Results
    print(f"\n[4/4] Computing statistics...")

    stats = mc_runner.get_statistics()

    print("\n" + "=" * 70)
    print("STATISTICAL RESULTS")
    print("=" * 70)

    # Apogee statistics
    print(f"\nApogee (m):")
    print(f"  Mean:         {stats['apogee_m']['mean']:.1f} m")
    print(f"  Std Dev:      {stats['apogee_m']['std']:.1f} m")
    print(f"  Min:          {stats['apogee_m']['min']:.1f} m")
    print(f"  Max:          {stats['apogee_m']['max']:.1f} m")
    print(f"  5th %ile:     {stats['apogee_m']['p05']:.1f} m")
    print(f"  95th %ile:    {stats['apogee_m']['p95']:.1f} m")
    print(f"  Spread:       {stats['apogee_m']['p95'] - stats['apogee_m']['p05']:.1f} m (90% interval)")

    # Velocity statistics
    print(f"\nMax Velocity (m/s):")
    print(f"  Mean:         {stats['max_velocity_ms']['mean']:.1f} m/s")
    print(f"  Std Dev:      {stats['max_velocity_ms']['std']:.1f} m/s")

    # Landing dispersion
    print(f"\nLanding Dispersion (m):")
    print(f"  Mean distance: {stats['lateral_distance_m']['mean']:.1f} m")
    print(f"  Std Dev:       {stats['lateral_distance_m']['std']:.1f} m")
    print(f"  Max distance:  {stats['lateral_distance_m']['max']:.1f} m")

    # Flight time
    print(f"\nFlight Time (s):")
    print(f"  Mean:         {stats['flight_time_s']['mean']:.1f} s")
    print(f"  Std Dev:      {stats['flight_time_s']['std']:.1f} s")

    # Export Data
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n" + "=" * 70)
    print("EXPORTING DATA")
    print("=" * 70)

    # Export in RocketPy format
    input_file, output_file = mc_runner.save_rocketpy_format(
        output_dir=str(output_dir),
        filename_prefix="mc_results"
    )

    print(f"✓ Data exported:")
    print(f"  Input parameters:  {input_file}")
    print(f"  Output targets:    {output_file}")

    # Summary
    print(f"\n" + "=" * 70)
    print("MONTE CARLO ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Configuration:  {config_path}")
    print(f"Samples:        {len(results)} successful")
    print(f"Apogee:         {stats['apogee_m']['mean']:.1f} ± {stats['apogee_m']['std']:.1f} m")
    print(f"Max velocity:   {stats['max_velocity_ms']['mean']:.1f} ± {stats['max_velocity_ms']['std']:.1f} m/s")
    print(f"Landing range:  {stats['lateral_distance_m']['mean']:.1f} ± {stats['lateral_distance_m']['std']:.1f} m")
    print(f"Data files:     {output_dir.absolute()}")
    print()

    # Interpretation guide
    print("Interpretation:")
    print("  • Apogee spread (90% interval) indicates uncertainty in altitude prediction")
    print("  • Landing dispersion shows how far the rocket might drift")
    print("  • Statistical analysis tools can be added for parameter importance")
    print()


if __name__ == "__main__":
    main()
