"""
Tests for variance-based sensitivity analysis.

This module tests the VarianceBasedSensitivityAnalyzer class and related
utility functions.
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from src.variance_sensitivity import VarianceBasedSensitivityAnalyzer
from src.sensitivity_utils import (
    load_monte_carlo_data,
    save_monte_carlo_data,
    calculate_jacobian,
    validate_linear_approximation,
    estimate_parameter_statistics,
    filter_significant_parameters
)


@pytest.fixture
def sample_monte_carlo_data():
    """Create sample Monte Carlo data for testing."""
    np.random.seed(42)
    n_samples = 100

    # Create correlated parameters
    param1 = np.random.normal(10.0, 0.5, n_samples)  # rocket mass
    param2 = np.random.normal(1500.0, 50.0, n_samples)  # motor thrust

    # Create target that depends on parameters
    # apogee ≈ -100*mass + 0.5*thrust + noise
    target1 = -100 * param1 + 0.5 * param2 + np.random.normal(0, 10, n_samples)

    parameters_df = pd.DataFrame({
        "rocket.dry_mass_kg": param1,
        "motor.thrust_avg": param2
    })

    targets_df = pd.DataFrame({
        "apogee_m": target1
    })

    return parameters_df, targets_df


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestVarianceBasedSensitivityAnalyzer:
    """Tests for VarianceBasedSensitivityAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        param_names = ["rocket.dry_mass_kg", "motor.thrust_avg"]
        target_names = ["apogee_m"]

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=param_names,
            target_names=target_names
        )

        assert analyzer.parameter_names == param_names
        assert analyzer.target_names == target_names
        assert analyzer.nominal_means is None
        assert analyzer.nominal_stds is None
        assert len(analyzer.regression_models) == 0

    def test_initialization_empty_parameters(self):
        """Test that initialization fails with empty parameters."""
        with pytest.raises(ValueError, match="parameter_names cannot be empty"):
            VarianceBasedSensitivityAnalyzer(
                parameter_names=[],
                target_names=["apogee_m"]
            )

    def test_initialization_empty_targets(self):
        """Test that initialization fails with empty targets."""
        with pytest.raises(ValueError, match="target_names cannot be empty"):
            VarianceBasedSensitivityAnalyzer(
                parameter_names=["rocket.dry_mass_kg"],
                target_names=[]
            )

    def test_set_nominal_parameters(self, sample_monte_carlo_data):
        """Test setting nominal parameters."""
        parameters_df, _ = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=["apogee_m"]
        )

        means = {"rocket.dry_mass_kg": 10.0, "motor.thrust_avg": 1500.0}
        stds = {"rocket.dry_mass_kg": 0.5, "motor.thrust_avg": 50.0}

        analyzer.set_nominal_parameters(means=means, stds=stds)

        assert analyzer.nominal_means == means
        assert analyzer.nominal_stds == stds

    def test_set_nominal_parameters_missing_parameter(self):
        """Test that setting nominals fails if parameter is missing."""
        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=["rocket.dry_mass_kg", "motor.thrust_avg"],
            target_names=["apogee_m"]
        )

        means = {"rocket.dry_mass_kg": 10.0}  # Missing motor.thrust_avg
        stds = {"rocket.dry_mass_kg": 0.5, "motor.thrust_avg": 50.0}

        with pytest.raises(ValueError, match="Missing nominal means"):
            analyzer.set_nominal_parameters(means=means, stds=stds)

    def test_set_nominal_parameters_negative_std(self):
        """Test that setting nominals fails with negative std."""
        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=["rocket.dry_mass_kg"],
            target_names=["apogee_m"]
        )

        means = {"rocket.dry_mass_kg": 10.0}
        stds = {"rocket.dry_mass_kg": -0.5}  # Negative!

        with pytest.raises(ValueError, match="must be positive"):
            analyzer.set_nominal_parameters(means=means, stds=stds)

    def test_fit_regression(self, sample_monte_carlo_data):
        """Test fitting regression models."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        # Set nominal parameters
        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)

        # Fit models
        analyzer.fit(parameters_df, targets_df)

        # Check that models were fitted
        assert "apogee_m" in analyzer.regression_models
        assert "apogee_m" in analyzer.sensitivity_coefficients
        assert "apogee_m" in analyzer.lae

    def test_fit_without_nominal_parameters(self, sample_monte_carlo_data):
        """Test that fitting fails without nominal parameters."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        with pytest.raises(ValueError, match="Nominal parameters must be set"):
            analyzer.fit(parameters_df, targets_df)

    def test_sensitivity_coefficients_sum(self, sample_monte_carlo_data):
        """Test that sensitivity coefficients are reasonable."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(parameters_df, targets_df)

        # Get sensitivities
        sensitivities = analyzer.sensitivity_coefficients["apogee_m"]

        # Sensitivities should be non-negative percentages
        for param, sens in sensitivities.items():
            assert sens >= 0, f"Sensitivity for {param} is negative"
            assert sens <= 100, f"Sensitivity for {param} exceeds 100%"

        # LAE should be non-negative
        lae = analyzer.lae["apogee_m"]
        assert lae >= 0
        assert lae <= 100

    def test_get_sensitivity_summary(self, sample_monte_carlo_data):
        """Test getting sensitivity summary."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(parameters_df, targets_df)

        # Get summary
        summary = analyzer.get_sensitivity_summary()

        assert "apogee_m" in summary
        assert "LAE" in summary["apogee_m"]
        assert "rocket.dry_mass_kg" in summary["apogee_m"]
        assert "motor.thrust_avg" in summary["apogee_m"]

    def test_get_importance_ranking(self, sample_monte_carlo_data):
        """Test getting importance ranking."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(parameters_df, targets_df)

        # Get ranking
        ranking = analyzer.get_importance_ranking("apogee_m")

        # Check structure
        assert len(ranking) == 2
        assert all(isinstance(item, tuple) for item in ranking)
        assert all(len(item) == 2 for item in ranking)

        # Check that it's sorted (descending)
        sensitivities = [s for _, s in ranking]
        assert sensitivities == sorted(sensitivities, reverse=True)

    def test_get_prediction_intervals(self, sample_monte_carlo_data):
        """Test getting prediction intervals."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(parameters_df, targets_df)

        # Get prediction intervals
        mean_pred, lower, upper = analyzer.get_prediction_intervals("apogee_m")

        # Check that intervals make sense
        assert lower < mean_pred < upper
        assert isinstance(mean_pred, (int, float))
        assert isinstance(lower, (int, float))
        assert isinstance(upper, (int, float))

    def test_plot_sensitivity_bars(self, sample_monte_carlo_data, temp_output_dir):
        """Test generating sensitivity bar plot."""
        parameters_df, targets_df = sample_monte_carlo_data

        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(parameters_df, targets_df)

        # Generate plot
        output_path = temp_output_dir / "sensitivity_bars.png"
        fig = analyzer.plot_sensitivity_bars(output_path=str(output_path))

        # Check that file was created
        assert output_path.exists()
        assert fig is not None


