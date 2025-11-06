"""
Sensitivity Analysis Utility Functions.

This module provides utility functions for loading, processing, and analyzing
Monte Carlo simulation data for sensitivity analysis.

Functions support the RocketPy standard file formats (.inputs.txt, .outputs.txt)
and provide helper methods for data manipulation and validation.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def load_monte_carlo_data(
    input_file: Union[str, Path],
    output_file: Union[str, Path],
    parameter_names: Optional[List[str]] = None,
    target_names: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load Monte Carlo simulation data from RocketPy standard format files.

    RocketPy exports Monte Carlo results in two text files:
    - .inputs.txt: Parameter values for each simulation
    - .outputs.txt: Output values for each simulation

    Args:
        input_file: Path to .inputs.txt file
        output_file: Path to .outputs.txt file
        parameter_names: List of parameter names to load (None = all)
        target_names: List of target variable names to load (None = all)

    Returns:
        Tuple of (parameters_df, targets_df)
        - parameters_df: DataFrame with shape (N samples, P parameters)
        - targets_df: DataFrame with shape (N samples, T targets)

    Raises:
        FileNotFoundError: If input or output files don't exist
        ValueError: If files have mismatched sample counts
        ValueError: If requested columns don't exist

    Example:
        >>> params, targets = load_monte_carlo_data(
        ...     "outputs/mc_results.inputs.txt",
        ...     "outputs/mc_results.outputs.txt",
        ...     parameter_names=["rocket.dry_mass_kg", "motor.thrust_avg"],
        ...     target_names=["apogee_m"]
        ... )
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    # Check files exist
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not output_path.exists():
        raise FileNotFoundError(f"Output file not found: {output_path}")

    logger.info(f"Loading Monte Carlo data from {input_path.parent}")

    # Load input parameters
    try:
        parameters_df = pd.read_csv(input_path, sep=r'\s+')
        logger.debug(f"Loaded {len(parameters_df)} parameter samples")
    except Exception as e:
        raise ValueError(f"Failed to load input file: {e}")

    # Load output targets
    try:
        targets_df = pd.read_csv(output_path, sep=r'\s+')
        logger.debug(f"Loaded {len(targets_df)} target samples")
    except Exception as e:
        raise ValueError(f"Failed to load output file: {e}")

    # Validate sample counts match
    if len(parameters_df) != len(targets_df):
        raise ValueError(
            f"Sample count mismatch: {len(parameters_df)} parameters vs "
            f"{len(targets_df)} targets"
        )

    # Filter columns if requested
    if parameter_names is not None:
        missing_params = set(parameter_names) - set(parameters_df.columns)
        if missing_params:
            raise ValueError(
                f"Parameters not found in input file: {missing_params}"
            )
        parameters_df = parameters_df[parameter_names]

    if target_names is not None:
        missing_targets = set(target_names) - set(targets_df.columns)
        if missing_targets:
            raise ValueError(
                f"Targets not found in output file: {missing_targets}"
            )
        targets_df = targets_df[target_names]

    logger.info(
        f"Loaded {len(parameters_df)} samples with "
        f"{len(parameters_df.columns)} parameters and "
        f"{len(targets_df.columns)} targets"
    )

    return parameters_df, targets_df


def save_monte_carlo_data(
    parameters_df: pd.DataFrame,
    targets_df: pd.DataFrame,
    output_dir: Union[str, Path],
    filename_prefix: str = "monte_carlo"
) -> Tuple[Path, Path]:
    """
    Save Monte Carlo data in RocketPy standard format.

    Creates two files:
    - {prefix}.inputs.txt: Parameter values
    - {prefix}.outputs.txt: Target values

    Args:
        parameters_df: DataFrame with parameter values (N × P)
        targets_df: DataFrame with target values (N × T)
        output_dir: Directory to save files
        filename_prefix: Prefix for output filenames

    Returns:
        Tuple of (input_file_path, output_file_path)

    Example:
        >>> input_path, output_path = save_monte_carlo_data(
        ...     params_df, targets_df,
        ...     output_dir="outputs/",
        ...     filename_prefix="sensitivity_data"
        ... )
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_file = output_path / f"{filename_prefix}.inputs.txt"
    output_file = output_path / f"{filename_prefix}.outputs.txt"

    # Save with space-separated format
    parameters_df.to_csv(input_file, sep=' ', index=False)
    targets_df.to_csv(output_file, sep=' ', index=False)

    logger.info(f"Saved Monte Carlo data to {output_path}")
    logger.debug(f"  - {input_file.name} ({len(parameters_df)} samples)")
    logger.debug(f"  - {output_file.name} ({len(targets_df)} samples)")

    return input_file, output_file


