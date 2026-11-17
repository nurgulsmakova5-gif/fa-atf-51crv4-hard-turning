"""Non-nested vs nested grouped model selection over twelve configurations (Section 3.3, Table A1)."""
import numpy as np, pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.compose import TransformedTargetRegressor
from common import load_tasks, nrmse

def configs():
    c = {}
    for mf in (1.0, 'sqrt'):
        for leaf in (1, 3, 5):
            c[f'RF(max_features={mf}, min_samples_leaf={leaf})'] = (lambda mf=mf, leaf=leaf:
                RandomForestRegressor(n_estimators=200, max_features=mf, min_samples_leaf=leaf, random_state=0, n_jobs=1))
    for k in (3, 7):
        c[f'kNN(k={k})'] = lambda k=k: make_pipeline(StandardScaler(), KNeighborsRegressor(n_neighbors=k))
    for a in (0.1, 10.0):
        c[f'QuadRidge(alpha={a})'] = lambda a=a: make_pipeline(StandardScaler(), PolynomialFeatures(2), StandardScaler(), Ridge(alpha=a))
    for C in (1.0, 10.0):
        c[f'SVR(C={C})'] = lambda C=C: TransformedTargetRegressor(make_pipeline(StandardScaler(), SVR(C=C, epsilon=0.1, gamma='scale')), transformer=StandardScaler())
    return c

def cv_pred(fac, X, y, folds):
    p = np.empty(len(y))
    for tr, te in folds:
        m = fac(); m.fit(X[tr], y[tr]); p[te] = m.predict(X[te])
    return p

if __name__ == '__main__':
    C = configs(); assert len(C) == 12
    rows, sel = [], []
    for name, t in load_tasks().items():
        if t['cls']: continue
        X, y, g = t['X'], t['y'], t['g']
        for rep in range(10):
            outer = list(GroupKFold(t['k'], shuffle=True, random_state=100 + rep).split(X, y, g))
            errs = {k: nrmse(y, cv_pred(f, X, y, outer)) for k, f in C.items()}
            best = min(errs, key=errs.get)
            p = np.empty(len(y))
            for i, (tr, te) in enumerate(outer):
                inner = list(GroupKFold(4, shuffle=True, random_state=rep).split(X[tr], y[tr], g[tr]))
                ie = {k: nrmse(y[tr], cv_pred(f, X[tr], y[tr], inner)) for k, f in C.items()}
                kbest = min(ie, key=ie.get); sel.append(dict(task=name, rep=rep, fold=i, selected=kbest))
                m = C[kbest](); m.fit(X[tr], y[tr]); p[te] = m.predict(X[te])
            nested = nrmse(y, p)
            rows.append(dict(task=name, rep=rep, non_nested=errs[best], nested=nested, best_non_nested=best,
                             rel=(errs[best] - nested) / nested))
            print(name, rep, round(errs[best], 3), round(nested, 3), flush=True)
    pd.DataFrame(rows).to_csv('results/nested_runs.csv', index=False)
    pd.DataFrame(sel).to_csv('results/nested_selected.csv', index=False)
