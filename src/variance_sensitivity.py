"""
Variance-Based Sensitivity Analysis Module.

This module implements variance-based (first-order) sensitivity analysis using
multiple linear regression. It follows the methodology from RocketPy's official
sensitivity analysis framework.

Mathematical Background:
    The sensitivity coefficient S(j) represents the fractional contribution of
    parameter j to the total variance of the output:

    S(j) = 100 × (β_j² × σ_j²) / (σ_ε² + Σ_k(σ_k² × β_k²))

    where:
    - β_j is the regression coefficient for parameter j
    - σ_j is the standard deviation of parameter j
    - σ_ε is the residual standard error

    The Linear Approximation Error (LAE) quantifies how well the linear model
    approximates the true response:

    LAE = 100 × σ_ε² / (σ_ε² + Σ_k(σ_k² × β_k²))

    A low LAE (<10%) indicates the linear approximation is valid.

Reference:
    RocketPy Sensitivity Analysis Documentation
    https://docs.rocketpy.org/en/latest/user/sensitivity.html
"""

import logging
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

try:
    import statsmodels.api as sm
    from statsmodels.regression.linear_model import RegressionResultsWrapper
except ImportError:
    raise ImportError(
        "statsmodels is required for variance-based sensitivity analysis. "
        "Install it with: pip install statsmodels>=0.14.0"
    )

try:
    from prettytable import PrettyTable
except ImportError:
    raise ImportError(
        "prettytable is required for formatted output. "
        "Install it with: pip install prettytable>=3.9.0"
    )

logger = logging.getLogger(__name__)


