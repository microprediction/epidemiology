"""Predicted immunity factor from the CoMix decomposition, no epidemic data used.

Within-age activity variance that acts like fixed heterogeneity during a wave growing at rate r:
    CV2_eff = sp2 + rho * ss2,   rho = r / (r + 1/tau),
with the persistent sp2, the switching ss2 and its correlation time tau from 17_comix.py; day-to-day noise
(correlation time under a week) is left out. The joint age x activity lambda follows 16_age_activity.py with the UK
Prem matrix and the same CV2_eff in every age band. Also reported: the frozen value with all of sp2 + ss2."""
import numpy as np, pandas as pd, os, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
def mod(n):
    s = importlib.util.spec_from_file_location(n, os.path.join(HERE, n + ".py")); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
J, A = mod("16_age_activity"), mod("12_age")
M = pd.read_csv(os.path.join(HERE, "..", "data", "contacts", "prem2021_all_GBR.csv")).values.astype(float)
N = A.pop16("GBR"); n = N / N.sum()
print(f"{'cap':>4} {'r/day':>6} {'CV2_eff':>8} {'lam (age x activity)':>21} {'turnover R=1.6':>15} {'R=2.5':>7}")
for cap in (20, 50, 100):
    f = json.load(open(os.path.join(HERE, "out", f"17_comix_cap{cap}.json")))
    for r in (0.02, 0.05, 0.1, 0.2, None):
        cv2 = f["sp2"] + f["ss2"] if r is None else f["sp2"] + r / (r + 1 / f["tau"]) * f["ss2"]
        J.CV2 = {"0-19": cv2, "20-64": cv2, "65+": cv2}
        K, pop = J.joint(M, n); lam = J.lam_of(K, pop)
        lab = "frozen" if r is None else f"{r:.2f}"
        print(f"{cap:4d} {lab:>6} {cv2:8.2f} {lam:21.2f} {1 - 1.6 ** (-1 / lam):15.3f} {1 - 2.5 ** (-1 / lam):7.3f}", flush=True)