def calculate_jacobian(
    regression_models: Dict[str, any],
    parameter_names: List[str]
) -> np.ndarray:
    """
    Extract Jacobian matrix from fitted regression models.

    The Jacobian J[i,j] represents ∂(target_i) / ∂(parameter_j),
    estimated from the regression coefficients.

    Args:
        regression_models: Dict mapping target names to fitted models
        parameter_names: List of parameter names in order

    Returns:
        Jacobian matrix with shape (n_targets, n_parameters)

    Example:
        >>> jacobian = calculate_jacobian(
        ...     analyzer.regression_models,
        ...     analyzer.parameter_names
        ... )
        >>> print(f"d(apogee)/d(mass) = {jacobian[0, 0]:.2f}")
    """
    target_names = list(regression_models.keys())
    n_targets = len(target_names)
    n_params = len(parameter_names)

    jacobian = np.zeros((n_targets, n_params))

    for i, target_name in enumerate(target_names):
        model = regression_models[target_name]
        # Extract coefficients (skip intercept at index 0)
        beta = model.params[1:]
        jacobian[i, :] = beta

    return jacobian


def validate_linear_approximation(
    lae: float,
    threshold_excellent: float = 10.0,
    threshold_adequate: float = 30.0
) -> Tuple[str, str]:
    """
    Validate the linear approximation based on LAE value.

    Args:
        lae: Linear Approximation Error (percentage)
        threshold_excellent: LAE threshold for excellent approximation
        threshold_adequate: LAE threshold for adequate approximation

    Returns:
        Tuple of (status, message)
        - status: "excellent", "adequate", or "poor"
        - message: Human-readable interpretation

    Example:
        >>> status, msg = validate_linear_approximation(5.2)
        >>> print(status)
        excellent
        >>> print(msg)
        Linear approximation is excellent (LAE = 5.2% < 10%)
    """
    if lae < threshold_excellent:
        status = "excellent"
        message = (
            f"Linear approximation is excellent "
            f"(LAE = {lae:.1f}% < {threshold_excellent}%)"
        )
    elif lae < threshold_adequate:
        status = "adequate"
        message = (
            f"Linear approximation is adequate "
            f"(LAE = {lae:.1f}% < {threshold_adequate}%)"
        )
    else:
        status = "poor"
        message = (
            f"Linear approximation may not be valid "
            f"(LAE = {lae:.1f}% > {threshold_adequate}%). "
            f"Consider non-linear effects or parameter interactions."
        )

    return status, message


def estimate_parameter_statistics(
    data: pd.DataFrame
) -> Dict[str, Dict[str, float]]:
    """
    Estimate mean and standard deviation for each parameter from data.

    Useful for setting nominal parameters when they're not known a priori.

    Args:
        data: DataFrame with parameters as columns

    Returns:
        Dictionary mapping parameter names to {"mean": ..., "std": ...}

    Example:
        >>> stats = estimate_parameter_statistics(parameters_df)
        >>> print(stats["rocket.dry_mass_kg"])
        {'mean': 10.05, 'std': 0.48}
    """
    stats = {}

    for column in data.columns:
        stats[column] = {
            "mean": float(data[column].mean()),
            "std": float(data[column].std())
        }

    return stats


def filter_significant_parameters(
    sensitivity_coefficients: Dict[str, float],
    lae: float,
    significance_threshold: Optional[float] = None
) -> List[str]:
    """
    Filter parameters that have significant sensitivity.

    A parameter is considered significant if its sensitivity coefficient
    is greater than the LAE (or a custom threshold).

    Args:
        sensitivity_coefficients: Dict mapping parameter names to sensitivities
        lae: Linear Approximation Error
        significance_threshold: Custom threshold (default: use LAE)

    Returns:
        List of significant parameter names, sorted by sensitivity

    Example:
        >>> significant = filter_significant_parameters(
        ...     sensitivities, lae=5.2
        ... )
        >>> print(f"Focus on these {len(significant)} parameters: {significant}")
    """
    threshold = significance_threshold if significance_threshold else lae

    significant_params = [
        param for param, sens in sensitivity_coefficients.items()
        if sens > threshold
    ]

    # Sort by sensitivity (descending)
    significant_params.sort(
        key=lambda p: sensitivity_coefficients[p],
        reverse=True
    )

    logger.info(
        f"Found {len(significant_params)} significant parameters "
        f"(sensitivity > {threshold:.1f}%)"
    )

    return significant_params


