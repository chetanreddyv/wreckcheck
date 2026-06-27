# Scoring Formula & Readiness Tiers

This reference document defines the complete point deduction table, calculation constraints, and enterprise readiness tier thresholds required for generating a ReadinessScorer report.

---

## 1. Deduction Table

Start at **100 points** for each individual sub-score (Security Score and Architecture Score). Deduct points for every identified finding based on its severity and originating agent:

| Severity | Source | Points Deducted |
| :--- | :--- | :--- |
| 🔴 **CRITICAL** | CodeSentinel | −25 per finding |
| 🟠 **HIGH** | CodeSentinel | −15 per finding |
| 🟡 **MEDIUM** | CodeSentinel | −8 per finding |
| 🔵 **LOW** | CodeSentinel | −3 per finding |
| 🚨 **FAIL** | ArchitectReview | −20 per failed check |
| ⚠️ **WARN** | ArchitectReview | −7 per warning |
| ⚪ **INFO** | Either | −0 (no deduction) |

> **Score Floor**: The score floor for both sub-scores and the final score is strictly **0**. Scores cannot drop below zero.

---

## 2. Calculation Procedure

1. **Calculate Security Score**:
   $$\text{Security Score} = \max(0, 100 - \sum \text{CodeSentinel Deductions})$$

2. **Calculate Architecture Score**:
   $$\text{Architecture Score} = \max(0, 100 - \sum \text{ArchitectReview Deductions})$$

3. **Compute Weighted Final Score**:
   Carry intermediate values to two decimal places:
   $$\text{Raw Final Score} = (\text{Security Score} \times 0.60) + (\text{Architecture Score} \times 0.40)$$

4. **Apply Caps and Floors**:
   - If both CodeSentinel and ArchitectReview returned a `FAIL` verdict: set Final Score = **0**.
   - If CodeSentinel returned a `FAIL` verdict (but ArchitectReview did not): cap Final Score at **49** ($\min(\text{Raw Final Score}, 49)$).

5. **Round Final Score**: Round the resultant integer to the nearest whole number.

---

## 3. Readiness Tiers

Map the final integer score to its corresponding deployment tier and recommendation:

| Score | Tier Label | Recommendation | Action Required |
| :---: | :--- | :--- | :--- |
| **80–100** | ✅ Production Ready | Approve for deployment | None. Proceed with production release. |
| **60–79** | ⚠️ Conditionally Ready | Fix WARN items before deploy | Allow staging deployment; require fix verification before production. |
| **40–59** | 🔶 Needs Significant Work | Block deploy; address HIGHs first | Block release. Prioritize remediating HIGH and FAIL findings. |
| **0–39** | 🚨 Not Ready | Block; escalate CRITICALs immediately | Immediate engineering escalation. Major security or architectural blockers present. |
