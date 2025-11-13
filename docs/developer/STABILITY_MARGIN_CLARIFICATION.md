# Static Margin vs Stability Margin - Technical Clarification

## Overview

RocketPy provides **two different stability metrics** that are often confused:

1. **Static Margin** (`rocket.static_margin(time)`)
2. **Stability Margin** (`rocket.stability_margin(mach, time)`)

## Key Differences

### Static Margin
```python
static_margin(time) = (CoM(time) - CP(Mach=0)) / (2 * radius)
```

- **Function of**: Time only
- **CP assumption**: Fixed at Mach = 0 (subsonic, incompressible flow)
- **Use case**: Conservative estimate for subsonic rockets
- **Valid for**: Mach < 0.3 approximately
- **Aerospace standard**: Most design guidelines reference this

### Stability Margin  
```python
stability_margin(mach, time) = (CoM(time) - CP(mach)) / (2 * radius)
```

- **Function of**: Both Mach number AND time
- **CP behavior**: Varies with Mach (accounts for transonic/supersonic CP shift)
- **Use case**: Accurate prediction for high-speed rockets
- **Valid for**: All Mach regimes (subsonic, transonic, supersonic)
- **More realistic**: Captures CP travel during flight

## Why This Matters

### CP Movement in Transonic Region

As rockets accelerate through the transonic region (Mach 0.8 - 1.2):
- **CP typically moves AFT** (toward tail)
- This **increases** stability margin
- Ignoring this can lead to **overly conservative designs**

### Common Mistakes

❌ **WRONG**: Plotting `static_margin` vs Mach
```python
# This is meaningless - static_margin doesn't depend on Mach!
for mach in mach_range:
    sm = rocket.static_margin(time)  # Always uses CP(Mach=0)
```

✅ **CORRECT**: Use `stability_margin` for Mach-dependent analysis
```python
# This correctly shows how stability changes with Mach
for mach in mach_range:
    sm = rocket.stability_margin(mach, time)  # Uses CP(mach)
```

## Plot Naming Conventions

### rocket-sim Implementation

| Plot Name | Function Used | Description |
|-----------|---------------|-------------|
| `static_margin_vs_time.png` | `static_margin(time)` | **Static margin** at Mach=0 vs time |
| `static_margin_enhanced.png` | `static_margin(time)` | Same with aerospace guidelines |
| `stability_margin_surface.png` | `stability_margin(mach, time)` | **Stability margin** as function of Mach & time |

### Title Clarifications (v2.0)

**Before** (ambiguous):
- "Static Margin vs Time" 
- "Stability Margin Surface (Mach vs Time)"

**After** (explicit):
- "Static Margin vs Time (at Mach=0)"
- "Stability Margin (function of Mach & Time)"

## When to Use Each

### Use Static Margin When:
- ✅ Rocket is **subsonic only** (Mach < 0.3)
- ✅ Following **aerospace design guidelines** (typically reference Mach=0)
- ✅ Need **conservative estimate** for certification
- ✅ Comparing to **published design standards**

### Use Stability Margin When:
- ✅ Rocket reaches **transonic or supersonic** speeds
- ✅ Need **accurate prediction** of flight behavior
- ✅ Analyzing **CP travel effects**
- ✅ Optimizing fin size (avoid over-design)

## Example Flight Scenario

**Rocket**: Lumière (from 02_complete.yaml)
- Max Mach: 0.884 (transonic)
- Burn time: 4.9s

### Static Margin (Mach=0):
```
t=0s:    1.40 calibers  (CP fixed at subsonic position)
t=4.9s:  1.83 calibers  (CoM moved forward as propellant burns)
```

### Stability Margin (actual Mach):
```
t=0s, M=0:      1.40 calibers  (same as static)
t=4.6s, M=0.88: 1.95 calibers  (CP shifted aft in transonic region!)
t=4.9s, M=0.70: 1.87 calibers  (CP moving back forward as slowing)
```

**Key insight**: Actual stability margin at max-Q is **higher** than static margin predicts, because CP moves aft in transonic flight.

## Code Examples

### Correct: Static Margin Plot
```python
# Plot static margin (CP fixed at Mach=0)
time_range = np.linspace(0, burnout_time, 100)
static_margins = [rocket.static_margin(t) for t in time_range]

plt.plot(time_range, static_margins)
plt.xlabel("Time (s)")
plt.ylabel("Static Margin (calibers)")
plt.title("Static Margin vs Time (at Mach=0)")
```

### Correct: Stability Margin Surface
```python
# Plot stability margin (CP varies with Mach)
mach_range = np.linspace(0, 1.2, 50)
time_range = np.linspace(0, burnout_time, 50)

for i, t in enumerate(time_range):
    for j, m in enumerate(mach_range):
        margin[i, j] = rocket.stability_margin(m, t)

plt.contourf(mach_range, time_range, margin)
plt.xlabel("Mach Number")
plt.ylabel("Time (s)")
plt.title("Stability Margin (function of Mach & Time)")
```

### WRONG: Don't Do This!
```python
# ❌ WRONG - static_margin doesn't depend on Mach!
mach_range = np.linspace(0, 1.2, 50)
wrong_margins = [rocket.static_margin(5.0) for m in mach_range]
# This just plots the same value 50 times!

plt.plot(mach_range, wrong_margins)
plt.title("Static Margin vs Mach")  # MISLEADING!
```

## RocketPy Source Code Reference

From `rocketpy/rocket/rocket.py`:

```python
def evaluate_static_margin(self):
    """Static margin uses CP at Mach=0 (fixed)"""
    self.static_margin.set_source(
        lambda time: (
            self.center_of_mass.get_value_opt(time)
            - self.cp_position.get_value_opt(0)  # ← Always Mach=0!
        ) / (2 * self.radius)
    )

def evaluate_stability_margin(self):
    """Stability margin uses CP at actual Mach (variable)"""
    self.stability_margin.set_source(
        lambda mach, time: (
            self.center_of_mass.get_value_opt(time)
            - self.cp_position.get_value_opt(mach)  # ← Actual Mach!
        ) / (2 * self.radius)
    )
```

## Aerospace Guidelines Context

Most aerospace design guidelines (e.g., Barrowman, Niskanen) specify:
- **Minimum static margin**: 1.0 - 1.5 calibers (at Mach=0)
- **Design target**: 2.0 - 2.5 calibers (at Mach=0)

These are **conservative** values that:
1. Assume worst-case (subsonic CP position)
2. Provide safety factor for uncertainties
3. Are valid across all Mach regimes

**However**: Actual in-flight stability (stability margin) is often **higher** than static margin predicts, especially in transonic region.

## Conclusion

- **Static margin** = simplified metric assuming Mach=0 (conservative)
- **Stability margin** = realistic metric accounting for CP travel with Mach
- **Both are valid** - use static margin for design, stability margin for analysis
- **Never plot static margin vs Mach** - it doesn't vary with Mach by definition!

## See Also

- [RocketPy Documentation - Stability](https://docs.rocketpy.org/)
- [Barrowman Method for CP Calculation](https://www.apogeerockets.com/education/downloads/barrowman.pdf)
- OpenRocket Technical Documentation