def create_sensitivity_comparison(
    oat_sensitivities: Dict[str, float],
    variance_sensitivities: Dict[str, float]
) -> pd.DataFrame:
    """
    Create comparison table between OAT and variance-based sensitivities.

    Useful for understanding differences between the two methods.

    Args:
        oat_sensitivities: Dict of OAT sensitivity indices
        variance_sensitivities: Dict of variance-based sensitivity coefficients

    Returns:
        DataFrame with columns: Parameter, OAT_Index, Variance_Coeff, Rank_OAT, Rank_Variance

    Example:
        >>> comparison = create_sensitivity_comparison(
        ...     oat_analyzer.sensitivity_data["apogee_m"],
        ...     variance_analyzer.sensitivity_coefficients["apogee_m"]
        ... )
        >>> print(comparison)
    """
    # Get common parameters
    common_params = set(oat_sensitivities.keys()) & set(variance_sensitivities.keys())

    data = []
    for param in common_params:
        data.append({
            "Parameter": param,
            "OAT_Index": oat_sensitivities[param],
            "Variance_Coeff(%)": variance_sensitivities[param]
        })

    df = pd.DataFrame(data)

    # Add rankings
    df["Rank_OAT"] = df["OAT_Index"].rank(ascending=False, method='min').astype(int)
    df["Rank_Variance"] = df["Variance_Coeff(%)"].rank(ascending=False, method='min').astype(int)

    # Sort by variance-based ranking
    df = df.sort_values("Rank_Variance")

    return df


def calculate_variance_reduction(
    sensitivity_coefficients: Dict[str, float],
    parameters_to_control: List[str]
) -> float:
    """
    Calculate potential variance reduction from controlling specific parameters.

    If you could measure/control certain parameters perfectly (eliminating
    their uncertainty), this calculates the resulting variance reduction.

    Args:
        sensitivity_coefficients: Dict of variance-based sensitivities (%)
        parameters_to_control: List of parameter names to control

    Returns:
        Total variance reduction percentage

    Example:
        >>> # How much variance reduction if we control mass and thrust?
        >>> reduction = calculate_variance_reduction(
        ...     sensitivities,
        ...     ["rocket.dry_mass_kg", "motor.thrust_avg"]
        ... )
        >>> print(f"Controlling these parameters reduces variance by {reduction:.1f}%")
    """
    total_reduction = 0.0

    for param in parameters_to_control:
        if param in sensitivity_coefficients:
            total_reduction += sensitivity_coefficients[param]

    return total_reduction


def export_sensitivity_to_json(
    sensitivity_coefficients: Dict[str, Dict[str, float]],
    lae: Dict[str, float],
    nominal_parameters: Dict[str, Dict[str, float]],
    output_file: Union[str, Path]
) -> None:
    """
    Export sensitivity analysis results to JSON format.

    Args:
        sensitivity_coefficients: Sensitivities for all targets
        lae: LAE values for all targets
        nominal_parameters: Nominal means and stds
        output_file: Path to output JSON file

    Example:
        >>> export_sensitivity_to_json(
        ...     analyzer.sensitivity_coefficients,
        ...     analyzer.lae,
        ...     {"rocket.dry_mass_kg": {"mean": 10.0, "std": 0.5}},
        ...     "outputs/sensitivity_results.json"
        ... )
    """
    import json

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "sensitivity_coefficients": sensitivity_coefficients,
        "linear_approximation_error": lae,
        "nominal_parameters": nominal_parameters
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Exported sensitivity results to {output_path}")


def load_sensitivity_from_json(
    input_file: Union[str, Path]
) -> Dict:
    """
    Load previously exported sensitivity analysis results from JSON.

    Args:
        input_file: Path to JSON file

    Returns:
        Dictionary with sensitivity results

    Example:
        >>> results = load_sensitivity_from_json("outputs/sensitivity_results.json")
        >>> print(results["sensitivity_coefficients"]["apogee_m"])
    """
    import json

    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    with open(input_path, 'r') as f:
        results = json.load(f)

    logger.info(f"Loaded sensitivity results from {input_path}")

    return results
