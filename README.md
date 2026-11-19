# Capstone Project: A/B Test on the Impact of a Free Trial


## Description
Analysis of the impact of adding a "7-Day Free Trial" option on the pricing page of a digital product (simulated data). The experiment aims to measure whether this option reduces visitor hesitation and increases the conversion rate to paid subscriptions, without harming Average Revenue Per User (ARPU) or increasing the cancellation rate.

## Question and Hypothesis
**Question:** Does adding a 7-day free trial option increase the rate of paid subscriptions?

**Decision Required:** Launch the option for all subscription plans or do not launch it.

**Treatment:** Displaying the "7-Day Free Trial" option on the pricing page.

**Hypothesis:** If the free trial option is added, the paid subscription rate will increase (expected positive effect), because the free trial reduces initial financial hesitation and encourages visitors to use the service.

**What would change our minds:** We will refrain from launching if the cancellation rate increases with statistical significance, or if revenue per user decreases with statistical significance.

## Design
- **Target Population:** Pricing page visitors.
- **Randomization Unit:** User (User ID or cookies).
- **Groups:** A (Control, without free trial) and B (Treatment, with free trial).
- **Allocation Ratio and Implementation:** 50/50; each user is randomly assigned to A or B with a 50% probability for each (`numpy.random.choice`).
- **Primary Metric:** Conversion rate, i.e., the percentage of users who completed a paid subscription.
- **Guardrail Metrics:** Average Revenue Per User (ARPU) in SAR, and immediate cancellation rate.
- **Significance Level and Power:** α = 5% (two-tailed) and 80% statistical power.
- **Minimum Detectable Effect (MDE):** A 1 percentage point increase (from 5% to 6%).
- **Sample Size Calculation:** Two-proportion difference test formula:
  n = (z₁₋α/₂ + z₁₋β)² × [p₁(1−p₁) + p₂(1−p₂)] / (p₂−p₁)²
  Result: **8,155 users per group**.
- **Duration:** With an average of 2,000 daily users, approximately 8.2 days are required, rounded up to **14 days** (two full weeks to cover the weekly cycle). This yields 28,000 users, which is above the minimum required.

## Data and Quality Checks
- The data is **programmatically simulated** (Simulation) with `seed = 2026`, and is not real data. It is saved in `data/dataset.csv` (28,000 records).
- Columns: `user_id`, `group`, `converted`, `revenue`, and `cancelled`.
- **Simulation Assumptions:** True conversion rate of 5.0% for Group A and 6.2% for Group B (true effect of 1.2 percentage points); subscriber revenue from a normal distribution (mean 100 and standard deviation 20 SAR); cancellation probability of 2.0% for Group A and 2.1% for Group B.
- **Quality Checks (executed automatically by `main.py`):** No missing values, no duplicate records in `user_id`, record count matches expected (28,000), and Sample Ratio Mismatch (SRM) check using a chi-square test.

## Methodology
- **Primary Metric and Cancellation Rate:** Two-proportion z-test, because the sample size is large (thousands of users) and the metric is binary (0/1).
- **Revenue Per User:** Two-sample z-test for the difference between means.
- **Rationale:** Random assignment allows direct comparison between the two groups without additional models.
- 95% confidence intervals and two-tailed p-values for all metrics.

## Results
**SRM Check:** Allocation is valid (Group A: 13,944 | Group B: 14,056 | p = 0.5033).

**Primary Metric (Conversion Rate):**

| Group | Conversion Rate |
|---|---|
| A (Control) | 5.17% |
| B (Treatment) | 6.05% |

The difference is **+0.88 percentage points**, 95% confidence interval: [0.34%, 1.42%], p = 0.0013. The effect is positive and statistically significant.

**Guardrail Metrics:**

| Metric | Difference | 95% CI | p-value | Status |
|---|---|---|---|---|
| Revenue Per User | +0.80 SAR | [0.25, 1.35] | 0.0042 | Healthy (Improved) |
| Immediate Cancellation Rate | +0.01 percentage points | [-0.07%, 0.09%] | 0.7490 | Healthy (No evidence of harm) |

**Statistical and Business Significance:**
- **Statistically:** The effect is significant at the 5% level. The estimated effect (0.88 percentage points) is slightly below the designed MDE (1 percentage point), and the confidence interval is relatively wide (0.34 to 1.42), so the true effect size is not precisely determined.
- **Business-wise:** Increasing the conversion rate means direct growth in the number of subscribers, and the ~0.80 SAR increase in revenue per user indicates that growth did not come at the expense of subscription value. There is no evidence of an increase in cancellations.

## Final Recommendation
**Launch** the free trial option to all users, because it increased both the conversion rate and revenue per user with statistical significance without evidence of harm to guardrail metrics. It is recommended to monitor the cancellation rate post-launch, as cancellation in this simulation is simplified.

## Limitations and Assumptions
- **Simulated Data:** Results are for training purposes and do not reflect real user behavior.
- **Simulated Effect and MDE:** The true effect assumed in the simulation (1.2 percentage points) is slightly larger than the MDE (1 percentage point), while the estimated effect in this sample is 0.88 percentage points due to random variation.
- **Simplified Cancellation:** Immediate cancellation was assumed as a fixed probability, and actual behavior was not tracked over the 7-day trial period.
- **Revenue Distribution:** The simulation assumed that subscribers in both groups have the same revenue distribution, whereas free trial users might choose different plans in reality. Therefore, the increase in revenue per user is solely due to higher conversion.
- **Non-Significance Does Not Mean Equivalence:** The lack of a significant difference in cancellations means there is no evidence of harm, not proof that the two groups are equal.

## How to Run
From the terminal:

```bash
pip install -r requirements.txt
python main.py
```

The script will automatically create the directories, save the generated data in `data/dataset.csv`, the charts in `outputs/charts/`, and the text results in `outputs/results/`.

## Repository Structure
```
Athkax_program/
├── README.md
├── main.py                  # Main script: data generation, checks, analysis, and charts
├── requirements.txt         # numpy, pandas, scipy, matplotlib
├── data/
│   └── dataset.csv          # Simulated data
└── outputs/
    ├── charts/
    │   ├── conversion_rates.png
    │   └── revenue_distribution.png
    └── results/
        └── analysis_summary.txt
```

## About the Program
This project was completed as part of the "Experiments, A/B Testing, and Causal Inference" program at SDAIA Academy, November 2026.
SDAIA Academy GitHub: https://github.com/SDAIAAcademy
