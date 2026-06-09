# PEC Cavity Convergence Plot

This animation shows grid refinement for a rectangular PEC cavity reference case.

The cavity dimensions are 80 mm x 84 mm x 84 mm. The mode is the 111 scalar reference diagnostic. The analytical reference frequency is computed from the closed-form rectangular PEC cavity formula.

The numerical sequence is computed with a deterministic finite-difference scalar diagnostic. The error curve is computed from the numerical values and the analytical reference; it is not drawn by hand.

The animation demonstrates convergence behavior:

| Grid | Numerical frequency (GHz) | Relative error (%) |
| --- | ---: | ---: |
| 8^3 | 3.127232556 | 0.506923 |
| 12^3 | 3.135523195 | 0.243156 |
| 16^3 | 3.138695318 | 0.142235 |
| 20^3 | 3.140235798 | 0.093224 |

This is a bounded diagnostic. It is not external validation, not production readiness, not a validated eigenmode claim, and not a production full-wave solver claim.

No external images were used. No screenshots were used. No generative image tools were used. No private source code is published.

Copyright &copy; 2026 Harun Aktas. All rights reserved.
