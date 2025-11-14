"""Air brakes controller implementation with realistic hardware constraints.

This module provides control laws for air brakes systems, accounting for:
- Servo motor lag (actuation delay)
- Microcontroller computation time
- Rate limiting (maximum deployment speed)
- Sensor noise and filtering
- Different control algorithms (PID, bang-bang, model-predictive)
- Advanced apogee prediction using numerical integration (Euler, RK45)
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Callable
from abc import ABC, abstractmethod
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# NUMERICAL INTEGRATORS FOR APOGEE PREDICTION
# ============================================================================

class ApogeePredictor(ABC):
    """Abstract base class for apogee prediction methods.
    
    Different predictors use various numerical integration techniques to
    simulate the rocket's trajectory from current state to apogee, accounting
    for drag, gravity, and air brakes configuration.
    """
    
    @abstractmethod
    def predict_apogee(
        self,
        altitude: float,
        velocity_z: float,
        mass: float,
        drag_coefficient: float,
        reference_area: float,
        air_density: float,
        deployment_level: float
    ) -> float:
        """Predict apogee altitude from current state.
        
        Parameters
        ----------
        altitude : float
            Current altitude (m)
        velocity_z : float
            Current vertical velocity (m/s)
        mass : float
            Current rocket mass (kg)
        drag_coefficient : float
            Current drag coefficient (dimensionless)
        reference_area : float
            Reference area for drag calculation (m²)
        air_density : float
            Current air density (kg/m³)
        deployment_level : float
            Current air brakes deployment [0, 1]
            
        Returns
        -------
        float
            Predicted apogee altitude (m)
        """
        pass


class ConstantDecelerationPredictor(ApogeePredictor):
    """Simple predictor assuming constant deceleration.
    
    This is the baseline method - fast but inaccurate as it ignores
    changing drag forces and air density with altitude.
    
    Uses: h_apogee = h + v²/(2g)
    """
    
    def predict_apogee(
        self,
        altitude: float,
        velocity_z: float,
        mass: float,
        drag_coefficient: float,
        reference_area: float,
        air_density: float,
        deployment_level: float
    ) -> float:
        """Predict apogee using kinematic equation with constant g."""
        g = 9.81  # m/s²
        
        if velocity_z > 0:
            # Ascending: simple ballistic prediction
            return altitude + (velocity_z ** 2) / (2 * g)
        else:
            # Descending: already past apogee
            return altitude


class EulerPredictor(ApogeePredictor):
    """Apogee predictor using forward Euler integration.
    
    Integrates the equations of motion forward in time with fixed time step:
        dv/dt = -g - (0.5 * ρ * v² * Cd * A) / m
        dh/dt = v
        
    More accurate than constant deceleration as it accounts for changing
    drag forces. Still has numerical errors due to fixed time step.
    
    Parameters
    ----------
    dt : float
        Integration time step (s). Smaller = more accurate but slower.
        Default: 0.1s
    max_iterations : int
        Maximum integration steps before stopping. Default: 1000
    """
    
    def __init__(self, dt: float = 0.1, max_iterations: int = 1000):
        """Initialize Euler predictor.
        
        Parameters
        ----------
        dt : float
            Time step for integration (s)
        max_iterations : int
            Maximum number of steps to prevent infinite loops
        """
        self.dt = dt
        self.max_iterations = max_iterations
    
    def predict_apogee(
        self,
        altitude: float,
        velocity_z: float,
        mass: float,
        drag_coefficient: float,
        reference_area: float,
        air_density: float,
        deployment_level: float
    ) -> float:
        """Predict apogee using Euler forward integration."""
        if velocity_z <= 0:
            return altitude  # Already descending
        
        h = altitude
        v = velocity_z
        g = 9.81  # m/s²
        
        # Integrate until velocity becomes negative (apogee reached)
        for _ in range(self.max_iterations):
            if v <= 0:
                break
            
            # Drag force: F_drag = 0.5 * ρ * v² * Cd * A
            # Acceleration: a = -g - F_drag/m
            drag_accel = (0.5 * air_density * v**2 * drag_coefficient * reference_area) / mass
            acceleration = -g - drag_accel
            
            # Euler forward step
            v_new = v + acceleration * self.dt
            h_new = h + v * self.dt
            
            # Update for next iteration
            v = v_new
            h = h_new
            
            # Simple air density model (exponential atmosphere)
            # ρ(h) = ρ₀ * exp(-h/H) where H ≈ 8500m (scale height)
            air_density = air_density * np.exp(-self.dt * v / 8500)
        
        return h


class RK45Predictor(ApogeePredictor):
    """Apogee predictor using Runge-Kutta 4th/5th order adaptive integration.
    
    Uses the Dormand-Prince RK45 method with adaptive step size control for
    accurate and efficient trajectory integration. This is the most accurate
    predictor but also the most computationally expensive.
    
    The RK45 method:
    - Uses 6 function evaluations per step
    - Estimates both 4th and 5th order solutions
    - Adapts step size based on local error estimate
    - Optimal balance between accuracy and computational cost
    
    Parameters
    ----------
    tol : float
        Error tolerance for adaptive step size. Smaller = more accurate.
        Default: 1e-3
    dt_initial : float
        Initial time step (s). Will be adapted. Default: 0.1s
    dt_min : float
        Minimum allowed time step (s). Default: 1e-4s
    dt_max : float
        Maximum allowed time step (s). Default: 1.0s
    max_iterations : int
        Maximum integration steps. Default: 1000
    """
    
    def __init__(
        self,
        tol: float = 1e-3,
        dt_initial: float = 0.1,
        dt_min: float = 1e-4,
        dt_max: float = 1.0,
        max_iterations: int = 1000
    ):
        """Initialize RK45 predictor with adaptive step size control."""
        self.tol = tol
        self.dt = dt_initial
        self.dt_min = dt_min
        self.dt_max = dt_max
        self.max_iterations = max_iterations
    
    def _derivatives(
        self,
        h: float,
        v: float,
        mass: float,
        drag_coefficient: float,
        reference_area: float,
        air_density_0: float
    ) -> Tuple[float, float]:
        """Compute derivatives dh/dt and dv/dt.
        
        Returns
        -------
        Tuple[float, float]
            (dh/dt, dv/dt) - velocity and acceleration
        """
        g = 9.81  # m/s²
        
        # Only compute air density if drag is non-zero
        if drag_coefficient > 0 and reference_area > 0:
            # Exponential atmosphere model
            H_scale = 8500  # m (scale height)
            air_density = air_density_0 * np.exp(-h / H_scale)
            
            # Drag acceleration
            if v > 0:
                drag_accel = (0.5 * air_density * v**2 * drag_coefficient * reference_area) / mass
            else:
                drag_accel = 0
        else:
            # No drag case
            drag_accel = 0
        
        dh_dt = v
        dv_dt = -g - drag_accel
        
        return dh_dt, dv_dt
    
    def predict_apogee(
        self,
        altitude: float,
        velocity_z: float,
        mass: float,
        drag_coefficient: float,
        reference_area: float,
        air_density: float,
        deployment_level: float
    ) -> float:
        """Predict apogee using RK45 adaptive integration."""
        if velocity_z <= 0:
            return altitude  # Already descending
        
        h = altitude
        v = velocity_z
        dt = self.dt
        
        # RK45 Dormand-Prince coefficients
        # Butcher tableau coefficients
        a21, a31, a32 = 1/5, 3/40, 9/40
        a41, a42, a43 = 44/45, -56/15, 32/9
        a51, a52, a53, a54 = 19372/6561, -25360/2187, 64448/6561, -212/729
        a61, a62, a63, a64, a65 = 9017/3168, -355/33, 46732/5247, 49/176, -5103/18656
        
        # 5th order solution weights
        b1, b2, b3, b4, b5, b6 = 35/384, 0, 500/1113, 125/192, -2187/6784, 11/84
        
        # 4th order solution weights (for error estimate)
        b1s, b2s, b3s, b4s, b5s, b6s = 5179/57600, 0, 7571/16695, 393/640, -92097/339200, 187/2100
        
        iteration = 0
        while iteration < self.max_iterations and v > 0:
            iteration += 1
            
            # K1
            k1_h, k1_v = self._derivatives(h, v, mass, drag_coefficient, reference_area, air_density)
            
            # K2
            k2_h, k2_v = self._derivatives(
                h + dt * a21 * k1_h,
                v + dt * a21 * k1_v,
                mass, drag_coefficient, reference_area, air_density
            )
            
            # K3
            k3_h, k3_v = self._derivatives(
                h + dt * (a31 * k1_h + a32 * k2_h),
                v + dt * (a31 * k1_v + a32 * k2_v),
                mass, drag_coefficient, reference_area, air_density
            )
            
            # K4
            k4_h, k4_v = self._derivatives(
                h + dt * (a41 * k1_h + a42 * k2_h + a43 * k3_h),
                v + dt * (a41 * k1_v + a42 * k2_v + a43 * k3_v),
                mass, drag_coefficient, reference_area, air_density
            )
            
            # K5
            k5_h, k5_v = self._derivatives(
                h + dt * (a51 * k1_h + a52 * k2_h + a53 * k3_h + a54 * k4_h),
                v + dt * (a51 * k1_v + a52 * k2_v + a53 * k3_v + a54 * k4_v),
                mass, drag_coefficient, reference_area, air_density
            )
            
            # K6
            k6_h, k6_v = self._derivatives(
                h + dt * (a61 * k1_h + a62 * k2_h + a63 * k3_h + a64 * k4_h + a65 * k5_h),
                v + dt * (a61 * k1_v + a62 * k2_v + a63 * k3_v + a64 * k4_v + a65 * k5_v),
                mass, drag_coefficient, reference_area, air_density
            )
            
            # 5th order solution
            h_new = h + dt * (b1*k1_h + b2*k2_h + b3*k3_h + b4*k4_h + b5*k5_h + b6*k6_h)
            v_new = v + dt * (b1*k1_v + b2*k2_v + b3*k3_v + b4*k4_v + b5*k5_v + b6*k6_v)
            
            # 4th order solution (for error estimate)
            h_err = h + dt * (b1s*k1_h + b2s*k2_h + b3s*k3_h + b4s*k4_h + b5s*k5_h + b6s*k6_h)
            v_err = v + dt * (b1s*k1_v + b2s*k2_v + b3s*k3_v + b4s*k4_v + b5s*k5_v + b6s*k6_v)
            
            # Error estimate (max of relative and absolute error)
            error_h = abs(h_new - h_err)
            error_v = abs(v_new - v_err)
            error = float(max(error_h / max(abs(h_new), 1.0), error_v / max(abs(v_new), 1.0)))
            
            # Adaptive step size control
            if error < self.tol or error == 0:
                # Accept step
                h = h_new
                v = v_new
                
                # Increase step size for next iteration (but not too much)
                if error > 0:
                    dt_new = 0.9 * dt * (self.tol / error) ** 0.2
                    dt = min(dt_new, self.dt_max)
                else:
                    # Error is zero (or negligible), increase step size moderately
                    dt = min(dt * 1.5, self.dt_max)
            else:
                # Reject step and retry with smaller dt
                dt_new = 0.9 * dt * (self.tol / error) ** 0.2
                dt = max(dt_new, self.dt_min)
                # Don't update h, v - retry this step with smaller dt
        
        return h


# ============================================================================
# AIR BRAKES CONTROLLER
# ============================================================================

@dataclass
class ControllerConfig:
    """Configuration for air brakes controller.

    This dataclass defines the control algorithm and hardware constraints
    for realistic air brakes actuation during flight.
    """

    # Control algorithm selection
    algorithm: str = "pid"  # Options: pid, bang_bang, model_predictive, custom

    # Target parameters
    target_apogee_m: float = 3000.0  # Target apogee altitude (m)
    apogee_tolerance_m: float = 50.0  # Acceptable apogee error (m)
    
    # Apogee prediction method
    apogee_prediction_method: str = "ballistic"  # Options: ballistic, euler, rk45
    
    # Numerical integrator parameters
    euler_dt: float = 0.05  # Euler time step (s)
    euler_max_iterations: int = 500  # Max Euler steps
    rk45_tol: float = 1e-3  # RK45 error tolerance
    rk45_dt_initial: float = 0.1  # RK45 initial time step (s)
    rk45_dt_min: float = 1e-4  # RK45 minimum time step (s)
    rk45_dt_max: float = 0.5  # RK45 maximum time step (s)
    rk45_max_iterations: int = 500  # Max RK45 steps

    # PID parameters (for algorithm="pid")
    kp: float = 0.001  # Proportional gain
    ki: float = 0.0001  # Integral gain
    kd: float = 0.01  # Derivative gain

    # Bang-bang parameters (for algorithm="bang_bang")
    deploy_threshold_m: float = 100.0  # Deploy if predicted overshoot > threshold

    # Hardware constraints
    sampling_rate_hz: float = 20.0  # Controller update frequency (Hz)
    computation_time_s: float = 0.005  # Microcontroller computation delay (5ms)
    actuator_lag_s: float = 0.050  # Servo motor lag time constant (50ms)
    max_deployment_rate: float = 2.0  # Maximum deployment speed (1/s, 0 to 1)

    # Safety constraints
    min_activation_time_s: float = 3.5  # Don't deploy before motor burnout
    min_activation_altitude_m: float = 500.0  # Don't deploy below this altitude
    retraction_altitude_m: float = 200.0  # Retract below this for landing
    
    # Air brakes physical parameters (for apogee prediction)
    airbrakes_cd: float = 1.5  # Air brakes drag coefficient when deployed
    airbrakes_area: float = 0.005  # Air brakes reference area (m²)
    rocket_diameter: float = 0.127  # Rocket diameter (m) for drag calculation
    
    # Physical model parameters (calculated automatically from rocket and environment)
    # These are NOT read from config file - they are computed by RocketBuilder
    rocket_mass: float = 15.0  # Rocket mass during coast (kg) - from rocket.dry_mass
    rocket_drag_coefficient: float = 0.45  # Rocket Cd (power-off, mean over Mach range) - from drag curve
    override_rocket_drag: bool = False  # If True, use ONLY airbrake drag; if False, ADD to rocket drag
    atmosphere_scale_height: float = 8500.0  # Atmospheric scale height H (m) - from environment
    sea_level_density: float = 1.225  # Sea level air density (kg/m³) - from environment

    # State estimation
    use_kalman_filter: bool = False  # Use Kalman filter for state estimation
    altitude_filter_alpha: float = 0.7  # EMA filter coefficient (if not Kalman)

    # Logging
    log_controller_data: bool = True  # Store controller data for analysis


class AirBrakesController:
    """Air brakes controller with realistic hardware modeling.

    This class implements control algorithms for air brakes deployment,
    accounting for real-world hardware constraints like servo lag,
    computation delays, and rate limiting.

    The controller is designed to be used with RocketPy's Flight simulation
    via the controller_function interface.

    Attributes:
        config: ControllerConfig with algorithm parameters and constraints
        _integral: Integral term for PID controller
        _prev_error: Previous error for derivative calculation
        _commanded_deployment: Commanded deployment level [0, 1]
        _actual_deployment: Actual deployment level after lag [0, 1]
        _computation_buffer: Buffer for computation delay simulation

    Example:
        >>> config = ControllerConfig(
        ...     algorithm="pid",
        ...     target_apogee_m=3000,
        ...     kp=0.001, ki=0.0001, kd=0.01,
        ...     sampling_rate_hz=20,
        ... )
        >>> controller = AirBrakesController(config)
        >>> controller_func = controller.get_controller_function()
        >>>
        >>> # Add to RocketPy rocket
        >>> air_brakes = rocket.add_air_brakes(
        ...     drag_coefficient_curve="path/to/cd.csv",
        ...     controller_function=controller_func,
        ...     sampling_rate=config.sampling_rate_hz,
        ... )
    """

    def __init__(self, config: ControllerConfig):
        """Initialize air brakes controller.

        Args:
            config: ControllerConfig with algorithm and hardware parameters
        """
        self.config = config

        # Controller state
        self._integral = 0.0
        self._prev_error = 0.0
        self._commanded_deployment = 0.0
        self._actual_deployment = 0.0

        # Computation delay buffer (stores commanded deployment)
        self._computation_buffer: List[Tuple[float, float]] = []  # [(time, command)]

        # Filtered state (for noise reduction)
        self._filtered_altitude = None
        self._filtered_velocity = None

        # Data storage for plotting and analysis
        self.time_history: List[float] = []
        self.commanded_deployment_history: List[float] = []
        self.actual_deployment_history: List[float] = []
        self.predicted_apogee_history: List[float] = []
        self.error_history: List[float] = []
        self.p_term_history: List[float] = []
        self.i_term_history: List[float] = []
        self.d_term_history: List[float] = []
        self.control_signal_history: List[float] = []

        logger.info(f"AirBrakesController initialized: algorithm={config.algorithm}, "
                   f"target={config.target_apogee_m}m, rate={config.sampling_rate_hz}Hz")

    def reset_state(self):
        """Reset controller state for new simulation.

        This method should be called between Monte Carlo runs to prevent
        state contamination. It's automatically called on first controller
        invocation (when observed_variables is empty).
        """
        self._integral = 0.0
        self._prev_error = 0.0
        self._commanded_deployment = 0.0
        self._actual_deployment = 0.0
        self._computation_buffer = []
        self._filtered_altitude = None
        self._filtered_velocity = None
        
        # Clear history data
        self.time_history = []
        self.commanded_deployment_history = []
        self.actual_deployment_history = []
        self.predicted_apogee_history = []
        self.error_history = []
        self.p_term_history = []
        self.i_term_history = []
        self.d_term_history = []
        self.control_signal_history = []
        
        logger.debug("Controller state reset for new simulation")

    def generate_parameters_documentation(self, filepath: str):
        """Generate a comprehensive .txt file documenting all controller parameters.
        
        This creates a human-readable documentation of all parameters used by the
        air brakes controller, including both user-configured and automatically
        calculated values.
        
        Args:
            filepath: Path where to save the documentation file (.txt)
        
        Example:
            >>> controller.generate_parameters_documentation('outputs/airbrake_params.txt')
        """
        from datetime import datetime
        
        doc = []
        doc.append("=" * 80)
        doc.append("AIR BRAKES CONTROLLER - PARAMETERS DOCUMENTATION")
        doc.append("=" * 80)
        doc.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        doc.append("")
        
        # Control Algorithm
        doc.append("-" * 80)
        doc.append("CONTROL ALGORITHM")
        doc.append("-" * 80)
        doc.append(f"Algorithm:                     {self.config.algorithm}")
        doc.append(f"Target apogee:                 {self.config.target_apogee_m:.1f} m")
        doc.append(f"Apogee prediction method:      {self.config.apogee_prediction_method}")
        doc.append("")
        
        # PID Gains (if applicable)
        if self.config.algorithm == "pid":
            doc.append("-" * 80)
            doc.append("PID CONTROLLER GAINS")
            doc.append("-" * 80)
            doc.append(f"Proportional gain (Kp):        {self.config.kp:.6f}")
            doc.append(f"Integral gain (Ki):            {self.config.ki:.6f}")
            doc.append(f"Derivative gain (Kd):          {self.config.kd:.6f}")
            doc.append("")
        
        # Numerical Integration Parameters
        doc.append("-" * 80)
        doc.append("APOGEE PREDICTION - NUMERICAL INTEGRATION")
        doc.append("-" * 80)
        if self.config.apogee_prediction_method == "euler":
            doc.append(f"Method:                        Forward Euler")
            doc.append(f"Time step (dt):                {self.config.euler_dt:.4f} s")
            doc.append(f"Max iterations:                {self.config.euler_max_iterations}")
        elif self.config.apogee_prediction_method == "rk45":
            doc.append(f"Method:                        Runge-Kutta 4/5 (Dormand-Prince)")
            doc.append(f"Error tolerance:               {self.config.rk45_tol:.1e}")
            doc.append(f"Initial time step:             {self.config.rk45_dt_initial:.4f} s")
            doc.append(f"Min time step:                 {self.config.rk45_dt_min:.1e} s")
            doc.append(f"Max time step:                 {self.config.rk45_dt_max:.4f} s")
            doc.append(f"Max iterations:                {self.config.rk45_max_iterations}")
        else:
            doc.append(f"Method:                        Ballistic (constant deceleration)")
            doc.append(f"Formula:                       h_apo = h + v²/(2g)")
        doc.append("")
        
        # Hardware Constraints
        doc.append("-" * 80)
        doc.append("HARDWARE CONSTRAINTS")
        doc.append("-" * 80)
        doc.append(f"Sampling rate:                 {self.config.sampling_rate_hz:.1f} Hz")
        doc.append(f"Computation delay:             {self.config.computation_time_s * 1000:.1f} ms")
        doc.append(f"Actuator lag (servo):          {self.config.actuator_lag_s * 1000:.1f} ms")
        doc.append(f"Max deployment rate:           {self.config.max_deployment_rate:.2f} /s")
        doc.append("")
        
        # Safety Constraints
        doc.append("-" * 80)
        doc.append("SAFETY CONSTRAINTS")
        doc.append("-" * 80)
        doc.append(f"Min activation time:           {self.config.min_activation_time_s:.1f} s")
        doc.append(f"Min activation altitude:       {self.config.min_activation_altitude_m:.1f} m")
        doc.append("")
        
        # Physical Model - Rocket
        doc.append("-" * 80)
        doc.append("PHYSICAL MODEL - ROCKET PARAMETERS")
        doc.append("-" * 80)
        doc.append(f"Rocket mass (coast):           {self.config.rocket_mass:.2f} kg")
        doc.append(f"  Source:                      rocket.dry_mass (automatic)")
        doc.append(f"Rocket diameter:               {self.config.rocket_diameter:.4f} m")
        doc.append(f"  Source:                      rocket.geometry.caliber_m")
        doc.append(f"Rocket drag coefficient:       {self.config.rocket_drag_coefficient:.4f}")
        doc.append(f"  Source:                      Mean Cd from power_off_drag curve (automatic)")
        doc.append(f"Rocket reference area:         {np.pi * (self.config.rocket_diameter/2)**2:.6f} m²")
        doc.append(f"  Formula:                     π * (diameter/2)²")
        doc.append("")
        
        # Physical Model - Air Brakes
        doc.append("-" * 80)
        doc.append("PHYSICAL MODEL - AIR BRAKES PARAMETERS")
        doc.append("-" * 80)
        doc.append(f"Air brakes drag coefficient:   {self.config.airbrakes_cd:.2f}")
        doc.append(f"  Source:                      User configuration")
        doc.append(f"Air brakes reference area:     {self.config.airbrakes_area:.6f} m²")
        doc.append(f"  Source:                      User configuration")
        doc.append(f"Override rocket drag:          {self.config.override_rocket_drag}")
        doc.append(f"  Description:                 false=ADD airbrake to rocket drag (default)")
        doc.append(f"                               true=use ONLY airbrake drag")
        doc.append("")
        
        # Drag Model
        doc.append("-" * 80)
        doc.append("DRAG MODEL")
        doc.append("-" * 80)
        if self.config.override_rocket_drag:
            doc.append(f"Mode:                          AIRBRAKE ONLY")
            doc.append(f"Total drag area:               Cd_ab * A_ab * deployment")
            doc.append(f"  = {self.config.airbrakes_cd:.2f} * {self.config.airbrakes_area:.6f} * deployment")
        else:
            doc.append(f"Mode:                          ROCKET + AIRBRAKE (default)")
            doc.append(f"Total drag area:               Cd_rocket * A_rocket + Cd_ab * A_ab * deployment")
            rocket_area = np.pi * (self.config.rocket_diameter/2)**2
            doc.append(f"  = {self.config.rocket_drag_coefficient:.4f} * {rocket_area:.6f} + {self.config.airbrakes_cd:.2f} * {self.config.airbrakes_area:.6f} * deployment")
        doc.append(f"Effective Cd:                  total_drag_area / rocket_reference_area")
        doc.append("")
        
        # Atmospheric Model
        doc.append("-" * 80)
        doc.append("ATMOSPHERIC MODEL")
        doc.append("-" * 80)
        doc.append(f"Model:                         Exponential atmosphere")
        doc.append(f"Density formula:               ρ(h) = ρ₀ * exp(-h/H)")
        doc.append(f"Scale height (H):              {self.config.atmosphere_scale_height:.1f} m")
        doc.append(f"  Source:                      Fitted from environment model (automatic)")
        doc.append(f"Sea level density (ρ₀):        {self.config.sea_level_density:.4f} kg/m³")
        doc.append(f"  Source:                      From environment model (automatic)")
        doc.append("")
        
        # State Estimation
        doc.append("-" * 80)
        doc.append("STATE ESTIMATION")
        doc.append("-" * 80)
        doc.append(f"Kalman filter:                 {self.config.use_kalman_filter}")
        if not self.config.use_kalman_filter:
            doc.append(f"Altitude filter (EMA alpha):   {self.config.altitude_filter_alpha:.2f}")
            doc.append(f"  (0=max filtering, 1=no filtering)")
        doc.append("")
        
        # Summary
        doc.append("=" * 80)
        doc.append("NOTES")
        doc.append("=" * 80)
        doc.append("Parameters marked 'automatic' are calculated from rocket configuration")
        doc.append("and environment model to ensure consistency between simulation and prediction.")
        doc.append("")
        doc.append("For questions or issues, refer to the DySi documentation:")
        doc.append("  docs/user/air_brakes_controller.md")
        doc.append("=" * 80)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(doc))
        
        logger.info(f"Air brakes parameters documentation saved to: {filepath}")

    def get_controller_function(self) -> Callable:
        """Get controller function for RocketPy integration.

        Returns:
            Callable controller function with signature:
            (time, sampling_rate, state, state_history, observed_variables,
             air_brakes, sensors) -> tuple

        Example:
            >>> controller_func = controller.get_controller_function()
            >>> air_brakes = rocket.add_air_brakes(
            ...     drag_coefficient_curve="cd.csv",
            ...     controller_function=controller_func,
            ...     sampling_rate=20,
            ... )
        """
        def controller_function(
            time: float,
            sampling_rate: float,
            state: List[float],
            state_history: List[List[float]],
            observed_variables: List,
            air_brakes,
            sensors: Optional[List] = None
        ):
            """RocketPy controller function with realistic hardware modeling.

            Args:
                time: Current simulation time (s)
                sampling_rate: Controller sampling rate (Hz)
                state: Current state [x,y,z,vx,vy,vz,e0,e1,e2,e3,wx,wy,wz]
                state_history: List of all previous states
                observed_variables: List of previous controller outputs
                air_brakes: AirBrakes instance to control
                sensors: Optional list of sensor instances

            Returns:
                Tuple with (time, commanded_deployment, actual_deployment,
                           target_apogee, predicted_apogee, control_signal)
            """
            # Extract state
            altitude = state[2]  # z position (m)
            vz = state[5]  # vertical velocity (m/s)

            # Initialize/reset on first call (new simulation)
            if not observed_variables:
                # Auto-reset state for new simulation (prevents Monte Carlo contamination)
                self.reset_state()
                self._filtered_altitude = altitude
                self._filtered_velocity = vz
                air_brakes.deployment_level = 0.0
                return (time, 0.0, 0.0, self.config.target_apogee_m, 0.0, 0.0)

            # --- Safety checks ---

            # Don't deploy during motor burn
            if time < self.config.min_activation_time_s:
                air_brakes.deployment_level = 0.0
                return (time, 0.0, 0.0, self.config.target_apogee_m, altitude, 0.0)

            # Don't deploy below minimum altitude
            if altitude < self.config.min_activation_altitude_m:
                air_brakes.deployment_level = 0.0
                return (time, 0.0, 0.0, self.config.target_apogee_m, altitude, 0.0)

            # Retract for landing
            if altitude < self.config.retraction_altitude_m and vz < 0:
                air_brakes.deployment_level = 0.0
                return (time, 0.0, 0.0, self.config.target_apogee_m, altitude, 0.0)

            # --- State filtering ---

            dt = 1.0 / sampling_rate

            if self.config.use_kalman_filter:
                # TODO: Implement Kalman filter for robust state estimation
                filtered_altitude = altitude
                filtered_vz = vz
            else:
                # Simple exponential moving average (EMA) filter
                alpha = self.config.altitude_filter_alpha
                filtered_altitude = alpha * altitude + (1 - alpha) * self._filtered_altitude
                filtered_vz = alpha * vz + (1 - alpha) * self._filtered_velocity

            self._filtered_altitude = filtered_altitude
            self._filtered_velocity = filtered_vz

            # --- Apogee prediction ---

            # Initialize predictor on first use
            if not hasattr(self, '_apogee_predictor'):
                if self.config.apogee_prediction_method == "euler":
                    self._apogee_predictor = EulerPredictor(
                        dt=self.config.euler_dt,
                        max_iterations=self.config.euler_max_iterations
                    )
                elif self.config.apogee_prediction_method == "rk45":
                    self._apogee_predictor = RK45Predictor(
                        tol=self.config.rk45_tol,
                        dt_initial=self.config.rk45_dt_initial,
                        dt_min=self.config.rk45_dt_min,
                        dt_max=self.config.rk45_dt_max,
                        max_iterations=self.config.rk45_max_iterations
                    )
                else:  # ballistic
                    self._apogee_predictor = ConstantDecelerationPredictor()
            
            # Get rocket parameters for physics-based prediction
            rocket_mass = self.config.rocket_mass  # kg
            
            # Base rocket drag (power-off configuration)
            rocket_drag_coefficient = self.config.rocket_drag_coefficient
            rocket_diameter = self.config.rocket_diameter  # m
            rocket_reference_area = np.pi * (rocket_diameter / 2) ** 2  # m²
            
            # Air brakes contribution (when deployed)
            airbrakes_cd = self.config.airbrakes_cd
            airbrakes_area = self.config.airbrakes_area  # m²
            
            # CRITICAL: Calculate TOTAL drag accounting for current air brakes deployment
            # Two modes based on override_rocket_drag setting:
            # 
            # Mode 1 (override_rocket_drag=False, DEFAULT): ADD air brakes drag to rocket drag
            #   Total drag = rocket_drag + air_brakes_drag
            #   Cd_eff * A_ref = Cd_rocket * A_rocket + Cd_brakes * A_brakes * deployment
            #   This is the standard RocketPy behavior (override_rocket_drag=False)
            #
            # Mode 2 (override_rocket_drag=True): Use ONLY air brakes drag
            #   Total drag = air_brakes_drag
            #   Cd_eff * A_ref = Cd_brakes * A_brakes * deployment
            #   Use when airbrake has its own Mach-dependent curve and replaces rocket drag
            
            current_deployment = self._actual_deployment
            
            if self.config.override_rocket_drag:
                # Mode 2: Only airbrake drag
                total_drag_area = airbrakes_cd * airbrakes_area * current_deployment
            else:
                # Mode 1: Rocket drag + airbrake drag (DEFAULT)
                total_drag_area = (rocket_drag_coefficient * rocket_reference_area + 
                                  airbrakes_cd * airbrakes_area * current_deployment)
            
            # Use rocket area as reference and calculate effective Cd
            effective_drag_coefficient = total_drag_area / rocket_reference_area
            
            # Air density at current altitude (exponential atmosphere model)
            air_density = self.config.sea_level_density * np.exp(
                -filtered_altitude / self.config.atmosphere_scale_height
            )
            
            # Predict apogee using selected method with CURRENT air brakes configuration
            predicted_apogee = self._apogee_predictor.predict_apogee(
                altitude=filtered_altitude,
                velocity_z=filtered_vz,
                mass=rocket_mass,
                drag_coefficient=effective_drag_coefficient,
                reference_area=rocket_reference_area,
                air_density=air_density,
                deployment_level=current_deployment  # passed for info, already in Cd_effective
            )

            # --- Control algorithm selection ---

            if self.config.algorithm == "pid":
                control_signal, error, p_term, i_term, d_term = self._pid_control(
                    predicted_apogee,
                    filtered_vz,
                    dt
                )
            elif self.config.algorithm == "bang_bang":
                control_signal = self._bang_bang_control(
                    predicted_apogee,
                    self.config.target_apogee_m
                )
                error = predicted_apogee - self.config.target_apogee_m
                p_term = i_term = d_term = 0.0
            elif self.config.algorithm == "model_predictive":
                control_signal = self._model_predictive_control(
                    filtered_altitude,
                    filtered_vz,
                    predicted_apogee
                )
                error = predicted_apogee - self.config.target_apogee_m
                p_term = i_term = d_term = 0.0
            else:
                logger.warning(f"Unknown algorithm '{self.config.algorithm}', using PID")
                control_signal, error, p_term, i_term, d_term = self._pid_control(
                    predicted_apogee, filtered_vz, dt
                )

            # --- Hardware constraints ---

            # 1. Computation delay: Store command, retrieve delayed command
            self._computation_buffer.append((time, control_signal))

            delayed_command = 0.0
            for buf_time, buf_command in self._computation_buffer:
                if time - buf_time >= self.config.computation_time_s:
                    delayed_command = buf_command
                    break

            # Clean old buffer entries (keep last 10)
            if len(self._computation_buffer) > 10:
                self._computation_buffer = self._computation_buffer[-10:]

            self._commanded_deployment = delayed_command

            # 2. Rate limiting (maximum deployment speed)
            max_change = self.config.max_deployment_rate * dt
            rate_limited = np.clip(
                delayed_command,
                self._actual_deployment - max_change,
                self._actual_deployment + max_change
            )

            # 3. Actuator lag (first-order lag, servo motor dynamics)
            # τ * dy/dt + y = u  →  y(t+dt) ≈ y(t) + (u - y(t)) * dt / τ
            tau = self.config.actuator_lag_s
            lag_factor = dt / (tau + dt)  # Discrete first-order lag
            self._actual_deployment += (rate_limited - self._actual_deployment) * lag_factor

            # 4. Clamp to [0, 1]
            self._actual_deployment = np.clip(self._actual_deployment, 0.0, 1.0)

            # --- Apply to air brakes ---
            air_brakes.deployment_level = self._actual_deployment

            # --- Save data for plotting ---
            self.time_history.append(time)
            self.commanded_deployment_history.append(self._commanded_deployment)
            self.actual_deployment_history.append(self._actual_deployment)
            self.predicted_apogee_history.append(predicted_apogee)
            self.error_history.append(error)
            self.p_term_history.append(p_term)
            self.i_term_history.append(i_term)
            self.d_term_history.append(d_term)
            self.control_signal_history.append(control_signal)

            # --- Return data for logging ---
            return (
                time,
                self._commanded_deployment,  # What controller commanded
                self._actual_deployment,     # What actually happened
                self.config.target_apogee_m,
                predicted_apogee,
                control_signal  # Raw control output before delays
            )

        return controller_function

    def _pid_control(
        self,
        predicted_apogee: float,
        velocity_z: float,
        dt: float
    ) -> tuple:
        """PID control algorithm for air brakes deployment.

        Args:
            predicted_apogee: Predicted apogee altitude (m)
            velocity_z: Vertical velocity (m/s)
            dt: Time step (s)

        Returns:
            Tuple of (deployment, error, p_term, i_term, d_term)
        """
        # Error: positive if overshooting target
        error = predicted_apogee - self.config.target_apogee_m

        # PID terms
        proportional = self.config.kp * error

        self._integral += error * dt
        # Anti-windup: clamp integral
        self._integral = np.clip(self._integral, -100, 100)
        integral = self.config.ki * self._integral

        derivative = self.config.kd * (error - self._prev_error) / dt if dt > 0 else 0
        self._prev_error = error

        # PID output
        output = proportional + integral + derivative

        # Map to [0, 1] deployment
        # Deploy more if overshooting (positive error)
        deployment = np.clip(output, 0.0, 1.0)

        return deployment, error, proportional, integral, derivative

    def _bang_bang_control(
        self,
        predicted_apogee: float,
        target_apogee: float
    ) -> float:
        """Bang-bang (on-off) control for air brakes.

        Simple two-state controller: fully deployed if overshooting,
        fully retracted otherwise.

        Args:
            predicted_apogee: Predicted apogee altitude (m)
            target_apogee: Target apogee altitude (m)

        Returns:
            Deployment level: 0.0 or 1.0
        """
        error = predicted_apogee - target_apogee

        if error > self.config.deploy_threshold_m:
            return 1.0  # Fully deploy
        else:
            return 0.0  # Fully retract

    def _model_predictive_control(
        self,
        altitude: float,
        velocity_z: float,
        predicted_apogee: float
    ) -> float:
        """Model predictive control (simplified version).

        This is a placeholder for advanced MPC algorithms that optimize
        trajectory over a prediction horizon. Current implementation is
        a simple proportional controller with velocity feedforward.

        Args:
            altitude: Current altitude (m)
            velocity_z: Vertical velocity (m/s)
            predicted_apogee: Predicted apogee (m)

        Returns:
            Deployment level [0, 1]
        """
        # Simple model-based approach:
        # Deploy proportionally to overshoot, scaled by velocity

        error = predicted_apogee - self.config.target_apogee_m

        # Proportional term
        proportional = 0.001 * error

        # Velocity feedforward (more aggressive if ascending fast)
        if velocity_z > 0:
            feedforward = 0.01 * velocity_z
        else:
            feedforward = 0.0

        deployment = proportional + feedforward
        deployment = np.clip(deployment, 0.0, 1.0)

        return deployment


def create_pid_controller(
    target_apogee_m: float,
    kp: float = 0.001,
    ki: float = 0.0001,
    kd: float = 0.01,
    sampling_rate_hz: float = 20.0,
    actuator_lag_s: float = 0.050,
    max_rate: float = 2.0
) -> AirBrakesController:
    """Create a PID air brakes controller with common defaults.

    Convenience function for quickly creating a PID controller with
    typical parameters for competition rockets.

    Args:
        target_apogee_m: Target apogee altitude (m)
        kp: Proportional gain (default: 0.001)
        ki: Integral gain (default: 0.0001)
        kd: Derivative gain (default: 0.01)
        sampling_rate_hz: Controller update rate (default: 20 Hz)
        actuator_lag_s: Servo lag time constant (default: 50ms)
        max_rate: Maximum deployment speed (default: 2.0 per second)

    Returns:
        Configured AirBrakesController instance

    Example:
        >>> controller = create_pid_controller(
        ...     target_apogee_m=3000,
        ...     kp=0.002, ki=0.0002, kd=0.015
        ... )
        >>> controller_func = controller.get_controller_function()
    """
    config = ControllerConfig(
        algorithm="pid",
        target_apogee_m=target_apogee_m,
        kp=kp,
        ki=ki,
        kd=kd,
        sampling_rate_hz=sampling_rate_hz,
        actuator_lag_s=actuator_lag_s,
        max_deployment_rate=max_rate,
    )
    return AirBrakesController(config)


def create_bang_bang_controller(
    target_apogee_m: float,
    deploy_threshold_m: float = 100.0,
    sampling_rate_hz: float = 10.0,
    actuator_lag_s: float = 0.050
) -> AirBrakesController:
    """Create a bang-bang (on-off) air brakes controller.

    Bang-bang controllers are simple and robust but result in oscillatory
    behavior. Suitable for initial testing or systems with fast actuators.

    Args:
        target_apogee_m: Target apogee altitude (m)
        deploy_threshold_m: Deploy if overshoot exceeds this (default: 100m)
        sampling_rate_hz: Controller update rate (default: 10 Hz)
        actuator_lag_s: Servo lag time constant (default: 50ms)

    Returns:
        Configured AirBrakesController instance

    Example:
        >>> controller = create_bang_bang_controller(
        ...     target_apogee_m=3000,
        ...     deploy_threshold_m=50
        ... )
    """
    config = ControllerConfig(
        algorithm="bang_bang",
        target_apogee_m=target_apogee_m,
        deploy_threshold_m=deploy_threshold_m,
        sampling_rate_hz=sampling_rate_hz,
        actuator_lag_s=actuator_lag_s,
    )
    return AirBrakesController(config)


# Example controller functions for direct use (without class wrapper)

def simple_apogee_controller(
    target_apogee: float = 3000.0,
    kp: float = 0.001
) -> Callable:
    """Create a simple proportional controller function.

    This is a lightweight alternative to AirBrakesController for simple
    use cases where full hardware modeling is not needed.

    Args:
        target_apogee: Target apogee altitude (m)
        kp: Proportional gain

    Returns:
        Controller function compatible with RocketPy

    Example:
        >>> controller_func = simple_apogee_controller(target_apogee=3000)
        >>> air_brakes = rocket.add_air_brakes(
        ...     drag_coefficient_curve="cd.csv",
        ...     controller_function=controller_func,
        ...     sampling_rate=10
        ... )
    """
    def controller(time, sampling_rate, state, state_history,
                  observed_variables, air_brakes, sensors=None):
        altitude = state[2]
        vz = state[5]

        # Don't deploy during motor burn (first 4 seconds)
        if time < 4.0:
            air_brakes.deployment_level = 0.0
            return None

        # Predict apogee (simple ballistic)
        g = 9.81
        predicted_apogee = altitude + (vz ** 2) / (2 * g) if vz > 0 else altitude

        # Proportional control
        error = predicted_apogee - target_apogee
        deployment = kp * error
        deployment = np.clip(deployment, 0.0, 1.0)

        air_brakes.deployment_level = deployment

        return (time, deployment, predicted_apogee)

    return controller
