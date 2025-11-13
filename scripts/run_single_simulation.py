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
from dataclasses import asdict
import signal
from datetime import datetime

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
from src.state_exporter import StateExporter
from src.curve_plotter import CurvePlotter
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
        help="Log file path (default: auto-generated in outputs/<name>/simulation.log)",
    )

    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=300,
        help="Simulation timeout in seconds (default: 300). Set to 0 to disable timeout.",
    )

    return parser.parse_args()


def main():
    """Main execution function."""
    # Parse arguments
    args = parse_arguments()

    # Determine output name early for log file
    output_name = None
    sim_output_dir = None
    
    # Setup logging with auto-generated log file if not specified
    log_level = "DEBUG" if args.verbose else "INFO"
    
    # Setup without file logging initially (will be configured after loading config)
    setup_logging(level=log_level, log_file=None)

    logger = logging.getLogger(__name__)

    logger.info("=" * 60)
    logger.info("ROCKET FLIGHT SIMULATION")
    logger.info("=" * 60)
    logger.info(f"Configuration file: {args.config}")
    logger.info(f"Output directory: {args.output_dir}")
    if args.timeout > 0:
        logger.info(f"Simulation timeout: {args.timeout}s")

    # Flag to track if simulation timed out
    simulation_timed_out = False
    flight = None

    try:
        # 1. Load configurations
        logger.info("\n--- LOADING CONFIGURATION ---")
        loader = ConfigLoader()
        rocket_cfg, motor_cfg, env_cfg, sim_cfg = loader.load_complete_config(
            args.config
        )
        logger.info(f"Loaded configuration for rocket: {rocket_cfg.name}")

        # Now we know the rocket name, setup log file if not provided
        output_name = args.name if args.name else rocket_cfg.name.replace(" ", "_").lower()
        sim_output_dir = Path(args.output_dir) / output_name
        sim_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup log file in the simulation output directory
        if args.log_file:
            # If user provided a log file name, place it in the output directory
            log_file = sim_output_dir / args.log_file
        else:
            # Auto-generate log file name with timestamp
            log_file = sim_output_dir / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Re-setup logging with file
        setup_logging(level=log_level, log_file=str(log_file))
        logger = logging.getLogger(__name__)  # Refresh logger
        logger.info(f"Log file: {log_file}")

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
        rocket_builder = RocketBuilder(rocket_cfg, motor=motor, motor_config=motor_cfg)
        rocket = rocket_builder.build()
        rocket_summary = rocket_builder.get_summary()
        logger.info(
            f"Rocket: {rocket_summary['name']}, "
            f"mass={rocket_summary['total_mass_kg']:.1f} kg, "
            f"static margin={rocket_summary['static_margin_calibers']:.2f} cal"
        )

        # Check for unstable rocket
        if rocket_summary['static_margin_calibers'] < 0:
            logger.warning("⚠️  UNSTABLE ROCKET DETECTED!")
            logger.warning(f"   Static margin = {rocket_summary['static_margin_calibers']:.2f} cal (negative = unstable)")
            logger.warning("   The simulation may be slow or fail to converge.")
            logger.warning(f"   Timeout is set to {args.timeout}s - partial results will be saved if timeout occurs.")

        # 4. Run simulation with timeout
        logger.info("\n--- RUNNING SIMULATION ---")
        simulator = FlightSimulator(rocket, env, sim_cfg)
        
        # Setup timeout handler if timeout is enabled
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Simulation exceeded timeout of {args.timeout} seconds")
        
        if args.timeout > 0:
            # Set alarm for timeout
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(args.timeout)
        
        try:
            flight = simulator.run()
            
            # Cancel alarm if simulation completed
            if args.timeout > 0:
                signal.alarm(0)
                
        except TimeoutError as e:
            logger.error(f"\n⏱️  SIMULATION TIMEOUT: {e}")
            logger.warning("Simulation did not complete within the time limit.")
            logger.warning("This usually indicates an unstable rocket (negative static margin).")
            logger.warning("Attempting to save partial results...")
            simulation_timed_out = True
            
            # Cancel alarm
            if args.timeout > 0:
                signal.alarm(0)
        
        except RuntimeError as e:
            # FlightSimulator may wrap TimeoutError in RuntimeError
            if "timeout" in str(e).lower():
                logger.error(f"\n⏱️  SIMULATION TIMEOUT: {e}")
                logger.warning("Simulation did not complete within the time limit.")
                logger.warning("This usually indicates an unstable rocket (negative static margin).")
                logger.warning("Attempting to save partial results...")
                simulation_timed_out = True
                
                # Cancel alarm
                if args.timeout > 0:
                    signal.alarm(0)
            else:
                # Re-raise if it's not a timeout error
                raise

        # 5. Print summary (if simulation completed)
        if not simulation_timed_out and flight:
            logger.info("\n--- SIMULATION RESULTS ---")
            simulator.print_summary()
        else:
            logger.warning("\n--- PARTIAL RESULTS (TIMEOUT) ---")
            logger.warning("Simulation did not complete successfully.")
            logger.warning("State data (motor, rocket, environment) will still be exported.")

        # 6. Export state (initial and final) - ALWAYS export, even on timeout
        if not args.no_export:
            logger.info("\n--- EXPORTING STATE (JSON + TXT) ---")
            
            # Create state exporter
            state_exporter = StateExporter(
                motor=motor,
                rocket=rocket,
                environment=env,
                sim_config=asdict(sim_cfg)
            )
            
            # Export initial state
            initial_json = state_exporter.export_initial_state(sim_output_dir / "initial_state")
            logger.info(f"Initial state: {initial_json}")
            logger.info(f"Initial state (readable): {initial_json.with_name('initial_state_READABLE.txt')}")
            
            # Export final state only if simulation completed
            if not simulation_timed_out and flight:
                final_json = state_exporter.export_final_state(flight, sim_output_dir / "final_state")
                logger.info(f"Final state: {final_json}")
                logger.info(f"Final state (readable): {final_json.with_name('final_state_READABLE.txt')}")
            else:
                logger.warning("Final state export skipped (simulation timed out)")

        # 7. Generate curve plots (motor/rocket/environment) - ALWAYS plot, even on timeout
        if not args.no_plots:
            logger.info("\n--- GENERATING CURVE PLOTS ---")
            
            # Extract max_mach from flight if available
            max_mach = 2.0  # default
            if flight:
                try:
                    max_mach = float(flight.max_mach_number)
                    logger.info(f"Using max Mach from flight: {max_mach:.3f}")
                except Exception as e:
                    logger.warning(f"Could not get max_mach_number from flight: {e}, using default 2.0")
            
            # Create curve plotter with flight data
            curve_plotter = CurvePlotter(motor, rocket, env, max_mach=max_mach, flight=flight)
            
            # Plot all curves (organized in motor/, rocket/, environment/ subdirectories)
            curves_dir = sim_output_dir / "curves"
            plot_paths = curve_plotter.plot_all_curves(curves_dir)
            
            logger.info(f"Generated {len(plot_paths)} curve plots:")
            for plot_name, plot_path in sorted(plot_paths.items()):
                logger.info(f"  {plot_name}: {plot_path}")

        # 8. Export trajectory data (only if simulation completed)
        if not args.no_export and not simulation_timed_out and flight:
            logger.info("\n--- EXPORTING TRAJECTORY DATA ---")

            # Create data handler
            data_handler = DataHandler(output_dir=str(sim_output_dir / "data"))

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
        elif simulation_timed_out:
            logger.warning("Trajectory data export skipped (simulation timed out)")

        # 9. Create trajectory plots (only if simulation completed)
        if not args.no_plots and not simulation_timed_out and flight:
            logger.info("\n--- CREATING TRAJECTORY PLOTS ---")

            try:
                # Create visualizer
                visualizer = Visualizer(output_dir=str(sim_output_dir / "plots" / "trajectory"))

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
        elif simulation_timed_out:
            logger.warning("Trajectory plots skipped (simulation timed out)")

        # 10. Success/Partial success message
        logger.info("\n" + "=" * 60)
        if simulation_timed_out:
            logger.warning("SIMULATION TIMED OUT - PARTIAL RESULTS SAVED")
            logger.warning("=" * 60)
            logger.warning(f"\nPartial results saved to: {sim_output_dir}/")
            logger.warning("\nAvailable outputs:")
            logger.warning(f"  {sim_output_dir}/")
            logger.warning("    ├── simulation_YYYYMMDD_HHMMSS.log (this log file)")
            logger.warning("    ├── initial_state.json / .txt")
            logger.warning("    └── plots/")
            logger.warning("        ├── motor/       (11 motor performance plots)")
            logger.warning("        ├── rocket/      (12-15 rocket characteristic plots)")
            logger.warning("        ├── stability/   (7+ stability analysis plots)")
            logger.warning("        └── environment/ (2 atmospheric/wind plots)")
            logger.warning("\n⚠️  Missing outputs (simulation did not complete):")
            logger.warning("    ├── final_state.json / .txt")
            logger.warning("    ├── data/ (CSV trajectory data)")
            logger.warning("    └── plots/trajectory/ (5 trajectory visualization plots)")
            logger.warning("\n💡 Suggestions:")
            logger.warning("   - Check static margin (should be positive, typically 1.5-2.5 calibers)")
            logger.warning("   - Add more fins or adjust fin position if margin is negative")
            logger.warning("   - Increase timeout with --timeout <seconds> if rocket is stable")
            return 2  # Exit code 2 for timeout
        else:
            logger.info("SIMULATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"\nResults saved to: {sim_output_dir}/")
            logger.info("\nOutput structure:")
            logger.info(f"  {sim_output_dir}/")
            logger.info("    ├── simulation_YYYYMMDD_HHMMSS.log (this log file)")
            logger.info("    ├── initial_state.json / .txt")
            logger.info("    ├── final_state.json / .txt")
            logger.info("    ├── plots/")
            logger.info("    │   ├── motor/       (11 motor performance plots)")
            logger.info("    │   ├── rocket/      (12-15 rocket characteristic plots)")
            logger.info("    │   ├── stability/   (6 essential stability plots + report)")
            logger.info("    │   ├── trajectory/  (5 trajectory visualization plots)")
            logger.info("    │   └── environment/ (2 atmospheric/wind plots)")
            logger.info("    └── data/")
            logger.info("        └── *.csv        (time series trajectory data)")
            return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1

    except Exception as e:
        logger.error(f"Simulation failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
