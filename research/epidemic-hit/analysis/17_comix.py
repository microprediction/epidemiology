"""How long do busy phases last? CoMix UK panel (Zenodo 13684044): the same people surveyed repeatedly, 2020-22.

Activity of person p on survey day t: number of contacts recorded (capped at CAP), divided by the mean for the same
calendar week and age band, so lockdowns and seasons drop out. Adults 18-69 in the diary, with consistent gender and
age band across rounds (panel + panel_id identifies the person).
Within-person covariance of deviations d = a - 1 at time lags l between surveys:
    C(0) = sp2 + ss2 + sn2,     C(l) = sp2 + ss2 exp(-kappa l)   for l >= 7 days,
persistent variance sp2, switching (transient) variance ss2 with correlation time 1/kappa, and day-to-day noise sn2.
The Green-Kubo number of the switching part is K = ss2 / kappa."""
import numpy as np, pandas as pd, os, json
from scipy.optimize import least_squares
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data", "comix")
CAP = int(os.environ.get("CAP", 100))
e = pd.read_csv(os.path.join(D, "CoMix_uk_participant_extra.csv"), usecols=["part_id", "survey_round", "panel", "panel_id"])
c = pd.read_csv(os.path.join(D, "CoMix_uk_participant_common.csv"))
s = pd.read_csv(os.path.join(D, "CoMix_uk_sday.csv"))
x = e.merge(c, on="part_id").merge(s[["part_id", "sday_id"]], on="part_id")
x["date"] = pd.to_datetime(x.sday_id, format="%Y.%m.%d")
x["person"] = x.panel + "_" + x.panel_id.astype(str)
n = pd.read_csv(os.path.join(D, "CoMix_uk_contact_common.csv"), usecols=["part_id"]).part_id.value_counts()
x["contacts"] = x.part_id.map(n).fillna(0).clip(upper=CAP)
adult = ["18-29", "30-39", "40-49", "50-59", "60-69"]
x = x[x.part_age.isin(adult)]
g = x.groupby("person").agg(ng=("part_gender", "nunique"), na=("part_age", "nunique"), n=("part_id", "size"))
keep = g[(g.ng == 1) & (g.na <= 2) & (g.n >= 3)].index
x = x[x.person.isin(keep)].copy()
x["week"] = x.date.dt.to_period("W")
x["a"] = x.contacts / x.groupby(["week", "part_age"]).contacts.transform("mean")
x = x[np.isfinite(x.a)]
x["d"] = x.a - 1
print(f"CAP {CAP}: {x.person.nunique()} adults, {len(x)} survey days, mean contacts {x.contacts.mean():.2f}, CV^2 of a {x.a.var():.2f}")
# pairs within person
edges = [7, 14, 21, 28, 42, 56, 84, 112, 168, 224, 336, 448, 700]
sums = np.zeros(len(edges) - 1); cnts = np.zeros(len(edges) - 1)
for _, g in x.groupby("person"):
    t = g.date.values.astype("datetime64[D]").astype(int); d = g.d.values
    i, j = np.triu_indices(len(t), 1)
    lag = np.abs(t[j] - t[i]); prod = d[i] * d[j]
    k = np.searchsorted(edges, lag, side="right") - 1
    ok = (k >= 0) & (k < len(sums))
    np.add.at(sums, k[ok], prod[ok]); np.add.at(cnts, k[ok], 1)
C = sums / cnts; mid = np.array([(edges[i] + edges[i + 1]) / 2 for i in range(len(C))])
C0 = float((x.d ** 2).mean())
print(f"C(0) = {C0:.3f}")
for m_, c_, n_ in zip(mid, C, cnts):
    print(f"  lag {m_:6.0f} d: C = {c_:.3f}  (pairs {int(n_)})")
res = least_squares(lambda p: (p[0] + p[1] * np.exp(-mid / p[2]) - C) * np.sqrt(cnts / cnts.max()), [C[-1], C[0] - C[-1], 30],
                    bounds=([0, 0, 1], [10, 10, 2000]))
sp2, ss2, tau = res.x; sn2 = C0 - sp2 - ss2
print(f"persistent sp2 = {sp2:.3f}, switching ss2 = {ss2:.3f} with correlation time {tau:.0f} days, day-to-day noise sn2 = {sn2:.3f}")
print(f"K (switching) = ss2 * tau = {ss2 * tau:.1f} days;  shares of C(0): persistent {sp2/C0:.2f}, switching {ss2/C0:.2f}, daily {sn2/C0:.2f}")
json.dump(dict(CAP=CAP, C0=C0, lag_mid=mid.tolist(), C=C.tolist(), pairs=cnts.tolist(), sp2=sp2, ss2=ss2, tau=tau, sn2=sn2),
          open(os.path.join(HERE, "out", f"17_comix_cap{CAP}.json"), "w"), indent=1)
