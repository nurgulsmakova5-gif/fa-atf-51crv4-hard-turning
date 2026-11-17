"""CV-based split-free conformal intervals with row-wise, grouped row-level and grouped
cluster-level calibration, evaluated by leave-one-group-out (Section 3.4)."""
import numpy as np, pandas as pd, math
from sklearn.model_selection import KFold, GroupKFold, LeaveOneGroupOut
from common import load_tasks, models
ALPHA = 0.1

def qhat(scores, alpha=ALPHA):
    n = len(scores); k = math.ceil((n + 1) * (1 - alpha))
    return np.inf if k > n else np.sort(scores)[k - 1]

rows, detail = [], []
for name, t in load_tasks().items():
    if t['cls']: continue
    X, y, g = t['X'], t['y'], t['g']; sd = y.std()
    fac = lambda: models(False)['RF']
    res = {v: [] for v in ('row', 'grouped_row', 'grouped_cluster')}
    for tr, te in LeaveOneGroupOut().split(X, y, g):
        Xtr, ytr, gtr = X[tr], y[tr], g[tr]
        n_cal_groups = len(np.unique(gtr))
        f = fac().fit(Xtr, ytr); pte = f.predict(X[te])
        for v in res:
            inner = (KFold(5, shuffle=True, random_state=0).split(Xtr) if v == 'row'
                     else GroupKFold(5, shuffle=True, random_state=0).split(Xtr, ytr, gtr))
            oofp = np.empty(len(ytr))
            for a, b in inner:
                m = fac().fit(Xtr[a], ytr[a]); oofp[b] = m.predict(Xtr[b])
            r = np.abs(ytr - oofp)
            s = np.array([r[gtr == k].max() for k in np.unique(gtr)]) if v == 'grouped_cluster' else r
            q = qhat(s)
            cov = np.abs(y[te] - pte) <= q
            res[v].append((cov.mean(), cov.all(), len(te), 2 * q / sd))
            detail.append(dict(task=name, variant=v, group=g[te][0], n_obs=len(te), n_cal_groups=n_cal_groups,
                               n_scores=len(s), k_index=math.ceil((len(s) + 1) * (1 - ALPHA)), q=q,
                               width_sd=2 * q / sd, coverage=cov.mean(), all_covered=bool(cov.all())))
    for v, lst in res.items():
        c, a, n, w = map(np.array, zip(*lst))
        rows.append(dict(task=name, variant=v, marginal=float((c * n).sum() / n.sum()), simultaneous=float(a.mean()),
                         width_sd=float(np.mean(w)), n_groups=len(lst)))
    print(name, flush=True)
pd.DataFrame(rows).to_csv('results/conformal.csv', index=False)
pd.DataFrame(detail).to_csv('results/conformal_detail.csv', index=False)
print(pd.DataFrame(rows).round(3))
