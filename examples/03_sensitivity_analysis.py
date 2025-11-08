#!/usr/bin/env python3
"""
Variance-Based Sensitivity Analysis Example

This standalone script demonstrates:
- Loading Monte Carlo simulation results
- Performing variance-based sensitivity analysis
- Computing sensitivity coefficients and LAE
- Ranking parameters by importance
- Generating sensitivity bar plots
- Identifying critical design parameters

Usage:
    # First run Monte Carlo to generate data:
    python examples/02_monte_carlo_simple.py

    # Then run sensitivity analysis:
    python examples/03_sensitivity_analysis.py
    python examples/03_sensitivity_analysis.py --input-dir outputs/monte_carlo_example
"""

import argparse
from pathlib import Path
import sys
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.variance_sensitivity import VarianceBasedSensitivityAnalyzer
from src.sensitivity_utils import filter_significant_parameters


def main():
    """Run variance-based sensitivity analysis on Monte Carlo results."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Perform variance-based sensitivity analysis")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="outputs/monte_carlo_example",
        help="Directory containing Monte Carlo results"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/sensitivity_example",
        help="Directory for sensitivity plots and results"
    )
    parser.add_argument(
        "--target",
        type=str,
        default="apogee_m",
        help="Target variable for sensitivity analysis"
    )
    args = parser.parse_args()

    # Resolve paths
    input_dir = project_root / args.input_dir
    output_dir = project_root / args.output_dir

    print("=" * 70)
    print("VARIANCE-BASED SENSITIVITY ANALYSIS")
    print("=" * 70)

    # Step 1: Load Monte Carlo Data
    print(f"\n[1/4] Loading Monte Carlo results from {input_dir}...")

    input_file = input_dir / "mc_results_input_samples.csv"
    output_file = input_dir / "mc_results_outputs.csv"

    if not input_file.exists() or not output_file.exists():
        print(f"ERROR: Monte Carlo data files not found in {input_dir}")
        print(f"\nExpected files:")
        print(f"  - {input_file}")
        print(f"  - {output_file}")
        print(f"\nPlease run Monte Carlo simulation first:")
        print(f"  python examples/02_monte_carlo_simple.py")
        sys.exit(1)

    try:
        parameters_df = pd.read_csv(input_file)
        targets_df = pd.read_csv(output_file)
    except Exception as e:
        print(f"ERROR loading CSV files: {e}")
        sys.exit(1)

    print(f"✓ Data loaded:")
    print(f"  Samples:      {len(parameters_df)}")
    print(f"  Parameters:   {list(parameters_df.columns)}")
    print(f"  Targets:      {list(targets_df.columns)}")

    # Verify target exists
    if args.target not in targets_df.columns:
        print(f"\nERROR: Target '{args.target}' not found in output data")
        print(f"Available targets: {list(targets_df.columns)}")
        sys.exit(1)

    # Step 2: Setup Sensitivity Analyzer
    print(f"\n[2/4] Setting up variance-based analyzer...")

    analyzer = VarianceBasedSensitivityAnalyzer(
        parameter_names=list(parameters_df.columns),
        target_names=[args.target]
    )

    # Estimate nominal parameters from data
    means = parameters_df.mean().to_dict()
    stds = parameters_df.std().to_dict()

    analyzer.set_nominal_parameters(means=means, stds=stds)

    print(f"✓ Analyzer configured for target: {args.target}")
    print(f"  Nominal parameters:")
    for param in parameters_df.columns:
        print(f"    • {param}: μ={means[param]:.3f}, σ={stds[param]:.3f}")

    # Step 3: Fit Regression and Compute Sensitivity
    print(f"\n[3/4] Fitting linear regression model...")

    try:
        analyzer.fit(parameters_df, targets_df[[args.target]])
        print(f"✓ Regression model fitted")
    except Exception as e:
        print(f"ERROR during regression: {e}")
        sys.exit(1)

    # Get LAE (Linear Approximation Error)
    lae = analyzer.lae[args.target]
    print(f"  Linear Approximation Error (LAE): {lae:.2f}%")

    if lae < 10:
        lae_status = "✓ Excellent (< 10%)"
    elif lae < 30:
        lae_status = "~ Adequate (< 30%)"
    else:
        lae_status = "✗ Poor (> 30%) - Consider non-linear model"

    print(f"  Model quality: {lae_status}")

    # Step 4: Analyze and Rank Parameters
    print(f"\n[4/4] Computing sensitivity coefficients...")

    sensitivities = analyzer.sensitivity_coefficients[args.target]
    ranking = analyzer.get_importance_ranking(args.target)

    print("\n" + "=" * 70)
    print(f"SENSITIVITY RESULTS FOR {args.target.upper()}")
    print("=" * 70)

    print(f"\nParameter Importance Ranking:")
    print(f"{'Rank':<6} {'Parameter':<35} {'Sensitivity':<15} {'Status'}")
    print("-" * 70)

    for i, (param, sensitivity) in enumerate(ranking, 1):
        if sensitivity > lae:
            status = "✓ Significant"
        else:
            status = "  (< LAE)"
        print(f"{i:<6} {param:<35} {sensitivity:>6.2f}% {' '*7} {status}")

    # Identify significant parameters
    significant_params = filter_significant_parameters(sensitivities, lae)

    print(f"\nSignificant Parameters (sensitivity > LAE):")
    if significant_params:
        for param in significant_params:
            print(f"  ✓ {param}: {sensitivities[param]:.2f}%")
    else:
        print(f"  None (all parameters have sensitivity < LAE={lae:.2f}%)")

    # Total variance explained
    total_sensitivity = sum(sensitivities.values())
    print(f"\nVariance Decomposition:")
    print(f"  Explained by parameters: {total_sensitivity:.1f}%")
    print(f"  Residual (LAE):          {lae:.1f}%")
    print(f"  Total:                   {total_sensitivity + lae:.1f}%")

    # Generate Plots
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n" + "=" * 70)
    print("GENERATING PLOTS")
    print("=" * 70)

    plot_path = output_dir / f"sensitivity_bars_{args.target}.png"
    analyzer.plot_sensitivity_bars(
        output_path=str(plot_path),
        target_name=args.target,
        figsize=(10, 6)
    )
    print(f"✓ Sensitivity bar plot saved: {plot_path}")

    # Summary
    print(f"\n" + "=" * 70)
    print("SENSITIVITY ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Target variable:     {args.target}")
    print(f"Samples analyzed:    {len(parameters_df)}")
    print(f"LAE:                 {lae:.2f}%")
    print(f"Significant params:  {len(significant_params)}/{len(sensitivities)}")

    if significant_params:
        top_param = ranking[0][0]
        top_sensitivity = ranking[0][1]
        print(f"Most influential:    {top_param} ({top_sensitivity:.1f}%)")

    print(f"Output plots:        {output_dir.absolute()}")
    print()

    # Interpretation guide
    print("Interpretation:")
    print("  • Sensitivity % = contribution to output variance")
    print("  • If a parameter were known perfectly, output variance would")
    print("    decrease by its sensitivity percentage")
    print("  • Focus quality control on parameters with high sensitivity")
    print("  • Parameters with sensitivity < LAE may not be statistically significant")
    print()

    # Design recommendations
    if significant_params:
        print("Design Recommendations:")
        top_3 = ranking[:3]
        print(f"  Priority 1: Control {top_3[0][0]} (reduces variance by {top_3[0][1]:.1f}%)")
        if len(top_3) > 1:
            print(f"  Priority 2: Control {top_3[1][0]} (reduces variance by {top_3[1][1]:.1f}%)")
        if len(top_3) > 2:
            print(f"  Priority 3: Control {top_3[2][0]} (reduces variance by {top_3[2][1]:.1f}%)")
        print()


if __name__ == "__main__":
    main()
