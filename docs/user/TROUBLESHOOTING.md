# Troubleshooting Guide

Common errors, solutions, and debugging tips for the rocket simulation framework.

## Table of Contents

1. [Import Errors](#import-errors)
2. [Configuration Errors](#configuration-errors)
3. [Simulation Failures](#simulation-failures)
4. [Validation Warnings](#validation-warnings)
5. [Performance Issues](#performance-issues)
6. [Data Export Problems](#data-export-problems)
7. [Notebook Issues](#notebook-issues)

---

## Import Errors

### Error: `ModuleNotFoundError: No module named 'src'`

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
```

**Cause**: Package not installed in editable mode

**Solution**:
```bash
# Navigate to project root
cd /path/to/rocket-sim

# Install package in editable mode
pip install -e .

# Verify installation
python -c "from src.config_loader import ConfigLoader; print('Success!')"
```

**In Jupyter Notebooks**: Restart kernel after installing package

---

### Error: `ImportError: cannot import name 'X' from 'src.Y'`

**Cause**: Outdated Python cache or module doesn't exist

**Solution**:
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall package
pip install -e . --force-reinstall --no-deps
```

---

## Configuration Errors

### Error: `FileNotFoundError: [Errno 2] No such file or directory: 'configs/X.yaml'`

**Cause**: Config file path is incorrect or file was moved

**Solution**: Update config paths to new organized structure
- Old: `configs/simple_rocket.yaml`
- New: `configs/single_sim/01_minimal.yaml`

**Available Configs**:
```
configs/
├── single_sim/01_minimal.yaml
├── single_sim/02_complete.yaml
├── monte_carlo/01_basic_mc.yaml
└── monte_carlo/02_competition_mc.yaml
```

---

### Error: `KeyError: 'X' during config loading`

**Symptoms**:
```python
KeyError: 'rocket'
```

**Cause**: YAML file missing required section

**Solution**: Check config file has all four required sections:
```yaml
rocket:
  # ... rocket params

motor:
  # ... motor params

environment:
  # ... environment params

simulation:
  # ... simulation params
```

**Quick Fix**: Start from a template in `configs/templates/`

---

### Error: `ValidationError: X is required`

**Cause**: Required field missing in config

**Solution**: Add missing field. Check schema in [configs/README_CONFIGS.md](../configs/README_CONFIGS.md)

**Example**:
```yaml
# Missing dry_mass_kg
rocket:
  name: "My Rocket"
  # ERROR: dry_mass_kg required!

# Fixed
rocket:
  name: "My Rocket"
  dry_mass_kg: 16.0  # Added required field
```

---

## Simulation Failures

### Error: `RuntimeError: Flight simulation did not converge`

**Symptoms**: Simulation runs but fails to complete

**Common Causes**:
1. Unstable rocket (CP in front of CG)
2. Invalid geometry (negative values)
3. Extremely tight tolerances
4. Motor burnout before rail clearance

**Solutions**:

**1. Check Stability**:
```python
from src.rocket_builder import RocketBuilder

builder = RocketBuilder(rocket_cfg)
rocket = builder.build(motor)
stability = builder.get_stability_info()

print(f"Static margin: {stability['static_margin_calibers']} calibers")
# Should be > 1.0, ideally 1.5-2.5
```

**2. Validate Configuration**:
```python
from src.validators import RocketValidator

warnings = RocketValidator.validate(rocket_cfg)
for w in warnings:
    if w.level == "ERROR":
        print(f"Critical: {w.message}")
```

**3. Relax Tolerances**:
```yaml
simulation:
  rtol: 1.0e-3  # Relaxed from 1.0e-6
  atol: 1.0e-3  # Relaxed from 1.0e-6
  max_time_step_s: 0.1  # Add step limit
```

**4. Check Rail Clearance**:
```yaml
simulation:
  rail:
    length_m: 5.0  # Increase if off-rail velocity too low
```

---

### Error: Rocket flips over / unstable flight

**Symptoms**: Rocket trajectory shows erratic behavior or flip

**Cause**: Center of pressure (CP) in front of center of gravity (CG)

**Solution**: Achieve static margin ≥ 1 caliber

**Options**:
```yaml
# Option 1: Move fins further back
rocket:
  fins:
    position_m: -1.0  # More negative = further from nose

# Option 2: Increase fin span
rocket:
  fins:
    span_m: 0.15  # Larger fins → CP moves back

# Option 3: Add nose weight (move CG forward)
rocket:
  dry_mass_kg: 18.0  # Add mass
  cg_location_m: 0.8  # Closer to nose
```

**Verify**:
```python
stability_info = rocket_builder.get_stability_info()
print(f"Static margin: {stability_info['static_margin_calibers']:.2f} cal")
# Target: 1.5-2.5 calibers
```

---

### Error: `ValueError: Thrust curve file not found`

**Symptoms**:
```
ValueError: Could not find thrust source: data/motors/XYZ.eng
```

**Cause**: Motor file path incorrect or file doesn't exist

**Solution**:
```bash
# Check if file exists
ls data/motors/

# Update config with correct path
# Relative to project root
motor:
  thrust_source: "data/motors/Cesaroni_5472M2250-P.eng"
```

**Download Motors**: Get `.eng` files from [ThrustCurve.org](https://www.thrustcurve.org/)

---

## Validation Warnings

### Warning: `Static margin X calibers is below recommended minimum of 1.5`

**Severity**: Warning (simulation will run but may be unstable)

**Solution**: See "Rocket flips over" section above

---

### Warning: `Mass X kg seems unusually high/low`

**Severity**: Info

**Action**: Verify dry mass is correct. Typical values:
- Small rocket (3" diameter): 3-8 kg
- Medium rocket (4-6" diameter): 10-20 kg
- Large rocket (6-8" diameter): 20-40 kg

---

### Warning: `Rail length may be insufficient for stable flight`

**Severity**: Warning

**Cause**: Off-rail velocity predicted to be too low (<20 m/s recommended)

**Solution**:
```yaml
simulation:
  rail:
    length_m: 8.0  # Increase rail length
```

---

## Performance Issues

### Issue: Monte Carlo simulation is very slow

**Symptoms**: 100 simulations taking >10 minutes

**Solutions**:

**1. Enable Parallel Execution**:
```python
results = mc_runner.run(parallel=True, max_workers=4)
# Use max_workers = number of CPU cores
```

**2. Reduce Number of Simulations**:
```python
# For testing
mc_runner = MonteCarloRunner(..., num_simulations=20)

# For production
mc_runner = MonteCarloRunner(..., num_simulations=100)
```

**3. Disable Verbose Output**:
```yaml
simulation:
  verbose: false
```

**4. Optimize Tolerances**:
```yaml
simulation:
  rtol: 1.0e-4  # Slightly relaxed
  atol: 1.0e-4
```

---

### Issue: Notebook kernel keeps dying during Monte Carlo

**Cause**: Memory exhaustion from too many simulations

**Solution**:
```python
# Process in batches
batch_size = 50
total_sims = 200

all_results = []
for i in range(0, total_sims, batch_size):
    mc_runner.num_simulations = min(batch_size, total_sims - i)
    results = mc_runner.run()
    all_results.extend(results)

    # Free memory
    import gc
    gc.collect()
```

---

## Data Export Problems

### Error: `PermissionError: [Errno 13] Permission denied`

**Cause**: Output directory doesn't exist or no write permission

**Solution**:
```python
from pathlib import Path

output_dir = Path("outputs/my_simulation")
output_dir.mkdir(parents=True, exist_ok=True)  # Create if missing

# Then export
handler.export_trajectory_csv(flight, output_dir / "trajectory.csv")
```

---

### Issue: CSV file is empty or corrupted

**Cause**: Simulation failed but export was still attempted

**Solution**: Check simulation success before export
```python
try:
    flight = simulator.run()
    summary = simulator.get_summary()

    # Verify flight succeeded
    if summary['apogee_m'] > 0:
        handler.export_trajectory_csv(flight, "trajectory.csv")
    else:
        print("Simulation failed - no data to export")
except Exception as e:
    print(f"Simulation error: {e}")
```

---

## Notebook Issues

### Issue: Notebook imports fail after package changes

**Cause**: Jupyter kernel using old Python environment

**Solution**:
```python
# In notebook, restart kernel:
# Kernel → Restart Kernel

# Or programmatically:
import IPython
IPython.Application.instance().kernel.do_shutdown(True)
```

---

### Issue: Plots not showing in notebook

**Cause**: Matplotlib backend not configured

**Solution**:
```python
import matplotlib.pyplot as plt

# Add magic command at top of notebook
%matplotlib inline

# Or for interactive plots
%matplotlib widget
```

---

### Issue: "Installation check" cell fails in notebook

**Error**:
```
✗ Package not installed or incorrect setup
Error: No module named 'src'
```

**Solution**:
```bash
# In terminal, navigate to project root
cd /path/to/rocket-sim

# Install package
pip install -e .

# Restart Jupyter kernel
# Then run installation check cell again
```

---

## Getting Help

### Debugging Checklist

1. **Validate configuration**:
   ```python
   from src.validators import validate_all_configs
   warnings = validate_all_configs(rocket_cfg, motor_cfg, env_cfg, sim_cfg)
   ```

2. **Check stability**:
   ```python
   stability = rocket_builder.get_stability_info()
   print(stability)
   ```

3. **Enable verbose mode**:
   ```yaml
   simulation:
     verbose: true
   ```

4. **Test with minimal config**:
   ```python
   # Try with configs/single_sim/01_minimal.yaml first
   ```

5. **Check RocketPy version**:
   ```bash
   pip show rocketpy
   # Should be compatible version
   ```

### Common Diagnostic Commands

```bash
# Check Python environment
python --version
pip list | grep rocketpy

# Verify package installation
python -c "import src; print(src.__file__)"

# Clear Python cache
find . -name "*.pyc" -delete
find . -type d -name __pycache__ -exec rm -rf {} +

# Check file paths
ls -R configs/
ls -R data/motors/

# Test basic import
python -c "from src.config_loader import ConfigLoader; print('OK')"
```

### Where to Get More Help

1. **Check documentation**:
   - [MODULE_REFERENCE.md](MODULE_REFERENCE.md) - Quick reference
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [../configs/README_CONFIGS.md](../configs/README_CONFIGS.md) - Config schema

2. **Run example notebooks**: Start with [00_getting_started.ipynb](../notebooks/00_getting_started.ipynb)

3. **Validate configs**: Use validators before running simulations

4. **Check RocketPy docs**: [https://docs.rocketpy.org/](https://docs.rocketpy.org/)

5. **GitHub Issues**: Check existing issues or open a new one

---

## Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| Import errors | `pip install -e .` |
| Config not found | Use `configs/single_sim/01_minimal.yaml` |
| Simulation fails | Check stability margin |
| Unstable flight | Increase fin span or move fins back |
| Slow Monte Carlo | Enable `parallel=True` |
| Notebook import fails | Restart kernel after `pip install -e .` |
| Plots not showing | Add `%matplotlib inline` |
| Permission error | `mkdir -p outputs/` |
| Motor file not found | Check path: `data/motors/*.eng` |
| Convergence issues | Relax `rtol` and `atol` |
