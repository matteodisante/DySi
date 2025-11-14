"""Tests for apogee prediction methods.

This module tests the different numerical integration methods for
apogee prediction: ballistic, Euler, and RK45.
"""

import pytest
import numpy as np
from src.air_brakes_controller import (
    ConstantDecelerationPredictor,
    EulerPredictor,
    RK45Predictor
)


class TestApogeePredictors:
    """Test suite for apogee prediction methods."""
    
    def test_ballistic_predictor_ascending(self):
        """Test ballistic predictor during ascent."""
        predictor = ConstantDecelerationPredictor()
        
        # Test case: 2000m altitude, 100 m/s upward velocity
        predicted = predictor.predict_apogee(
            altitude=2000.0,
            velocity_z=100.0,
            mass=15.0,
            drag_coefficient=0.5,
            reference_area=0.01,
            air_density=1.0,
            deployment_level=0.0
        )
        
        # Analytical: h_max = h + v²/(2g) = 2000 + 100²/(2*9.81) ≈ 2509.7m
        expected = 2000.0 + 100.0**2 / (2 * 9.81)
        
        assert abs(predicted - expected) < 1.0, \
            f"Ballistic predictor error: {predicted} vs {expected}"
    
    def test_ballistic_predictor_descending(self):
        """Test ballistic predictor during descent."""
        predictor = ConstantDecelerationPredictor()
        
        # Test case: descending (negative velocity)
        predicted = predictor.predict_apogee(
            altitude=2500.0,
            velocity_z=-50.0,
            mass=15.0,
            drag_coefficient=0.5,
            reference_area=0.01,
            air_density=1.0,
            deployment_level=0.0
        )
        
        # Should return current altitude when descending
        assert predicted == 2500.0, \
            f"Ballistic should return current altitude when descending: {predicted}"
    
    def test_euler_predictor_zero_drag(self):
        """Test Euler predictor with zero drag (should match ballistic)."""
        predictor = EulerPredictor(dt=0.01, max_iterations=1000)
        
        # Zero drag case (Cd=0 or A=0)
        predicted = predictor.predict_apogee(
            altitude=2000.0,
            velocity_z=100.0,
            mass=15.0,
            drag_coefficient=0.0,  # No drag
            reference_area=0.01,
            air_density=1.0,
            deployment_level=0.0
        )
        
        # Should be close to ballistic prediction
        expected = 2000.0 + 100.0**2 / (2 * 9.81)
        error_pct = abs(predicted - expected) / expected * 100
        
        assert error_pct < 2.0, \
            f"Euler with zero drag should match ballistic: {error_pct:.2f}% error"
    
    def test_euler_predictor_with_drag(self):
        """Test Euler predictor with realistic drag."""
        predictor = EulerPredictor(dt=0.05, max_iterations=1000)
        
        # Realistic case with drag
        predicted = predictor.predict_apogee(
            altitude=2000.0,
            velocity_z=100.0,
            mass=15.0,
            drag_coefficient=0.5,
            reference_area=0.01,
            air_density=1.0,
            deployment_level=0.0
        )
        
        # With drag, apogee should be LOWER than ballistic prediction
        ballistic_apogee = 2000.0 + 100.0**2 / (2 * 9.81)
        
        assert predicted < ballistic_apogee, \
            f"Drag should lower apogee: {predicted} vs {ballistic_apogee}"
        
        # Check reasonable range (drag reduces apogee by 10-30%)
        assert 0.7 * ballistic_apogee < predicted < ballistic_apogee, \
            f"Predicted apogee out of reasonable range: {predicted}"
    
    def test_rk45_predictor_zero_drag(self):
        """Test RK45 predictor with zero drag."""
        predictor = RK45Predictor(tol=1e-4, dt_initial=0.1, max_iterations=1000)
        
        # Zero drag case
        predicted = predictor.predict_apogee(
            altitude=2000.0,
            velocity_z=100.0,
            mass=15.0,
            drag_coefficient=0.0,
            reference_area=0.01,
            air_density=1.0,
            deployment_level=0.0
        )
        
        # Should match ballistic very closely (RK45 is high accuracy)
        expected = 2000.0 + 100.0**2 / (2 * 9.81)
        error_pct = abs(predicted - expected) / expected * 100
        
        assert error_pct < 0.5, \
            f"RK45 with zero drag should closely match ballistic: {error_pct:.2f}% error"
    
    def test_rk45_vs_euler_consistency(self):
        """Test that RK45 and Euler give similar results."""
        euler_pred = EulerPredictor(dt=0.01, max_iterations=1000)
        rk45_pred = RK45Predictor(tol=1e-4, dt_initial=0.1, max_iterations=1000)
        
        # Same test case
        params = {
            "altitude": 2000.0,
            "velocity_z": 100.0,
            "mass": 15.0,
            "drag_coefficient": 0.5,
            "reference_area": 0.01,
            "air_density": 1.0,
            "deployment_level": 0.0
        }
        
        euler_result = euler_pred.predict_apogee(**params)
        rk45_result = rk45_pred.predict_apogee(**params)
        
        # RK45 should be more accurate, but results should be close
        error_pct = abs(euler_result - rk45_result) / rk45_result * 100
        
        assert error_pct < 10.0, \
            f"Euler and RK45 should give similar results: {error_pct:.2f}% difference"
    
    def test_high_drag_scenario(self):
        """Test predictors with high drag (air brakes deployed)."""
        euler_pred = EulerPredictor(dt=0.05, max_iterations=1000)
        
        # High drag case (air brakes fully deployed)
        predicted = euler_pred.predict_apogee(
            altitude=2000.0,
            velocity_z=100.0,
            mass=15.0,
            drag_coefficient=1.5,  # High Cd with air brakes
            reference_area=0.02,   # Larger area with deployment
            air_density=1.0,
            deployment_level=1.0
        )
        
        # Ballistic prediction
        ballistic = 2000.0 + 100.0**2 / (2 * 9.81)
        
        # High drag should reduce apogee (expect 5-20% reduction)
        reduction_pct = (ballistic - predicted) / ballistic * 100
        
        assert reduction_pct > 3.0, \
            f"High drag should reduce apogee significantly: {reduction_pct:.1f}% reduction"
        
        assert predicted > 2000.0, \
            f"Predicted apogee should still be above current altitude: {predicted}m"


