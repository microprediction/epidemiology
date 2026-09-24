"""Age structure and within-age activity together, with no fitting.

Age groups: Prem et al. (2021) matrix M. Within each age band, activity a is gamma with mean 1 and CV^2 from POLYMOD
(15_polymod.py pooled: 0-19 0.53, 20-64 0.63, 65+ 0.77; all contacts), discretized into 12 equal-probability bins.
A person of age i and activity a meets people of age j at rate a M_ij, weighted by the partners' activity:
next-generation operator K[(i,a),(j,b)] = a M_ij b w_b / <b>, w the bin weights. lam is computed by the same
eigenvector formula as for age alone (12_age.py), applied to the joint (age, activity) structure, and checked by
simulating the joint SIR to the peak. This is the frozen (persistent) case: activity held for the whole wave."""
import numpy as np, pandas as pd, os, importlib.util
from scipy.stats import gamma
from scipy.integrate import solve_ivp
HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("a", os.path.join(HERE, "12_age.py")); A = importlib.util.module_from_spec(s); s.loader.exec_module(A)
CV2 = {"0-19": 0.53, "20-64": 0.63, "65+": 0.77}
band = ["0-19"] * 4 + ["20-64"] * 9 + ["65+"] * 3
NB = 12


def bins(cv2):
    k = 1 / cv2; q = (np.arange(NB) + 0.5) / NB
    a = gamma.ppf(q, k, scale=1 / k); return a / a.mean()


def joint(M, n):
    acts = [bins(CV2[b]) for b in band]
    idx = [(i, k) for i in range(16) for k in range(NB)]
    K = np.zeros((16 * NB, 16 * NB)); pop = np.zeros(16 * NB)
    for x, (i, k) in enumerate(idx):
        pop[x] = n[i] / NB
        for y, (j, l) in enumerate(idx):
            K[x, y] = acts[i][k] * M[i, j] * acts[j][l] / NB
    return K, pop


def lam_of(K, pop):
    w, V = np.linalg.eig(K); v = np.abs(V[:, np.argmax(w.real)].real)
    wl, U = np.linalg.eig(K.T); u = np.abs(U[:, np.argmax(wl.real)].real)
    return (u @ v ** 2 / (u @ v)) / (pop @ v)


def peak_attack(K, pop, R, gamma_=0.2):
    rho = np.max(np.linalg.eigvals(K).real); beta = R * gamma_ / rho; m = len(pop)
    f = lambda t, y: np.r_[-beta * y[:m] * (K @ y[m:]), beta * y[:m] * (K @ y[m:]) - gamma_ * y[m:]]
    sol = solve_ivp(f, (0, 3000), np.r_[np.ones(m) - 1e-8, np.full(m, 1e-8)], rtol=1e-8, atol=1e-14, dense_output=True, max_step=2)
    t = np.linspace(0, 3000, 30001); Y = sol.sol(t); k = int(np.argmax(pop @ Y[m:]))
    return float(pop @ (1 - Y[:m, k])), float(pop @ (1 - Y[:m, -1]))


if __name__ == "__main__":
    for c in ["USA", "SWE", "ESP", "GBR", "BRA"]:
        M = pd.read_csv(os.path.join(HERE, "..", "data", "contacts", f"prem2021_all_{c}.csv")).values.astype(float)
        N = A.pop16(c); n = N / N.sum()
        K, pop = joint(M, n); lam = lam_of(K, pop)
        line = f"{c}: lam (age x activity, frozen) {lam:.2f}"
        for R in (1.3, 1.6, 2.5):
            a, z = peak_attack(K, pop, R)
            line += f" | R {R}: peak {a:.3f} rule {1 - R ** (-1 / lam):.3f} final {z:.3f} textbook {1 - 1 / R:.3f}"
        print(line, flush=True)
