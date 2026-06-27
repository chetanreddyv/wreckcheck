# Context Flags & Override Policy

This reference document defines how project context flags provided by the Scout agent adjust, waive, or downgrade specific audit findings during point deduction calculations.

---

## 1. Override Rules Table

When Scout outputs specific environmental or architectural flags, apply the following modifications before totaling point deductions:

| Context Flag | Target Check / Finding | Override Action | Adjusted Deduction |
| :--- | :--- | :--- | :--- |
| `internal-only: true` | Missing license or open-source header check | Downgrade severity from **HIGH** → **LOW** | −3 pts (instead of −15 pts) |
| `no-external-deps: true` | Supply-chain security checks (AG06) | Disable check entirely | −0 pts (waived) |
| `eval-harness-planned: true` | Missing evaluation harness / benchmark suites | Downgrade severity from **HIGH** → **MEDIUM** | −8 pts (instead of −15 pts) |
| `observability-waived: true` | Monitoring and telemetry checks (AG07) | Disable check entirely | −0 pts (waived) |

---

## 2. Default Impact Rule

If no context flags are provided by Scout, or if a finding does not match any targeted target check in the table above, apply all checks at their **default baseline impact** as defined in the Deduction Table.

---

## 3. Dispute Resolution & Top-3 Ranking

When applying overrides:
1. Recalculate each finding's effective point deduction after applying downgrades or waivers.
2. Sort the **Top-3 Gaps** in the final report based strictly on the *adjusted* point deduction. Waived findings (0 pts) must never appear in the Top-3 Gaps list.