if __name__ == "__main__":
    # Run basic smoke tests
    print("Testing Apogee Predictors...")
    
    test_suite = TestApogeePredictors()
    
    print("\n1. Testing ballistic predictor (ascending)...")
    test_suite.test_ballistic_predictor_ascending()
    print("   ✓ Ballistic ascending: PASS")
    
    print("\n2. Testing ballistic predictor (descending)...")
    test_suite.test_ballistic_predictor_descending()
    print("   ✓ Ballistic descending: PASS")
    
    print("\n3. Testing Euler predictor (zero drag)...")
    test_suite.test_euler_predictor_zero_drag()
    print("   ✓ Euler zero drag: PASS")
    
    print("\n4. Testing Euler predictor (with drag)...")
    test_suite.test_euler_predictor_with_drag()
    print("   ✓ Euler with drag: PASS")
    
    print("\n5. Testing RK45 predictor (zero drag)...")
    test_suite.test_rk45_predictor_zero_drag()
    print("   ✓ RK45 zero drag: PASS")
    
    print("\n6. Testing RK45 vs Euler consistency...")
    test_suite.test_rk45_vs_euler_consistency()
    print("   ✓ RK45 vs Euler: PASS")
    
    print("\n7. Testing high drag scenario...")
    test_suite.test_high_drag_scenario()
    print("   ✓ High drag: PASS")
    
    print("\n" + "="*60)
    print("All tests PASSED! ✓")
    print("="*60)
