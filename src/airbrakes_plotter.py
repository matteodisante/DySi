"""Air brakes visualization module.

This module provides specialized plotting functions for air brakes control data,
including deployment levels, controller output, apogee predictions, and PID terms.
"""

from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
import logging

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from src.air_brakes_controller import AirBrakesController

logger = logging.getLogger(__name__)


class AirBrakesPlotter:
    """Plotter for air brakes control data and performance analysis.
    
    This class creates comprehensive visualizations of air brakes behavior during
    flight, including:
    - Commanded vs actual deployment (showing lag effects)
    - PID controller terms (P, I, D components)
    - Apogee prediction vs actual apogee
    - Control errors and corrections
    - Deployment rate and saturation analysis
    
    Attributes:
        controller: AirBrakesController instance with history data
        output_dir: Directory for saving plots
        burnout_time: Motor burnout time (s)
        apogee_time: Apogee time (s)
        parachute_deploy_time: Parachute deployment time (s)
        target_apogee: Target apogee (m)
    """
    
    def __init__(
        self,
        controller: 'AirBrakesController',
        output_dir: str = "outputs/curves/airbrakes",
        burnout_time: Optional[float] = None,
        apogee_time: Optional[float] = None,
        parachute_deploy_time: Optional[float] = None,
        target_apogee: Optional[float] = None
    ):
        """Initialize AirBrakesPlotter.
        
        Args:
            controller: AirBrakesController instance with recorded history data
            output_dir: Directory where plots will be saved
            burnout_time: Motor burnout time (s) for event marker
            apogee_time: Apogee time (s) for event marker
            parachute_deploy_time: Parachute deployment time (s) for event marker
            target_apogee: Target apogee (m) for reference lines
        """
        self.controller = controller
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Critical flight events for markers
        self.burnout_time = burnout_time
        self.apogee_time = apogee_time
        self.parachute_deploy_time = parachute_deploy_time
        self.target_apogee = target_apogee or controller.config.target_apogee_m
        
        # Extract data from controller
        self.time = np.array(controller.time_history)
        self.commanded_deployment = np.array(controller.commanded_deployment_history)
        self.actual_deployment = np.array(controller.actual_deployment_history)
        self.predicted_apogee = np.array(controller.predicted_apogee_history)
        self.error = np.array(controller.error_history)
        self.p_term = np.array(controller.p_term_history)
        self.i_term = np.array(controller.i_term_history)
        self.d_term = np.array(controller.d_term_history)
        self.control_signal = np.array(controller.control_signal_history)
        
        # Limit time axis to parachute deployment (or slightly after apogee if no parachute time)
        if parachute_deploy_time is not None:
            # Add 2 seconds margin after parachute deployment
            self.time_limit = parachute_deploy_time + 2.0
        elif apogee_time is not None:
            # If no parachute time, use apogee + 5 seconds
            self.time_limit = apogee_time + 5.0
        else:
            # Fallback to full time range
            self.time_limit = self.time[-1] if len(self.time) > 0 else 100.0
        
        # Filter data to time_limit
        if len(self.time) > 0:
            mask = self.time <= self.time_limit
            self.time = self.time[mask]
            self.commanded_deployment = self.commanded_deployment[mask]
            self.actual_deployment = self.actual_deployment[mask]
            self.predicted_apogee = self.predicted_apogee[mask]
            self.error = self.error[mask]
            self.p_term = self.p_term[mask]
            self.i_term = self.i_term[mask]
            self.d_term = self.d_term[mask]
            self.control_signal = self.control_signal[mask]
        
        logger.info(f"AirBrakesPlotter initialized, output: {self.output_dir}, time_limit: {self.time_limit:.1f}s")
    
    def _add_event_markers(
        self,
        ax,
        time_limit: float,
        add_legend: bool = True,
        include_burnout: bool = True,
        include_apogee: bool = True,
        include_parachute: bool = True
    ) -> None:
        """Add vertical lines marking critical flight events.
        
        Args:
            ax: Matplotlib axis to add markers to
            time_limit: Maximum time shown in plot
            add_legend: Whether to add legend
            include_burnout: Include motor burnout marker
            include_apogee: Include apogee marker
            include_parachute: Include parachute deployment marker
        """
        added_markers = False
        
        # Burnout
        if include_burnout and self.burnout_time and self.burnout_time <= time_limit:
            ax.axvline(x=self.burnout_time, color='#FF8C00', linestyle='--',
                      linewidth=1.5, alpha=0.7, label='Burnout', zorder=100)
            added_markers = True
        
        # Apogee
        if include_apogee and self.apogee_time and self.apogee_time <= time_limit:
            ax.axvline(x=self.apogee_time, color='#DC143C', linestyle='-',
                      linewidth=2, alpha=0.8, label='Apogee', zorder=100)
            added_markers = True
        
        # Parachute deployment
        if include_parachute and self.parachute_deploy_time and self.parachute_deploy_time <= time_limit:
            ax.axvline(x=self.parachute_deploy_time, color='#228B22', linestyle=':',
                      linewidth=1.5, alpha=0.7, label='Parachute', zorder=100)
            added_markers = True
        
        if added_markers and add_legend:
            # Get existing handles and add event markers to legend
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(loc='best', fontsize=9, framealpha=0.9)
    
    def plot_deployment_comparison(
        self,
        filename: str = "deployment_comparison.png"
    ) -> Optional[Path]:
        """Plot commanded vs actual deployment showing lag effects.
        
        This plot shows:
        - Commanded deployment (what controller wants)
        - Actual deployment (what physically happens after lag)
        - Difference highlighting servo lag and rate limiting
        
        Args:
            filename: Output filename
            
        Returns:
            Path to saved plot or None if data unavailable
        """
        try:
            output_path = self.output_dir / filename
            
            # Check if data exists
            if len(self.time) == 0:
                logger.warning("No air brakes deployment data available")
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # --- Subplot 1: Deployment levels ---
            ax1.plot(self.time, self.commanded_deployment * 100, 'r--', linewidth=2, 
                    label='Commanded Deployment', alpha=0.8, zorder=5)
            
            ax1.plot(self.time, self.actual_deployment * 100, 'b-', linewidth=2.5,
                    label='Actual Deployment', alpha=0.9, zorder=6)
            
            ax1.set_ylabel('Deployment Level (%)', fontsize=12, fontweight='bold')
            ax1.set_title('Air Brakes Deployment: Commanded vs Actual', 
                         fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(-5, 105)
            
            # Add deployment zones
            ax1.axhspan(0, 10, alpha=0.1, color='green', label='Retracted (<10%)')
            ax1.axhspan(90, 100, alpha=0.1, color='red', label='Fully Deployed (>90%)')
            
            # Event markers
            self._add_event_markers(ax1, self.time_limit, add_legend=False)
            
            ax1.legend(loc='best', fontsize=10, framealpha=0.9, ncol=2)
            
            # --- Subplot 2: Lag error ---
            lag_error = (self.commanded_deployment - self.actual_deployment) * 100
            ax2.plot(self.time, lag_error, 'purple', linewidth=2, alpha=0.8)
            ax2.fill_between(self.time, 0, lag_error, alpha=0.3, color='purple')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
            
            ax2.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Lag Error (%)', fontsize=12, fontweight='bold')
            ax2.set_title('Commanded - Actual (Servo Lag Effect)', 
                         fontsize=13, fontweight='bold')
            ax2.grid(True, alpha=0.3, linestyle='--')
            
            # Annotate max lag
            max_lag_idx = np.argmax(np.abs(lag_error))
            max_lag = lag_error[max_lag_idx]
            max_lag_time = self.time[max_lag_idx]
            ax2.annotate(f'Max lag: {max_lag:.1f}%',
                       xy=(max_lag_time, max_lag),
                       xytext=(max_lag_time + 2, max_lag * 1.2),
                       fontsize=9, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.4', facecolor='yellow', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='purple', lw=1.5))
            
            self._add_event_markers(ax2, self.time_limit, add_legend=True,
                                   include_parachute=False)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Deployment comparison plot saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating deployment comparison plot: {e}", exc_info=True)
            return None
    
    def plot_controller_performance(
        self,
        filename: str = "controller_performance.png"
    ) -> Optional[Path]:
        """Plot controller performance: error, PID terms, and apogee prediction.
        
        This plot shows:
        - Apogee prediction error vs time
        - PID controller terms (P, I, D)
        - Predicted vs target apogee evolution
        
        Args:
            filename: Output filename
            
        Returns:
            Path to saved plot or None if data unavailable
        """
        try:
            output_path = self.output_dir / filename
            
            # Check for data
            if len(self.time) == 0:
                logger.warning("No controller data available")
                return None
            
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.25)
            
            # --- Subplot 1: Predicted Apogee Evolution ---
            ax1 = fig.add_subplot(gs[0, :])
            ax1.plot(self.time, self.predicted_apogee, 'b-', linewidth=2, 
                    label='Predicted Apogee', alpha=0.8)
            
            # Target apogee line
            ax1.axhline(y=self.target_apogee, color='green', linestyle='--', 
                       linewidth=2, label=f'Target: {self.target_apogee:.0f}m', alpha=0.7)
            
            # Actual apogee at apogee_time
            if self.apogee_time is not None:
                ax1.axvline(x=self.apogee_time, color='red', linestyle=':', 
                           linewidth=1.5, label='Actual Apogee Time', alpha=0.7)
            
            ax1.set_ylabel('Altitude (m)', fontsize=11, fontweight='bold')
            ax1.set_title('Apogee Prediction Evolution', fontsize=13, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best', fontsize=10)
            
            self._add_event_markers(ax1, self.time_limit, add_legend=False)
            
            # --- Subplot 2: Control Error ---
            ax2 = fig.add_subplot(gs[1, 0])
            ax2.plot(self.time, self.error, 'r-', linewidth=2, alpha=0.8)
            ax2.fill_between(self.time, 0, self.error, alpha=0.2, color='red')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
            
            ax2.set_ylabel('Error (m)', fontsize=11, fontweight='bold')
            ax2.set_title('Apogee Prediction Error', fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            
            # Highlight zones
            ax2.axhspan(-50, 50, alpha=0.1, color='green', label='Tolerance ±50m')
            ax2.legend(loc='best', fontsize=9)
            
            self._add_event_markers(ax2, self.time_limit, add_legend=False,
                                   include_parachute=False)
            
            # --- Subplot 3: Deployment Response ---
            ax3 = fig.add_subplot(gs[1, 1])
            ax3.plot(self.time, self.actual_deployment * 100, 'b-', linewidth=2)
            ax3.set_ylabel('Deployment (%)', fontsize=11, fontweight='bold')
            ax3.set_title('Air Brakes Deployment', fontsize=12, fontweight='bold')
            ax3.grid(True, alpha=0.3)
            ax3.set_ylim(-5, 105)
            
            self._add_event_markers(ax3, self.time_limit, add_legend=False,
                                   include_parachute=False)
            
            # --- Subplot 4-6: PID Terms ---
            # P term
            ax4 = fig.add_subplot(gs[2, 0])
            ax4.plot(self.time, self.p_term, 'b-', linewidth=2, label='P term', alpha=0.8)
            ax4.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
            ax4.set_ylabel('P Contribution', fontsize=10, fontweight='bold')
            ax4.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
            ax4.set_title('Proportional Term', fontsize=11, fontweight='bold')
            ax4.grid(True, alpha=0.3)
            
            # I term  
            ax4_twin = ax4.twinx()
            ax4_twin.plot(self.time, self.i_term, 'orange', linewidth=1.5, 
                         label='I term', alpha=0.7, linestyle='--')
            ax4_twin.set_ylabel('I Contribution', fontsize=10, fontweight='bold', color='orange')
            ax4_twin.tick_params(axis='y', labelcolor='orange')
            
            # Combined legend
            lines1, labels1 = ax4.get_legend_handles_labels()
            lines2, labels2 = ax4_twin.get_legend_handles_labels()
            ax4.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9)
            
            # D term
            ax5 = fig.add_subplot(gs[2, 1])
            ax5.plot(self.time, self.d_term, 'green', linewidth=2, label='D term', alpha=0.8)
            ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
            ax5.set_ylabel('D Contribution', fontsize=10, fontweight='bold')
            ax5.set_xlabel('Time (s)', fontsize=10, fontweight='bold')
            ax5.set_title('Derivative Term', fontsize=11, fontweight='bold')
            ax5.grid(True, alpha=0.3)
            ax5.legend(loc='best', fontsize=9)
            
            fig.suptitle('Air Brakes Controller Performance Analysis', 
                        fontsize=15, fontweight='bold', y=0.995)
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Controller performance plot saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating controller performance plot: {e}", exc_info=True)
            return None
    
    def plot_deployment_rate_analysis(
        self,
        filename: str = "deployment_rate_analysis.png"
    ) -> Optional[Path]:
        """Plot deployment rate showing saturation and dynamics.
        
        Shows:
        - Deployment rate over time
        - Rate limiting saturation events
        - Acceleration/deceleration phases
        
        Args:
            filename: Output filename
            
        Returns:
            Path to saved plot or None if data unavailable
        """
        try:
            output_path = self.output_dir / filename
            
            if len(self.time) < 2:
                logger.warning("Insufficient data for rate analysis")
                return None
            
            # Calculate deployment rate (derivative)
            dt = np.diff(self.time)
            rate = np.diff(self.actual_deployment) / dt  # Rate in 1/s
            rate_time = self.time[:-1] + dt / 2  # Midpoint time for rate
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
            
            # --- Subplot 1: Deployment Level ---
            ax1.plot(self.time, self.actual_deployment * 100, 'b-', linewidth=2.5, label='Deployment Level')
            ax1.set_ylabel('Deployment (%)', fontsize=12, fontweight='bold')
            ax1.set_title('Air Brakes Deployment and Rate Analysis', 
                         fontsize=14, fontweight='bold')
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim(-5, 105)
            ax1.legend(loc='best', fontsize=10)
            
            self._add_event_markers(ax1, self.time_limit, add_legend=False)
            
            # --- Subplot 2: Deployment Rate ---
            ax2.plot(rate_time, rate, 'r-', linewidth=2, alpha=0.8, label='Deployment Rate')
            ax2.fill_between(rate_time, 0, rate, alpha=0.2, color='red')
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
            
            # Rate limits from controller config
            max_rate = self.controller.config.max_deployment_rate
            ax2.axhline(y=max_rate, color='orange', linestyle='--', linewidth=2, 
                       label=f'Max Rate Limit: ±{max_rate:.1f}/s', alpha=0.7)
            ax2.axhline(y=-max_rate, color='orange', linestyle='--', linewidth=2, alpha=0.7)
            
            # Highlight saturated regions
            saturated = np.abs(rate) >= (max_rate * 0.95)
            if np.any(saturated):
                ax2.fill_between(rate_time, -max_rate * 1.2, max_rate * 1.2,
                                where=saturated, alpha=0.15, color='orange',
                                label='Rate Saturated')
            
            ax2.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Rate (1/s)', fontsize=12, fontweight='bold')
            ax2.set_title('Deployment Rate (positive = opening, negative = closing)', 
                         fontsize=13, fontweight='bold')
            ax2.grid(True, alpha=0.3)
            ax2.legend(loc='best', fontsize=10)
            
            self._add_event_markers(ax2, self.time_limit, add_legend=False,
                                   include_parachute=False)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Deployment rate analysis plot saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating deployment rate plot: {e}", exc_info=True)
            return None
    
    def plot_all_airbrakes_analysis(self) -> Dict[str, Path]:
        """Generate all air brakes analysis plots.
        
        Returns:
            Dictionary mapping plot names to file paths
        """
        logger.info("Generating all air brakes analysis plots...")
        
        plots = {}
        
        # 1. Deployment comparison (commanded vs actual)
        path = self.plot_deployment_comparison()
        if path:
            plots['deployment_comparison'] = path
        
        # 2. Controller performance (PID terms, error, apogee)
        path = self.plot_controller_performance()
        if path:
            plots['controller_performance'] = path
        
        # 3. Deployment rate analysis
        path = self.plot_deployment_rate_analysis()
        if path:
            plots['deployment_rate_analysis'] = path
        
        logger.info(f"Generated {len(plots)} air brakes plots")
        return plots


def create_airbrakes_plots(
    controller: 'AirBrakesController',
    output_dir: str,
    burnout_time: Optional[float] = None,
    apogee_time: Optional[float] = None,
    parachute_deploy_time: Optional[float] = None,
    target_apogee: Optional[float] = None
) -> Dict[str, Path]:
    """Convenience function to create all air brakes plots.
    
    Args:
        controller: AirBrakesController instance with history data
        output_dir: Directory for plots
        burnout_time: Motor burnout time (s)
        apogee_time: Apogee time (s)
        parachute_deploy_time: Parachute deployment time (s)
        target_apogee: Target apogee (m)
        
    Returns:
        Dictionary of generated plot paths
    """
    plotter = AirBrakesPlotter(
        controller=controller,
        output_dir=output_dir,
        burnout_time=burnout_time,
        apogee_time=apogee_time,
        parachute_deploy_time=parachute_deploy_time,
        target_apogee=target_apogee
    )
    
    return plotter.plot_all_airbrakes_analysis()
