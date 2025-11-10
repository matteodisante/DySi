# Timeout and Automatic Logging Feature

**Date**: 2025-11-10  
**Version**: 2.0  
**Author**: GitHub Copilot + Matteo Di Sante

## Overview

This document describes the new **timeout system** and **automatic log file generation** features added to the rocket simulation system to handle unstable rocket configurations gracefully.

## Problem Statement

### Original Issues

1. **Unstable rockets hang simulation**: Rockets with negative static margin (e.g., 1 fin instead of 3-4) cause the simulation to appear "frozen" because:
   - The rocket becomes unstable immediately after leaving the rail
   - The ODE solver takes extremely small time steps to track chaotic motion
   - The simulation can run for hours without completing

2. **No visibility during long simulations**: Users had no way to:
   - Know if the simulation was still running or frozen
   - Get partial results if they needed to stop early
   - See what happened before the simulation got stuck

3. **No automatic log files**: Users had to manually specify `--log-file` parameter for every simulation, making it easy to lose debugging information.

## Solution Implemented

### 1. Simulation Timeout System

Added a configurable timeout mechanism that:
- ✅ **Detects hung simulations** using POSIX signals (SIGALRM)
- ✅ **Saves partial results** (motor/rocket/environment curves, initial state)
- ✅ **Provides helpful diagnostics** about why the simulation timed out
- ✅ **Suggests fixes** (add more fins, check static margin)

#### Usage

```bash
# Default timeout: 300 seconds (5 minutes)
python scripts/run_single_simulation.py --config my_rocket.yaml

# Custom timeout: 60 seconds
python scripts/run_single_simulation.py --config my_rocket.yaml --timeout 60

# Disable timeout (original behavior)
python scripts/run_single_simulation.py --config my_rocket.yaml --timeout 0
```

#### What Gets Saved on Timeout

Even if the simulation times out, the following are **ALWAYS saved**:

```
outputs/<rocket_name>/
├── simulation_YYYYMMDD_HHMMSS.log  ✅ FULL LOG
├── initial_state.json               ✅ Initial conditions
├── initial_state_READABLE.txt       ✅ Human-readable format
└── curves/
    ├── motor/                       ✅ All 11 motor plots
    │   ├── thrust.png
    │   ├── mass_evolution.png
    │   ├── burn_characteristics.png
    │   └── ... (8 more plots)
    ├── rocket/                      ✅ Drag curves
    │   ├── power_on_drag.png
    │   └── power_off_drag.png
    └── environment/                 ✅ Atmospheric data
        ├── atmospheric_profile.png
        └── wind_profile.png
```

**Missing on timeout** (requires completed simulation):
- `final_state.json` / `final_state_READABLE.txt`
- `trajectory/*.csv` (time series data)
- `plots/*.png` (trajectory visualizations)

### 2. Automatic Log File Generation

Every simulation now **automatically creates a timestamped log file** in the output directory:

```
outputs/<rocket_name>/simulation_YYYYMMDD_HHMMSS.log
```

#### Features

- ✅ **Auto-generated filename** with timestamp
- ✅ **Saved alongside results** in the same output directory
- ✅ **Complete simulation log** (all INFO, WARNING, ERROR messages)
- ✅ **Manual override** still possible with `--log-file` parameter

#### Example Log File Content

```log
2025-11-10 12:42:25 - __main__ - INFO - ROCKET FLIGHT SIMULATION
2025-11-10 12:42:25 - __main__ - INFO - Configuration file: configs/02_complete.yaml
2025-11-10 12:42:25 - __main__ - WARNING - ⚠️  UNSTABLE ROCKET DETECTED!
2025-11-10 12:42:25 - __main__ - WARNING -    Static margin = -3.09 cal (negative = unstable)
2025-11-10 12:42:25 - __main__ - WARNING -    Timeout is set to 30s - partial results will be saved if timeout occurs.
2025-11-10 12:42:25 - src.flight_simulator - INFO - Starting flight simulation...
```

### 3. Unstable Rocket Detection

The system now **automatically detects unstable rockets** before running the simulation:

