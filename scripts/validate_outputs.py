#!/usr/bin/env python3
"""
Comprehensive Output Validation Script

Validates that ALL simulation outputs (plots, reports, JSON files, CSVs) 
contain actual simulation data and not hardcoded values or stale data.

Usage:
    python scripts/validate_outputs.py <output_directory>

Example:
    python scripts/validate_outputs.py outputs/artemis/FINAL_CORRECTED
"""

import json
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple


class OutputValidator:
    """Validates simulation outputs against source data."""
    
    def __init__(self, output_dir: Path):
        """Initialize validator with output directory.
        
        Args:
            output_dir: Path to simulation output directory
        """
        self.output_dir = Path(output_dir)
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.checks_total = 0
        
        # Try to find summary.json in multiple locations
        summary_paths = [
            self.output_dir / "summary.json",
            self.output_dir / "data" / f"{self.output_dir.name}_summary.json",
        ]
        
        trajectory_paths = [
            self.output_dir / "trajectory.csv",
            self.output_dir / "data" / f"{self.output_dir.name}_trajectory.csv",
        ]
        
        initial_state_paths = [
            self.output_dir / "initial_state.json",
            self.output_dir / "initial_state",
        ]
        
        final_state_paths = [
            self.output_dir / "final_state.json",
            self.output_dir / "final_state",
        ]
        
        # Load all data sources
        self.summary = self._load_json_multi(summary_paths)
        self.initial_state = self._load_json_multi(initial_state_paths)
        self.final_state = self._load_json_multi(final_state_paths)
        self.trajectory = self._load_csv_multi(trajectory_paths)
        
    def _load_json_multi(self, paths: List[Path]) -> Dict:
        """Try loading JSON from multiple possible paths."""
        for path in paths:
            result = self._load_json(path)
            if result:  # If we got valid data
                return result
        return {}
    
    def _load_csv_multi(self, paths: List[Path]) -> pd.DataFrame:
        """Try loading CSV from multiple possible paths."""
        for path in paths:
            result = self._load_csv(path)
            if not result.empty:  # If we got valid data
                return result
        return pd.DataFrame()
    
    def _load_json(self, path: Path) -> Dict:
        """Load JSON file with error handling."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.warnings.append(f"Could not load {path}: {e}")
            return {}
    
    def _load_csv(self, path: Path) -> pd.DataFrame:
        """Load CSV file with error handling."""
        try:
            return pd.read_csv(path)
        except Exception as e:
            self.warnings.append(f"Could not load {path}: {e}")
            return pd.DataFrame()
    
    def _check(self, condition: bool, error_msg: str, warning: bool = False):
        """Record a validation check result."""
        self.checks_total += 1
        if condition:
            self.checks_passed += 1
        else:
            if warning:
                self.warnings.append(error_msg)
            else:
                self.errors.append(error_msg)
    
    def validate_summary_completeness(self) -> bool:
        """Validate that summary.json contains all required fields."""
        print("\n" + "="*70)
        print("1. VALIDATING SUMMARY COMPLETENESS")
        print("="*70)
        
        required_sections = [
            'configuration',
            'flight_results',
            'simulation_info'
        ]
        
        for section in required_sections:
            self._check(
                section in self.summary,
                f"Missing required section: {section}"
            )
        
        if 'flight_results' in self.summary:
            critical_metrics = [
                'max_altitude_m',
                'max_velocity_ms',
                'max_acceleration_ms2',
                'max_mach_number',
                'max_dynamic_pressure_pa',
                'max_dynamic_pressure_time_s',
                'apogee_time_s',
                'impact_time_s',
                'impact_velocity_ms'
            ]
            
            for metric in critical_metrics:
                self._check(
                    metric in self.summary['flight_results'],
                    f"Missing critical metric: {metric}"
                )
        
        print(f"✓ Checked {self.checks_total} summary fields")
        return len(self.errors) == 0
    
    def validate_critical_events_consistency(self) -> bool:
        """Validate that critical event times are consistent across files."""
        print("\n" + "="*70)
        print("2. VALIDATING CRITICAL EVENTS CONSISTENCY")
        print("="*70)
        
        if not self.summary or 'flight_results' not in self.summary:
            self.warnings.append("Cannot validate events - summary incomplete")
            return False
        
        fr = self.summary['flight_results']
        
        # Max-Q validation
        if 'max_dynamic_pressure_time_s' in fr and not self.trajectory.empty:
            max_q_time = fr['max_dynamic_pressure_time_s']
            
            # Find closest time in trajectory
            if 'time' in self.trajectory.columns:
                closest_idx = (self.trajectory['time'] - max_q_time).abs().idxmin()
                traj_time = self.trajectory.loc[closest_idx, 'time']
                
                # Should match within 0.1 seconds (CSV resolution)
                self._check(
                    abs(traj_time - max_q_time) < 0.1,
                    f"Max-Q time mismatch: summary={max_q_time:.2f}s, trajectory closest={traj_time:.2f}s"
                )
                print(f"  Max-Q time: {max_q_time:.2f}s (summary) vs {traj_time:.2f}s (trajectory)")
        
        # Apogee validation
        if 'apogee_time_s' in fr and 'max_altitude_m' in fr and not self.trajectory.empty:
            apogee_time = fr['apogee_time_s']
            max_alt = fr['max_altitude_m']
            
            if 'time' in self.trajectory.columns and 'z' in self.trajectory.columns:
                # Find maximum altitude in trajectory
                max_alt_idx = self.trajectory['z'].idxmax()
                traj_apogee_time = self.trajectory.loc[max_alt_idx, 'time']
                traj_max_alt = self.trajectory.loc[max_alt_idx, 'z']
                
                self._check(
                    abs(traj_apogee_time - apogee_time) < 0.1,
                    f"Apogee time mismatch: summary={apogee_time:.2f}s, trajectory={traj_apogee_time:.2f}s"
                )
                
                self._check(
                    abs(traj_max_alt - max_alt) < 1.0,  # 1m tolerance
                    f"Max altitude mismatch: summary={max_alt:.1f}m, trajectory={traj_max_alt:.1f}m"
                )
                print(f"  Apogee: {apogee_time:.2f}s @ {max_alt:.1f}m (summary) vs {traj_apogee_time:.2f}s @ {traj_max_alt:.1f}m (trajectory)")
        
        # Max velocity validation
        if 'max_velocity_ms' in fr and not self.trajectory.empty:
            max_vel_summary = fr['max_velocity_ms']
            
            if all(col in self.trajectory.columns for col in ['vx', 'vy', 'vz']):
                # Calculate total velocity magnitude
                self.trajectory['v_total'] = np.sqrt(
                    self.trajectory['vx']**2 + 
                    self.trajectory['vy']**2 + 
                    self.trajectory['vz']**2
                )
                max_vel_traj = self.trajectory['v_total'].max()
                
                # Should match within 1% or 1 m/s
                tolerance = max(0.01 * max_vel_summary, 1.0)
                self._check(
                    abs(max_vel_traj - max_vel_summary) < tolerance,
                    f"Max velocity mismatch: summary={max_vel_summary:.1f}m/s, trajectory={max_vel_traj:.1f}m/s"
                )
                print(f"  Max velocity: {max_vel_summary:.1f}m/s (summary) vs {max_vel_traj:.1f}m/s (trajectory)")
        
        return len(self.errors) == 0
    
    def validate_no_hardcoded_values(self) -> bool:
        """Check for suspicious hardcoded values."""
        print("\n" + "="*70)
        print("3. CHECKING FOR HARDCODED VALUES")
        print("="*70)
        
        if not self.summary or 'flight_results' not in self.summary:
            return False
        
        fr = self.summary['flight_results']
        
        # Check for suspicious exact round numbers
        suspicious_values = {
            'max_mach_number': [2.0, 1.5, 1.0, 0.5],  # Common hardcoded values
            'max_dynamic_pressure_pa': [10000.0, 50000.0, 100000.0],  # Round kPa values
        }
        
        for metric, suspicious_list in suspicious_values.items():
            if metric in fr:
                value = fr[metric]
                for suspicious_val in suspicious_list:
                    if abs(value - suspicious_val) < 1e-6:
                        self.warnings.append(
                            f"WARNING: {metric}={value} is suspiciously round - verify not hardcoded"
                        )
                        print(f"  ⚠️  {metric} = {value} (suspiciously exact)")
        
        # Check that critical values are non-zero
        non_zero_metrics = [
            'max_altitude_m',
            'max_velocity_ms',
            'max_mach_number',
            'max_dynamic_pressure_pa'
        ]
        
        for metric in non_zero_metrics:
            if metric in fr:
                self._check(
                    fr[metric] > 0,
                    f"{metric} is zero or negative: {fr[metric]}"
                )
        
        return len(self.errors) == 0
    
    def validate_trajectory_continuity(self) -> bool:
        """Validate trajectory data is continuous and realistic."""
        print("\n" + "="*70)
        print("4. VALIDATING TRAJECTORY CONTINUITY")
        print("="*70)
        
        if self.trajectory.empty:
            self.errors.append("Trajectory CSV is empty or missing")
            return False
        
        # Check required columns
        required_cols = ['time', 'x', 'y', 'z', 'vx', 'vy', 'vz']
        for col in required_cols:
            self._check(
                col in self.trajectory.columns,
                f"Missing trajectory column: {col}"
            )
        
        if 'time' in self.trajectory.columns:
            # Check time is monotonically increasing
            time_diffs = self.trajectory['time'].diff().dropna()
            self._check(
                (time_diffs > 0).all(),
                "Time in trajectory is not monotonically increasing"
            )
            
            # Check for reasonable time steps (typically 0.01 to 1.0 seconds)
            if len(time_diffs) > 0:
                max_dt = time_diffs.max()
                self._check(
                    max_dt < 2.0,
                    f"Trajectory has large time gaps (max {max_dt:.3f}s)",
                    warning=True
                )
            
            print(f"  ✓ Trajectory has {len(self.trajectory)} points")
            print(f"  ✓ Time range: {self.trajectory['time'].min():.2f}s to {self.trajectory['time'].max():.2f}s")
        
        # Check for NaN values
        nan_cols = self.trajectory.columns[self.trajectory.isna().any()].tolist()
        if nan_cols:
            self.warnings.append(f"Trajectory has NaN values in: {nan_cols}")
        
        return len(self.errors) == 0
    
    def validate_plot_files_exist(self) -> bool:
        """Validate that expected plot files were generated."""
        print("\n" + "="*70)
        print("5. VALIDATING PLOT FILES EXISTENCE")
        print("="*70)
        
        curves_dir = self.output_dir / "curves"
        if not curves_dir.exists():
            self.errors.append("curves/ directory does not exist")
            return False
        
        # Expected plot categories
        expected_subdirs = {
            'motor': ['thrust.png', 'mass_evolution.png', 'center_of_mass.png'],
            'rocket': ['static_margin_vs_time.png', 'stability_margin.png'],
            'aerodynamics': ['drag_coefficient_vs_mach.png', 'cp_vs_mach.png'],
        }
        
        total_plots = 0
        missing_plots = []
        
        for subdir, expected_files in expected_subdirs.items():
            subdir_path = curves_dir / subdir
            if subdir_path.exists():
                for filename in expected_files:
                    plot_path = subdir_path / filename
                    if plot_path.exists():
                        total_plots += 1
                        # Check file is not empty (at least 1KB)
                        if plot_path.stat().st_size < 1024:
                            self.warnings.append(f"Plot file suspiciously small: {plot_path}")
                    else:
                        missing_plots.append(str(plot_path.relative_to(self.output_dir)))
        
        if missing_plots:
            self.warnings.append(f"Missing {len(missing_plots)} expected plots: {missing_plots[:5]}")
        
        print(f"  ✓ Found {total_plots} plot files in curves/")
        
        return True
    
    def validate_max_q_in_outputs(self) -> bool:
        """Specifically validate Max-Q appears correctly in all outputs."""
        print("\n" + "="*70)
        print("6. VALIDATING MAX-Q ACROSS OUTPUTS")
        print("="*70)
        
        if not self.summary or 'flight_results' not in self.summary:
            return False
        
        fr = self.summary['flight_results']
        
        # Check Max-Q in summary
        has_max_q_pressure = 'max_dynamic_pressure_pa' in fr
        has_max_q_time = 'max_dynamic_pressure_time_s' in fr
        
        self._check(
            has_max_q_pressure,
            "Max-Q pressure missing from summary"
        )
        self._check(
            has_max_q_time,
            "Max-Q time missing from summary"
        )
        
        if has_max_q_pressure and has_max_q_time:
            max_q_pa = fr['max_dynamic_pressure_pa']
            max_q_time = fr['max_dynamic_pressure_time_s']
            max_q_kpa = max_q_pa / 1000.0
            
            print(f"  ✓ Max-Q in summary: {max_q_kpa:.1f} kPa at {max_q_time:.2f}s")
            
            # Validate Max-Q is reasonable (typical range: 1-100 kPa for model rockets)
            self._check(
                0.1 < max_q_kpa < 200,
                f"Max-Q value suspicious: {max_q_kpa:.1f} kPa (expected 0.1-200 kPa)",
                warning=True
            )
            
            # Check Max-Q time is during powered flight (typically)
            if 'motor_burnout_time_s' in fr:
                burnout = fr['motor_burnout_time_s']
                # Max-Q typically occurs before or shortly after burnout
                self._check(
                    max_q_time <= burnout * 1.5,
                    f"Max-Q time ({max_q_time:.2f}s) suspiciously late (burnout at {burnout:.2f}s)",
                    warning=True
                )
        
        # Check for aerodynamic forces at Max-Q
        force_metrics = [
            'max_aerodynamic_drag_n',
            'max_aerodynamic_lift_n',
            'max_bending_moment_nm'
        ]
        
        forces_present = sum(1 for m in force_metrics if m in fr)
        if forces_present > 0:
            print(f"  ✓ Found {forces_present}/3 aerodynamic force metrics")
            for metric in force_metrics:
                if metric in fr:
                    print(f"    - {metric}: {fr[metric]:.2f}")
        
        return len(self.errors) == 0
    
    def generate_report(self) -> str:
        """Generate validation report."""
        report = []
        report.append("\n" + "="*70)
        report.append("VALIDATION SUMMARY")
        report.append("="*70)
        
        # Statistics
        pass_rate = (self.checks_passed / self.checks_total * 100) if self.checks_total > 0 else 0
        report.append(f"\nChecks: {self.checks_passed}/{self.checks_total} passed ({pass_rate:.1f}%)")
        
        # Errors
        if self.errors:
            report.append(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                report.append(f"  {i}. {error}")
        else:
            report.append("\n✅ No errors found!")
        
        # Warnings
        if self.warnings:
            report.append(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                report.append(f"  {i}. {warning}")
        
        # Overall verdict
        report.append("\n" + "="*70)
        if len(self.errors) == 0 and len(self.warnings) == 0:
            report.append("✅ VALIDATION PASSED - All outputs verified!")
        elif len(self.errors) == 0:
            report.append("⚠️  VALIDATION PASSED WITH WARNINGS - Review recommended")
        else:
            report.append("❌ VALIDATION FAILED - Critical issues found")
        report.append("="*70 + "\n")
        
        return "\n".join(report)
    
    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        print("\n" + "="*70)
        print(f"VALIDATING OUTPUT DIRECTORY: {self.output_dir}")
        print("="*70)
        
        # Run all validation methods
        self.validate_summary_completeness()
        self.validate_critical_events_consistency()
        self.validate_no_hardcoded_values()
        self.validate_trajectory_continuity()
        self.validate_plot_files_exist()
        self.validate_max_q_in_outputs()
        
        # Print report
        print(self.generate_report())
        
        # Save report to file
        report_path = self.output_dir / "validation_report.txt"
        with open(report_path, 'w') as f:
            f.write(self.generate_report())
        print(f"Validation report saved to: {report_path}")
        
        return len(self.errors) == 0


def main():
    """Main validation script entry point."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_outputs.py <output_directory>")
        print("\nExample:")
        print("  python scripts/validate_outputs.py outputs/artemis/FINAL_CORRECTED")
        sys.exit(1)
    
    output_dir = Path(sys.argv[1])
    
    if not output_dir.exists():
        print(f"❌ Error: Output directory does not exist: {output_dir}")
        sys.exit(1)
    
    # Run validation
    validator = OutputValidator(output_dir)
    success = validator.run_all_validations()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