class TestSensitivityUtils:
    """Tests for sensitivity utility functions."""

    def test_save_and_load_monte_carlo_data(self, sample_monte_carlo_data, temp_output_dir):
        """Test saving and loading Monte Carlo data."""
        parameters_df, targets_df = sample_monte_carlo_data

        # Save data
        input_path, output_path = save_monte_carlo_data(
            parameters_df=parameters_df,
            targets_df=targets_df,
            output_dir=temp_output_dir,
            filename_prefix="test_mc"
        )

        # Check files were created
        assert input_path.exists()
        assert output_path.exists()

        # Load data
        loaded_params, loaded_targets = load_monte_carlo_data(
            input_file=input_path,
            output_file=output_path
        )

        # Check data matches
        pd.testing.assert_frame_equal(loaded_params, parameters_df)
        pd.testing.assert_frame_equal(loaded_targets, targets_df)

    def test_load_monte_carlo_data_with_filters(self, sample_monte_carlo_data, temp_output_dir):
        """Test loading specific columns."""
        parameters_df, targets_df = sample_monte_carlo_data

        # Save data
        input_path, output_path = save_monte_carlo_data(
            parameters_df=parameters_df,
            targets_df=targets_df,
            output_dir=temp_output_dir,
            filename_prefix="test_mc"
        )

        # Load only specific columns
        loaded_params, loaded_targets = load_monte_carlo_data(
            input_file=input_path,
            output_file=output_path,
            parameter_names=["rocket.dry_mass_kg"],
            target_names=["apogee_m"]
        )

        assert list(loaded_params.columns) == ["rocket.dry_mass_kg"]
        assert list(loaded_targets.columns) == ["apogee_m"]

    def test_validate_linear_approximation(self):
        """Test LAE validation function."""
        # Excellent approximation
        status, msg = validate_linear_approximation(5.0)
        assert status == "excellent"
        assert "excellent" in msg.lower()

        # Adequate approximation
        status, msg = validate_linear_approximation(20.0)
        assert status == "adequate"
        assert "adequate" in msg.lower()

        # Poor approximation
        status, msg = validate_linear_approximation(50.0)
        assert status == "poor"
        assert "poor" in msg.lower() or "not" in msg.lower()

    def test_estimate_parameter_statistics(self, sample_monte_carlo_data):
        """Test parameter statistics estimation."""
        parameters_df, _ = sample_monte_carlo_data

        stats = estimate_parameter_statistics(parameters_df)

        assert "rocket.dry_mass_kg" in stats
        assert "motor.thrust_avg" in stats

        # Check structure
        for param, param_stats in stats.items():
            assert "mean" in param_stats
            assert "std" in param_stats
            assert isinstance(param_stats["mean"], float)
            assert isinstance(param_stats["std"], float)
            assert param_stats["std"] > 0

    def test_filter_significant_parameters(self):
        """Test filtering significant parameters."""
        sensitivities = {
            "param1": 50.0,  # Significant
            "param2": 30.0,  # Significant
            "param3": 5.0,   # Not significant (< LAE)
            "param4": 2.0,   # Not significant
        }
        lae = 10.0

        significant = filter_significant_parameters(sensitivities, lae)

        assert len(significant) == 2
        assert "param1" in significant
        assert "param2" in significant
        assert "param3" not in significant
        assert "param4" not in significant

        # Check that it's sorted
        assert significant[0] == "param1"  # Highest sensitivity first


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_sensitivity_workflow(self, sample_monte_carlo_data, temp_output_dir):
        """Test complete sensitivity analysis workflow."""
        parameters_df, targets_df = sample_monte_carlo_data

        # Step 1: Create analyzer
        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(parameters_df.columns),
            target_names=list(targets_df.columns)
        )

        # Step 2: Set nominal parameters
        means = {col: parameters_df[col].mean() for col in parameters_df.columns}
        stds = {col: parameters_df[col].std() for col in parameters_df.columns}
        analyzer.set_nominal_parameters(means=means, stds=stds)

        # Step 3: Fit models
        analyzer.fit(parameters_df, targets_df)

        # Step 4: Get summary
        summary = analyzer.get_sensitivity_summary()
        assert "apogee_m" in summary

        # Step 5: Get ranking
        ranking = analyzer.get_importance_ranking("apogee_m")
        assert len(ranking) > 0

        # Step 6: Generate plot
        plot_path = temp_output_dir / "sensitivity_plot.png"
        analyzer.plot_sensitivity_bars(output_path=str(plot_path))
        assert plot_path.exists()

        # Step 7: Check LAE is reasonable
        lae = analyzer.lae["apogee_m"]
        assert 0 <= lae <= 100

    def test_monte_carlo_to_sensitivity_integration(self, sample_monte_carlo_data, temp_output_dir):
        """Test integration with Monte Carlo data export."""
        parameters_df, targets_df = sample_monte_carlo_data

        # Simulate Monte Carlo export
        input_path, output_path = save_monte_carlo_data(
            parameters_df=parameters_df,
            targets_df=targets_df,
            output_dir=temp_output_dir,
            filename_prefix="mc_results"
        )

        # Load for sensitivity analysis
        params, targets = load_monte_carlo_data(
            input_file=input_path,
            output_file=output_path
        )

        # Run sensitivity analysis
        analyzer = VarianceBasedSensitivityAnalyzer(
            parameter_names=list(params.columns),
            target_names=list(targets.columns)
        )

        stats = estimate_parameter_statistics(params)
        means = {p: s["mean"] for p, s in stats.items()}
        stds = {p: s["std"] for p, s in stats.items()}

        analyzer.set_nominal_parameters(means=means, stds=stds)
        analyzer.fit(params, targets)

        # Verify results
        summary = analyzer.get_sensitivity_summary()
        assert len(summary) > 0
