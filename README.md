# epidemiology

Site: https://epidemiology.microprediction.org

Why epidemics turn over long before the herd-immunity threshold their early growth implies, and a one-parameter rule
for where they turn: the threshold 1 - R^(-1/lam), with lam the immunity factor.

- `docs/`: the site (GitHub Pages). Built from `tools/pages/` by `python3 tools/assemble.py`; check with
  `node docs/header-check.js`.
- `research/epidemic-hit/`: the analysis. `fetch_data.py` and `fetch/` download every data set from its primary
  source into `research/epidemic-hit/data/` (not committed). `analysis/` holds numbered scripts; `FINDINGS.md` is the
  dated log.

Origin: P. Cotton, "A Fundamental Theorem for Epidemiology" (27 May 2020) and "Addressing the Herd Immunity Paradox
Using Symmetry, Convexity Adjustments and Bond Prices", arXiv:2006.07341.