```python
if rocket_summary['static_margin_calibers'] < 0:
    logger.warning("⚠️  UNSTABLE ROCKET DETECTED!")
    logger.warning(f"   Static margin = {rocket_summary['static_margin_calibers']:.2f} cal")
    logger.warning("   The simulation may be slow or fail to converge.")
    logger.warning(f"   Timeout is set to {args.timeout}s - partial results will be saved.")
```

This gives users:
- 📊 **Immediate feedback** about stability issues
- ⚠️ **Warning before long waits**
- 💡 **Suggestions** for fixing the problem

## Technical Implementation

### 1. Timeout Mechanism (`run_single_simulation.py`)

```python
import signal
from datetime import datetime

def timeout_handler(signum, frame):
    raise TimeoutError(f"Simulation exceeded timeout of {args.timeout} seconds")

# Setup timeout
if args.timeout > 0:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(args.timeout)

try:
    flight = simulator.run()
    signal.alarm(0)  # Cancel if completed
except TimeoutError as e:
    logger.error(f"⏱️  SIMULATION TIMEOUT: {e}")
    simulation_timed_out = True
    signal.alarm(0)
```

### 2. Auto Log File Setup

```python
# Early setup without file logging
setup_logging(level=log_level, log_file=None)

# After loading config and knowing rocket name
output_name = args.name or rocket_cfg.name.replace(" ", "_").lower()
sim_output_dir = Path(args.output_dir) / output_name
sim_output_dir.mkdir(parents=True, exist_ok=True)

# Create timestamped log file
if not args.log_file:
    log_file = sim_output_dir / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    setup_logging(level=log_level, log_file=str(log_file))
```

### 3. Reconfigurable Logging (`src/utils.py`)

Fixed `setup_logging()` to allow reconfiguration (needed for auto log file):

```python
def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers to allow reconfiguration
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add new handlers
    console_handler = logging.StreamHandler()
    root_logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        root_logger.addHandler(file_handler)
```

### 4. Partial Export Logic

```python
# ALWAYS export (even on timeout)
if not args.no_export:
    state_exporter.export_initial_state(sim_output_dir / "initial_state")
    
    # Only export final state if simulation completed
    if not simulation_timed_out and flight:
        state_exporter.export_final_state(flight, sim_output_dir / "final_state")

# ALWAYS plot curves (even on timeout)
if not args.no_plots:
    curve_plotter.plot_all_curves(curves_dir)

# Only export trajectory data if simulation completed
if not args.no_export and not simulation_timed_out and flight:
    data_handler.export_complete_dataset(...)
```

## Exit Codes

The script now returns different exit codes for different scenarios:

- **0**: Simulation completed successfully
- **1**: File not found or other error
- **2**: Simulation timed out (partial results saved)

This allows automation scripts to detect timeout scenarios:

```bash
python scripts/run_single_simulation.py --config rocket.yaml
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo "Simulation timed out - check static margin!"
fi
```

## User Interface Improvements

### Console Output on Timeout

```
⏱️  SIMULATION TIMEOUT: Simulation exceeded timeout of 60 seconds
Simulation did not complete within the time limit.
This usually indicates an unstable rocket (negative static margin).
Attempting to save partial results...

--- PARTIAL RESULTS (TIMEOUT) ---
Simulation did not complete successfully.
State data (motor, rocket, environment) will still be exported.

============================================================
SIMULATION TIMED OUT - PARTIAL RESULTS SAVED
============================================================

Partial results saved to: outputs/hermes_unstable_test/

Available outputs:
  outputs/hermes_unstable_test/
    ├── simulation_YYYYMMDD_HHMMSS.log (this log file)
    ├── initial_state.json / .txt
    └── curves/
        ├── motor/       (11 motor curve plots)
        ├── rocket/      (drag curves)
        └── environment/ (wind, atmosphere)

⚠️  Missing outputs (simulation did not complete):
    ├── final_state.json / .txt
    ├── trajectory/ (CSV data)
    └── plots/ (trajectory visualizations)

💡 Suggestions:
   - Check static margin (should be positive, typically 1.5-2.5 calibers)
   - Add more fins or adjust fin position if margin is negative
   - Increase timeout with --timeout <seconds> if rocket is stable
```

### Log File Location in Output

