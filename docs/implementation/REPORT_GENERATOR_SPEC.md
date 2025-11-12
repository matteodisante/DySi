# Report Generator Module - Specification

## Overview
This document specifies a separate report generation module for creating comprehensive HTML/PDF flight analysis reports with embedded plots and interpretation.

**IMPORTANT**: Reports are SEPARATE from state export files. State files contain only raw data; reports contain analysis and interpretation.

## Module Structure

```
src/
├── report_generator.py      # Main report generation module
└── templates/
    ├── report_template.html  # Jinja2 HTML template
    └── report_styles.css     # CSS styling
```

## Requirements

### Python Dependencies
```
jinja2>=3.0.0        # HTML templating
markdown>=3.4.0      # Markdown to HTML conversion
weasyprint>=57.0     # HTML to PDF conversion (optional)
plotly>=5.0.0        # Interactive plots (optional)
```

## Report Structure

### 1. Executive Summary
- Rocket name and configuration
- Launch site and date
- Key performance metrics table:
  - Apogee altitude
  - Maximum velocity
  - Maximum acceleration
  - Flight time
  - Impact point
  - Drift distance

### 2. Mission Profile
- Flight phases timeline:
  - Rail departure
  - Powered flight
  - Coasting ascent
  - Apogee
  - Descent
  - Parachute deployment
  - Landing
- Key events table with timestamps

### 3. Rocket Configuration Summary
- Visual: Rocket schematic (embedded PNG from plots/)
- Mass breakdown table
- Inertia properties
- Aerodynamic surfaces specifications
- Stability metrics (static margin at liftoff and burnout)

### 4. Motor Performance Analysis
- Visual: Thrust curve (embedded PNG)
- Performance metrics:
  - Total impulse
  - Average thrust
  - Maximum thrust
  - Burn time
  - Specific impulse
- Mass evolution plot
- Center of mass evolution

### 5. Flight Trajectory Analysis
- Visuals:
  - 3D trajectory plot
  - Altitude vs time
  - Velocity vs time
  - Acceleration vs time
- Ground track (x-y plot showing drift)
- Comparison to predictions (if available)

### 6. Aerodynamic Performance
- Drag coefficient vs Mach number
- Center of pressure evolution
- Static margin vs time
- Stability margin surface (Mach vs time)
- Angle of attack profile

### 7. Recovery System Performance
- Parachute deployment analysis
- Descent rate profile
- Landing velocity
- Impact kinetic energy

### 8. Monte Carlo Results (if applicable)
- Distribution plots for:
  - Apogee altitude
  - Drift distance
  - Maximum velocity
- Percentile tables (P10, P50, P90)
- Sensitivity analysis charts
- Dispersion ellipse plot

### 9. Warnings and Recommendations
- Automated checks:
  - Rail velocity adequate (> 15 m/s)
  - Static stability margin in range (1.5-3.0 cal)
  - Maximum acceleration within limits
  - Descent rate safe (< 10 m/s)
  - Kinetic energy at landing
- Recommendations for improvements

### 10. Appendices
- Complete configuration (YAML)
- Detailed flight data tables
- Environment conditions
- Computational details (solver tolerances, time steps)

## Implementation Specification

### Class Structure

```python
class ReportGenerator:
    """Generate comprehensive flight analysis reports."""
    
    def __init__(self, 
                 flight_data: Dict,
                 config: Dict,
                 output_dir: str,
                 plots_dir: str):
        """Initialize report generator.
        
        Args:
            flight_data: Flight simulation results
            config: Rocket configuration
            output_dir: Directory for report output
            plots_dir: Directory containing plot PNG files
        """
        
    def generate_html_report(self, output_path: str) -> str:
        """Generate HTML report.
        
        Returns:
            Path to generated HTML file
        """
        
    def generate_pdf_report(self, output_path: str) -> str:
        """Generate PDF report from HTML.
        
        Returns:
            Path to generated PDF file
        """
        
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section."""
        
    def _generate_trajectory_analysis(self) -> str:
        """Generate trajectory analysis section."""
        
    def _generate_stability_analysis(self) -> str:
        """Generate stability analysis section."""
        
    def _embed_plot(self, plot_path: str, caption: str) -> str:
        """Embed plot image with caption."""
        
    def _create_metrics_table(self, metrics: Dict) -> str:
        """Create HTML table from metrics dictionary."""
        
    def _add_warning(self, message: str, severity: str):
        """Add warning to recommendations section."""
```

### HTML Template Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ rocket_name }} - Flight Analysis Report</title>
    <link rel="stylesheet" href="report_styles.css">
</head>
<body>
    <header>
        <h1>Flight Analysis Report</h1>
        <h2>{{ rocket_name }}</h2>
        <p>Generated: {{ timestamp }}</p>
    </header>
    
    <nav>
        <ul>
            <li><a href="#summary">Executive Summary</a></li>
            <li><a href="#mission">Mission Profile</a></li>
            <li><a href="#configuration">Configuration</a></li>
            <!-- ... more sections ... -->
        </ul>
    </nav>
    
    <main>
        <section id="summary">
            <h2>Executive Summary</h2>
            {{ summary_content }}
        </section>
        
        <section id="trajectory">
            <h2>Flight Trajectory</h2>
            <figure>
                <img src="{{ altitude_plot_path }}" alt="Altitude vs Time">
                <figcaption>Figure 1: Altitude profile</figcaption>
            </figure>
            {{ trajectory_analysis }}
        </section>
        
        <!-- ... more sections ... -->
    </main>
    
    <footer>
        <p>Generated by RocketSim v{{ version }}</p>
    </footer>
