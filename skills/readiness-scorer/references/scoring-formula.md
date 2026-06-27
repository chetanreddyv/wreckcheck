# Scoring Formula & Readiness Tiers

This reference document defines the complete point deduction table, calculation constraints, and enterprise readiness tier thresholds required for generating a ReadinessScorer report.

---

## 1. Deduction Table

Start at **100 points** for each individual sub-score (Security Score, Architecture Score, and Safety Score). Deduct points for every identified finding based on its severity and originating agent:

### CodeSentinel Deductions (Security Score)

| Severity | Points Deducted |
| :--- | :--- |
| 🔴 **CRITICAL** | −25 per finding |
| 🟠 **HIGH** | −15 per finding |
| 🟡 **MEDIUM** | −8 per finding |
| 🔵 **LOW** | −3 per finding |
| ⚪ **INFO** | −0 (no deduction) |

### ArchitectReview Deductions (Architecture Score)

| Severity | Points Deducted |
| :--- | :--- |
| 🔴 **CRITICAL** | −25 per finding |
| 🟠 **HIGH** | −15 per finding |
| 🟡 **MEDIUM** | −8 per finding |
| 🔵 **LOW** | −3 per finding |
| ⚪ **INFO** | −0 (no deduction) |

### HarnessGuard Deductions (Safety Score)

| Severity | Points Deducted |
| :--- | :--- |
| 🔴 **CRITICAL** | −25 per finding |
| 🟠 **HIGH** | −15 per finding |
| 🟡 **MEDIUM** | −8 per finding |
| 🔵 **LOW** | −3 per finding |
| ⚪ **INFO** | −0 (no deduction) |

> **Score Floor**: The score floor for all sub-scores and the final score is strictly **0**. Scores cannot drop below zero.

---

## 2. Calculation Procedure

1. **Calculate Security Score** (from CodeSentinel):
   $$\text{Security Score} = \max(0, 100 - \sum \text{CodeSentinel Deductions})$$

2. **Calculate Architecture Score** (from ArchitectReview):
   $$\text{Architecture Score} = \max(0, 100 - \sum \text{ArchitectReview Deductions})$$

3. **Calculate Safety Score** (from HarnessGuard):
   $$\text{Safety Score} = \max(0, 100 - \sum \text{HarnessGuard Deductions})$$

4. **Compute Weighted Final Score**:
   Carry intermediate values to two decimal places:
   $$\text{Raw Final Score} = (\text{Security Score} \times 0.40) + (\text{Architecture Score} \times 0.30) + (\text{Safety Score} \times 0.30)$$

5. **Apply Caps and Floors**:
   - If all three agents returned a `FAIL` verdict: set Final Score = **0**.
   - If CodeSentinel returned a `FAIL` verdict (but others did not): cap Final Score at **49** ($\min(\text{Raw Final Score}, 49)$).

6. **Round Final Score**: Round the resultant integer to the nearest whole number.

---

## 3. Readiness Tiers

Map the final integer score to its corresponding deployment tier and recommendation:

| Score | Tier Label | Recommendation | Action Required |
| :---: | :--- | :--- | :--- |
| **80–100** | ✅ Production Ready | Approve for deployment | None. Proceed with production release. |
| **60–79** | ⚠️ Conditionally Ready | Fix WARN items before deploy | Allow staging deployment; require fix verification before production. |
| **40–59** | 🔶 Needs Significant Work | Block deploy; address HIGHs first | Block release. Prioritize remediating HIGH and FAIL findings. |
| **0–39** | 🚨 Not Ready | Block; escalate CRITICALs immediately | Immediate engineering escalation. Major security or architectural blockers present. |