```
Results saved to: outputs/hermes_stable/

Output structure:
  outputs/hermes_stable/
    ├── simulation_YYYYMMDD_HHMMSS.log (this log file) ⭐ NEW!
    ├── initial_state.json / .txt
    ├── final_state.json / .txt
    ├── curves/
    │   ├── motor/       (11 motor curve plots)
    │   ├── rocket/      (drag curves)
    │   └── environment/ (wind, atmosphere)
    ├── trajectory/
    │   └── *.csv        (time series data)
    └── plots/
        └── *.png        (trajectory visualizations)
```

## CLI Changes

### New Parameter

```
--timeout, -t INTEGER    Simulation timeout in seconds (default: 300).
                         Set to 0 to disable timeout.
```

### Updated Parameter

```
--log-file STRING       Log file path (default: auto-generated in outputs/<name>/simulation.log)
```

## Testing

### Test Case 1: Unstable Rocket (1 fin)

```bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --name unstable_test \
    --timeout 60
```

**Expected behavior**:
- ✅ Detects negative static margin (-3.09 cal)
- ✅ Warns user about potential timeout
- ✅ Simulation completes quickly (rocket falls immediately, apogee=0m)
- ✅ All plots generated (motor curves, drag curves, etc.)
- ✅ Log file created with full details
- ✅ Exit code 0 (completed, even if apogee=0)

### Test Case 2: Stable Rocket (4 fins)

```bash
# First, edit config to use 4 fins
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --name stable_test \
    --timeout 300
```

**Expected behavior**:
- ✅ Positive static margin (~2.0 cal)
- ✅ No instability warnings
- ✅ Simulation completes within timeout
- ✅ All outputs generated (full trajectory, plots, state files)
- ✅ Log file with complete simulation details
- ✅ Exit code 0

### Test Case 3: Manual Log File Override

```bash
python scripts/run_single_simulation.py \
    --config configs/single_sim/02_complete.yaml \
    --log-file custom_log.txt
```

**Expected behavior**:
- ✅ Log written to `custom_log.txt` (not auto-generated name)
- ✅ Still creates outputs/<name>/ directory for other files

## Benefits

1. **Better User Experience**:
   - No more "frozen" simulations without explanation
   - Clear diagnostics when things go wrong
   - Always have log files for debugging

2. **Graceful Degradation**:
   - Partial results are better than nothing
   - Motor/rocket/environment data still useful even if flight failed

3. **Debugging Improvements**:
   - Timestamped logs make it easy to correlate issues
   - All simulation details preserved automatically
   - No manual log file management needed

4. **Safety Net**:
   - Default 5-minute timeout prevents infinite runs
   - Can disable for known slow simulations
   - Exit codes help automation detect problems

## Future Enhancements

Possible improvements:

1. **Progress Callback**: Show simulation progress during long runs
2. **Incremental Trajectory Export**: Save trajectory data periodically during simulation
3. **Resume Capability**: Save simulation state to resume after timeout
4. **Adaptive Timeout**: Automatically estimate timeout based on rocket parameters
5. **Parallel Monte Carlo with Timeout**: Apply timeout to individual Monte Carlo runs

## Related Files Modified

1. `scripts/run_single_simulation.py`:
   - Added timeout mechanism with SIGALRM
   - Auto log file generation
   - Partial export logic
   - Improved error messages

2. `src/utils.py`:
   - Fixed `setup_logging()` to allow reconfiguration
   - Added handler removal before adding new ones

3. `src/flight_simulator.py`:
   - Fixed compatibility with RocketPy API changes
   - Handle missing `apogee_x`/`apogee_y` attributes
   - Use `Function.get_value_opt()` instead of direct calls

## Compatibility

- ✅ **Backward compatible**: Existing scripts work without changes
- ✅ **Optional features**: Can disable timeout with `--timeout 0`
- ✅ **Manual override**: Can still specify custom log file path
- ✅ **RocketPy versions**: Compatible with both old and new RocketPy APIs

## Summary

This feature set transforms the simulation system from a "run and hope" approach to a robust, production-ready tool that:
- ✅ **Detects problems early** (unstable rockets)
- ✅ **Prevents infinite hangs** (timeout)
- ✅ **Saves partial results** (always useful data)
- ✅ **Provides complete logs** (automatic timestamped files)
- ✅ **Guides users** (helpful error messages and suggestions)

**Result**: Users can confidently run simulations knowing they'll get useful output and diagnostics, even if the rocket configuration is problematic.
