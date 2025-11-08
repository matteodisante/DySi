#!/usr/bin/env python3
"""
Basic Single Flight Simulation Example

This standalone script demonstrates:
- Loading a configuration from YAML
- Building rocket components
- Running a single flight simulation
- Extracting and printing key metrics
- Generating basic plots

Usage:
    python examples/01_basic_simulation.py
    python examples/01_basic_simulation.py --config configs/single_sim/02_complete.yaml
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config_loader import ConfigLoader
from src.motor_builder import MotorBuilder
from src.environment_setup import EnvironmentBuilder
from src.rocket_builder import RocketBuilder
from src.flight_simulator import FlightSimulator
from src.visualizer import Visualizer
from src.validators import RocketValidator, MotorValidator, EnvironmentValidator


def main():
    """Run a single flight simulation and generate outputs."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run a single rocket flight simulation")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/single_sim/01_minimal.yaml",
        help="Path to configuration YAML file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/basic_simulation",
        help="Directory for output files (plots, data)"
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip plot generation"
    )
    args = parser.parse_args()

    # Resolve paths
    config_path = project_root / args.config
    output_dir = project_root / args.output_dir

    print("=" * 70)
    print("ROCKET FLIGHT SIMULATION")
    print("=" * 70)

    # Step 1: Load Configuration
    print(f"\n[1/6] Loading configuration from {config_path.name}...")
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

    # Step 2: Validate Configuration
    print(f"\n[2/6] Validating configuration...")
    rocket_warnings = RocketValidator.validate(rocket_cfg)
    motor_warnings = MotorValidator.validate(motor_cfg)
    env_warnings = EnvironmentValidator.validate(env_cfg)

    all_warnings = rocket_warnings + motor_warnings + env_warnings
    if all_warnings:
        print(f"  Found {len(all_warnings)} validation warnings:")
        for w in all_warnings:
            print(f"    {w.level}: {w.message}")
    else:
        print("✓ No validation warnings")

    # Check for critical errors
    errors = [w for w in all_warnings if w.level == "ERROR"]
    if errors:
        print("\nCRITICAL ERRORS FOUND - Cannot proceed with simulation")
        sys.exit(1)

    # Step 3: Build Motor
    print(f"\n[3/6] Building motor...")
    motor_builder = MotorBuilder(motor_cfg)
    motor = motor_builder.build()
    print("✓ Motor built successfully")

    # Step 4: Build Environment
    print(f"\n[4/6] Building environment...")
    env_builder = EnvironmentBuilder(env_cfg)
    environment = env_builder.build()
    print(f"✓ Environment built: ({env_cfg.latitude_deg}°N, {env_cfg.longitude_deg}°E)")

    # Step 5: Build Rocket
    print(f"\n[5/6] Building rocket...")
    rocket_builder = RocketBuilder(rocket_cfg)
    rocket = rocket_builder.build(motor)

    # Check stability
    stability_info = rocket_builder.get_stability_info()
    static_margin = stability_info['static_margin_calibers']

    if static_margin >= 1.5:
        stability_status = "✓ STABLE"
    elif static_margin >= 1.0:
        stability_status = "⚠ MARGINALLY STABLE"
    else:
        stability_status = "✗ UNSTABLE"

    print(f"✓ Rocket built: {rocket_cfg.name}")
    print(f"  Static margin: {static_margin:.2f} calibers [{stability_status}]")

    # Step 6: Run Simulation
    print(f"\n[6/6] Running flight simulation...")
    simulator = FlightSimulator(
        rocket=rocket,
        motor=motor,
        environment=environment,
        rail_length_m=sim_cfg.rail_length_m,
        inclination_deg=sim_cfg.inclination_deg,
        heading_deg=sim_cfg.heading_deg
    )

    try:
        flight = simulator.run()
        print("✓ Simulation complete!")
    except Exception as e:
        print(f"✗ Simulation failed: {e}")
        sys.exit(1)

    # Extract and Print Results
    print("\n" + "=" * 70)
    print("FLIGHT RESULTS")
    print("=" * 70)

    summary = simulator.get_summary()

    print(f"\nApogee:")
    print(f"  Altitude:     {summary['apogee_m']:.1f} m ({summary['apogee_m']/0.3048:.1f} ft)")
    print(f"  Time:         {summary['apogee_time_s']:.1f} s")
    print(f"  Coordinates:  ({summary['apogee_lat']:.6f}°, {summary['apogee_lon']:.6f}°)")

    print(f"\nVelocity:")
    print(f"  Max velocity: {summary['max_velocity_ms']:.1f} m/s")
    print(f"  Max Mach:     {summary['max_mach_number']:.2f}")
    print(f"  Off-rail:     {summary['out_of_rail_velocity_ms']:.1f} m/s @ {summary['out_of_rail_time_s']:.2f} s")

    print(f"\nAcceleration:")
    print(f"  Max accel:    {summary['max_acceleration_ms2']:.1f} m/s² ({summary['max_acceleration_ms2']/9.81:.1f} g)")

    print(f"\nFlight Duration:")
    print(f"  Total time:   {summary['flight_time_s']:.1f} s")

    print(f"\nLanding:")
    print(f"  Distance:     {summary['lateral_distance_m']:.1f} m from launch")
    print(f"  Impact vel:   {summary['impact_velocity_ms']:.1f} m/s")

    # Generate Plots (if requested)
    if not args.no_plots:
        print(f"\n" + "=" * 70)
        print("GENERATING PLOTS")
        print("=" * 70)

        output_dir.mkdir(parents=True, exist_ok=True)

        visualizer = Visualizer(flight)

        plots = [
            ("trajectory_3d.png", "plot_trajectory_3d", "3D trajectory"),
            ("altitude_vs_time.png", "plot_altitude_vs_time", "Altitude vs time"),
            ("velocity_vs_time.png", "plot_velocity_vs_time", "Velocity vs time"),
        ]

        for filename, method_name, description in plots:
            plot_path = output_dir / filename
            print(f"  Creating {description}...")
            getattr(visualizer, method_name)(output_path=str(plot_path))

        print(f"\n✓ Plots saved to: {output_dir.absolute()}")

    # Summary
    print(f"\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print(f"Configuration:  {config_path}")
    print(f"Rocket:         {rocket_cfg.name}")
    print(f"Apogee:         {summary['apogee_m']:.1f} m")
    print(f"Max Mach:       {summary['max_mach_number']:.2f}")
    if not args.no_plots:
        print(f"Outputs:        {output_dir.absolute()}")
    print()


if __name__ == "__main__":
    main()