class VarianceBasedSensitivityAnalyzer:
    """
    Variance-based sensitivity analyzer using multiple linear regression.

    This class performs first-order sensitivity analysis by fitting a linear
    regression model to Monte Carlo simulation data and calculating variance-based
    sensitivity coefficients.

    The analysis assumes a linear relationship between input parameters and output
    variables. The Linear Approximation Error (LAE) quantifies the validity of
    this assumption.

    Attributes:
        parameter_names: List of parameter names being analyzed
        target_names: List of target variable names (outputs)
        regression_models: Fitted regression models (one per target variable)
        sensitivity_coefficients: Dict mapping targets to sensitivity coefficients
        nominal_means: Nominal mean values for each parameter
        nominal_stds: Nominal standard deviations for each parameter
        lae: Linear Approximation Error for each target variable

    Example:
        >>> # After running Monte Carlo simulation
        >>> from monte_carlo_runner import MonteCarloRunner
        >>> mc_runner = MonteCarloRunner(...)
        >>> results = mc_runner.run()
        >>> params, targets = mc_runner.export_for_sensitivity()
        >>>
        >>> # Perform sensitivity analysis
        >>> analyzer = VarianceBasedSensitivityAnalyzer(
        ...     parameter_names=["rocket.dry_mass_kg", "motor.thrust_avg"],
        ...     target_names=["apogee_m"]
        ... )
        >>> analyzer.set_nominal_parameters(
        ...     means={"rocket.dry_mass_kg": 10.0, "motor.thrust_avg": 1500.0},
        ...     stds={"rocket.dry_mass_kg": 0.5, "motor.thrust_avg": 50.0}
        ... )
        >>> analyzer.fit(params, targets)
        >>> analyzer.print_summary()
        >>> analyzer.plot_sensitivity_bars("outputs/sensitivity_bars.png")
    """

    def __init__(
        self,
        parameter_names: List[str],
        target_names: List[str],
    ):
        """
        Initialize the variance-based sensitivity analyzer.

        Args:
            parameter_names: List of parameter names (e.g., ["rocket.dry_mass_kg"])
            target_names: List of target variable names (e.g., ["apogee_m"])

        Raises:
            ValueError: If parameter_names or target_names are empty
        """
        if not parameter_names:
            raise ValueError("parameter_names cannot be empty")
        if not target_names:
            raise ValueError("target_names cannot be empty")

        self.parameter_names = parameter_names
        self.target_names = target_names

        # Will be populated by set_nominal_parameters()
        self.nominal_means: Optional[Dict[str, float]] = None
        self.nominal_stds: Optional[Dict[str, float]] = None

        # Will be populated by fit()
        self.regression_models: Dict[str, RegressionResultsWrapper] = {}
        self.sensitivity_coefficients: Dict[str, Dict[str, float]] = {}
        self.lae: Dict[str, float] = {}

        # Store fitted data for prediction intervals
        self._parameters_data: Optional[pd.DataFrame] = None
        self._targets_data: Optional[pd.DataFrame] = None

        logger.info(
            f"Initialized VarianceBasedSensitivityAnalyzer with "
            f"{len(parameter_names)} parameters and {len(target_names)} targets"
        )

    def set_nominal_parameters(
        self,
        means: Dict[str, float],
        stds: Dict[str, float]
    ) -> None:
        """
        Set nominal mean and standard deviation for each parameter.

        These values are used to calculate sensitivity coefficients and
        interpret the effect of parameter variations.

        Args:
            means: Dictionary mapping parameter names to nominal mean values
            stds: Dictionary mapping parameter names to nominal std deviations

        Raises:
            ValueError: If means or stds don't match parameter_names
            ValueError: If any std is non-positive

        Example:
            >>> analyzer.set_nominal_parameters(
            ...     means={"rocket.dry_mass_kg": 10.0, "motor.thrust_avg": 1500.0},
            ...     stds={"rocket.dry_mass_kg": 0.5, "motor.thrust_avg": 50.0}
            ... )
        """
        # Validate that all parameters have nominal values
        missing_means = set(self.parameter_names) - set(means.keys())
        missing_stds = set(self.parameter_names) - set(stds.keys())

        if missing_means:
            raise ValueError(
                f"Missing nominal means for parameters: {missing_means}"
            )
        if missing_stds:
            raise ValueError(
                f"Missing nominal stds for parameters: {missing_stds}"
            )

        # Validate positive standard deviations
        for param, std in stds.items():
            if std <= 0:
                raise ValueError(
                    f"Standard deviation for '{param}' must be positive, got {std}"
                )

        self.nominal_means = means
        self.nominal_stds = stds

        logger.info(f"Set nominal parameters for {len(means)} parameters")

    def fit(
        self,
        parameters: Union[pd.DataFrame, np.ndarray],
        targets: Union[pd.DataFrame, np.ndarray]
    ) -> None:
        """
        Fit multiple linear regression models and calculate sensitivity coefficients.

        This method:
        1. Fits a linear regression model for each target variable
        2. Calculates variance-based sensitivity coefficients
        3. Computes Linear Approximation Error (LAE)
        4. Stores results for later analysis

        Args:
            parameters: Parameter matrix (N samples × P parameters)
            targets: Target variable matrix (N samples × T targets)

        Raises:
            ValueError: If nominal parameters haven't been set
            ValueError: If data dimensions don't match
            RuntimeError: If regression fitting fails

        Example:
            >>> analyzer.fit(parameters_matrix, targets_matrix)
        """
        if self.nominal_means is None or self.nominal_stds is None:
            raise ValueError(
                "Nominal parameters must be set before fitting. "
                "Call set_nominal_parameters() first."
            )

        # Convert to DataFrame if needed
        if isinstance(parameters, np.ndarray):
            parameters = pd.DataFrame(parameters, columns=self.parameter_names)
        if isinstance(targets, np.ndarray):
            targets = pd.DataFrame(targets, columns=self.target_names)

        # Validate dimensions
        if list(parameters.columns) != self.parameter_names:
            raise ValueError(
                f"Parameter columns {list(parameters.columns)} don't match "
                f"expected {self.parameter_names}"
            )
        if list(targets.columns) != self.target_names:
            raise ValueError(
                f"Target columns {list(targets.columns)} don't match "
                f"expected {self.target_names}"
            )
        if len(parameters) != len(targets):
            raise ValueError(
                f"Parameters ({len(parameters)} samples) and targets "
                f"({len(targets)} samples) must have same length"
            )

        n_samples = len(parameters)
        if n_samples < len(self.parameter_names) + 1:
            logger.warning(
                f"Only {n_samples} samples for {len(self.parameter_names)} parameters. "
                f"Consider using more samples for reliable regression."
            )

        self._parameters_data = parameters.copy()
        self._targets_data = targets.copy()

        logger.info(f"Fitting regression models on {n_samples} samples...")

        # Fit regression model for each target variable
        for target_name in self.target_names:
            logger.debug(f"Fitting model for target: {target_name}")

            # Prepare data
            X = parameters[self.parameter_names].values
            y = targets[target_name].values

            # Add constant term (intercept)
            X_with_const = sm.add_constant(X)

            # Fit OLS regression
            try:
                model = sm.OLS(y, X_with_const).fit()
                self.regression_models[target_name] = model

                logger.debug(
                    f"Model R²={model.rsquared:.4f}, "
                    f"Adjusted R²={model.rsquared_adj:.4f}"
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to fit regression model for '{target_name}': {e}"
                )

            # Calculate sensitivity coefficients
            self._calculate_sensitivity_coefficients(target_name, model)

            # Calculate LAE
            self._calculate_lae(target_name, model)

        logger.info("Regression fitting complete")

    def _calculate_sensitivity_coefficients(
        self,
        target_name: str,
        model: RegressionResultsWrapper
    ) -> None:
        """
        Calculate variance-based sensitivity coefficients for a target variable.

        The sensitivity coefficient S(j) represents the percentage contribution
        of parameter j to the total variance:

        S(j) = 100 × (β_j² × σ_j²) / (σ_ε² + Σ_k(σ_k² × β_k²))

        Args:
            target_name: Name of the target variable
            model: Fitted regression model
        """
        # Extract regression coefficients (excluding intercept)
        beta = model.params[1:]  # Skip intercept

        # Get residual standard error
        sigma_epsilon = np.sqrt(model.scale)  # model.scale = MSE

        # Calculate variance contributions from each parameter
        variance_contributions = {}
        total_explained_variance = 0.0

        for i, param_name in enumerate(self.parameter_names):
            sigma_j = self.nominal_stds[param_name]
            beta_j = beta[i]

            # Variance contribution: β_j² × σ_j²
            var_contrib = (beta_j ** 2) * (sigma_j ** 2)
            variance_contributions[param_name] = var_contrib
            total_explained_variance += var_contrib

        # Total variance = explained + residual
        total_variance = sigma_epsilon ** 2 + total_explained_variance

        # Calculate sensitivity coefficients as percentages
        sensitivities = {}
        for param_name in self.parameter_names:
            S_j = 100 * variance_contributions[param_name] / total_variance
            sensitivities[param_name] = S_j

        self.sensitivity_coefficients[target_name] = sensitivities

        logger.debug(
            f"Calculated sensitivity coefficients for '{target_name}': "
            f"{sensitivities}"
        )

    def _calculate_lae(
        self,
        target_name: str,
        model: RegressionResultsWrapper
    ) -> None:
        """
        Calculate Linear Approximation Error (LAE).

        LAE quantifies the percentage of variance that cannot be explained by
        the linear model:

        LAE = 100 × σ_ε² / (σ_ε² + Σ_k(σ_k² × β_k²))

        Low LAE (<10%) indicates the linear approximation is valid.
        High LAE (>50%) suggests significant non-linear effects.

        Args:
            target_name: Name of the target variable
            model: Fitted regression model
        """
        # Extract regression coefficients (excluding intercept)
        beta = model.params[1:]

        # Get residual standard error
        sigma_epsilon = np.sqrt(model.scale)

        # Calculate total explained variance
        total_explained_variance = 0.0
        for i, param_name in enumerate(self.parameter_names):
            sigma_j = self.nominal_stds[param_name]
            beta_j = beta[i]
            total_explained_variance += (beta_j ** 2) * (sigma_j ** 2)

        # Total variance
        total_variance = sigma_epsilon ** 2 + total_explained_variance

        # LAE as percentage
        lae = 100 * (sigma_epsilon ** 2) / total_variance

        self.lae[target_name] = lae

        if lae < 10:
            logger.info(f"LAE for '{target_name}': {lae:.2f}% (excellent)")
        elif lae < 30:
            logger.info(f"LAE for '{target_name}': {lae:.2f}% (good)")
        else:
            logger.warning(
                f"LAE for '{target_name}': {lae:.2f}% (high - "
                f"linear approximation may not be adequate)"
            )

    def get_sensitivity_summary(
        self,
        target_name: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Get sensitivity analysis summary.

        Args:
            target_name: Specific target to get summary for, or None for all targets

        Returns:
            Dictionary mapping target names to sensitivity information:
            {
                "target_name": {
                    "parameter_name": sensitivity_coefficient,
                    ...
                    "LAE": lae_value
                }
            }

        Raises:
            RuntimeError: If fit() hasn't been called yet

        Example:
            >>> summary = analyzer.get_sensitivity_summary()
            >>> print(summary["apogee_m"]["rocket.dry_mass_kg"])
            71.2  # 71.2% variance contribution
        """
        if not self.regression_models:
            raise RuntimeError("No models fitted. Call fit() first.")

        targets_to_summarize = (
            [target_name] if target_name else self.target_names
        )

        summary = {}
        for target in targets_to_summarize:
            target_summary = self.sensitivity_coefficients[target].copy()
            target_summary["LAE"] = self.lae[target]
            summary[target] = target_summary

        return summary

    def get_importance_ranking(
        self,
        target_name: str
    ) -> List[Tuple[str, float]]:
        """
        Get parameters ranked by sensitivity (highest to lowest).

        Args:
            target_name: Target variable to rank parameters for

        Returns:
            List of (parameter_name, sensitivity_coefficient) tuples,
            sorted by sensitivity in descending order

        Example:
            >>> ranking = analyzer.get_importance_ranking("apogee_m")
            >>> for param, sensitivity in ranking[:3]:
            ...     print(f"{param}: {sensitivity:.1f}%")
            rocket.dry_mass_kg: 71.2%
            motor.thrust_avg: 15.3%
            environment.wind.velocity_ms: 8.1%
        """
        if target_name not in self.sensitivity_coefficients:
            raise ValueError(f"Unknown target: {target_name}")

        sensitivities = self.sensitivity_coefficients[target_name]

        # Sort by sensitivity (descending)
        ranking = sorted(
            sensitivities.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return ranking

    def get_prediction_intervals(
        self,
        target_name: str,
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Get prediction interval for a target variable.

        Args:
            target_name: Target variable name
            confidence: Confidence level (default: 0.95 for 95% interval)

        Returns:
            Tuple of (mean_prediction, lower_bound, upper_bound)

        Example:
            >>> mean, lower, upper = analyzer.get_prediction_intervals("apogee_m")
            >>> print(f"95% Prediction Interval: [{lower:.1f}, {upper:.1f}]")
            95% Prediction Interval: [2951.3, 3410.7]
        """
        if target_name not in self.regression_models:
            raise ValueError(f"Unknown target: {target_name}")

        model = self.regression_models[target_name]

        # Get predictions for the fitted data
        X = self._parameters_data[self.parameter_names].values
        X_with_const = sm.add_constant(X)

        predictions = model.get_prediction(X_with_const)
        prediction_summary = predictions.summary_frame(alpha=1 - confidence)

        # Calculate mean prediction and interval
        mean_pred = prediction_summary['mean'].mean()
        lower_bound = prediction_summary['obs_ci_lower'].min()
        upper_bound = prediction_summary['obs_ci_upper'].max()

        return mean_pred, lower_bound, upper_bound

    def print_summary(self, target_name: Optional[str] = None) -> None:
        """
        Print formatted sensitivity analysis summary using PrettyTable.

        Args:
            target_name: Specific target to print, or None for all targets

        Example:
            >>> analyzer.print_summary("apogee_m")

            Sensitivity Analysis Summary: apogee_m
            +-------------------------+----------------+---------------+-------------+
            | Parameter               | Sensitivity(%) | Nominal mean  | Nominal sd  |
            +-------------------------+----------------+---------------+-------------+
            | rocket.dry_mass_kg      |          71.20 |        10.000 |       0.500 |
            | motor.thrust_avg        |          15.30 |      1500.000 |      50.000 |
            | environment.wind.vel_ms |           8.10 |         5.000 |       2.000 |
            +-------------------------+----------------+---------------+-------------+
            | Linear Approx Error (LAE)|           5.40 |               |             |
            +-------------------------+----------------+---------------+-------------+
        """
        if not self.regression_models:
            raise RuntimeError("No models fitted. Call fit() first.")

        targets_to_print = (
            [target_name] if target_name else self.target_names
        )

        for target in targets_to_print:
            print(f"\nSensitivity Analysis Summary: {target}")
            print("=" * 80)

            # Create table
            table = PrettyTable()
            table.field_names = [
                "Parameter",
                "Sensitivity(%)",
                "Nominal mean",
                "Nominal sd",
                "Effect per sd"
            ]
            table.align["Parameter"] = "l"
            table.align["Sensitivity(%)"] = "r"
            table.align["Nominal mean"] = "r"
            table.align["Nominal sd"] = "r"
            table.align["Effect per sd"] = "r"

            # Get ranking
            ranking = self.get_importance_ranking(target)

            # Get regression model for effect calculation
            model = self.regression_models[target]
            beta = model.params[1:]  # Exclude intercept

            # Add rows for each parameter
            for param_name, sensitivity in ranking:
                nominal_mean = self.nominal_means[param_name]
                nominal_sd = self.nominal_stds[param_name]

                # Effect per standard deviation: β_j × σ_j
                param_idx = self.parameter_names.index(param_name)
                effect_per_sd = beta[param_idx] * nominal_sd

                table.add_row([
                    param_name,
                    f"{sensitivity:.2f}",
                    f"{nominal_mean:.3f}",
                    f"{nominal_sd:.3f}",
                    f"{effect_per_sd:.2f}"
                ])

            # Add LAE row
            table.add_row([
                "Linear Approx. Error (LAE)",
                f"{self.lae[target]:.2f}",
                "",
                "",
                ""
            ])

            print(table)

            # Print prediction interval
            mean_pred, lower, upper = self.get_prediction_intervals(target)
            print(f"\nEstimated mean value: {mean_pred:.2f}")
            print(f"95% Prediction Interval: [{lower:.2f}, {upper:.2f}]")

            # Interpretation guidelines
            lae_value = self.lae[target]
            print("\nInterpretation Guidelines:")
            if lae_value < 10:
                print("✓ LAE < 10%: Linear approximation is excellent")
            elif lae_value < 30:
                print("~ LAE < 30%: Linear approximation is adequate")
            else:
                print("✗ LAE > 30%: Linear approximation may not be valid")
                print("  Consider non-linear effects or interactions")

            print("\nSensitivity Interpretation:")
            print("- S(j) = X% means: if parameter j were known perfectly,")
            print("  the output variance would decrease by X%")

    def plot_sensitivity_bars(
        self,
        output_path: Optional[str] = None,
        target_name: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = 300
    ) -> Figure:
        """
        Create bar plot of sensitivity coefficients, sorted by importance.

        Args:
            output_path: Path to save figure (optional)
            target_name: Specific target to plot, or None for first target
            figsize: Figure size in inches (width, height)
            dpi: Resolution in dots per inch

        Returns:
            matplotlib Figure object

        Example:
            >>> fig = analyzer.plot_sensitivity_bars("outputs/sensitivity.png")
        """
        if not self.regression_models:
            raise RuntimeError("No models fitted. Call fit() first.")

        # Default to first target if not specified
        target = target_name if target_name else self.target_names[0]

        # Get ranking
        ranking = self.get_importance_ranking(target)

        # Prepare data
        param_names = [param for param, _ in ranking]
        sensitivities = [sens for _, sens in ranking]

        # Create figure
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

        # Create bar plot
        y_pos = np.arange(len(param_names))
        bars = ax.barh(y_pos, sensitivities, align='center', alpha=0.8)

        # Color bars by sensitivity magnitude
        for i, (bar, sens) in enumerate(zip(bars, sensitivities)):
            if sens > 50:
                bar.set_color('#d62728')  # Red - very high
            elif sens > 20:
                bar.set_color('#ff7f0e')  # Orange - high
            elif sens > 10:
                bar.set_color('#2ca02c')  # Green - moderate
            else:
                bar.set_color('#1f77b4')  # Blue - low

        # Add LAE reference line
        lae_value = self.lae[target]
        ax.axvline(lae_value, color='gray', linestyle='--', linewidth=2,
                   label=f'LAE = {lae_value:.1f}%', alpha=0.7)

        # Formatting
        ax.set_yticks(y_pos)
        ax.set_yticklabels(param_names)
        ax.invert_yaxis()  # Highest sensitivity at top
        ax.set_xlabel('Sensitivity Coefficient (%)', fontsize=12)
        ax.set_title(
            f'Variance-Based Sensitivity Analysis: {target}',
            fontsize=14,
            fontweight='bold'
        )
        ax.legend()
        ax.grid(axis='x', alpha=0.3)

        # Add value labels on bars
        for i, (y, sens) in enumerate(zip(y_pos, sensitivities)):
            ax.text(
                sens + 1,
                y,
                f'{sens:.1f}%',
                va='center',
                fontsize=10
            )

        plt.tight_layout()

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
            logger.info(f"Saved sensitivity bar plot to {output_path}")

        return fig
