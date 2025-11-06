# Sensitivity Analysis: Theory and Methodology

Comprehensive guide to sensitivity analysis methods implemented in the Rocket Simulation Framework.

## Table of Contents

1. [Introduction](#introduction)
2. [Variance-Based Sensitivity Analysis](#variance-based-sensitivity-analysis)
3. [One-At-a-Time (OAT) Sensitivity](#one-at-a-time-oat-sensitivity)
4. [Linear Approximation Error](#linear-approximation-error)
5. [Sobol Indices (Theory)](#sobol-indices-theory)
6. [Method Comparison](#method-comparison)
7. [Interpretation Guidelines](#interpretation-guidelines)
8. [Best Practices](#best-practices)
9. [References](#references)

---

## Introduction

### What is Sensitivity Analysis?

**Sensitivity analysis** quantifies how uncertainty in input parameters propagates to output metrics. It answers the question:

> **"Which input parameters have the greatest influence on the outputs of interest?"**

### Why is it Important for Rocket Simulations?

1. **Design Optimization**: Identify which parameters to focus on for performance improvements
2. **Uncertainty Quantification**: Understand which uncertainties dominate output variability
3. **Robustness Analysis**: Determine sensitivity to manufacturing tolerances
4. **Validation**: Guide instrumentation decisions (measure most influential parameters)
5. **Risk Assessment**: Identify critical parameters requiring tight tolerances

### Types of Sensitivity Analysis

| Type | Local/Global | Computational Cost | Interaction Effects | Use Case |
|------|--------------|-------------------|-------------------|----------|
| **One-At-a-Time (OAT)** | Local | Low (2N+1 sims) | ✗ Not captured | Quick screening |
| **Variance-Based** | Global | Medium (100-1000 sims) | ✓ Implicitly captured | Comprehensive analysis |
| **Sobol Indices** | Global | High (N(2P+2) sims) | ✓ Explicitly quantified | Detailed interaction study |
| **Morris Screening** | Global | Medium (r(P+1) sims) | ✓ Qualitative | Parameter ranking |

**This framework implements**: OAT and Variance-Based methods.

---

## Variance-Based Sensitivity Analysis

### Mathematical Foundation

Variance-based sensitivity uses **multiple linear regression** to decompose output variance into contributions from each input parameter.

#### The Linear Model

For a target output \( y \) and \( P \) input parameters \( x_1, x_2, \ldots, x_P \):

```
y = β₀ + β₁·x₁ + β₂·x₂ + ... + βₚ·xₚ + ε
```

Where:
- \( β₀ \): Intercept (baseline output)
- \( β_j \): Regression coefficient for parameter \( j \)
- \( ε \): Residual error (model uncertainty)

#### Ordinary Least Squares (OLS) Solution

The regression coefficients are estimated using OLS:

```
β̂ = (XᵀX)⁻¹Xᵀy
```

Where:
- \( X \): Design matrix (N × P) of parameter values
- \( y \): Vector (N × 1) of target outputs
- \( β̂ \): Vector (P × 1) of estimated coefficients

We use **statsmodels** library for robust OLS regression with diagnostic statistics.

### Sensitivity Coefficient Formula

The **sensitivity coefficient** \( S_j \) represents the percentage of output variance explained by parameter \( j \):

```
       β²ⱼ · σ²ⱼ
Sⱼ = ────────────── × 100%
     σ²ε + Σₖ(β²ₖ · σ²ₖ)
```

Where:
- \( β_j \): Standardized regression coefficient for parameter \( j \)
- \( σ_j \): Standard deviation of parameter \( j \)
- \( σ_ε \): Residual standard error
- Summation is over all \( k = 1, \ldots, P \)

#### Interpretation

- **\( S_j = 50% \)**: Parameter \( j \) contributes 50% of the output variance
- **\( \sum_j S_j ≈ 100% - LAE \)**: Sum approaches 100% for good linear models
- **\( S_j < LAE \)**: Parameter effect is not statistically significant

### Standardized vs. Unstandardized Coefficients

#### Standardized Coefficients (Used for Sensitivity)

Standardized coefficients allow fair comparison between parameters with different units/scales:

```
β*ⱼ = βⱼ · (σⱼ / σy)
```

Where:
- \( β^*_j \): Standardized coefficient
- \( σ_y \): Standard deviation of output \( y \)

**Key property**: \( |β^*_j| \) directly indicates relative importance.

#### Example: Apogee Sensitivity

Consider apogee prediction:

```
Apogee = β₀ + β₁·(Thrust) + β₂·(Mass) + β₃·(Wind) + ε
```

**Standardized coefficients**:
- \( β^*_1 = 0.85 \) (Thrust)
- \( β^*_2 = -0.42 \) (Mass)
- \( β^*_3 = -0.18 \) (Wind)

**Interpretation**:
- Thrust is most influential (positive: more thrust → higher apogee)
- Mass is second (negative: more mass → lower apogee)
- Wind has minor effect

### Variance Decomposition

The total output variance can be decomposed:

```
Var(y) = Var(ŷ) + Var(ε)
```

Where:
- \( Var(y) \): Total output variance
- \( Var(ŷ) \): Variance explained by the model
- \( Var(ε) \): Residual variance (unexplained)

The **R²** (coefficient of determination) measures model fit:

```
       Var(ŷ)
R² = ─────────
      Var(y)
```

- \( R² = 1.0 \): Perfect fit (all variance explained)
- \( R² = 0.0 \): Model explains nothing

### Multicollinearity Concerns

**Multicollinearity** occurs when input parameters are correlated, inflating coefficient standard errors.

**Detection**:
- **Variance Inflation Factor (VIF)**:
  ```
         1
  VIF = ─────
        1 - R²ⱼ
  ```
  Where \( R²_j \) is the R² from regressing \( x_j \) on all other parameters.

  **Guidelines**:
  - VIF < 5: No multicollinearity
  - 5 < VIF < 10: Moderate multicollinearity
  - VIF > 10: Severe multicollinearity (problematic)

**Solution**: Use **orthogonal sampling** (Latin Hypercube Sampling) or **PCA**.

### Algorithm Implementation

```python
def fit_variance_based_sensitivity(params_df, targets_df):
    """
    Fit variance-based sensitivity model.

    Steps:
    1. Standardize parameters (zero mean, unit variance)
    2. Fit OLS regression for each target
    3. Extract coefficients β and residual std σε
    4. Calculate sensitivity coefficients Sⱼ
    5. Validate using Linear Approximation Error
    """
    results = {}

    for target_name in targets_df.columns:
        y = targets_df[target_name]
        X = params_df

        # Standardize
        X_std = (X - X.mean()) / X.std()
        y_std = (y - y.mean()) / y.std()

        # Fit OLS
        model = sm.OLS(y_std, sm.add_constant(X_std)).fit()

        # Extract coefficients
        betas = model.params[1:]  # Exclude intercept
        sigma_epsilon = np.sqrt(model.scale)  # Residual std

        # Calculate sensitivities
        variance_components = betas**2  # Already standardized
        total_variance = variance_components.sum() + sigma_epsilon**2

        sensitivities = 100 * variance_components / total_variance

        # LAE
        lae = 100 * sigma_epsilon**2 / total_variance

        results[target_name] = {
            'sensitivities': sensitivities,
            'lae': lae,
            'r_squared': model.rsquared,
        }

    return results
```

---

## One-At-a-Time (OAT) Sensitivity

### Methodology

OAT sensitivity evaluates **local derivatives** by perturbing one parameter at a time while holding others constant.

#### Algorithm

For \( P \) parameters:

1. **Baseline Simulation**: Evaluate output at nominal parameter values \( x₀ \)
   ```
   y₀ = f(x₀)
   ```

2. **Perturbations**: For each parameter \( j = 1, \ldots, P \):
   - Positive perturbation: \( x^+_j = x₀ + δ·x₀,j \)
   - Negative perturbation: \( x^-_j = x₀ - δ·x₀,j \)

   Where \( δ \) is the perturbation fraction (e.g., 10%).

3. **Evaluate Outputs**:
   ```
   y^+_j = f(x^+_j)
   y^-_j = f(x^-_j)
   ```

4. **Calculate Local Derivative**:
   ```
   ∂y     y^+_j - y^-_j
   ── ≈ ────────────────
   ∂xⱼ      2δ·x₀,j
   ```

**Total simulations**: \( 2P + 1 \) (baseline + 2 per parameter).

### Normalized Sensitivity

To compare parameters with different units, use **normalized sensitivity**:

```
        ∂y   x₀,j
S*ⱼ = ── · ────
       ∂xⱼ   y₀
```

**Interpretation**: \( S^*_j = 0.5 \) means a 1% change in \( x_j \) causes a 0.5% change in \( y \).

### Tornado Diagram

A **tornado diagram** visualizes OAT sensitivities:

- **X-axis**: Output value
- **Y-axis**: Parameters (ranked by effect magnitude)
- **Bars**: Extend from \( y^-_j \) to \( y^+_j \)

**Example**:
```
Motor Thrust   |=============================|  (largest effect)
Dry Mass       |===================|
Wind Speed     |===========|
CG Location    |======|                       (smallest effect)
```

### Limitations

1. **Local Analysis**: Only valid near nominal point \( x₀ \)
2. **No Interactions**: Assumes parameter effects are additive
3. **Linearity Assumption**: Assumes \( ∂y/∂x_j \) is constant
4. **Inefficient for Many Parameters**: Scales linearly with \( P \)

### When to Use OAT

✅ **Good for**:
- Quick parameter screening (small \( P \))
- Initial exploration before Monte Carlo
- Validating variance-based results
- Deterministic models (no stochasticity)

❌ **Not ideal for**:
- Highly nonlinear models
- Strong parameter interactions
- Global sensitivity across wide ranges

---

## Linear Approximation Error

### Definition

**Linear Approximation Error (LAE)** quantifies how well a linear model fits the data:

```
       σ²ε
LAE = ────── × 100%
      σ²y
```

Where:
- \( σ²_ε \): Residual variance (unexplained by linear model)
- \( σ²_y \): Total output variance

Equivalently:
```
LAE = (1 - R²) × 100%
```

### Interpretation Guidelines

| LAE | Model Quality | Recommendation |
|-----|--------------|----------------|
| < 5% | Excellent | Linear model is highly accurate |
| 5-10% | Good | Linear approximation is acceptable |
| 10-20% | Fair | Use cautiously; check residuals |
| > 20% | Poor | Linear model is inadequate; consider nonlinear methods |

### Why LAE Matters

1. **Validates Methodology**: Ensures variance-based sensitivity is appropriate
2. **Significance Threshold**: Parameters with \( S_j < LAE \) are not statistically significant
3. **Model Selection**: High LAE suggests need for nonlinear regression or Sobol indices

### Example

**Scenario**: Apogee prediction with 5 parameters

**Results**:
- \( R² = 0.92 \)
- \( LAE = 8\% \)
- Sensitivities: Thrust (65%), Mass (18%), Wind (9%), CG (4%), Fins (4%)

**Interpretation**:
- Linear model is **good** (LAE = 8% < 10%)
- Thrust, Mass, Wind are **significant** (\( S_j > LAE \))
- CG and Fins are **not significant** (\( S_j < LAE \)) — effects likely due to noise

### Checking Residuals

Even with low LAE, inspect **residual plots**:

```python
import matplotlib.pyplot as plt

# Residuals vs. Fitted
plt.scatter(model.fittedvalues, model.resid)
plt.axhline(0, color='red', linestyle='--')
plt.xlabel('Fitted Values')
plt.ylabel('Residuals')
plt.title('Residual Plot')
```

**Good residual plot**:
- Random scatter around zero
- No patterns (funnels, curves, clusters)
- Homoscedasticity (constant variance)

---

## Sobol Indices (Theory)

### Overview

**Sobol indices** provide rigorous variance decomposition including interaction effects. While not yet implemented, the theory is included for completeness and future work.

### First-Order Indices

The **first-order Sobol index** \( S_i \) measures the main effect of parameter \( i \):

```
     Var[E(y | xᵢ)]
Sᵢ = ──────────────
        Var(y)
```

**Interpretation**: Fraction of variance due to \( x_i \) alone (no interactions).

### Total-Order Indices

The **total-order Sobol index** \( S_{T_i} \) includes main effect plus all interactions involving \( x_i \):

```
           E[Var(y | x₋ᵢ)]
S_Tᵢ = 1 - ─────────────────
              Var(y)
```

Where \( x_{-i} \) denotes all parameters except \( x_i \).

**Interpretation**: Total contribution including interactions.

### Interaction Indices

The **interaction effect** is:

```
S_interaction,i = S_Tᵢ - Sᵢ
```

- \( S_{interaction,i} = 0 \): No interactions involving \( x_i \)
- \( S_{interaction,i} > 0 \): Parameter \( x_i \) interacts with others

### Computational Cost

**Saltelli sampling scheme** requires \( N(2P + 2) \) simulations:
- \( N \): Base sample size (e.g., 1000)
- \( P \): Number of parameters

**Example**: 10 parameters, N=1000 → 22,000 simulations.

**Why so many?**
- Accurate variance estimation requires large sample sizes
- Interaction indices need cross-sample evaluations

### Convergence

Sobol indices converge slowly: \( O(1/\sqrt{N}) \).

**Practical implications**:
- N=1000: ±3% error
- N=10,000: ±1% error

### Comparison with Variance-Based

| Aspect | Variance-Based | Sobol Indices |
|--------|---------------|---------------|
| Simulations | 100-1000 | 1000-10,000+ |
| Interaction Effects | Implicit (absorbed in LAE) | Explicit quantification |
| Linearity Assumption | Yes (linear regression) | No (model-free) |
| Computational Cost | Medium | High |
| Best For | Linear/mildly nonlinear | Highly nonlinear, complex interactions |

---

## Method Comparison

### Comparison Matrix

| Criteria | OAT | Variance-Based | Sobol Indices |
|----------|-----|----------------|---------------|
| **Simulations** | 2P+1 | 100-1000 | N(2P+2) |
| **Sensitivity Type** | Local derivatives | Global variance | Global variance |
| **Interaction Effects** | ✗ None | ✓ Implicit | ✓ Explicit |
| **Linearity Requirement** | Assumed | Validated (LAE) | None |
| **Computational Cost** | Very Low | Medium | High |
| **Ease of Interpretation** | High | High | Medium |
| **Parameter Ranking** | ✓ Direct | ✓ Direct | ✓ Direct |
| **Confidence Intervals** | ✗ Difficult | ✓ Via bootstrap | ✓ Via resampling |

### When to Use Each Method

#### Use OAT When:
- Quick screening needed (limited time/resources)
- Few parameters (\( P < 10 \))
- Model is approximately linear near nominal point
- Validating other methods

#### Use Variance-Based When:
- Comprehensive global analysis needed
- Model is linear or mildly nonlinear
- 100-1000 simulations feasible
- Clear parameter ranking desired
- Interaction effects not critical

#### Use Sobol (Future) When:
- Model is highly nonlinear
- Interaction effects are important
- High computational budget available
- Rigorous variance decomposition required

### Workflow Recommendation

**Phase 1**: OAT Sensitivity (Quick Screening)
- Identify obviously unimportant parameters
- Eliminate parameters with negligible effects
- Reduce dimensionality for Phase 2

**Phase 2**: Variance-Based Sensitivity (Comprehensive Analysis)
- Quantify global sensitivities
- Validate with LAE
- Identify significant parameters

**Phase 3** (Optional): Sobol Indices (Detailed Study)
- Quantify interaction effects
- Refine understanding for most influential parameters

---

## Interpretation Guidelines

### Reading Sensitivity Coefficients

#### Variance-Based Sensitivities

**Example Output**:
```
Parameter       Sensitivity
─────────────  ────────────
Motor Thrust        65.2%
Dry Mass           18.4%
Wind Speed          9.1%
CG Location         4.2%
Fin Cant Angle      3.1%
─────────────  ────────────
LAE                 8.0%
```

**Interpretation**:
1. **Thrust dominates** (65%): Most important parameter
2. **Mass is secondary** (18%): Significant but less critical
3. **Wind is tertiary** (9%): Moderate effect
4. **CG and Fins are marginal** (< LAE): Effects may be noise
5. **LAE is acceptable** (8% < 10%): Linear model is valid

**Actions**:
- **Prioritize thrust accuracy**: Measure/calibrate thrust curves
- **Control mass carefully**: Weigh components precisely
- **Monitor wind conditions**: Check forecasts on launch day
- **Relax CG/fin tolerances**: Less critical (within reason)

#### OAT Sensitivities (Tornado Diagram)

**Example**:
```
Parameter        Low         Nominal        High
────────────  ─────────  ─────────────  ─────────
Thrust        |======2800=======3200========>3600|
Mass          |<2900======3200========3400====|
Wind          |<3050======3200=====3300=====|
CG            |<3150======3200====3250====|
```

**Interpretation**:
- **Thrust**: ±10% variation → ±400m apogee change
- **Mass**: -10% → +300m, +10% → -200m (asymmetric)
- **Wind**: Smaller effect (±100m)
- **CG**: Minimal effect (±50m)

### Statistical Significance

A parameter is **statistically significant** if:

```
Sⱼ > LAE + margin
```

**Recommended margin**: 2-5% for conservative analysis.

**Example**:
- LAE = 8%
- Margin = 2%
- Threshold = 10%

Parameters with \( S_j > 10\% \) are confidently significant.

### Confidence Intervals

Use **bootstrap resampling** to estimate confidence intervals:

1. Resample Monte Carlo data (with replacement)
2. Recalculate sensitivities for each bootstrap sample
3. Compute 95% confidence interval (2.5th, 97.5th percentiles)

**Example**:
```
Parameter    Sensitivity    95% CI
──────────  ────────────  ──────────
Thrust         65.2%       [62.1, 68.3]
Mass           18.4%       [15.7, 21.2]
Wind            9.1%       [ 6.8, 11.5]
```

**Interpretation**: Thrust sensitivity is 65% ± 3% (95% confidence).

---

## Best Practices

### 1. Sample Size Selection

#### Variance-Based Analysis

**Rule of Thumb**: \( N \geq 10P \) simulations

| Parameters (P) | Minimum Simulations | Recommended |
|---------------|-------------------|-------------|
| 5             | 50                | 100-200     |
| 10            | 100               | 200-500     |
| 20            | 200               | 500-1000    |

**Why?**: Regression needs adequate degrees of freedom for stable coefficient estimation.

#### OAT Analysis

**Fixed**: \( N = 2P + 1 \)

**Example**: 10 parameters → 21 simulations.

### 2. Parameter Variation Ranges

#### Variance-Based

Use realistic uncertainty ranges:

```yaml
variations:
  motor_thrust_std_pct: 5.0      # ±5% (manufacturer spec)
  dry_mass_std_kg: 0.5           # ±0.5 kg (weighing accuracy)
  wind_speed_std_ms: 2.0         # ±2 m/s (forecast uncertainty)
```

**Guidelines**:
- **Tight tolerances**: Precision manufacturing (±2-5%)
- **Moderate uncertainties**: Standard components (±5-10%)
- **High uncertainties**: Environmental factors (±10-50%)

#### OAT

Use consistent perturbation percentage:

```python
perturbation_pct = 10.0  # ±10% for all parameters
```

**Note**: Ensure perturbations don't violate physical constraints (e.g., negative mass).

### 3. Validate Linear Approximation

Always check LAE before trusting variance-based results:

```python
lae = analyzer.get_linear_approximation_error()

for target, error in lae.items():
    if error > 10:
        print(f"⚠ Warning: LAE for {target} is {error:.1f}%")
        print("  Consider using Sobol indices or nonlinear regression")
```

### 4. Cross-Validate Methods

Compare OAT and variance-based results:

```python
# OAT
oat_sensitivities = oat_analyzer.run()

# Variance-based
vb_sensitivities = vb_analyzer.get_sensitivity_coefficients()

# Compare rankings
print("Parameter Ranking Comparison:")
print("OAT        Variance-Based")
for param in parameters:
    oat_rank = rank(oat_sensitivities[param])
    vb_rank = rank(vb_sensitivities[param])
    print(f"{param:12s}  {oat_rank}           {vb_rank}")
```

**Expect**: Similar rankings for top parameters (minor differences for weak parameters).

### 5. Focus on Significant Parameters

After sensitivity analysis:

1. **Identify significant parameters** (\( S_j > LAE \))
2. **Prioritize control** for high-sensitivity parameters
3. **Relax tolerances** for low-sensitivity parameters (cost savings)
4. **Design experiments** to refine high-sensitivity estimates

### 6. Document Assumptions

Clearly state:
- Parameter uncertainty ranges and sources
- Number of simulations
- LAE values and model fit
- Any parameter correlations

**Example**:
```
Sensitivity Analysis Metadata:
- Method: Variance-Based (OLS Regression)
- Simulations: 500 Monte Carlo runs
- LAE (Apogee): 7.2% (Good linear fit)
- Parameter Ranges: ±5% thrust, ±0.5 kg mass, ±2 m/s wind
- Correlations: None assumed (independent sampling)
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Multicollinearity

**Symptom**: Large coefficient standard errors, unstable sensitivities.

**Cause**: Correlated parameters (e.g., mass and CG often correlated).

**Solution**:
- Use **orthogonal sampling** (Latin Hypercube)
- Check VIF for each parameter
- Remove or combine correlated parameters

### Pitfall 2: Insufficient Sample Size

**Symptom**: High variability in sensitivities across bootstrap samples.

**Cause**: Too few Monte Carlo simulations.

**Solution**:
- Increase \( N \) (aim for 10-20 samples per parameter)
- Check bootstrap confidence intervals

### Pitfall 3: Overfitting

**Symptom**: \( R² \) near 1.0 but poor predictive performance.

**Cause**: Too many parameters relative to sample size.

**Solution**:
- Use **cross-validation** to assess predictive accuracy
- Apply **regularization** (Ridge, Lasso) if \( P \) is large

### Pitfall 4: Ignoring LAE

**Symptom**: Interpreting sensitivities when LAE > 20%.

**Cause**: Using variance-based method on highly nonlinear model.

**Solution**:
- Check LAE before interpretation
- Use Sobol indices for high-LAE cases
- Consider polynomial regression or GAM (Generalized Additive Models)

### Pitfall 5: Misinterpreting OAT Results

**Symptom**: Assuming OAT derivatives apply globally.

**Cause**: Extrapolating local sensitivity beyond nominal point.

**Solution**:
- Clearly label OAT as **local** analysis
- Validate with variance-based global analysis
- Use OAT only for screening

---

## Practical Example

### Rocket Apogee Sensitivity

**Scenario**: Determine which parameters most influence apogee altitude.

#### Parameters

| Parameter | Nominal | Uncertainty | Distribution |
|-----------|---------|------------|--------------|
| Motor Thrust | 1670 N | ±5% | Normal |
| Dry Mass | 15.4 kg | ±0.5 kg | Normal |
| Wind Speed | 5 m/s | ±2 m/s | Normal |
| CG Location | 1.27 m | ±0.05 m | Normal |
| Drag Coefficient | 0.45 | ±10% | Normal |

#### Step 1: OAT Screening

```python
oat = OATSensitivityAnalyzer(
    base_config_path='configs/rocket.yaml',
    parameters={
        'motor_thrust': 1670.0,
        'dry_mass': 15.4,
        'wind_speed': 5.0,
        'cg_location': 1.27,
        'drag_coefficient': 0.45,
    },
    perturbation_pct=10.0,
)

oat_results = oat.run()
oat.plot_tornado_diagram('apogee_m')
```

**Results**:
- Thrust: ∂(apogee)/∂(thrust) = 2.1 m/N
- Mass: ∂(apogee)/∂(mass) = -18.5 m/kg
- Wind: ∂(apogee)/∂(wind) = -12.3 m/(m/s)
- CG: ∂(apogee)/∂(cg) = 3.2 m/m
- Drag: ∂(apogee)/∂(cd) = -850 m/unit

#### Step 2: Variance-Based Analysis

```python
# Run Monte Carlo
mc = MonteCarloRunner(
    base_config_path='configs/rocket.yaml',
    mc_config=MonteCarloConfig(
        num_simulations=500,
        variations={
            'motor_thrust_std_pct': 5.0,
            'dry_mass_std_kg': 0.5,
            'wind_speed_std_ms': 2.0,
            'cg_location_std_m': 0.05,
            'drag_coefficient_std_pct': 10.0,
        }
    ),
)

mc_results = mc.run()

# Sensitivity analysis
params_df, targets_df = mc.export_for_sensitivity(
    parameter_names=['motor_thrust', 'dry_mass', 'wind_speed', 'cg_location', 'drag_coefficient'],
    target_names=['apogee_m'],
)

vb = VarianceBasedSensitivityAnalyzer()
vb.fit(params_df, targets_df)

sensitivities = vb.get_sensitivity_coefficients()
lae = vb.get_linear_approximation_error()
```

**Results**:
```
Parameter           Sensitivity (%)
────────────────   ────────────────
Motor Thrust             62.5
Dry Mass                 21.3
Wind Speed                8.7
Drag Coefficient          6.1
CG Location               1.4
────────────────   ────────────────
LAE                       6.8
R²                       93.2%
```

#### Step 3: Interpretation

1. **Thrust is dominant** (62.5%): Focus on accurate thrust curves
2. **Mass is important** (21.3%): Weigh components carefully
3. **Wind is moderate** (8.7%): Monitor weather forecasts
4. **Drag and CG are minor** (< 10%): Less critical to control tightly
5. **Model is valid** (LAE = 6.8% < 10%): Linear approximation is good

#### Step 4: Design Recommendations

**High Priority**:
- Measure motor thrust curves in test stand
- Target ±2% thrust variation (vs. ±5% nominal)
- Weigh all components to ±0.1 kg

**Medium Priority**:
- Check wind forecasts within 2 hours of launch
- Plan launch window for low-wind conditions

**Low Priority**:
- CG and drag tolerances can remain at ±5-10%
- Focus budget on motor/mass control, not aerodynamics

---

## References

### Books

1. **Saltelli, A., et al. (2008)**. *Global Sensitivity Analysis: The Primer*. Wiley.
   - Comprehensive reference for Sobol indices and variance-based methods

2. **Montgomery, D. C. (2017)**. *Design and Analysis of Experiments* (9th ed.). Wiley.
   - Statistical foundations for sensitivity analysis

3. **Iman, R. L., & Helton, J. C. (1988)**. "An Investigation of Uncertainty and Sensitivity Analysis Techniques for Computer Models." *Risk Analysis*, 8(1), 71-90.
   - Classic paper on variance-based methods

### Papers

4. **Sobol, I. M. (2001)**. "Global Sensitivity Indices for Nonlinear Mathematical Models and Their Monte Carlo Estimates." *Mathematics and Computers in Simulation*, 55(1-3), 271-280.
   - Original Sobol indices methodology

5. **Saltelli, A., Annoni, P., Azzini, I., Campolongo, F., Ratto, M., & Tarantola, S. (2010)**. "Variance Based Sensitivity Analysis of Model Output. Design and Estimator for the Total Sensitivity Index." *Computer Physics Communications*, 181(2), 259-270.
   - Efficient algorithms for Sobol indices

6. **Pianosi, F., Beven, K., Freer, J., Hall, J. W., Rougier, J., Stephenson, D. B., & Wagener, T. (2016)**. "Sensitivity Analysis of Environmental Models: A Systematic Review with Practical Workflow." *Environmental Modelling & Software*, 79, 214-232.
   - Review paper with practical guidance

### Software Libraries

7. **SALib** (Python): https://salib.readthedocs.io/
   - Sobol, Morris, FAST sensitivity analysis

8. **statsmodels** (Python): https://www.statsmodels.org/
   - OLS regression for variance-based methods

9. **sensitivity** (R): https://cran.r-project.org/web/packages/sensitivity/
   - Comprehensive sensitivity analysis in R

### RocketPy Resources

10. **RocketPy Documentation**: https://docs.rocketpy.org/
    - Monte Carlo and sensitivity analysis examples

11. **RocketPy Notebooks**: https://github.com/RocketPy-Team/RocketPy/tree/master/docs/notebooks
    - Example notebooks for sensitivity analysis

---

## Appendix: Mathematical Proofs

### Proof: Sensitivity Coefficient Formula

**Goal**: Derive the sensitivity coefficient \( S_j \) from variance decomposition.

**Assume**: Linear model with standardized variables:

```
y = β₁x₁ + β₂x₂ + ... + βₚxₚ + ε
```

Where \( E[x_j] = 0 \), \( Var(x_j) = 1 \), \( E[ε] = 0 \), and \( ε \) is independent of all \( x_j \).

**Step 1**: Total variance of \( y \)

```
Var(y) = Var(Σⱼ βⱼxⱼ + ε)
       = Var(Σⱼ βⱼxⱼ) + Var(ε)    [independence]
       = Σⱼ β²ⱼ Var(xⱼ) + σ²ε
       = Σⱼ β²ⱼ + σ²ε              [since Var(xⱼ) = 1]
```

**Step 2**: Variance contribution of parameter \( j \)

```
Contribution of xⱼ = β²ⱼ Var(xⱼ) = β²ⱼ
```

**Step 3**: Sensitivity coefficient

```
       β²ⱼ
Sⱼ = ──────────── × 100%
     Σₖ β²ₖ + σ²ε
```

For non-standardized variables, replace \( β²_j \) with \( β²_j σ²_j \). ∎

### Proof: LAE = 1 - R²

**Goal**: Show that LAE is equivalent to the complement of R².

**Recall**:

```
R² = Var(ŷ) / Var(y)

LAE = σ²ε / σ²y
```

**Proof**:

```
σ²y = σ²ŷ + σ²ε    [total variance decomposition]

σ²ε = σ²y - σ²ŷ

LAE = σ²ε / σ²y
    = (σ²y - σ²ŷ) / σ²y
    = 1 - σ²ŷ / σ²y
    = 1 - R²  ∎
```

---

## Glossary

- **LAE**: Linear Approximation Error — residual variance as percentage of total variance
- **OAT**: One-At-a-Time — local sensitivity method varying one parameter at a time
- **OLS**: Ordinary Least Squares — regression method minimizing squared residuals
- **R²**: Coefficient of determination — fraction of variance explained by model
- **Sobol Indices**: Variance-based global sensitivity indices including interaction effects
- **VIF**: Variance Inflation Factor — measure of multicollinearity
- **Sensitivity Coefficient (Sⱼ)**: Percentage of output variance explained by parameter \( j \)
- **Standardized Coefficient (β*ⱼ)**: Regression coefficient after standardizing variables

---

**End of Document**

For implementation details, see [API_REFERENCE.md](API_REFERENCE.md).
For system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
For practical examples, see [notebooks/03_sensitivity_analysis.ipynb](../notebooks/03_sensitivity_analysis.ipynb).