</body>
</html>
```

### CSS Styling

```css
/* Professional report styling */
body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 8px;
    margin-bottom: 30px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}

table th {
    background: #667eea;
    color: white;
    padding: 12px;
    text-align: left;
}

table td {
    padding: 10px;
    border-bottom: 1px solid #ddd;
}

figure {
    margin: 30px 0;
    text-align: center;
}

figure img {
    max-width: 100%;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.warning {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 15px;
    margin: 20px 0;
}

.metric-good {
    color: #28a745;
    font-weight: bold;
}

.metric-warning {
    color: #ffc107;
    font-weight: bold;
}

.metric-danger {
    color: #dc3545;
    font-weight: bold;
}

@media print {
    body { max-width: 100%; }
    nav { display: none; }
}
```

## Usage Example

```python
from src.report_generator import ReportGenerator

# After simulation completes
generator = ReportGenerator(
    flight_data=flight_summary,
    config=config_dict,
    output_dir="outputs/my_rocket/report",
    plots_dir="outputs/my_rocket/curves"
)

# Generate HTML report
html_path = generator.generate_html_report("outputs/my_rocket/report/report.html")
print(f"HTML report: {html_path}")

# Generate PDF report (optional, requires weasyprint)
pdf_path = generator.generate_pdf_report("outputs/my_rocket/report/report.pdf")
print(f"PDF report: {pdf_path}")
```

## Integration with flight_simulator.py

```python
# In flight_simulator.py, after state export

if export_state:
    # ... existing state export code ...
    
    # Generate analysis report
    from src.report_generator import ReportGenerator
    
    report_generator = ReportGenerator(
        flight_data=self.get_summary(),
        config=self.config,
        output_dir=str(output_path / "report"),
        plots_dir=str(output_path / "curves")
    )
    
    # Generate HTML (always)
    html_path = report_generator.generate_html_report(
        str(output_path / "report" / "report.html")
    )
    logger.info(f"HTML report generated: {html_path}")
    
    # Generate PDF (optional, if weasyprint available)
    try:
        pdf_path = report_generator.generate_pdf_report(
            str(output_path / "report" / "report.pdf")
        )
        logger.info(f"PDF report generated: {pdf_path}")
    except ImportError:
        logger.warning("PDF generation skipped (weasyprint not installed)")
```

## Automated Analysis Features

### Performance Checks
```python
def _check_rail_velocity(self):
    """Check if rail departure velocity is adequate."""
    rail_velocity = self.flight_data.get('out_of_rail_velocity_ms', 0)
    if rail_velocity < 15.0:
        self._add_warning(
            f"Rail velocity ({rail_velocity:.1f} m/s) is below recommended 15 m/s. "
            "Consider: longer rail, higher thrust motor, or reduced mass.",
            severity='warning'
        )

def _check_static_margin(self):
    """Check stability margin."""
    margin = self.flight_data.get('static_margin_cal', 0)
    if margin < 1.5:
        self._add_warning(
            f"Static margin ({margin:.2f} cal) below safe minimum 1.5 cal. "
            "Rocket may be unstable!",
            severity='danger'
        )
    elif margin > 4.0:
        self._add_warning(
            f"Static margin ({margin:.2f} cal) very high. "
            "Consider moving CoM forward for better performance.",
            severity='info'
        )

def _check_descent_rate(self):
    """Check parachute adequacy."""
    descent_rate = self.flight_data.get('impact_velocity_ms', 0)
    if descent_rate > 10.0:
        self._add_warning(
            f"Impact velocity ({descent_rate:.1f} m/s) too high! "
            "Increase parachute size (current cd_s may be inadequate).",
            severity='danger'
        )
```

## Future Enhancements

1. **Interactive Plots** - Use Plotly for interactive HTML plots
2. **Comparison Mode** - Compare multiple flights side-by-side
3. **Weather Integration** - Include actual weather conditions
4. **Photo Documentation** - Embed launch photos and videos
5. **Team Information** - Add team members, sponsors, etc.
6. **Export to Word** - Generate .docx for easy editing
7. **Email Distribution** - Automatically email reports to team

## Implementation Priority

**Priority: LOW** (Task 8)

This module is useful but not critical for core functionality. All necessary data is already exported in state files. Reports are "nice to have" for presentation purposes.

**Suggested Implementation Order:**
1. Basic HTML template with embedded plots
2. Executive summary and key metrics
3. Automated safety checks
4. PDF generation
5. Interactive features
6. Advanced visualizations

## Notes

- Reports should be regenerated from state files, not generated during simulation
- This allows multiple report formats from single simulation
- Reports are presentation layer, not data storage
- Keep report generation separate from simulation code
