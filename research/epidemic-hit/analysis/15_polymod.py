"""Independent proxy for activity heterogeneity: POLYMOD contact diaries (Mossong et al. 2008).

Activity of a participant = number of contacts recorded on the diary day, relative to the mean of their age band.
CV^2 within age bands (0-19, 20-64, 65+), by country, for all contacts and for close contacts (physical, or at
least 15 minutes). With activity scaling both susceptibility and infectivity and gamma-distributed:
lam_persistent = 1 + 2 CV^2 if the one-day activity persisted, and lam = 1 if it reshuffled immediately; the
measured one-day CV^2 bounds the frozen case. Weekday and weekend are pooled with POLYMOD's day-of-week mix."""
import numpy as np, pandas as pd, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "polymod")
p = pd.read_csv(os.path.join(D, "2008_Mossong_POLYMOD_participant_common.csv"))
h = pd.read_csv(os.path.join(D, "2008_Mossong_POLYMOD_hh_common.csv"))
c = pd.read_csv(os.path.join(D, "2008_Mossong_POLYMOD_contact_common.csv"))
p = p.merge(h[["hh_id", "country"]], on="hh_id", how="left")
c["close"] = (c.phys_contact == 1) | (c.duration_multi >= 3)
n_all = c.groupby("part_id").size(); n_close = c[c.close].groupby("part_id").size()
p["all"] = p.part_id.map(n_all).fillna(0); p["close"] = p.part_id.map(n_close).fillna(0)
p["band"] = pd.cut(p.part_age, [-1, 19, 64, 120], labels=["0-19", "20-64", "65+"])
p = p.dropna(subset=["band"])
def cv2(x):
    return x.var() / x.mean() ** 2 if x.mean() > 0 else np.nan
rows = []
for (cty, band), g in p.groupby(["country", "band"], observed=True):
    rows.append(dict(country=cty, band=band, n=len(g), mean_all=g["all"].mean(), cv2_all=cv2(g["all"]),
                     mean_close=g["close"].mean(), cv2_close=cv2(g["close"])))
T = pd.DataFrame(rows)
print(T.to_string(index=False, float_format=lambda v: f"{v:.2f}"))
w = p.groupby("band", observed=True).apply(lambda g: pd.Series(dict(cv2_all=cv2(g["all"]), cv2_close=cv2(g["close"]), n=len(g))))
print("\npooled over countries:\n", w.to_string(float_format=lambda v: f"{v:.2f}"))
adult = T[T.band == "20-64"]
print(f"\nadults 20-64: median CV^2 all {adult.cv2_all.median():.2f} -> 1 + 2 CV^2 = {1 + 2 * adult.cv2_all.median():.2f}; "
      f"close {adult.cv2_close.median():.2f} -> {1 + 2 * adult.cv2_close.median():.2f}")
T.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "15_polymod.csv"), index=False)
