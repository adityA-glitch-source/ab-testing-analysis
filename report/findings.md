# A/B Test Report — Landing Page Experiment

**Analyst:** Aditya Kumar 
**Date:** 2026-05-23  
**Dataset:** `ab_data.csv` — 294,478 user sessions, Jan 2017

---

## Executive Summary

The new landing page did **not** outperform the old one. After testing on over 290,000 users, the difference in conversion rates is small, not statistically significant, and points slightly *against* the new design. The recommendation is to **retain the current page** and re-examine the hypothesis.

---

## Experiment Design

| Parameter | Value |
|---|---|
| Hypothesis | New landing page increases conversion rate |
| Primary metric | Conversion rate (binary: converted / not converted) |
| Groups | Control (old page) / Treatment (new page) |
| Traffic split | ~50/50 |
| Test duration | ~22 days (January 2017) |
| Significance threshold | α = 0.05 |

**Power analysis:** To detect a 2 percentage point lift at 80% power, only ~3,800 users per group are needed. With 145k+ per group, this experiment was massively overpowered — if any meaningful effect existed, it would have been detected.

---

## Data Quality

| Issue | Rows affected | Action |
|---|---|---|
| Group/page mismatch | 3,893 | Removed |
| Duplicate user IDs | 3,894 | Kept first occurrence by timestamp |
| **Final clean dataset** | **290,584** | — |

---

## Results

| Metric | Control | Treatment |
|---|---|---|
| Users | 145,274 | 145,310 |
| Conversions | 17,489 | 17,264 |
| Conversion rate | **12.04%** | **11.88%** |
| Absolute difference | — | −0.16 pp |
| Relative lift | — | −1.31% |

### Statistical tests

| Test | Statistic | P-value | Conclusion |
|---|---|---|---|
| Two-proportion z-test | z = −1.31 | 0.19 | Not significant |
| Chi-square | χ² = 1.72 | ~0.19 | Not significant |
| Bayesian | P(trt > ctrl) ≈ 9% | — | Treatment likely worse |

**95% confidence interval** on the difference: −0.39 pp to +0.08 pp  
The entire CI includes zero and extends mostly negative — consistent with no effect or a small negative effect.

---

## Time Analysis

- No novelty effect detected: daily conversion rates were flat and parallel throughout the experiment
- Day-of-week patterns were consistent between groups, confirming no systematic bias

---

## Recommendation

**Do not ship the new page.**

Three independent statistical approaches agree: the new landing page shows no improvement. The experiment was large enough that a genuine 1%+ lift would have been detected. Consider:

1. **Qualitative review** — why did the new design underperform? User testing or session recordings may reveal friction points
2. **Iterate the hypothesis** — a different element (headline, CTA, layout) may have more impact
3. **Segment analysis** — if conversion data can be split by user source or device, segmented tests may reveal where improvements are possible

---

## Methods

All analysis performed in Python using `pandas`, `scipy`, `numpy`, and `matplotlib`.  
Bayesian test used a Beta-Binomial conjugate model with a uniform Beta(1,1) prior and 50,000 posterior samples.

Source code: [github.com/yourname/ab-testing-analysis](https://github.com)
