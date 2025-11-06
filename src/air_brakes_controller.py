"""Air brakes controller implementation with realistic hardware constraints.

This module provides control laws for air brakes systems, accounting for:
- Servo motor lag (actuation delay)
- Microcontroller computation time
- Rate limiting (maximum deployment speed)
- Sensor noise and filtering
- Different control algorithms (PID, bang-bang, model-predictive)
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Callable
import numpy as np
import logging

logger = logging.getLogger(__name__)


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

        logger.info(f"AirBrakesController initialized: algorithm={config.algorithm}, "
                   f"target={config.target_apogee_m}m, rate={config.sampling_rate_hz}Hz")

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

            # Initialize on first call
            if not observed_variables:
                self._filtered_altitude = altitude
                self._filtered_velocity = vz
                self._integral = 0.0
                self._prev_error = 0.0
                self._commanded_deployment = 0.0
                self._actual_deployment = 0.0
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

            # Simple ballistic trajectory prediction (ignoring drag for simplicity)
            # More sophisticated: use current drag to predict
            g = 9.81  # m/s²

            if filtered_vz > 0:
                # Ascending: predict apogee assuming constant deceleration
                predicted_apogee = filtered_altitude + (filtered_vz ** 2) / (2 * g)
            else:
                # Descending: already past apogee
                predicted_apogee = filtered_altitude

            # --- Control algorithm selection ---

            if self.config.algorithm == "pid":
                control_signal = self._pid_control(
                    predicted_apogee,
                    filtered_vz,
                    dt
                )
            elif self.config.algorithm == "bang_bang":
                control_signal = self._bang_bang_control(
                    predicted_apogee,
                    self.config.target_apogee_m
                )
            elif self.config.algorithm == "model_predictive":
                control_signal = self._model_predictive_control(
                    filtered_altitude,
                    filtered_vz,
                    predicted_apogee
                )
            else:
                logger.warning(f"Unknown algorithm '{self.config.algorithm}', using PID")
                control_signal = self._pid_control(predicted_apogee, filtered_vz, dt)

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
    ) -> float:
        """PID control algorithm for air brakes deployment.

        Args:
            predicted_apogee: Predicted apogee altitude (m)
            velocity_z: Vertical velocity (m/s)
            dt: Time step (s)

        Returns:
            Control signal [0, 1] for deployment level
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

        return deployment

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
